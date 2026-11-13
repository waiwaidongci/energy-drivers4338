# Schema v1

本地启动使用SQLAlchemy metadata创建初始表。自然键：users.email、building_datasets.name、building_days(dataset_id,building_code,day)、model_runs.name、driver_findings(run_id,feature)、retrofit_hypotheses.title。数值测量与解释列使用DOUBLE。

## v1.1 特征缺测（兼容增量）

`building_days`的七个特征列改为可空：空CSV单元格保存为NULL，表示该特征缺测，按训练阶段中位数补值。`energy_kwh`仍为NOT NULL且必须为正。已有数据库升级只需放开这七列：

```sql
ALTER TABLE building_days
  MODIFY temperature_c DOUBLE NULL, MODIFY operating_hours DOUBLE NULL,
  MODIFY area_m2 DOUBLE NULL, MODIFY visitors DOUBLE NULL,
  MODIFY humidity_pct DOUBLE NULL, MODIFY equipment_kw DOUBLE NULL,
  MODIFY holiday_flag DOUBLE NULL;
```

回滚前须确认表中没有NULL特征值（或先补齐），再改回 `DOUBLE NOT NULL`。旧数据没有NULL，升级后结果与复算指纹不变。

本目录用于后续版本迁移；当前无生产升级迁移工具。真实升级应编写版本化DDL与回滚步骤，不能仅依赖create_all修改现有列。
