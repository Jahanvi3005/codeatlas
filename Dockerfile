
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./

RUN VITE_API_URL=/api npm run build


FROM python:3.11-slim-bullseye AS backend-build
WORKDIR /app/backend


RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*


COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY backend/ ./


COPY --from=frontend-build /app/frontend/dist /app/backend/static


RUN mkdir -p /app/data/repos && chmod -R 777 /app/data


ENV PYTHONPATH=/app/backend
ENV DATA_DIR=/app/data
ENV PORT=7860
ENV PYTHONUNBUFFERED=1


EXPOSE 7860


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
