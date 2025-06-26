# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# 환경 변수에서 RDS 접속 정보 불러오기
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PWD = os.getenv("MYSQL_PWD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")  # 기본값 3306
MYSQL_DB = os.getenv("MYSQL_DB")

# SQLAlchemy 접속 URL 구성
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

# 엔진 및 세션 구성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# 데이터베이스 세션 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 오류: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 연결 오류")
    finally:
        db.close()