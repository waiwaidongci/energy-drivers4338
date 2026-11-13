import csv,io,json,hashlib
from sqlalchemy import select,func
from fastapi import HTTPException
from pydantic import ValidationError
from src.models import BuildingDataset,BuildingDay
from src.schemas.day import DayInput
from src.services.splitting import split_buildings
from src.constants.enums import FEATURES
def list_datasets(db):
    datasets=db.scalars(select(BuildingDataset).order_by(BuildingDataset.id)).all();result=[]
    for d in datasets:
        days=db.scalars(select(BuildingDay).where(BuildingDay.dataset_id==d.id).order_by(BuildingDay.building_code,BuildingDay.day)).all();split=split_buildings([{'id':x.id,'building_code':x.building_code} for x in days])
        result.append({'id':d.id,'name':d.name,'source_file':d.source_file,'note':d.note,'row_count':len(days),'building_count':len(split['train_buildings'])+len(split['test_buildings']),'locked_config':d.locked_config,'evaluation_released':d.evaluation_released,'train_buildings':split['train_buildings'],'test_buildings':split['test_buildings']})
    return result
def create_dataset(db,data):
    if db.scalar(select(BuildingDataset).where(BuildingDataset.name==data.name)):raise HTTPException(409,'数据集名称已存在')
    try:rows=[DayInput.model_validate(r) for r in csv.DictReader(io.StringIO(data.csv_text))]
    except (ValidationError,ValueError,csv.Error) as exc:raise HTTPException(422,f'CSV校验失败：{str(exc)[:300]}')
    if not 48<=len(rows)<=5000:raise HTTPException(422,'需要48–5000行楼宇日数据')
    if len({(r.building_code,r.day) for r in rows})!=len(rows):raise HTTPException(422,'同一楼宇同一天只能出现一次')
    try:split_buildings([{'id':i,'building_code':r.building_code} for i,r in enumerate(rows)])
    except ValueError as exc:raise HTTPException(422,str(exc))
    def digest(items):
        normalized=sorted([[r.building_code,r.day,*[float(getattr(r,f)) for f in (*FEATURES,'energy_kwh')]] for r in items],key=lambda r:(r[0],r[1]))
        return hashlib.sha256(json.dumps(normalized,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    incoming=digest(rows)
    for prior in db.scalars(select(BuildingDataset)).all():
        existing=db.scalars(select(BuildingDay).where(BuildingDay.dataset_id==prior.id)).all()
        if incoming==digest(existing):raise HTTPException(409,'楼宇日内容与已有数据集相同，不能通过重导旧数据重置封存研究')
    d=BuildingDataset(**data.model_dump(exclude={'csv_text'}));db.add(d);db.flush();db.add_all([BuildingDay(dataset_id=d.id,**r.model_dump()) for r in rows]);db.commit();return {'id':d.id,'row_count':len(rows)}
