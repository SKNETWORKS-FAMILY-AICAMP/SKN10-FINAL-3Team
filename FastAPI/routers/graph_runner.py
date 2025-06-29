from fastapi import APIRouter
from pydantic import BaseModel
from langgraph_graph.graph_builder import build_langgraph

router = APIRouter(tags=["LangGraph"])

# FastAPI의 요청 검증용 Pydantic 모델
class GraphInput(BaseModel):
    cat_cd: str
    e_description: str

@router.post("/run-graph")
async def run_graph(input_data: GraphInput):
    graph = build_langgraph()
    result = await graph.ainvoke({
        "cat_cd": input_data.cat_cd,
        "e_description": input_data.e_description
    })
    return result
