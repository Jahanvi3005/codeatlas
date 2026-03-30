from fastapi import APIRouter, Depends, HTTPException
from ...models.schemas import ChatQuery, ChatResponse
from ...services.qa_service import answer_query

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
def query_repository(request: ChatQuery):
    response = answer_query(request.repository_id, request.query)
    if not response:
        raise HTTPException(status_code=400, detail="Repository not found or not indexed")
    return response
