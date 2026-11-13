from sqlalchemy import select
from fastapi import HTTPException
from src.models import BuildingDataset,BuildingDay,ModelRun
from src.constants.enums import FEATURES,RunStatus
from src.services.imputation import is_missing,missing_summary
from src.services.splitting import split_buildings
def raw_days(db,dataset_id):
    days=db.scalars(select(BuildingDay).where(BuildingDay.dataset_id==dataset_id).order_by(BuildingDay.building_code,BuildingDay.day)).all()
    return [{'id':d.id,'building_code':d.building_code,'day':d.day,'energy_kwh':d.energy_kwh,**{f:getattr(d,f) for f in FEATURES}} for d in days]
def missing_info(rows):
    split=split_buildings(rows);scope={}
    for label,buildings in (('train',split['train_buildings']),('sealed',split['test_buildings'])):
        scope_rows=[r for r in rows if r['building_code'] in buildings]
        summary=missing_summary(scope_rows)
        summary['rows']=len(scope_rows)
        summary['buildings']={b:{'rows':sum(1 for r in scope_rows if r['building_code']==b),'cells':sum(1 for r in scope_rows if r['building_code']==b for f in FEATURES if is_missing(r[f]))} for b in buildings}
        scope[label]=summary
    return {'total':missing_summary(rows),'scope':scope,'basis':'特征缺测按对应训练阶段（每折或最终模型）的训练行中位数补齐；封存特征补值不参与选模'}
def list_days(db,dataset_id,building,offset,limit):
    dataset=db.get(BuildingDataset,dataset_id)
    if not dataset:raise HTTPException(404,'数据集不存在')
    rows=raw_days(db,dataset_id);split=split_buildings(rows);selected=[r for r in rows if not building or r['building_code']==building]
    output=[]
    for row in selected[offset:offset+limit]:
        sealed=row['building_code'] in split['test_buildings'];output.append({**row,'sealed':sealed,'missing_features':[f for f in FEATURES if is_missing(row[f])],'energy_kwh':row['energy_kwh'] if not sealed or dataset.evaluation_released else None})
    result={'total':len(selected),'rows':output,'missing':missing_info(rows)}
    run=db.scalar(select(ModelRun).where(ModelRun.dataset_id==dataset_id,ModelRun.status==RunStatus.COMPLETED).order_by(ModelRun.id.desc()))
    if run and run.result and 'imputation' in run.result:result['imputation']={k:run.result[k] for k in ('imputation','final_impute_values','folds') if k in run.result}
    return result
