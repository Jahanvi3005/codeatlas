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
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    # Mount regular static assets (JS/CSS)
    # Vite usually puts them in /assets/
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")

    # Serve the main index.html for the root and all other unknown paths (SPA behavior)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If it's a request for an API, we already missed it, so return 404
        if full_path.startswith("api"):
            return {"error": "API route not found"}
        # Otherwise, serve the React app
        return FileResponse(os.path.join(static_path, "index.html"))

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok"}
