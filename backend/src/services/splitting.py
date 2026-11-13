import numpy as np
from collections import Counter
from src.constants.enums import SPLIT_SEED
from src.services.imputation import median_values
def split_buildings(rows):
    groups=sorted({r['building_code'] for r in rows})
    if len(groups)<8:raise ValueError('至少需要8栋独立楼宇，封存后保留足够训练分组')
    counts=Counter(r['building_code'] for r in rows)
    if min(counts.values())<6:raise ValueError('每栋楼宇至少6天独立记录')
    shuffled=np.random.default_rng(SPLIT_SEED).permutation(groups).tolist();n_test=max(2,int(np.ceil(len(groups)*.25)))
    test=sorted(shuffled[-n_test:]);train=sorted(shuffled[:-n_test])
    return {'train_buildings':train,'test_buildings':test,'seed':SPLIT_SEED,'train_row_ids':[r['id'] for r in rows if r['building_code'] in train],'test_row_ids':[r['id'] for r in rows if r['building_code'] in test]}
def feature_matrix(rows,features):
    """Missing cells stay NaN; energy target is never imputed."""
    return np.array([[np.nan if r[f] is None else r[f] for f in features] for r in rows],float)
def training_arrays(rows,config):
    split=split_buildings(rows);train=[r for r in rows if r['building_code'] in split['train_buildings']]
    x=feature_matrix(train,config['features']);y=np.array([r['energy_kwh'] for r in train],float)
    if not np.isfinite(y).all():raise ValueError('训练目标必须为有限值；能耗缺测不能被补值')
    medians=median_values(x)
    if np.isnan(medians).any():
        raise ValueError(f'训练范围内特征全部缺测（{config["features"][int(np.where(np.isnan(medians))[0][0])]}），无法按训练中位数补值')
    filled=np.where(np.isnan(x),medians,x)
    if (np.std(filled,axis=0)<1e-10).any():raise ValueError('所选训练特征含常量列（或补值后为常量），请在封存前移除')
    if np.std(y)<1e-10:raise ValueError('训练目标为常量，无法进行驱动研究')
    return split,train,x,y,medians
