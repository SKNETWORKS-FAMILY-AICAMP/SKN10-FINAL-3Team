import logging
import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine
from database import Base
import pymysql
from router import strategy, case

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# 이관시 간략화 가능한 코드, 수정 예정
# MySQL 연결 테스트 함수
def test_mysql_connection():
    """MySQL 연결 테스트"""
    try:
        logger.info("MySQL 연결 테스트 시작...")
        
        # 환경변수 확인
        mysql_host = os.getenv("MYSQL_HOST")
        mysql_port = os.getenv("MYSQL_PORT")
        mysql_user = os.getenv("MYSQL_USER")
        mysql_pwd = os.getenv("MYSQL_PWD")
        mysql_db = os.getenv("MYSQL_DB")
        
        logger.info(f"MySQL 설정 확인:")
        logger.info(f"  HOST: {mysql_host}")
        logger.info(f"  PORT: {mysql_port}")
        logger.info(f"  USER: {mysql_user}")
        logger.info(f"  DB: {mysql_db}")
        
        if not all([mysql_host, mysql_port, mysql_user, mysql_pwd, mysql_db]):
            logger.error("MySQL 환경변수가 완전히 설정되지 않았습니다.")
            return False
        
        # 연결 테스트
        conn = pymysql.connect(
            host=mysql_host,
            port=int(mysql_port),
            user=mysql_user,
            password=mysql_pwd,
            database=mysql_db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # 간단한 쿼리 테스트
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            logger.info(f"MySQL 연결 테스트 성공: {result}")
        
        conn.close()
        logger.info("MySQL 연결 테스트 완료 - 정상 작동")
        return True
        
    except Exception as e:
        logger.error(f"MySQL 연결 테스트 실패: {str(e)}")
        return False

app = FastAPI()
router = APIRouter()

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# MySQL 연결 테스트 실행
test_mysql_connection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 또는 ["http://localhost:8000"]처럼 특정 도메인만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수 설정
RUNPOD_API_URL = os.getenv("RUNPOD_API_URL")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")

try:
    client = OpenAI(
        base_url=RUNPOD_API_URL,
        api_key=RUNPOD_API_KEY
    )
    logger.info(f"OpenAI 클라이언트 초기화 완료: {RUNPOD_API_URL}")
except Exception as e:
    logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
    client = None

@app.get("/")
def read_root():
    return {"message": "법률 자문 API 서버"}

# services/strategy
app.include_router(strategy.router, prefix="", tags=["전략 생성"])

# services/case
app.include_router(case.router, prefix="", tags=["통합 검색 처리"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)