from sqlalchemy import String,ForeignKey,Double,JSON,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class DriverFinding(Base):
    __tablename__='driver_findings'
    __table_args__=(UniqueConstraint('run_id','feature'),)
    id:Mapped[int]=mapped_column(primary_key=True)
    run_id:Mapped[int]=mapped_column(ForeignKey('model_runs.id'))
    feature:Mapped[str]=mapped_column(String(60))
    coefficient:Mapped[float]=mapped_column(Double)
    standardized_coefficient:Mapped[float]=mapped_column(Double)
    importance_mean:Mapped[float]=mapped_column(Double)
    importance_low:Mapped[float]=mapped_column(Double)
    importance_high:Mapped[float]=mapped_column(Double)
    repeats:Mapped[list]=mapped_column(JSON)
