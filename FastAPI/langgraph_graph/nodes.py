import httpx
import os
from dotenv import load_dotenv

load_dotenv()


# VectorSearch Node
async def vectorSearch_node(state: dict):
    print("\n========== [vectorSearch_node] BEFORE ==========")
    print(state)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['VECTORSEARCH_URL'],
            json={
                "query": state.get("e_description"),
                "cat_cd": state.get("cat_cd"),
            }
        )

    print("\n========== [vectorSearch_node] RES STATUS ==========")
    print(res.status_code)

    try:
        res.raise_for_status()
        result = res.json()
    except Exception as e:
        print("[vectorSearch_node] JSON decode or HTTP error:", str(e))
        print("[vectorSearch_node] raw text:", res.text)
        raise

    print("\n========== [vectorSearch_node] API RESULT ==========")
    print(result)

    new_state = {**state, **result}

    print("\n========== [vectorSearch_node] AFTER ==========")
    print(new_state)
    return new_state


# SQLSearch Node
async def SQLSearch_node(state: dict):
    print("\n========== [SQLSearch_node] BEFORE ==========")
    print(state)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['SQLSEARCH_URL'],
            json={
                "cat_cd": state.get("cat_cd"),
                "top_event_ids": state.get("top_event_ids"),
            }
        )

    print("\n========== [SQLSearch_node] RES STATUS ==========")
    print(res.status_code)

    try:
        res.raise_for_status()
        result = res.json()
    except Exception as e:
        print("[SQLSearch_node] JSON decode or HTTP error:", str(e))
        print("[SQLSearch_node] raw text:", res.text)
        raise

    print("\n========== [SQLSearch_node] API RESULT ==========")
    print(result)

    new_state = {**state, **result}

    print("\n========== [SQLSearch_node] AFTER ==========")
    print(new_state)
    return new_state


# ScoreCalc Node
async def scoreCalc_node(state: dict):
    print("\n========== [scoreCalc_node] BEFORE ==========")
    print(state)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['SCORECALC_URL'],
            json={
                "top_event_ids": state.get("top_event_ids"),
                "similar_count_by_team": state['similar_count_by_team'],
                "average_similar_scores_by_team": state['average_similar_scores_by_team'],
                "load_count_by_team": state['load_count_by_team'],
                "case_count_max": state['case_count_max'],
                "case_count_min": state['case_count_min'],
            }
        )

    print("\n========== [scoreCalc_node] RES STATUS ==========")
    print(res.status_code)

    try:
        res.raise_for_status()
        result = res.json()
    except Exception as e:
        print("[scoreCalc_node] JSON decode or HTTP error:", str(e))
        print("[scoreCalc_node] raw text:", res.text)
        raise

    print("\n========== [scoreCalc_node] API RESULT ==========")
    print(result)

    new_state = {**state, **result}

    print("\n========== [scoreCalc_node] AFTER ==========")
    print(new_state)
    return new_state


# Explain Node
async def explain_node(state: dict):
    print("\n========== [explain_node] BEFORE ==========")
    print(state)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            os.environ['FASTAPI_BASE_URL'] + os.environ['EXPLAIN_URL'],
            json={
                "recommended_team": state.get("recommended_team"),
                "score": state.get("score"),
                "details": state.get("details")
            }
        )

    print("\n========== [explain_node] RES STATUS ==========")
    print(res.status_code)

    try:
        res.raise_for_status()
        explanation = res.json().get("explanation")
    except Exception as e:
        print("[explain_node] JSON decode or HTTP error:", str(e))
        print("[explain_node] raw text:", res.text)
        raise

    print("\n========== [explain_node] explanation ==========")
    print(explanation)

    new_state = {**state, "explanation": explanation}

    print("\n========== [explain_node] AFTER ==========")
    print(new_state)
    return new_state
