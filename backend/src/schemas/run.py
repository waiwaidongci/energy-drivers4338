from pydantic import BaseModel,Field,model_validator
from src.constants.enums import FEATURES
class RunInput(BaseModel):
    name:str=Field(min_length=2,max_length=160)
    dataset_id:int
    features:list[str]=Field(default_factory=lambda:list(FEATURES),min_length=2,max_length=7)
    alphas:list[float]=Field(default_factory=lambda:[.05,.5,5,25],min_length=1,max_length=6)
    l1_ratios:list[float]=Field(default_factory=lambda:[.2,.6,.9],min_length=1,max_length=4)
    permutation_repeats:int=Field(default=20,ge=10,le=40)
    @model_validator(mode='after')
    def config_valid(self):
        import math
        if len(set(self.features))!=len(self.features) or any(f not in FEATURES for f in self.features):raise ValueError('特征非法或重复')
        if any(not math.isfinite(a) or not .00001<=a<=100 for a in self.alphas) or any(not math.isfinite(r) or not 0<r<=1 for r in self.l1_ratios):raise ValueError('alpha需在.00001–100，l1_ratio需在(0,1]')
        self.features=[f for f in FEATURES if f in self.features];self.alphas=sorted(set(self.alphas));self.l1_ratios=sorted(set(self.l1_ratios))
        return self
    def config(self):return self.model_dump(exclude={'name','dataset_id'})
