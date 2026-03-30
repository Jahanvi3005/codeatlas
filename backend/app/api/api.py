from fastapi import APIRouter

from .routes import repositories, chat, scraping, settings

api_router = APIRouter()
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(scraping.router, prefix="/scrape", tags=["scraping"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
