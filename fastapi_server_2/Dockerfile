# Python 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# FastAPI 서버 실행 (포트 8000)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]