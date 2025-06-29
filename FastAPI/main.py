from fastapi import FastAPI

from pydantic import BaseModel
from typing import TypedDict, Dict, Optional
from fastapi import Request
from langgraph.graph import StateGraph, END
from routers import scorecalc, explain, graph_runner

app = FastAPI()

# FastAPI 라우터 등록
app.include_router(scorecalc.router)
app.include_router(explain.router)
app.include_router(graph_runner.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)