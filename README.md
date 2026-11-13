# 砾山建筑能耗归因台 · Energy Drivers

在未见楼宇上评估一个经训练楼宇分组验证选择的模型，将特征依赖解释转为可现场验证的改造假设。

砾山公共建筑节能研究组有19位工程分析员，过去将所有楼宇日记录随机拆行，再用回归系数讨论改造。同楼记录泄漏让验证成绩乐观，相关特征系数不稳定，关联被直接当作节能因果。本项目承接机构级楼宇日数据，替代分组建模、最终评估、驱动解释和假设审阅，下游楼宇联络员组织现场复核。使用合成数据，不涉及住户或个人记录。

## 快速启动与角色

```sh
cp .env.example .env
docker compose up -d --build
docker compose ps
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18217，后端 http://localhost:19217，API文档 http://localhost:19217/docs。前端`/api/`由Nginx去前缀代理；直接后端请求不带`/api`。结束：`docker compose down -v --remove-orphans`（删除本题演示数据与卷）。

共用密码`Lishan2026!`。

| 邮箱 | 角色 | 页面与动作 |
|---|---|---|
| admin@lishan.demo | admin / 工程负责人 | 六页；导入、研究、假设、审阅批准、下载 |
| analyst@lishan.demo | analyst / 能耗分析员 | 六页；导入、研究、假设、下载；不能批准 |
| viewer@lishan.demo | viewer / 楼宇联络员 | 六页只读，可下载已审阅假设；不能写入和批准 |

JWT有效8小时，带盐PBKDF2-SHA256密码；独立审计/错误中间件，登录每来源每分钟30次。对外部署前替换演示凭证与JWT密钥。

## 一天的工作

1. 09:00 周山登录，核对`ls-energy-days.csv`的12栋×90日=1080行。
2. 09:05 查看训练/封存分组；LS-03、LS-09、LS-12为封存楼宇，其能耗目标在首次评估公开前隐藏。
3. 09:10 选择7个特征，α=[.05,.5,5,25]、l1_ratio=[.2,.6,.9]、20次置换，提交首次研究。
4. 09:12 系统锁定数据集方案，worker在9栋训练楼宇内作3折GroupKFold比较，每折单独学习StandardScaler。
5. 09:15 用胜出配置重拟合全部810个训练楼宇日，再读取270个封存楼宇日最终成绩。
6. 09:20 核对三栋封存楼宇散点、原单位/标准化系数、每项特征置换ΔMAE及20次分布。
7. 09:30 选“运行时长”等线索，提出运行排程和计量边界复核假设，写明两周独立观察计划。
8. 10:00 季砾用admin审阅，林岑用viewer下载带完整输入与训练选择双指纹的研究CSV。

初始seed只建立原始数据和三账号，第一份模型与解释来自真实提交。完成一次研究后，后续同配置复算会得到相同结果。

## 分组、封存与配置锁

- 原始行以`(dataset_id,building_code,day)`唯一；至少8栋、每栋至少6天，总计48–5000行。日期YYYY-MM-DD；七特征有限且在schema规定量程内，能耗目标为正。
- 按排序楼宇代码用seed97排列，最后约25%楼宇（至少2栋）封存，其余训练；12栋时为9/3分组。模型不会把同楼日期拆到训练与封存两侧。
- 训练组内部用3折GroupKFold，整栋楼进入训练或验证；保存每折楼宇、训练/验证行ID和实际拟合的scaler均值/尺度。每折Pipeline均重新fit，最终StandardScaler也只fit全部训练楼宇。
- 首次提交用数据库行锁原子保留特征、α/l1候选及重复次数。之后不同配置返回409，只允许同配置复算。源数据页在最终选模完成前隐藏封存楼宇目标，成功提交最终结果时再公开。
- 完全相同的楼宇日内容即使改数据集名称也不能重新导入（409），避免直接重导旧数据重置方案。新研究方案应使用真正新采集且尚未参与评估的楼宇；系统不能证明上游数据从未被人查看或跨来源改写。

按楼宇隔离、Pipeline学习范围与避免测试集参与选择的做法参照[scikit-learn数据泄漏指南](https://scikit-learn.org/stable/common_pitfalls.html)及[GroupKFold官方说明](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)。本项目固定使用scikit-learn1.5.2，不调用后续版本新增的shuffle参数。

## ElasticNet与解释口径

特征为室外温度°C、运行时长h、建筑面积m²、日到访人次、相对湿度%、设备装机kW、休息日0/1；目标为日能耗kWh。

ElasticNet在标准化X上最小化`||y−Xw||²/(2n) + α*l1_ratio*||w||₁ + α*(1−l1_ratio)*||w||²/2`，目标y保留原kWh单位。候选按三折平均MAE选优，同分按更小α、更小l1_ratio；未收敛候选保留记录，不参与选优。最终模型只在全部训练行上拟合，原单位系数`w/scale`，原单位截距`intercept−Σ(coef*mean)`；另展示每训练SD系数，避免直接比较不同原量纲系数。

封存最终评估报告MAE、RMSE、R²与全部封存点。R²可以为负；封存目标为常量时R²为空。温度、目标或其他封存特征的扰动不会改变训练候选、选择指纹或模型；会改变最终评估。测试集不会反过来选择特征或超参。

置换重要性固定已拟合模型，在封存行上逐项打乱特征，记录`ΔMAE = MAE(置换)−MAE(原始)`，seed97+特征索引、10–40次重复。展示全部值、均值和2.5/97.5%分位范围，负ΔMAE不裁剪。分位范围只描述重复置换的变动，不是抽样置信覆盖或因果节能区间。算法依照[scikit-learn置换重要性说明](https://scikit-learn.org/stable/modules/permutation_importance.html)，使用MAE误差增加而非准确率下降。

相关特征会共享解释份额，跨楼宇日的全局置换可能形成现实中少见的组合。当前没有因果识别、楼宇层面的不确定性bootstrap或干预验证；改造假设须另做现场观察。

## 失败态与复算

常量训练特征、常量训练目标、楼宇不足、每楼天数不足、非有限训练/封存值、非法特征/候选、模型未收敛、数据重复均明确拒绝或保存failed原因。常量特征在首次锁定前校验，失败不会消耗方案锁。

保存三类核验材料：train/test楼宇与行ID、每折训练/验证楼宇与行ID、每折及最终scaler均值/尺度。训练选择SHA256只包含训练观测、拆组与配置；完整输入SHA256另包含所有源数据和封存目标。固定cyclic求解、seed97与稳定排序便于复算。数值测量与DriverFinding标量使用MySQL DOUBLE，重复分布为JSON双精度，保留一致的持久化精度。

## 六页、五实体和共享代码

六页：研究首页、楼宇与样本、分组模型比较、驱动解释、改造假设、研究留痕。

BuildingDataset、BuildingDay、ModelRun、DriverFinding、RetrofitHypothesis五实体各贯穿model/schema/service/controller/route/前端API/Pinia store/页面。DriverFinding由真实计算持久化，通过独立API读取；假设引用具体finding，再由负责人批准交付。

共用DatasetSelect、ModelSummary、ImportancePlot、PredictionPlot、RunTable；通用PageHeading/StatusBadge/ErrorNotice/EmptyState。useTask与usePolling分别管理恢复状态和运行刷新。角色/状态枚举后端在`backend/src/constants/enums.py`（Role、RunStatus、HypothesisStatus、FEATURES），对应授权utils/auth、run_service/worker、hypothesis_service及输入schema；前端在`frontend/src/constants/enums.ts`（roles/statuses/features/shortNames），供App、StatusBadge、模型和解释页面使用。

## 技术与运行说明

| 层 | 实现 |
|---|---|
| 前端 | Vue3.5.45、TypeScript、Pinia、Vue Router、Vite6.4.6、Nginx1.27 |
| 后端 | Python3.11、FastAPI、SQLAlchemy、PyMySQL、PyJWT |
| 科学计算 | NumPy、scikit-learn1.5.2 Pipeline/StandardScaler/ElasticNet/GroupKFold |
| worker | 单Python消费者；MySQL任务状态为事实源，Redis唤醒；恢复queued/running |
| 数据服务 | MySQL8.0、Redis7 AOF |

五服务恰好frontend/backend/worker/db/redis，每个healthcheck真实检测。backend等db/redis；worker再等backend；frontend等backend。命名卷为数据库、Redis、后端/worker共享产物；当前结果在DB，交付CSV实时生成，共享卷预留扩展。`backend/migrations/README.md`说明metadata初始化v1与自然键，没有生产schema升级工具。

目录：`backend/src/{routes,controllers,services,models,schemas,middlewares,utils,constants,config}`、`backend/scripts/seed_demo.py`；`frontend/src/{api,stores,types,components/common,hooks,pages,router,utils,constants}`。

| 环境变量 | 默认 |
|---|---|
| COMPOSE_PROJECT_NAME | energy-drivers，顶层name与容器命名适配中文父目录 |
| FRONTEND_PORT/BACKEND_PORT/DB_PORT | 18217/19217/17717 |
| DB_PASSWORD | 本地MySQL演示密码 |
| JWT_SECRET | 独立项目签名密钥 |
| SEED_DEMO | true启动seed，失败记日志并允许API启动 |

seed以邮箱、数据集名、楼宇日自然键幂等，不覆盖已有数据集说明、配置锁或用户研究。固定seed97生成1080行，首个真实研究之后产生模型、七项解释与后续假设。

本地开发：db/redis启动后，在backend安装requirements并设置DATABASE_URL/REDIS_URL/JWT_SECRET，运行`uvicorn src.main:app --reload`与`python -m src.worker`；前端`npm ci && npm run dev`。Vite默认/api代理19217，本地API若用8000需同步代理目标。测试/截图/TESTING在批次根`test-artifacts/gb-0013/`。MIT License，见LICENSE。
