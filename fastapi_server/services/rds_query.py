# app/services/rds_query.py

import os
import pymysql
from typing import Optional, Dict
import logging
from contextlib import contextmanager

# 로깅 설정
logger = logging.getLogger(__name__)

# 연결 풀링을 위한 전역 변수 (선택사항)
# _connection_pool = []

def get_db_connection():
    """데이터베이스 연결을 생성하는 헬퍼 함수"""
    try:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PWD"),
            database=os.getenv("MYSQL_DB"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,  # 자동 커밋 활성화
            connect_timeout=10,  # 연결 타임아웃 설정
            read_timeout=30,  # 읽기 타임아웃 설정
            write_timeout=30   # 쓰기 타임아웃 설정
        )
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {str(e)}")
        raise

@contextmanager
def get_db_cursor():
    """컨텍스트 매니저를 사용한 안전한 데이터베이스 연결"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            yield cursor
    except Exception as e:
        logger.error(f"데이터베이스 작업 중 오류: {str(e)}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"연결 종료 중 오류: {str(e)}")

def get_case_by_id(case_id: int) -> Optional[Dict]:
    """RDS에서 case_id로 판례 정보 조회"""
    try:
        with get_db_cursor() as cursor:
            query = """
SELECT case_id, case_num, court_name, case_name, case_at, 
    refer_cases, refer_statutes, decision_summary, case_full,
    decision_issue, case_result, facts_summary, facts_keywords,
    issue_summary, issue_keywords, keywords
FROM `case` 
WHERE case_id = %s
            """
            cursor.execute(query, (case_id,))
            result = cursor.fetchone()
            return result

    except Exception as e:
        logger.error(f"get_case_by_id 실행 중 오류 발생: {str(e)}")
        raise

def search_cases_in_rds(filters: dict) -> list:
    """RDS에서 조건 기반 판례 검색"""
    try:
        with get_db_cursor() as cursor:
            query = "SELECT case_id FROM `case` WHERE 1=1"
            params = []

            if "사건번호" in filters:
                query += " AND case_num = %s"
                params.append(filters["사건번호"])

            if "법원명" in filters:
                query += " AND court_name = %s"
                params.append(filters["법원명"])

            if "사건명" in filters:
                query += " AND case_name = %s"
                params.append(filters["사건명"])

            if "선고일자" in filters:
                query += " AND DATE(case_at) = %s"
                params.append(filters["선고일자"])

            if "참조조문" in filters:
                query += " AND refer_statutes LIKE %s"
                params.append(f"%{filters['참조조문']}%")

            if "판례결과" in filters:
                query += " AND case_result = %s"
                params.append(filters["판례결과"])

            cursor.execute(query, params)
            result = cursor.fetchall()
            return [str(row["case_id"]) for row in result]

    except Exception as e:
        logger.error(f"search_cases_in_rds 실행 중 오류 발생: {str(e)}")
        raise
