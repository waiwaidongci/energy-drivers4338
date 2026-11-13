import random,math,json
from datetime import date,timedelta
from sqlalchemy import select,func
from src.config.database import Base,engine,Session
from src.models import User,BuildingDataset,BuildingDay,ModelRun,DriverFinding,RetrofitHypothesis
from src.utils.security import hash_password

def seed():
    Base.metadata.create_all(engine);rng=random.Random(97)
    with Session() as db:
        for role,name in [('admin','季砾 · 工程负责人'),('analyst','周山 · 能耗分析员'),('viewer','林岑 · 楼宇联络员')]:
            if not db.scalar(select(User).where(User.email==f'{role}@lishan.demo')):db.add(User(email=f'{role}@lishan.demo',name=name,role=role,password_hash=hash_password('Lishan2026!')))
        name='砾山12栋公共建筑 · 90日能耗特征'
        dataset=db.scalar(select(BuildingDataset).where(BuildingDataset.name==name))
        if not dataset:
            dataset=BuildingDataset(name=name,source_file='ls-energy-days.csv',note='2026-08-01起90日，机构级楼宇日记录；目标为日能耗kWh，固定按楼宇封存。');db.add(dataset);db.flush()
            for b in range(12):
                area=2500+b*350+rng.uniform(-80,80);equipment=40+area*.014+rng.uniform(-3,3);intercept=rng.gauss(0,7)
                for d in range(90):
                    day=date(2026,8,1)+timedelta(days=d);holiday=float(day.weekday()>=5);hours=9-2*holiday+rng.uniform(-1,1);temp=20+9*math.sin(d/18)+b*.12+rng.gauss(0,1.2);visitors=max(0,160+20*(b%4)+25*math.sin(d/7)+rng.gauss(0,30));humidity=max(5,min(95,55+12*math.sin(d/13)+rng.gauss(0,4)))
                    energy=.075*area+24*hours+7*temp+.24*visitors+1.7*equipment-10*holiday+intercept+rng.gauss(0,16)
                    db.add(BuildingDay(dataset_id=dataset.id,building_code=f'LS-{b+1:02d}',day=day.isoformat(),temperature_c=round(temp,3),operating_hours=round(hours,3),area_m2=round(area,2),visitors=round(visitors,0),humidity_pct=round(humidity,3),equipment_kw=round(equipment,3),holiday_flag=holiday,energy_kwh=round(energy,3)))
        db.commit();print(json.dumps({m.__tablename__:db.scalar(select(func.count()).select_from(m)) for m in (User,BuildingDataset,BuildingDay,ModelRun,DriverFinding,RetrofitHypothesis)},ensure_ascii=False))
if __name__=='__main__':seed()
