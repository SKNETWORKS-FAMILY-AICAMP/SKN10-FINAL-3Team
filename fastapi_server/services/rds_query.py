# app/services/rds_query.py

import os
import pymysql
from typing import Optional, Dict

def get_case_by_id(case_id: int) -> Optional[Dict]:
    """RDS에서 case_id로 판례 정보 조회"""
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
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
    """RDS에서 조건 기반 판례 검색"""
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PWD"),  # 반드시 환경변수에 저장
        database=os.getenv("MYSQL_DB"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
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

    finally:
        conn.close()
