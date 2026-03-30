from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid


from ...core.database import get_db
from ...models.schemas import RepositoryCreate, RepositoryResponse, TreeResponse, SummaryResponse
from ...models.entities import Repository, ProcessingStatus
from ...services import repo_service

router = APIRouter()

@router.post("/ingest", response_model=RepositoryResponse)
def ingest_repository(
    request: RepositoryCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)  
):
    repo_id = str(uuid.uuid4())
    repo = Repository(
        id=repo_id,
        url=request.url,
        name=request.url.split("/")[-1].replace(".git", ""),
        status=ProcessingStatus.PENDING
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    
    background_tasks.add_task(repo_service.process_repository, repo_id, request.url, db)
    return repo

@router.get("/{repo_id}/status", response_model=RepositoryResponse)
def get_repository_status(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.get("/{repo_id}/summary", response_model=SummaryResponse)
def get_repository_summary(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Repository processing not completed")
    
    summary = repo_service.get_summary(repo_id)
    return summary

@router.get("/{repo_id}/tree", response_model=TreeResponse)
def get_repository_tree(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    tree = repo_service.get_tree(repo_id)
    return {"tree": tree}
