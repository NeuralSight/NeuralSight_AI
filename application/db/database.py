from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import dotenv


dotenv.load_dotenv()

if not os.getenv("PRODUCTION"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./tester.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # SQLALCHEMY_DATABASE_URL = "postgresql://nsight:nsight@localhost/nsight"
    SQLALCHEMY_DATABASE_URL = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}'
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
