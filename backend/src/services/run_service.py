import json,hashlib
from sqlalchemy import select
from fastapi import HTTPException
from redis import Redis
from src.config.settings import REDIS_URL
from src.constants.enums import RunStatus
from src.models import BuildingDataset,ModelRun,DriverFinding
from src.services.day_service import raw_days
from src.services.splitting import training_arrays
from src.services.learning import fit_grouped
from src.services.inspection import inspect_holdout
queue=Redis.from_url(REDIS_URL)
def list_runs(db):return db.scalars(select(ModelRun).order_by(ModelRun.id.desc())).all()
def get_run(db,id):
    run=db.get(ModelRun,id)
    if not run:raise HTTPException(404,'模型研究不存在')
    return run
def create_run(db,data):
    dataset=db.scalar(select(BuildingDataset).where(BuildingDataset.id==data.dataset_id).with_for_update())
    if not dataset:raise HTTPException(404,'数据集不存在')
    config=data.config()
    if dataset.locked_config is not None and dataset.locked_config!=config:raise HTTPException(409,'数据集选模配置已锁定；公开封存评估后不得改特征或超参，只能同配置复算')
    if db.scalar(select(ModelRun).where(ModelRun.name==data.name)):raise HTTPException(409,'研究名称已存在')
    try:training_arrays(raw_days(db,dataset.id),config)
    except ValueError as exc:raise HTTPException(422,str(exc))
    dataset.locked_config=config;run=ModelRun(name=data.name,dataset_id=dataset.id,config=config,status=RunStatus.QUEUED);db.add(run);db.commit();queue.lpush('energy:runs',str(run.id));return run
def execute_run(db,id):
    run=db.get(ModelRun,id)
    if not run or run.status not in (RunStatus.QUEUED,RunStatus.RUNNING):return
    run.status=RunStatus.RUNNING;db.commit()
    try:
        dataset=db.get(BuildingDataset,run.dataset_id);rows=raw_days(db,dataset.id)
        model,report=fit_grouped(rows,run.config)
        # The winning configuration and training-only report exist before test targets are inspected.
        metrics,findings,points=inspect_holdout(model,report,rows,run.config)
        snapshot={'algorithm':'elasticnet-building-v1','dataset_id':dataset.id,'rows':rows,'config':run.config,'split':report['split']}
        fingerprint=hashlib.sha256(json.dumps(snapshot,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        # Recovery can rerun an interrupted job; findings are written in the same final transaction.
        existing={f.feature:f for f in db.scalars(select(DriverFinding).where(DriverFinding.run_id==run.id)).all()}
        for values in findings:
            if values['feature'] not in existing:db.add(DriverFinding(run_id=run.id,**values))
        run.result={**report,'metrics':metrics,'points':points,'input_fingerprint':fingerprint,'config':run.config};run.status=RunStatus.COMPLETED;run.error='';dataset.evaluation_released=True;db.commit()
    except Exception as exc:
        db.rollback();run=db.get(ModelRun,id);run.status=RunStatus.FAILED;run.error=str(exc)[:600];db.commit()
