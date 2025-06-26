# app/services/vector_search.py

import faiss
import numpy as np
import pickle
from pathlib import Path
from services.embedding import get_embedding

# 경로 설정
INDEX_PATH = Path("data/faiss_index.idx")
META_PATH = Path("data/faiss_meta.pkl")

# 인덱스 및 메타데이터 로딩
faiss_index = faiss.read_index(str(INDEX_PATH))
with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

def search_similar_cases(query: str) -> list:
    """OpenAI 임베딩 기반 FAISS 유사 판례 검색 (전체 대상)"""
    query_vec = np.array(get_embedding(query)).reshape(1, -1).astype("float32")
    total = faiss_index.ntotal
    scores, indices = faiss_index.search(query_vec, total)

    results = []
    for i, idx in enumerate(indices[0]):
        if 0 <= idx < len(metadata):
            case = metadata[idx]
            meta = case.get("meta", {})
            contents = case.get("contents", "")
            
            # case_id가 있으면 사용, 없으면 사건번호 사용
            case_id = meta.get("case_id")
            if case_id is None:
                case_id = meta.get("사건번호", f"CASE-{idx}")
            
            results.append({
                "case_id": str(case_id),
                "title": meta.get("사건명", ""),
                "summary": contents[:300],  # 요약 일부만
                "similarity": float(scores[0][i])
            })
    return results
