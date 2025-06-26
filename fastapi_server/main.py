import logging
import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Event, Base, EventRequest, EventResponse
from agent.strategy import generate_strategy

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

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

# ====================================
# models.py에 옮겨진 코드
# ====================================
# class CaseRequest(BaseModel):
#     event_id: Optional[str] = None
#     client_role: str
#     e_description: str
#     claim_summary: str
#     event_file: str

# class CaseResponse(BaseModel):
#     result: str

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

# ===================================
# strategy.py에 옮겨진 코드
# ===================================
#         if case.client_role == "피고":
#             system_prompt = f"""다음 사건에 대한 {case.client_role} 전략을 제시해주세요.
# 출력 양식:
# ### 전략 방향성:
# - ...
# ### 방어 논리:
# - ...
# ### 참고 사항:
# - ...
#             """
#         elif case.client_role == "원고":
#             system_prompt = f"""다음 사건에 대한 {case.client_role} 전략을 제시해주세요.
# 출력 양식:
# ### 예상 피고 주장:
# - ...
# ### 전략 방향성:
# - ...
# ### 필요한 증거:
# - ...
# ### 참고 사항:
# - ...
#             """
#         prompt = f"""
# 사건내용: {case.e_description}
# 청구내용: {case.claim_summary}
# 증거자료: {case.event_file}
#         """
#         logger.info("Runpod API 호출 시작")
        
#         # API 호출
#         response = client.chat.completions.create(
#             model="khs2617/gemma-3-1b-it-merged_model_strategy",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": prompt}],
#             max_tokens=1000,
#             temperature=0.1
#         )
        
#         logger.info("Runpod API 호출 완료")
#         logger.info(f"응답 타입: {type(response)}")
#         logger.info(f"응답 내용: {response}")
        
#         # 응답 검증
#         if response is None:
#             logger.error("API 응답이 None입니다.")
#             raise Exception("API 응답이 None입니다.")
        
#         if not hasattr(response, 'choices'):
#             logger.error("API 응답에 choices 속성이 없습니다.")
#             raise Exception("API 응답에 choices 속성이 없습니다.")
        
#         if not response.choices:
#             logger.error("API 응답의 choices가 비어있습니다.")
#             raise Exception("API 응답의 choices가 비어있습니다.")
        
#         first_choice = response.choices[0]
#         if first_choice is None:
#             logger.error("API 응답의 첫 번째 choice가 None입니다.")
#             raise Exception("API 응답의 첫 번째 choice가 None입니다.")
        
#         if not hasattr(first_choice, 'message'):
#             logger.error("API 응답의 choice에 message 속성이 없습니다.")
#             raise Exception("API 응답의 choice에 message 속성이 없습니다.")
        
#         message = first_choice.message
#         if message is None:
#             logger.error("API 응답의 message가 None입니다.")
#             raise Exception("API 응답의 message가 None입니다.")
        
#         if not hasattr(message, 'content'):
#             logger.error("API 응답의 message에 content 속성이 없습니다.")
#             raise Exception("API 응답의 message에 content 속성이 없습니다.")
        
#         content = message.content
#         if content is None:
#             logger.error("API 응답의 content가 None입니다.")
#             raise Exception("API 응답의 content가 None입니다.")
        
#         logger.info(f"API 응답 content: {content[:100]}...")
#         return CaseResponse(result=content)
        
#    except Exception as e:
#        logger.error(f"분석 중 오류 발생: {str(e)}")
#        import traceback
#        logger.error(f"상세 오류: {traceback.format_exc()}")
#        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

#====================================
# database.py에 옮겨진 코드
# ===================================
# # DB 세션 의존성
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     except Exception as e:
#         logger.error(f"데이터베이스 세션 오류: {str(e)}")
#         db.rollback()
#         raise HTTPException(status_code=500, detail="데이터베이스 연결 오류")
#     finally:
#         db.close()

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

#====================================
# database.py에 옮겨진 코드
# ===================================
# @app.post("/update-strategy/")
# async def update_ai_strategy(request: Request, db: Session = Depends(get_db)):
#     try:
#         body = await request.json()
#         logger.info(f"Request Body: {body}")
#     except Exception as e:
#         logger.error(f"Request body 파싱 실패: {str(e)}")
#         body = {}

#     # 1. event_id가 있는지 확인
#     event_id = body.get("event_id")
#     logger.info(f"Extracted event_id: {event_id}")
#     if not event_id:
#         raise HTTPException(status_code=400, detail="event_id is required")

#     # event_id를 정수로 변환
#     try:
#         event_id = int(event_id)
#     except (ValueError, TypeError):
#         raise HTTPException(status_code=400, detail="event_id must be a valid integer")

#     # 2. 해당 event 조회
#     event = db.query(Event).filter(Event.event_id == event_id).first()
#     if not event:
#         raise HTTPException(status_code=404, detail="Event not found")

#     if event.client_role == "피고":
#         system_prompt = f"""다음 사건에 대한 {event.client_role} 전략을 제시해주세요.
# 출력 양식:
# ### 전략 방향성:
# - ...
# ### 방어 논리:
# - ...
# ### 참고 사항:
# - ...
# """
#     elif event.client_role == "원고":
#         system_prompt = f"""다음 사건에 대한 {event.client_role} 전략을 제시해주세요.
# 출력 양식:
# ### 예상 피고 주장:
# - ...
# ### 전략 방향성:
# - ...
# ### 필요한 증거:
# - ...
# ### 참고 사항:
# - ...
# """
#     prompt = f"""
# 사건내용: {event.e_description}
# 청구내용: {event.claim_summary}
# 증거자료: {event.event_file}
#         """
#     logger.info("Runpod API 호출 시작")
    
#     # API 호출
#     response = client.chat.completions.create(
#         model="khs2617/gemma-3-1b-it-merged_model_strategy",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": prompt}],
#         max_tokens=1000,
#         temperature=0.1
#     )

#     # 3. ai_strategy 필드 업데이트
#     event.ai_strategy = response.choices[0].message.content
#     db.commit()

#    return {"message": f"AI 전략이 성공적으로 생성되었습니다. (Event ID: {event_id})"}

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