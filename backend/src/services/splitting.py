import numpy as np
from collections import Counter
from src.constants.enums import SPLIT_SEED
def split_buildings(rows):
    groups=sorted({r['building_code'] for r in rows})
    if len(groups)<8:raise ValueError('至少需要8栋独立楼宇，封存后保留足够训练分组')
    counts=Counter(r['building_code'] for r in rows)
    if min(counts.values())<6:raise ValueError('每栋楼宇至少6天独立记录')
    shuffled=np.random.default_rng(SPLIT_SEED).permutation(groups).tolist();n_test=max(2,int(np.ceil(len(groups)*.25)))
    test=sorted(shuffled[-n_test:]);train=sorted(shuffled[:-n_test])
    return {'train_buildings':train,'test_buildings':test,'seed':SPLIT_SEED,'train_row_ids':[r['id'] for r in rows if r['building_code'] in train],'test_row_ids':[r['id'] for r in rows if r['building_code'] in test]}
def training_arrays(rows,config):
    split=split_buildings(rows);train=[r for r in rows if r['building_code'] in split['train_buildings']]
    x=np.array([[r[f] for f in config['features']] for r in train],float);y=np.array([r['energy_kwh'] for r in train],float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('训练特征与目标必须为有限值')
    if (np.std(x,axis=0)<1e-10).any():raise ValueError('所选训练特征含常量列，请在封存前移除')
    if np.std(y)<1e-10:raise ValueError('训练目标为常量，无法进行驱动研究')
    return split,train,x,y
