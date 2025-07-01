# app/services/rds_query.py

import os
import pymysql
from typing import Optional, Dict

def get_case_by_id(case_id: int) -> Optional[Dict]:
    """RDS에서 case_id로 판례 정보 조회"""
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PWD"),
        database=os.getenv("MYSQL_DB"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
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

    finally:
        conn.close()

def search_cases_in_rds(filters: dict) -> list:
    """RDS에서 조건 기반 판례 검색 (핵심 필드만 사용, 한글-DB컬럼 매핑)"""
    # 한글 key와 DB 컬럼명 매핑
    ALLOWED_FILTERS = {
        "사건번호": "case_num",
        "법원명": "court_name",
        "사건명": "case_name",
        "선고일자": "case_at",
        "참조조문": "refer_statutes",
        "판례결과": "case_result"
    }
    
    print("🔍 [DEBUG] 원본 필터:", filters)
    
    # 허용된 필드만 남기기
    filters = {k: v for k, v in filters.items() if k in ALLOWED_FILTERS and v}
    
    print("🔍 [DEBUG] 정제된 필터:", filters)

    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            query = "SELECT case_id FROM `case` WHERE 1=1"
            params = []
            for kor_key, db_col in ALLOWED_FILTERS.items():
                if kor_key in filters:
                    if kor_key == "참조조문":
                        query += f" AND {db_col} LIKE %s"
                        params.append(f"%{filters[kor_key]}%")
                    elif kor_key == "선고일자":
                        query += f" AND DATE({db_col}) = %s"
                        params.append(filters[kor_key])
                    else:
                        query += f" AND {db_col} = %s"
                        params.append(filters[kor_key])
            print("[SQL DEBUG] query:", query)
            print("[SQL DEBUG] params:", params)
            cursor.execute(query, params)
            result = cursor.fetchall()
            print(f"[SQL DEBUG] 결과 개수: {len(result)}")
            return [str(row["case_id"]) for row in result]
    finally:
        conn.close()

def get_unique_column_values(column: str) -> list:
    """RDS에서 특정 컬럼의 유니크 값 리스트 반환"""
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            query = f"SELECT DISTINCT `{column}` FROM `case` WHERE `{column}` IS NOT NULL AND `{column}` != ''"
            cursor.execute(query)
            result = cursor.fetchall()
            return [row[column] for row in result if row[column]]
    finally:
        conn.close()