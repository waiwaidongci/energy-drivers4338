from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor
from src.schemas.dataset import DatasetInput
from src.controllers.dataset_controller import list_datasets,create_dataset
router=APIRouter(prefix='/datasets')
@router.get('')
def index(db=Depends(get_db),user=Depends(current_user)):return list_datasets(db)
@router.post('',status_code=201)
def create(data:DatasetInput,db=Depends(get_db),user=Depends(editor)):return create_dataset(db,data)
