from pydantic import BaseModel,Field,field_validator
from datetime import date
from typing import Optional
MISSING_TOKENS={''}
class DayInput(BaseModel):
    building_code:str=Field(min_length=2,max_length=60)
    day:str
    temperature_c:Optional[float]=Field(default=None,ge=-40,le=60,allow_inf_nan=False)
    operating_hours:Optional[float]=Field(default=None,ge=0,le=24,allow_inf_nan=False)
    area_m2:Optional[float]=Field(default=None,gt=0,le=200000,allow_inf_nan=False)
    visitors:Optional[float]=Field(default=None,ge=0,le=1000000,allow_inf_nan=False)
    humidity_pct:Optional[float]=Field(default=None,ge=0,le=100,allow_inf_nan=False)
    equipment_kw:Optional[float]=Field(default=None,ge=0,le=100000,allow_inf_nan=False)
    holiday_flag:Optional[float]=Field(default=None,ge=0,le=1,allow_inf_nan=False)
    energy_kwh:float=Field(gt=0,le=10000000,allow_inf_nan=False)
    @field_validator('energy_kwh',mode='before')
    @classmethod
    def energy_required(cls,value):
        if value is None or (isinstance(value,str) and value.strip() in MISSING_TOKENS):raise ValueError('能耗目标不能缺测，需填写正的kWh')
        return value
    @field_validator('temperature_c','operating_hours','area_m2','visitors','humidity_pct','equipment_kw','holiday_flag',mode='before')
    @classmethod
    def blank_feature(cls,value):
        # An empty CSV cell is a missing observation, not zero and not an error.
        if isinstance(value,str) and value.strip() in MISSING_TOKENS:return None
        return value
    @field_validator('day')
    @classmethod
    def valid_day(cls,value):
        if date.fromisoformat(value).isoformat()!=value:raise ValueError('日期须为YYYY-MM-DD')
        return value
