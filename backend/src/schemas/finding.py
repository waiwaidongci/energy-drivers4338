from pydantic import BaseModel
class FindingSummary(BaseModel):
    id:int
    run_id:int
    feature:str
    coefficient:float
    standardized_coefficient:float
    importance_mean:float
    importance_low:float
    importance_high:float
    repeats:list[float]
    model_config={'from_attributes':True}
