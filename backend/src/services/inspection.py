import numpy as np
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from src.constants.enums import SPLIT_SEED
from src.services.imputation import missing_summary
from src.services.splitting import feature_matrix
def inspect_holdout(model,report,rows,config):
    test=[r for r in rows if r['building_code'] in report['split']['test_buildings']]
    x=feature_matrix(test,config['features']);y=np.array([r['energy_kwh'] for r in test],float)
    if not np.isfinite(y).all():raise ValueError('封存目标必须为有限值，不能公开评估')
    if not np.isfinite(np.where(np.isnan(x),0.0,x)).all():raise ValueError('封存特征含非有限值，不能公开评估')
    prediction=model.predict(x);baseline=float(mean_absolute_error(y,prediction));findings=[]
    for j,feature in enumerate(config['features']):
        rng=np.random.default_rng(SPLIT_SEED+j);deltas=[]
        for _ in range(config['permutation_repeats']):
            corrupted=x.copy()
            # Permute the filled sealed column exactly as fitted; imputed cells are model inputs too.
            corrupted[:,j]=x[rng.permutation(len(x)),j]
            deltas.append(float(mean_absolute_error(y,model.predict(corrupted))-baseline))
        low,high=np.quantile(deltas,[.025,.975]).tolist()
        findings.append({'feature':feature,'coefficient':report['coefficient'][feature],'standardized_coefficient':report['standardized_coefficient'][feature],'importance_mean':float(np.mean(deltas)),'importance_low':low,'importance_high':high,'repeats':deltas})
    metrics={'mae':baseline,'rmse':float(np.sqrt(mean_squared_error(y,prediction))),'r2':None if np.std(y)<1e-10 else float(r2_score(y,prediction)),'n':len(test),'buildings':report['split']['test_buildings'],'missing':missing_summary(test)}
    points=[{'id':r['id'],'building_code':r['building_code'],'day':r['day'],'actual':float(actual),'prediction':float(pred),'residual':float(actual-pred),'missing_features':[feature for j,feature in enumerate(config['features']) if np.isnan(x[i,j])]} for i,(r,actual,pred) in enumerate(zip(test,y,prediction))]
    return metrics,findings,points

