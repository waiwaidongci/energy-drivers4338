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
    temperature_c:Mapped[float]=mapped_column(Double)
    operating_hours:Mapped[float]=mapped_column(Double)
    area_m2:Mapped[float]=mapped_column(Double)
    visitors:Mapped[float]=mapped_column(Double)
    humidity_pct:Mapped[float]=mapped_column(Double)
    equipment_kw:Mapped[float]=mapped_column(Double)
    holiday_flag:Mapped[float]=mapped_column(Double)
    energy_kwh:Mapped[float]=mapped_column(Double)
