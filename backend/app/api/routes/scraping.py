from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...core.database import get_db
from ...models.schemas import ScrapeRequest, ScrapeResponse
from ...models.entities import ScrapedSource, ProcessingStatus
from ...services import scrape_service

router = APIRouter()

@router.post("/docs", response_model=ScrapeResponse)
def scrape_docs(
    request: ScrapeRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)  
):
    scrape_id = str(uuid.uuid4())
    scrape = ScrapedSource(
        id=scrape_id,
        repository_id=request.repository_id,
        url=request.url,
        title="Pending...",
        status=ProcessingStatus.PENDING
    )
    db.add(scrape)
    db.commit()
    db.refresh(scrape)
    
    background_tasks.add_task(scrape_service.process_scrape, scrape_id, request.repository_id, request.url, db)
    
    return scrape

@router.get("/docs/{repo_id}", response_model=List[ScrapeResponse])
def get_scraped_sources(repo_id: str, db: Session = Depends(get_db)):
    sources = (
        db.query(ScrapedSource)
        .filter(ScrapedSource.repository_id == repo_id)
        .order_by(ScrapedSource.created_at.desc())
        .all()
    )
    return sources
