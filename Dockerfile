# --- STAGE 1: Build Frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Build Backend ---
FROM python:3.11-slim-bullseye AS backend-build
WORKDIR /app/backend

# Install system dependencies (needed for FAISS and git)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy the built frontend from STAGE 1
COPY --from=frontend-build /app/frontend/dist /app/backend/static

# Create data directories
RUN mkdir -p /app/data/repos && chmod -R 777 /app/data

# Environment Variables
ENV PYTHONPATH=/app/backend
ENV DATA_DIR=/app/data
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start command: Use Uvicorn to run FastAPI
# We will serve the static files via FastAPI itself
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
