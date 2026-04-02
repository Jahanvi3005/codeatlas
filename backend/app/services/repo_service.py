import os
import shutil
from git import Repo, exc
from sqlalchemy.orm import Session
import logging

from ..models.entities import Repository, ProcessingStatus
from ..core.config import settings
from . import scan_service, vector_service, intelligence_service

logger = logging.getLogger(__name__)

def update_status(db: Session, repo_id: str, status: ProcessingStatus, error_message: str = None):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if repo:
        repo.status = status
        repo.error_message = error_message
        db.commit()

def process_repository(repo_id: str, url: str, db: Session):
    repo_path = os.path.join(settings.REPOS_DIR, repo_id)
    
    try:
        # 1. Clone
        update_status(db, repo_id, ProcessingStatus.CLONING)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            
        logger.info(f"Cloning {url} into {repo_path}")
        Repo.clone_from(url, repo_path, depth=1)
        
        # 2. Parse and chunk files
        update_status(db, repo_id, ProcessingStatus.PARSING)
        files_data = scan_service.scan_and_chunk_repo(repo_path)
        
        # 3. Index embeddings
        update_status(db, repo_id, ProcessingStatus.INDEXING)
        vector_service.index_chunks(repo_id, files_data)
        
        # 4. Save metadata
        scan_service.save_metadata(repo_id, repo_path, files_data)
        
        # 5. Deep Intelligence Analysis
        update_status(db, repo_id, ProcessingStatus.COMPLETED)
        
        try:
            tree_data = scan_service.load_tree(repo_id)
            
            def get_names(nodes, depth=0):
                if depth > 2: return "" 
                res = ""
                for n in nodes[:15]: 
                    res += "  " * depth + f"- {n['name']} ({n['type']})\n"
                    if n.get('children'):
                        res += get_names(n['children'], depth + 1)
                return res
            
            tree_summary = get_names(tree_data)
            intel = intelligence_service.analyze_repo_intelligence(repo_path, tree_summary)
            scan_service.update_summary_with_intelligence(repo_id, intel)
        except Exception as e:
            print(f"Deep intelligence failed for {repo_id}: {e}")
        
    except exc.GitCommandError as e:
        logger.error(f"Git clone failed: {str(e)}")
        update_status(db, repo_id, ProcessingStatus.FAILED, "Failed to clone repository")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        update_status(db, repo_id, ProcessingStatus.FAILED, str(e))
    finally:
        
        pass

def get_summary(repo_id: str):
    return scan_service.load_summary(repo_id)

def get_tree(repo_id: str):
    return scan_service.load_tree(repo_id)
