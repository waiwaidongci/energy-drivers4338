import os
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:energy-demo-local@localhost:17717/energy")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
JWT_SECRET = os.getenv("JWT_SECRET", "local-energy-drivers-change-this-before-hosting")
SEED_DEMO = os.getenv("SEED_DEMO", "false").lower() == "true"
