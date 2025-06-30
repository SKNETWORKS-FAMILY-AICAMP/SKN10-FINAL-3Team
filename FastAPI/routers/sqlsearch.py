from fastapi import APIRouter
from services.sqlsearch_service import sqlsearch_node

router = APIRouter(prefix="/sqlsearch", tags=["SQLSearch"])

@router.post("/run")
async def run_sqlsearch(data: dict):
    result = sqlsearch_node(data)
    print("[DEBUG] sqlsearch router result:", result)
    return result
