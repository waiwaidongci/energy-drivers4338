from enum import StrEnum
class Role(StrEnum):
    ADMIN='admin'
    ANALYST='analyst'
    VIEWER='viewer'
class RunStatus(StrEnum):
    QUEUED='queued'
    RUNNING='running'
    COMPLETED='completed'
    FAILED='failed'
class HypothesisStatus(StrEnum):
    DRAFT='draft'
    APPROVED='approved'
FEATURES=('temperature_c','operating_hours','area_m2','visitors','humidity_pct','equipment_kw','holiday_flag')
SPLIT_SEED=97
CV_SPLITS=3
