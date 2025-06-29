import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# 2) 각 LangGraph 노드 함수 정의
async def vectorSearch_node(state: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['VECTORSEARCH_URL'],
            json={
                "query": state.get("e_description", "더미 사건 설명"),
                "cat_cd": state.get("cat_cd", "민사"),
            }
        )
    result = res.json()
    new_state = {**state, **result}
    return new_state

async def SQLSearch_node(state: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['SQLSEARCH_URL'],
            json={
                "query": state.get("e_description", "더미 사건 설명"),
                "cat_cd": state.get("cat_cd", "민사"),
            }
        )
    result = res.json()
    new_state = {**state, **result}
    return new_state

async def scoreCalc_node(state: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['SCORECALC_URL'],
            json={
                "similar_count_by_team": {
                    "민사 1팀": 2,
                    "민사 2팀": 1,
                    "민사 3팀": 1,
                    "민사 4팀": 1
                },
                "average_similar_scores_by_team": {
                    "민사 1팀": 5.0,
                    "민사 2팀": 8.0,
                    "민사 3팀": 5.0,
                    "민사 4팀": 2.0
                },
                "load_count_by_team": {
                    "민사 1팀": 8,
                    "민사 2팀": 5,
                    "민사 3팀": 4,
                    "민사 4팀": 2
                },
                "case_count_max": 10,
                "case_count_min": 2
            }
        )
    result = res.json()
    new_state = {**state, **result}
    return new_state

async def explain_node(state: dict):
    """
    LangGraph Explain 노드 - 내부 FastAPI API 호출
    """
    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['EXPLAIN_URL'],
            json={
                "recommended_team": state["recommended_team"],
                "score": state["score"],
                "details": state["details"]
            }
        )
    explanation = res.json().get("explanation")

    new_state = {**state, "explanation": explanation}
    print("explain_node new_state keys:", new_state.keys())

    return new_state