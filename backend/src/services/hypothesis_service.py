import csv,io,json
from sqlalchemy import select
from fastapi import HTTPException
from src.models import RetrofitHypothesis,DriverFinding,ModelRun
from src.constants.enums import HypothesisStatus
def list_hypotheses(db):return db.scalars(select(RetrofitHypothesis).order_by(RetrofitHypothesis.id.desc())).all()
def create_hypothesis(db,data):
    finding=db.get(DriverFinding,data.finding_id)
    if not finding:raise HTTPException(404,'驱动解释不存在，请先完成研究')
    if db.scalar(select(RetrofitHypothesis).where(RetrofitHypothesis.title==data.title)):raise HTTPException(409,'假设标题已存在')
    item=RetrofitHypothesis(**data.model_dump(),status=HypothesisStatus.DRAFT);db.add(item);db.commit();return item
def approve_hypothesis(db,id,user):
    item=db.get(RetrofitHypothesis,id)
    if not item:raise HTTPException(404,'改造假设不存在')
    item.status=HypothesisStatus.APPROVED;item.approved_by=user.email;db.commit();return item
def export_hypothesis(db,id):
    item=db.get(RetrofitHypothesis,id)
    if not item:raise HTTPException(404,'改造假设不存在')
    if item.status!=HypothesisStatus.APPROVED:raise HTTPException(409,'负责人审阅后才能导出')
    finding=db.get(DriverFinding,item.finding_id);run=db.get(ModelRun,finding.run_id)
    def safe(value):
        value=str(value);return "'"+value if value.startswith(('=','+','-','@','\t','\r')) else value
    out=io.StringIO();out.write('\ufeff');writer=csv.writer(out);writer.writerow(['feature','coefficient_per_original_unit','permutation_delta_mae','repeat_low','repeat_high','repeated_deltas','action','verification','approved_by','model_input_fingerprint','selection_fingerprint'])
    writer.writerow([finding.feature,finding.coefficient,finding.importance_mean,finding.importance_low,finding.importance_high,json.dumps(finding.repeats),safe(item.action),safe(item.verification),safe(item.approved_by),run.result['input_fingerprint'],run.result['selection_fingerprint']]);return out.getvalue()
