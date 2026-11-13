from sqlalchemy import String,ForeignKey,Double,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class BuildingDay(Base):
    __tablename__='building_days'
    __table_args__=(UniqueConstraint('dataset_id','building_code','day'),)
    id:Mapped[int]=mapped_column(primary_key=True)
    dataset_id:Mapped[int]=mapped_column(ForeignKey('building_datasets.id'))
    building_code:Mapped[str]=mapped_column(String(60))
    day:Mapped[str]=mapped_column(String(10))
    temperature_c:Mapped[float|None]=mapped_column(Double,nullable=True)
    operating_hours:Mapped[float|None]=mapped_column(Double,nullable=True)
    area_m2:Mapped[float|None]=mapped_column(Double,nullable=True)
    visitors:Mapped[float|None]=mapped_column(Double,nullable=True)
    humidity_pct:Mapped[float|None]=mapped_column(Double,nullable=True)
    equipment_kw:Mapped[float|None]=mapped_column(Double,nullable=True)
    holiday_flag:Mapped[float|None]=mapped_column(Double,nullable=True)
    energy_kwh:Mapped[float]=mapped_column(Double)
