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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 🌉 CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# 🏞️ SERVE FRONTEND (If built)
# We do this AFTER the API routes to ensure they take priority
static_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "static"))
print(f">>> Static path resolved to: {static_path}")
print(f">>> Static path exists: {os.path.exists(static_path)}")

if os.path.exists(static_path):
    assets_path = os.path.join(static_path, "assets")
    if os.path.exists(assets_path):
        # Mount CSS/JS assets
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
        print(f"✅ Mounted /assets from {assets_path}")
    else:
        print(f"⚠️ Assets dir not found at {assets_path}")

    # Serve the main index.html for root and all frontend routes (SPA behavior)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return {"error": "API route not found"}
        index_file = os.path.join(static_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend not built"}
else:
    print(f"⚠️ No static directory found. Serving API only.")

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}
