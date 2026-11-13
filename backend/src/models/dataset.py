from sqlalchemy import String,JSON,Boolean,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from src.config.database import Base
class BuildingDataset(Base):
    __tablename__='building_datasets'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(160),unique=True)
    source_file:Mapped[str]=mapped_column(String(160))
    note:Mapped[str]=mapped_column(String(600),default='')
    locked_config:Mapped[dict|None]=mapped_column(JSON,nullable=True,default=None)
    evaluation_released:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
