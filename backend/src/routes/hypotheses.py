from fastapi import APIRouter,Depends,Response
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.hypothesis import HypothesisInput
from src.controllers.hypothesis_controller import list_hypotheses,create_hypothesis,approve_hypothesis,export_hypothesis
router=APIRouter(prefix='/hypotheses')
@router.get('')
def index(db=Depends(get_db),user=Depends(current_user)):return list_hypotheses(db)
@router.post('',status_code=201)
def create(data:HypothesisInput,db=Depends(get_db),user=Depends(editor)):return create_hypothesis(db,data)
@router.patch('/{id}/approve')
def approve(id:int,db=Depends(get_db),user=Depends(admin)):return approve_hypothesis(db,id,user)
@router.get('/{id}/export')
def export(id:int,db=Depends(get_db),user=Depends(current_user)):return Response(export_hypothesis(db,id),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="energy-hypothesis-{id}.csv"'})
