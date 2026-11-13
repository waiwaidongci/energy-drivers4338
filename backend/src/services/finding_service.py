from sqlalchemy import select
from fastapi import HTTPException
from src.models import DriverFinding,ModelRun
def list_findings(db,run_id=None):
    q=select(DriverFinding)
    if run_id is not None:
        if not db.get(ModelRun,run_id):raise HTTPException(404,'模型研究不存在')
        q=q.where(DriverFinding.run_id==run_id)
    return db.scalars(q.order_by(DriverFinding.run_id.desc(),DriverFinding.importance_mean.desc())).all()
