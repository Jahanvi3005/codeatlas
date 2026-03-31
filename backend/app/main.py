print(">>> [1/4] Starting main.py loading...")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.api import api_router

print(">>> [2/4] Base imports successful. Initializing FastAPI app...")

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
    print(">>> [3/4] Running startup event...")
    try:
        # Import init_db inside to catch potential import errors
        print(">>> [3.1] Importing database init...")
        from .core.database import init_db
        print(">>> [3.2] Calling init_db()...")
        init_db()
        print("✅ [4/4] Backend initialized successfully.")
    except Exception as e:
        print(f"❌ ERROR DURING STARTUP: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # Keep the app running so Render sees the port as open 
        # but report the error in logs

@app.get("/")
async def root():
    return {"message": "CodeAtlas API is running", "docs": "/docs"}

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok"}
