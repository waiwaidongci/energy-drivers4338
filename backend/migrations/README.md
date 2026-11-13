# Schema v1

本地启动使用SQLAlchemy metadata创建初始表。自然键：users.email、building_datasets.name、building_days(dataset_id,building_code,day)、model_runs.name、driver_findings(run_id,feature)、retrofit_hypotheses.title。数值测量与解释列使用DOUBLE。

本目录用于后续版本迁移；当前无生产升级迁移工具。真实升级应编写版本化DDL与回滚步骤，不能仅依赖create_all修改现有列。
