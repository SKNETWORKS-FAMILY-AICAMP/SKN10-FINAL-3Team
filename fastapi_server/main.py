import logging
import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Event, Base, EventRequest, EventResponse
from agent.strategy import generate_strategy
import pymysql

# API 라우터 추가
from api import ask, combined

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 환경 변수 설정 (기본값 제공)
RUNPOD_API_URL = os.getenv("RUNPOD_API_URL")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")

# 데이터베이스 환경 변수 확인
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PWD = os.getenv("MYSQL_PWD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

if not all([MYSQL_USER, MYSQL_PWD, MYSQL_HOST, MYSQL_DB]):
    logger.warning("데이터베이스 환경 변수가 완전히 설정되지 않았습니다.")
    logger.warning(f"MYSQL_USER: {'설정됨' if MYSQL_USER else '설정되지 않음'}")
    logger.warning(f"MYSQL_PWD: {'설정됨' if MYSQL_PWD else '설정되지 않음'}")
    logger.warning(f"MYSQL_HOST: {'설정됨' if MYSQL_HOST else '설정되지 않음'}")
    logger.warning(f"MYSQL_DB: {'설정됨' if MYSQL_DB else '설정되지 않음'}")

# OpenAI 클라이언트 설정 (Runpod serverless vLLM용)
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

# ===================================
# /analyze-case/ 링크 변경할 예정
# /analyze-case/ => /analyze-strategy/
# ===================================
@app.post("/analyze-case/", response_model=EventResponse)
async def analyze_case(case: EventRequest):
    try:
        logger.info(f"분석 요청 받음: {case.client_role}")
        strategy = generate_strategy(case)
        return EventResponse(result=strategy)
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@app.post("/update-strategy/", response_model=EventResponse)
async def update_ai_strategy(case: EventRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"분석 요청 받음: {case.client_role}")
        strategy = generate_strategy(case)
        event = db.query(Event).filter(Event.event_id == case.event_id).first()
        event.ai_strategy = strategy
        db.commit()
        return {"message": f"AI 전략이 성공적으로 생성되었습니다. (Event ID: {case.event_id})"}

    except Exception as e:
        logger.error(f"Request body 파싱 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

# Chatbot API
app.include_router(ask.router, prefix="", tags=["판례 질문 응답"])
app.include_router(combined.router, prefix="", tags=["통합 검색 처리"])

# ===================================
# 기능 구현 안되어있음
# ===================================
# @app.options("/update-strategy/")
# async def preflight_handler(request: Request, path: str):
#     origin = request.headers.get("origin", "*")
#     acrh = request.headers.get("access-control-request-headers", "*")
#     headers = {
#         "Access-Control-Allow-Origin": origin,
#         "Access-Control-Allow-Methods": "POST,GET,OPTIONS",
#         "Access-Control-Allow-Headers": acrh,
#         "Access-Control-Allow-Credentials": "true",
#     }
#     return Response(status_code=200, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)