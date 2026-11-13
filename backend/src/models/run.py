from sqlalchemy import String,ForeignKey,JSON,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from src.config.database import Base
class ModelRun(Base):
    __tablename__='model_runs'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(160),unique=True)
    dataset_id:Mapped[int]=mapped_column(ForeignKey('building_datasets.id'))
    config:Mapped[dict]=mapped_column(JSON)
    status:Mapped[str]=mapped_column(String(20),default='queued')
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    error:Mapped[str]=mapped_column(String(600),default='')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
