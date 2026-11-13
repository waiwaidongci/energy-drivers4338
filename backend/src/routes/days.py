from fastapi import APIRouter,Depends,Query
from src.config.database import get_db
from src.utils.auth import current_user
from src.controllers.day_controller import list_days
router=APIRouter(prefix='/days')
@router.get('')
def index(dataset_id:int,building:str=Query(default='',max_length=60),offset:int=Query(default=0,ge=0),limit:int=Query(default=20,ge=1,le=200),db=Depends(get_db),user=Depends(current_user)):return list_days(db,dataset_id,building,offset,limit)
