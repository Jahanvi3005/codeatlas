# CodeAtlas

CodeAtlas is a full-stack AI-empowered repository intelligence platform. It clones your public Git repositories, chunks the code semantics into localized embeddings, and provides a polished chat interface to explore the architecture or debug its flows entirely using natural language. 

Built beautifully with a `React`, `Vite`, and `Tailwind CSS` frontend paired with a highly concurrent `FastAPI` and `FAISS`-powered Python backend.

## Features

- **Semantic Repo Ingestion**: Seamlessly processes `.py`, `.js`, `.tsx`, `.md`, and more to understand how the code interconnects.
- **Deep Code Q&A**: Employs `sentence-transformers` vectorization and `FAISS` indexing to ground chat responses directly to files and blocks within the repo.
- **Web Doc Enrichment**: Paste a URL to your project's hosted documentation to scrape (using `BeautifulSoup`), clean, and ingest it into the index context dynamically.
- **Dynamic Frontend**: Modern transitions built with `Framer Motion` and stylized using `Tailwind CSS`.

## Architecture Details
The platform parses git links and spins off a background task that clones the repository. A sliding-window chunking strategy overlaps snippets of code before encoding them into embeddings. Queries map against the FAISS vector index, pulling top nearest neighbors to be synthesized into responses alongside highly accurate file citations.

## Running Locally

### 1. Start the Backend
You will need Python 3.9+ installed.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173`.

## Deployment to Render

This project includes a `render.yaml` configuration for quick deployment.
1. Create a `New Blueprint Instance` on your Render Dashboard and connect this repository.
2. Render will spin up:
   - `codeatlas-backend`: A Python Web Service hosting the FastAPI instance.
   - `codeatlas-frontend`: A Static Site hosting the compiled React bundle.
3. *Note*: For persistent index storage across deployments, navigate to the `codeatlas-backend` service settings and configure a Persistent Disk mapped to `/data`.

## Future Enhancements
- Expand LLM integration (e.g. OpenAI/Anthropic keys for contextual generation).
- Graph visualization for folder structures.
- User authentication and persistent sessions.
