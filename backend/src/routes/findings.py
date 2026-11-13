from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user
from src.schemas.finding import FindingSummary
from src.controllers.finding_controller import list_findings
router=APIRouter(prefix='/findings')
@router.get('',response_model=list[FindingSummary])
def index(run_id:int|None=None,db=Depends(get_db),user=Depends(current_user)):return list_findings(db,run_id)
