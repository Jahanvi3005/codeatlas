print(">>> [1/4] Starting main.py loading...")

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.api import api_router
import time

print(">>> [2/4] Base imports successful. Defining lifespan...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print(">>> [3/4] Running startup routine...")
    try:
        from .core.database import init_db
        print(">>> [3.1] Initializing database...")
        init_db()
        print("✅ [4/4] Backend initialized successfully.")
    except Exception as e:
        print(f"❌ ERROR DURING STARTUP: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    # Shutdown logic (empty for now)
    print("👋 Backend shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI-powered repository intelligence platform",
    lifespan=lifespan
)

# 📥 REQUEST LOGGER MIDDLEWARE
# This will print every single request to Render logs so we can debug the 502/CORS
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"📥 [REQUEST] {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    print(f"📤 [RESPONSE] {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response

# 🌉 CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CodeAtlas API is running", "docs": "/docs"}

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok"}
