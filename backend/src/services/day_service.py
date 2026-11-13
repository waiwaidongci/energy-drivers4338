from sqlalchemy import select
from fastapi import HTTPException
from src.models import BuildingDataset,BuildingDay
from src.constants.enums import FEATURES
from src.services.splitting import split_buildings
def raw_days(db,dataset_id):
    days=db.scalars(select(BuildingDay).where(BuildingDay.dataset_id==dataset_id).order_by(BuildingDay.building_code,BuildingDay.day)).all()
    return [{'id':d.id,'building_code':d.building_code,'day':d.day,'energy_kwh':d.energy_kwh,**{f:getattr(d,f) for f in FEATURES}} for d in days]
def list_days(db,dataset_id,building,offset,limit):
    dataset=db.get(BuildingDataset,dataset_id)
    if not dataset:raise HTTPException(404,'数据集不存在')
    rows=raw_days(db,dataset_id);split=split_buildings(rows);selected=[r for r in rows if not building or r['building_code']==building]
    output=[]
    for row in selected[offset:offset+limit]:
        sealed=row['building_code'] in split['test_buildings'];output.append({**row,'sealed':sealed,'energy_kwh':row['energy_kwh'] if not sealed or dataset.evaluation_released else None})
    return {'total':len(selected),'rows':output}
