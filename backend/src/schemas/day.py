from pydantic import BaseModel,Field,field_validator
from datetime import date
class DayInput(BaseModel):
    building_code:str=Field(min_length=2,max_length=60)
    day:str
    temperature_c:float=Field(ge=-40,le=60,allow_inf_nan=False)
    operating_hours:float=Field(ge=0,le=24,allow_inf_nan=False)
    area_m2:float=Field(gt=0,le=200000,allow_inf_nan=False)
    visitors:float=Field(ge=0,le=1000000,allow_inf_nan=False)
    humidity_pct:float=Field(ge=0,le=100,allow_inf_nan=False)
    equipment_kw:float=Field(ge=0,le=100000,allow_inf_nan=False)
    holiday_flag:float=Field(ge=0,le=1,allow_inf_nan=False)
    energy_kwh:float=Field(gt=0,le=10000000,allow_inf_nan=False)
    @field_validator('day')
    @classmethod
    def valid_day(cls,value):
        if date.fromisoformat(value).isoformat()!=value:raise ValueError('日期须为YYYY-MM-DD')
        return value
