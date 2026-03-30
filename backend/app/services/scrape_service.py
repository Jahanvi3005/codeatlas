import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
import logging

from ..models.entities import ScrapedSource, ProcessingStatus
from . import chunk_service, vector_service

logger = logging.getLogger(__name__)

def update_status(db: Session, scrape_id: str, status: ProcessingStatus, title: str = None):
    source = db.query(ScrapedSource).filter(ScrapedSource.id == scrape_id).first()
    if source:
        source.status = status
        if title:
            source.title = title
        db.commit()

def process_scrape(scrape_id: str, repo_id: str, url: str, db: Session):
    try:
        update_status(db, scrape_id, ProcessingStatus.PARSING)
        
        headers = {
            "User-Agent": "CodeAtlas/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else "Untitled Document"
        
        # Clean up script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        chunks = chunk_service.chunk_text(text)
        
        update_status(db, scrape_id, ProcessingStatus.INDEXING, title=title)
        
        vector_service.index_scrape(repo_id, url, title, chunks)
        
        update_status(db, scrape_id, ProcessingStatus.COMPLETED)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to scrape {url}: {e}")
        update_status(db, scrape_id, ProcessingStatus.FAILED)
    except Exception as e:
        logger.error(f"Error processing scrape {url}: {e}")
        update_status(db, scrape_id, ProcessingStatus.FAILED)
