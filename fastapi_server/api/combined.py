# app/api/combined.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, validator
from typing import List, Dict, Union, Optional
from services.classify_llm import classify_query
from services.vector_search import search_similar_cases
from services.llm_handler import ask_openai
from services.rds_query import search_cases_in_rds, get_case_by_id
from services.ask_llm import generate_markdown_answer, classify_ask_type
import logging
import json

# 로그 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# 요청 스키마
class CombinedQueryRequest(BaseModel):
    query: str
    case1: Optional[Dict] = None
    case2: Optional[Dict] = None
    case_ids: Optional[List[int]] = None

class CaseIdQueryRequest(BaseModel):
    query: str
    case_id: Optional[int] = None

class CaseIdsQueryRequest(BaseModel):
    query: str
    case_ids: List[int]

# 응답 스키마들
class SimpleResponse(BaseModel):
    answer: str

class DetailedResponse(BaseModel):
    case_ids: List[str]
    answer: str

class CaseResult(BaseModel):
    case_id: str
    title: str
    summary: str
    similarity: float

class CombinedQueryResponse(BaseModel):
    search_type: str  # "조건기반" | "유사도기반" | "일반질문" | "판례비교" | "판례질문"
    case_ids: List[str]
    answer: str
    similar_cases: Optional[List[CaseResult]] = None

@router.post("/case-query/", response_model=DetailedResponse)
async def handle_case_query(request: CaseIdQueryRequest, raw_request: Request):
    """case_id로 판례 정보를 가져와서 질문에 답변"""
    # Raw request body 로깅
    try:
        body = await raw_request.body()
        logger.info(f"Raw request body: {body.decode('utf-8')}")
    except Exception as e:
        logger.error(f"Failed to read raw request body: {e}")
    
    logger.info(f"Received request data: {request}")
    logger.info(f"Request query: {request.query}")
    logger.info(f"Request case_id: {request.case_id} (type: {type(request.case_id)})")
    
    query = request.query
    case_id = request.case_id
    logger.info(f"CaseIdQueryRequest: {request}")

    # RDS에서 판례 정보 가져오기
    case_data = get_case_by_id(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail=f"case_id {case_id}에 해당하는 판례를 찾을 수 없습니다.")
    
    # 질문 유형 분류
    ask_type = classify_ask_type(query)
    
    logger.info(f"AskType: {ask_type}")

    if ask_type == "single_case_qa":
        # 단일 판례 질문인 경우
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        case_info = serialize_case(case_data)
        prompt = f"""
[질문]
{query}

[판례 정보]
{case_info}
"""
        answer = generate_markdown_answer(prompt)
        logger.info(f"Answer: {answer}")

        return DetailedResponse(
            case_ids=[str(case_id)],
            answer=answer
        )
    
    elif ask_type == "similarity":
        # 유사도 검색인 경우
        contents = (
            case_data.get("facts_summary", "") + "\n" +
            case_data.get("issue_summary", "") + "\n" +
            case_data.get("decision_summary", "")
        )
        raw_results = search_similar_cases(contents)
        
        filtered = [r for r in raw_results if r["similarity"] >= 0.5]
        sorted_results = sorted(filtered, key=lambda x: x["similarity"], reverse=True)
        
        if not sorted_results:
            return DetailedResponse(
                case_ids=[str(case_id)],
                answer="유사도가 0.5 이상인 판례가 없습니다."
            )
        
        case_ids = [str(r.get("case_id", f"CASE-{i}")) for i, r in enumerate(sorted_results)]
        
        return DetailedResponse(
            case_ids=case_ids,
            answer=f"유사한 판례 {len(case_ids)}건을 찾았습니다."
        )
    
    else:
        # 일반 질문인 경우
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        case_info = serialize_case(case_data)
        prompt = f"""
[질문]
{query}

[판례 정보]
{case_info}
"""
        answer = generate_markdown_answer(prompt)
        
        return DetailedResponse(
            case_ids=[str(case_id)],
            answer=answer
        )

@router.post("/cases-query/", response_model=DetailedResponse)
async def handle_cases_query(request: CaseIdsQueryRequest):
    """case_ids 배열로 여러 판례 정보를 가져와서 질문에 답변"""
    query = request.query
    case_ids = request.case_ids
    
    print(f"DEBUG: Received query: {query}")
    print(f"DEBUG: Received case_ids: {case_ids}")
    
    if not case_ids:
        raise HTTPException(status_code=400, detail="case_ids가 비어있습니다.")
    
    # RDS에서 판례 정보들 가져오기
    cases_data = []
    for case_id in case_ids:
        case_data = get_case_by_id(case_id)
        if not case_data:
            raise HTTPException(status_code=404, detail=f"case_id {case_id}에 해당하는 판례를 찾을 수 없습니다.")
        cases_data.append(case_data)
    
    print(f"DEBUG: Retrieved {len(cases_data)} cases from RDS")
    print(f"DEBUG: First case keys: {list(cases_data[0].keys()) if cases_data else 'No cases'}")
    
    # 질문 유형 분류
    ask_type = classify_ask_type(query)
    print(f"DEBUG: Classified query type: {ask_type}")
    
    if ask_type == "comparison" and len(cases_data) >= 2:
        # 판례 비교인 경우
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        case1_info = serialize_case(cases_data[0])
        case2_info = serialize_case(cases_data[1])
        
        prompt = f"""
[질문]
{query}

[판례1 정보]
{case1_info}

[판례2 정보]
{case2_info}
"""
        answer = generate_markdown_answer(prompt)
        
        return DetailedResponse(
            case_ids=[str(case_id) for case_id in case_ids],
            answer=answer
        )
    
    elif ask_type == "single_case_qa" and len(cases_data) == 1:
        # 단일 판례 질문인 경우
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        case_info = serialize_case(cases_data[0])
        print(f"DEBUG: Serialized case info length: {len(case_info)}")
        
        prompt = f"""
[질문]
{query}

[판례 정보]
{case_info}
"""
        print(f"DEBUG: Generated prompt length: {len(prompt)}")
        answer = generate_markdown_answer(prompt)
        print(f"DEBUG: Generated answer: {answer[:100]}...")
        
        return DetailedResponse(
            case_ids=[str(case_ids[0])],
            answer=answer
        )
    
    elif ask_type == "similarity" and len(cases_data) == 1:
        # 유사도 검색인 경우 (첫 번째 판례 기준)
        case_data = cases_data[0]
        contents = (
            case_data.get("facts_summary", "") + "\n" +
            case_data.get("issue_summary", "") + "\n" +
            case_data.get("decision_summary", "")
        )
        raw_results = search_similar_cases(contents)
        
        filtered = [r for r in raw_results if r["similarity"] >= 0.5]
        sorted_results = sorted(filtered, key=lambda x: x["similarity"], reverse=True)
        
        if not sorted_results:
            return DetailedResponse(
                case_ids=[str(case_ids[0])],
                answer="유사도가 0.5 이상인 판례가 없습니다."
            )
        
        similar_case_ids = [str(r.get("case_id", f"CASE-{i}")) for i, r in enumerate(sorted_results)]
        
        return DetailedResponse(
            case_ids=similar_case_ids,
            answer=f"유사한 판례 {len(similar_case_ids)}건을 찾았습니다."
        )
    
    else:
        # 일반 질문이거나 여러 판례에 대한 질문인 경우
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        cases_info = ""
        for i, case_data in enumerate(cases_data):
            cases_info += f"\n[판례{i+1} 정보]\n{serialize_case(case_data)}\n"
        
        prompt = f"""
[질문]
{query}

{cases_info}
"""
        print(f"DEBUG: Generated prompt length: {len(prompt)}")
        answer = generate_markdown_answer(prompt)
        print(f"DEBUG: Generated answer: {answer[:100]}...")
        
        return DetailedResponse(
            case_ids=[str(case_id) for case_id in case_ids],
            answer=answer
        )

@router.post("/combined/", response_model=Union[SimpleResponse, DetailedResponse, CombinedQueryResponse])
async def handle_combined_query(request: CombinedQueryRequest):
    query = request.query
    case1 = request.case1
    case2 = request.case2
    case_ids = request.case_ids

    # case_ids가 제공된 경우 RDS에서 케이스 데이터 가져오기
    if case_ids:
        print(f"DEBUG: Processing case_ids: {case_ids}")
        cases_data = []
        for case_id in case_ids:
            case_data = get_case_by_id(case_id)
            if not case_data:
                raise HTTPException(status_code=404, detail=f"case_id {case_id}에 해당하는 판례를 찾을 수 없습니다.")
            cases_data.append(case_data)
        
        print(f"DEBUG: Retrieved {len(cases_data)} cases from RDS")
        
        # 질문 유형 분류
        ask_type = classify_ask_type(query)
        print(f"DEBUG: Classified query type: {ask_type}")
        
        if ask_type == "comparison" and len(cases_data) >= 2:
            # 판례 비교인 경우
            def serialize_case(case: Dict) -> str:
                return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
            
            case1_info = serialize_case(cases_data[0])
            case2_info = serialize_case(cases_data[1])
            
            prompt = f"""
[질문]
{query}

[판례1 정보]
{case1_info}

[판례2 정보]
{case2_info}
"""
            answer = generate_markdown_answer(prompt)
            
            return DetailedResponse(
                case_ids=[str(case_id) for case_id in case_ids],
                answer=answer
            )
        
        elif ask_type == "single_case_qa" and len(cases_data) == 1:
            # 단일 판례 질문인 경우
            def serialize_case(case: Dict) -> str:
                return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
            
            case_info = serialize_case(cases_data[0])
            print(f"DEBUG: Serialized case info length: {len(case_info)}")
            
            prompt = f"""
[질문]
{query}

[판례 정보]
{case_info}
"""
            print(f"DEBUG: Generated prompt length: {len(prompt)}")
            answer = generate_markdown_answer(prompt)
            print(f"DEBUG: Generated answer: {answer[:100]}...")
            
            return DetailedResponse(
                case_ids=[str(case_ids[0])],
                answer=answer
            )
        
        elif ask_type == "similarity" and len(cases_data) == 1:
            # 유사도 검색인 경우 (첫 번째 판례 기준)
            case_data = cases_data[0]
            contents = (
                case_data.get("facts_summary", "") + "\n" +
                case_data.get("issue_summary", "") + "\n" +
                case_data.get("decision_summary", "")
            )
            raw_results = search_similar_cases(contents)
            
            filtered = [r for r in raw_results if r["similarity"] >= 0.5]
            sorted_results = sorted(filtered, key=lambda x: x["similarity"], reverse=True)
            
            if not sorted_results:
                return DetailedResponse(
                    case_ids=[str(case_ids[0])],
                    answer="유사도가 0.5 이상인 판례가 없습니다."
                )
            
            similar_case_ids = [str(r.get("case_id", f"CASE-{i}")) for i, r in enumerate(sorted_results)]
            
            return DetailedResponse(
                case_ids=similar_case_ids,
                answer=f"유사한 판례 {len(similar_case_ids)}건을 찾았습니다."
            )
        
        else:
            # 일반 질문이거나 여러 판례에 대한 질문인 경우
            def serialize_case(case: Dict) -> str:
                return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
            
            cases_info = ""
            for i, case_data in enumerate(cases_data):
                cases_info += f"\n[판례{i+1} 정보]\n{serialize_case(case_data)}\n"
            
            prompt = f"""
[질문]
{query}

{cases_info}
"""
            print(f"DEBUG: Generated prompt length: {len(prompt)}")
            answer = generate_markdown_answer(prompt)
            print(f"DEBUG: Generated answer: {answer[:100]}...")
            
            return DetailedResponse(
                case_ids=[str(case_id) for case_id in case_ids],
                answer=answer
            )

    # 기존 로직 (case1, case2 사용)
    # 입력 형태에 따른 분기 처리
    input_type = "ex1"  # 기본값
    if case1 is not None and case2 is not None:
        input_type = "ex3"  # case1과 case2 모두 있음
    elif case1 is not None:
        input_type = "ex2"  # case1만 있음

    # 1단계: ask.py의 세밀한 분류 먼저 시도
    try:
        ask_type = classify_ask_type(query)
        
        # 판례 비교 질문인 경우 (ex3 형태)
        if ask_type == "comparison":
            if not (case1 and case2):
                raise HTTPException(status_code=400, detail="판례 비교는 두 판례가 모두 필요합니다.")
            
            def serialize_case(case: Dict) -> str:
                return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])

            case1_info = serialize_case(case1)
            case2_info = serialize_case(case2)

            prompt = f"""
[질문]
{query}

[판례1 정보]
{case1_info}

[판례2 정보]
{case2_info}
"""
            answer = generate_markdown_answer(prompt)
            
            # ex3 형태 응답
            if input_type == "ex3":
                return DetailedResponse(
                    case_ids=[],
                    answer=answer
                )
            else:
                return CombinedQueryResponse(
                    search_type="판례비교",
                    case_ids=[],
                    answer=answer,
                    similar_cases=None
                )
        
        # 유사도 검색 질문인 경우
        elif ask_type == "similarity":
            if not case1:
                raw_results = search_similar_cases(query)
            else:
                contents = (
                    case1.get("facts_summary", "") + "\n" +
                    case1.get("issue_summary", "") + "\n" +
                    case1.get("decision_summary", "")
                )
                raw_results = search_similar_cases(contents)

            filtered = [r for r in raw_results if r["similarity"] >= 0.5]
            sorted_results = sorted(filtered, key=lambda x: x["similarity"], reverse=True)

            if not sorted_results:
                if input_type == "ex1":
                    return SimpleResponse(answer="유사도가 0.5 이상인 판례가 없습니다.")
                else:
                    return DetailedResponse(
                        case_ids=[],
                        answer="유사도가 0.5 이상인 판례가 없습니다."
                    )

            case_ids = [str(r.get("case_id", f"CASE-{i}")) for i, r in enumerate(sorted_results)]
            
            # 유사도 검색은 항상 case_ids를 포함한 응답 반환
            if input_type == "ex1":
                return DetailedResponse(
                    case_ids=case_ids,
                    answer=f"유사한 판례 {len(case_ids)}건을 찾았습니다."
                )
            elif input_type in ["ex2", "ex3"]:
                return DetailedResponse(
                    case_ids=case_ids,
                    answer=f"유사한 판례 {len(case_ids)}건을 찾았습니다."
                )
            else:
                similar_cases = [
                    CaseResult(
                        case_id=str(r.get("case_id", f"CASE-{i}")),
                        title=r.get("title", ""),
                        summary=r.get("summary", ""),
                        similarity=r.get("similarity", 0.0)
                    )
                    for i, r in enumerate(sorted_results)
                ]
                return CombinedQueryResponse(
                    search_type="유사도기반",
                    case_ids=case_ids,
                    answer=f"유사한 판례 {len(case_ids)}건을 찾았습니다.",
                    similar_cases=similar_cases
                )
        
        # 단일 판례 질문인 경우 (ex2 형태)
        elif ask_type == "single_case_qa" and case1:
            def serialize_case(case: Dict) -> str:
                return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
            case1_info = serialize_case(case1)
            prompt = f"""
[질문]
{query}

[판례 정보]
{case1_info}
"""
            answer = generate_markdown_answer(prompt)
            
            if input_type == "ex2":
                return DetailedResponse(
                    case_ids=[],
                    answer=answer
                )
            else:
                return CombinedQueryResponse(
                    search_type="판례질문",
                    case_ids=[],
                    answer=answer,
                    similar_cases=None
                )
    
    except Exception as e:
        # ask.py 분류가 실패하면 기존 로직으로 진행
        pass

    # 2단계: 기존 분류 로직 (query.py와 동일)
    try:
        result = classify_query(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 분류 실패: {e}")

    search_type = result.get("search_type", "")
    filters = result.get("filters", {})

    if search_type == "조건기반":
        try:
            case_ids = search_cases_in_rds(filters)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RDS 검색 실패: {e}")

        return DetailedResponse(
            case_ids=case_ids,
            answer=f"조건에 맞는 판례 {len(case_ids)}건을 찾았습니다."
        )

    elif search_type == "유사도기반":
        try:
            sim_results = search_similar_cases(query)
            case_ids = [str(r["case_id"]) for r in sim_results]

            return DetailedResponse(
                case_ids=case_ids,
                answer=f"유사한 판례 {len(case_ids)}건을 찾았습니다."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"벡터 검색 실패: {e}")

    else:  # 일반질문
        try:
            # 일반 질문에 대한 프롬프트 개선
            prompt = f"""
아래 질문에 대해 간단하고 명확하게 답변해 주세요.
법률 관련 질문이면 법률적 관점에서, 일반적인 질문이면 일반적인 관점에서 답변해 주세요.

[질문]
{query}

답변:
"""
            gpt_answer = ask_openai(prompt)
            
            # 빈 답변이나 None 처리
            if not gpt_answer or not gpt_answer.strip():
                gpt_answer = "해당 질문에 대한 답변을 찾지 못했습니다. 좀 더 구체적으로 질문해 주시면 도움을 드릴 수 있습니다."
                
        except Exception as e:
            gpt_answer = f"답변 생성 중 오류가 발생했습니다. 다시 시도해 주세요."

        if input_type == "ex1":
            return SimpleResponse(answer=gpt_answer)
        elif input_type in ["ex2", "ex3"]:
            return DetailedResponse(
                case_ids=[],
                answer=gpt_answer
            )
        else:
            return CombinedQueryResponse(
                search_type="일반질문",
                case_ids=[],
                answer=gpt_answer,
                similar_cases=None
            )
