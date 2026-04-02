import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeAtlas"
    API_V1_STR: str = "/api"
    
    # Storage Configuration
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    DB_URL: str = os.getenv("DB_URL", f"sqlite:///{os.path.join(DATA_DIR, 'codeatlas.db')}")
    REPOS_DIR: str = os.getenv("REPOS_DIR", os.path.join(DATA_DIR, "repos"))
    FAISS_INDEX_PATH: str = os.path.join(DATA_DIR, "faiss_index.bin")
    
    # Vector & LLM Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()

# Ensure critical directories exist immediately on startup
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.REPOS_DIR, exist_ok=True)
