from pydantic import BaseModel,Field
class DatasetInput(BaseModel):
    name:str=Field(min_length=2,max_length=160)
    source_file:str=Field(min_length=2,max_length=160)
    note:str=Field(default='',max_length=600)
    csv_text:str=Field(min_length=20,max_length=2000000)
