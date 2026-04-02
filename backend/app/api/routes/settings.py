from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...core.config import settings
import os

router = APIRouter()

class SettingsUpdate(BaseModel):
    ollama_url: str
    ollama_model: str

@router.get("/")
async def get_settings():
    return {
        "ollama_url": settings.OLLAMA_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL
    }

@router.put("/")
async def update_settings(update: SettingsUpdate):
   
    settings.OLLAMA_URL = update.ollama_url
    settings.OLLAMA_MODEL = update.ollama_model
    
    
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith("OLLAMA_URL="):
                    f.write(f"OLLAMA_URL={update.ollama_url}\n")
                elif line.startswith("OLLAMA_MODEL="):
                    f.write(f"OLLAMA_MODEL={update.ollama_model}\n")
                else:
                    f.write(line)
    except Exception as e:
        print(f"Failed to persist settings to .env: {e}")

    return {"message": "Settings updated successfully", "applied": update}
