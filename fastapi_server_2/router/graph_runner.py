from fastapi import APIRouter
from pydantic import BaseModel
from langgraph_graph.graph_builder import build_langgraph

router = APIRouter(tags=["LangGraph"])

# FastAPI의 요청 검증용 Pydantic 모델
class GraphInput(BaseModel):
    cat_cd: str
    e_description: str

@router.post("/run-recommend")
async def run_graph(input_data: GraphInput):
    try:
        graph = build_langgraph()
        result = await graph.ainvoke({
            "cat_cd": input_data.cat_cd,
            "e_description": input_data.e_description
        })
        print("[DEBUG] LangGraph 결과:", result)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

