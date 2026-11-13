import warnings,hashlib,json
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error
from sklearn.exceptions import ConvergenceWarning
from src.constants.enums import CV_SPLITS,SPLIT_SEED
from src.services.splitting import training_arrays
def make_model(alpha,l1_ratio):return Pipeline([('scale',StandardScaler()),('regression',ElasticNet(alpha=alpha,l1_ratio=l1_ratio,max_iter=30000,tol=1e-6,selection='cyclic',random_state=SPLIT_SEED))])
def fit_grouped(rows,config):
    split,train,x,y=training_arrays(rows,config);groups=np.array([r['building_code'] for r in train]);splits=list(GroupKFold(n_splits=CV_SPLITS).split(x,y,groups))
    candidates=[];fold_audit=[]
    for alpha in config['alphas']:
        for l1 in config['l1_ratios']:
            scores=[];converged=True
            for fold,(train_ix,val_ix) in enumerate(splits):
                model=make_model(alpha,l1)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always',ConvergenceWarning);model.fit(x[train_ix],y[train_ix])
                if any(issubclass(w.category,ConvergenceWarning) for w in caught):converged=False
                scores.append(float(mean_absolute_error(y[val_ix],model.predict(x[val_ix]))))
                if len(fold_audit)<CV_SPLITS:
                    fold_audit.append({'fold':fold+1,'train_buildings':sorted(set(groups[train_ix])),'validation_buildings':sorted(set(groups[val_ix])),'train_row_ids':[train[i]['id'] for i in train_ix],'validation_row_ids':[train[i]['id'] for i in val_ix],'scaler_mean':dict(zip(config['features'],model.named_steps['scale'].mean_.tolist())),'scaler_scale':dict(zip(config['features'],model.named_steps['scale'].scale_.tolist()))})
            candidates.append({'alpha':alpha,'l1_ratio':l1,'mean_mae':float(np.mean(scores)),'fold_maes':scores,'converged':converged})
    valid=[c for c in candidates if c['converged']]
    if not valid:raise ValueError('所有候选均未收敛，请检查共线性或调整预先约定的候选范围')
    best=min(valid,key=lambda c:(c['mean_mae'],c['alpha'],c['l1_ratio']))
    model=make_model(best['alpha'],best['l1_ratio'])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always',ConvergenceWarning);model.fit(x,y)
    if any(issubclass(w.category,ConvergenceWarning) for w in caught):raise ValueError('最终训练未收敛，不公开封存评估')
    scale=model.named_steps['scale'];reg=model.named_steps['regression'];coefs=reg.coef_/scale.scale_;intercept=float(reg.intercept_-np.dot(coefs,scale.mean_))
    training_snapshot={'version':'elasticnet-building-v1','config':config,'split':split,'training_rows':[{k:r[k] for k in ['id','building_code','day','energy_kwh',*config['features']]} for r in train]}
    selection_fingerprint=hashlib.sha256(json.dumps(training_snapshot,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    report={'split':split,'folds':fold_audit,'candidates':candidates,'best':best,'final_scaler_mean':dict(zip(config['features'],scale.mean_.tolist())),'final_scaler_scale':dict(zip(config['features'],scale.scale_.tolist())),'final_fit_row_ids':[r['id'] for r in train],'coefficient':dict(zip(config['features'],coefs.tolist())),'standardized_coefficient':dict(zip(config['features'],reg.coef_.tolist())),'intercept':intercept,'selection_fingerprint':selection_fingerprint}
    return model,report
