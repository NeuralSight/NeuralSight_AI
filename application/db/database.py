from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import dotenv


# psql \
#    --host=nsight.cftp73dgheul.us-east-1.rds.amazonaws.com \
#    --port=5432 \
#    --username=nsight \
#    --dbname=nsight
#    --password=neurallabs \


dotenv.load_dotenv()


if not os.getenv("PRODUCTION"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./neurallabs.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/nsight"
    # SQLALCHEMY_DATABASE_URL = "sqlite:///./neurallabs.db"
    SQLALCHEMY_DATABASE_URL = f"postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}"
    print(f"DB URL  {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
