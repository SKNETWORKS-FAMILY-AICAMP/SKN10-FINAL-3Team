# app/services/vector_search.py

import faiss
import numpy as np
import pickle
from pathlib import Path
from models.gpt import get_embedding
import logging

# 로그 설정
logger = logging.getLogger(__name__)

# 경로 설정
INDEX_PATH = Path("vectordb/faiss_case_db/faiss_index.idx")
META_PATH = Path("vectordb/faiss_case_db/faiss_meta.pkl")

# 인덱스 및 메타데이터 로딩
try:
    faiss_index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    logger.info("FAISS 인덱스 및 메타데이터 로딩 완료")
except Exception as e:
    logger.error(f"FAISS 인덱스 로딩 실패: {e}")
    faiss_index = None
    metadata = []

def search_similar_cases(query: str, similarity_threshold: float = 1.95) -> list:
    """OpenAI 임베딩 기반 FAISS 유사 판례 검색 (유사도 임계값 기준 필터링)"""
    try:
        if faiss_index is None or not metadata:
            logger.error("FAISS 인덱스가 로드되지 않았습니다.")
            return []
        
        print(f"DEBUG: 검색 쿼리: {query}")
        print(f"DEBUG: 유사도 임계값: {similarity_threshold}")
        
        # 임베딩 생성
        try:
            query_vec = np.array(get_embedding(query)).reshape(1, -1).astype("float32")
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            return []
        
        total = faiss_index.ntotal
        print(f"DEBUG: FAISS 인덱스 총 문서 수: {total}")
        
        # 전체 검색 후 임계값으로 필터링
        scores, indices = faiss_index.search(query_vec, total)
        print(f"DEBUG: 검색된 결과 수: {len(indices[0])}")
        print(f"DEBUG: 최고 유사도 점수: {scores[0][0]:.4f}")
        print(f"DEBUG: 최저 유사도 점수: {scores[0][-1]:.4f}")

        results = []
        results_dict = {}

        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(metadata):
                # case: 특정 판례 메타 데이터 (case_id, case_num)
                case = metadata[idx]

                # case_id가 있으면 사용, 없으면 사건번호 사용
                case_id = case.get("case_id")
                if case_id is None:
                    case_id = case.get("사건번호", f"{idx}")
                
                similarity_score = float(scores[0][i])
                
                # 유사도 임계값 이하인 결과만 포함 (FAISS는 거리 기반이므로 낮은 값이 더 유사함)
                if similarity_score <= similarity_threshold:
                    # 상위 10개 결과에 대해 상세 정보 출력
                    if len(results_dict) < 10:
                        print(f"DEBUG: [{len(results_dict)+1}] case_id: {case_id}, 유사도: {similarity_score:.4f}")
                    if case_id not in results_dict.keys():
                        results_dict[case_id] = similarity_score
                    
                        # results.append({
                        #     "case_id": str(case_id),
                        #     "similarity": similarity_score
                        # })
        
        results = [{"case_id": k, "similarity": v} for k, v in list(results_dict.items())]
        print(f"DEBUG: 임계값 {similarity_threshold} 이하 결과 수: {len(results)}")
        return results
        
    except Exception as e:
        logger.error(f"벡터 검색 중 오류 발생: {e}")
        return []
