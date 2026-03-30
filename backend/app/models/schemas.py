from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .entities import ProcessingStatus

class RepositoryCreate(BaseModel):
    url: str

class RepositoryResponse(BaseModel):
    id: str
    url: str
    name: str
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatQuery(BaseModel):
    query: str
    repository_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]

class ScrapeRequest(BaseModel):
    url: str
    repository_id: str

class ScrapeResponse(BaseModel):
    id: str
    url: str
    title: str
    status: ProcessingStatus

class TreeNode(BaseModel):
    name: str
    path: str
    type: str  # "file" or "directory"
    children: Optional[List["TreeNode"]] = None

class TreeResponse(BaseModel):
    tree: List[TreeNode]
    
class SummaryResponse(BaseModel):
    file_count: int
    language_counts: dict
    total_size_bytes: int
    architecture: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    flow_chart: Optional[str] = None
    deep_summary: Optional[str] = None
