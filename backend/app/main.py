from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import init_db
from .api.api import api_router

# Router and Middleware setup

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI-powered repository intelligence platform"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting CodeAtlas Backend...")
    try:
        # Initialize Database in startup to prevent blocking port binding
        init_db()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Error during startup: {e}")

@app.get("/")
async def root():
    return {"message": "CodeAtlas API is running", "docs": "/docs"}

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok"}
