import os
import numpy as np
import json
import requests
import time
from ..core.config import settings

# Offloading embeddings to HuggingFace Inference API to save RAM on Render Free Tier.
# This prevents OOM (Out of Memory) crashes by avoiding loading Torch/Sentence-Transformers locally.

def get_embeddings(texts: list) -> np.ndarray:
    """Query HuggingFace Inference API for embeddings."""
    # We use the same model as configured or a standard embedding model
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}
    
    # HF Inference API might return 503 if model is loading
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json={"inputs": texts}, timeout=60)
            if response.status_code == 503:
                print(f"Embedding model loading, waiting... (Attempt {attempt+1})")
                time.sleep(10)
                continue
                
            response.raise_for_status()
            embeddings = response.json()
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error calling HF Embedding API: {e}")
                raise e
            time.sleep(2)
    return np.zeros((len(texts), 384), dtype=np.float32)

def get_dimension():
    return 384  # fixed for all-MiniLM-L6-v2

def get_faiss_index(repo_id: str):
    """
    Returns the loaded FAISS index and metadata for a repo.
    """
    import faiss
    repo_data_dir = os.path.join(settings.DATA_DIR, repo_id)
    index_path = os.path.join(repo_data_dir, "faiss_index.bin")
    meta_path = os.path.join(repo_data_dir, "faiss_meta.json")
    
    if os.path.exists(index_path) and os.path.exists(meta_path):
        index = faiss.read_index(index_path)
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        return index, metadata
        
    # Return empty if doesn't exist
    index = faiss.IndexFlatL2(get_dimension())
    return index, []

def save_faiss_index(repo_id: str, index, metadata):
    import faiss
    repo_data_dir = os.path.join(settings.DATA_DIR, repo_id)
    os.makedirs(repo_data_dir, exist_ok=True)
    
    faiss.write_index(index, os.path.join(repo_data_dir, "faiss_index.bin"))
    with open(os.path.join(repo_data_dir, "faiss_meta.json"), 'w') as f:
        json.dump(metadata, f)

def index_chunks(repo_id: str, files_data: list):
    """
    Indexes the file chunks into FAISS and stores the metadata
    """
    import faiss
    index, metadata = get_faiss_index(repo_id)
    
    texts_to_embed = []
    new_metadata = []
    
    for file in files_data:
        path = file["path"]
        for chunk in file["chunks"]:
            # Contextualize chunk
            text = f"File: {path}\nContent:\n{chunk}"
            texts_to_embed.append(text)
            new_metadata.append({
                "repo_id": repo_id,
                "path": path,
                "text": text,
                "source_type": "repo_code"
            })
            
    if not texts_to_embed:
        return
        
    # Process in batches of 50 to avoid HF API payload limits
    batch_size = 50
    all_embeddings = []
    for i in range(0, len(texts_to_embed), batch_size):
        batch = texts_to_embed[i:i + batch_size]
        embeddings = get_embeddings(batch)
        all_embeddings.append(embeddings)
    
    embeddings = np.vstack(all_embeddings)
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings)
    metadata.extend(new_metadata)
    
    save_faiss_index(repo_id, index, metadata)
    
def index_scrape(repo_id: str, url: str, title: str, chunks: list):
    """
    Indexes newly scraped external docs into the repo's FAISS index.
    """
    import faiss
    index, metadata = get_faiss_index(repo_id)
    
    texts_to_embed = []
    new_metadata = []
    
    for chunk in chunks:
        text = f"Source: {title} ({url})\nContent:\n{chunk}"
        texts_to_embed.append(text)
        new_metadata.append({
            "repo_id": repo_id,
            "path": url,
            "text": text,
            "source_type": "external_doc"
        })
        
    if not texts_to_embed:
        return
        
    embeddings = get_embeddings(texts_to_embed)
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings)
    metadata.extend(new_metadata)
    
    save_faiss_index(repo_id, index, metadata)

def search_index(repo_id: str, query: str, top_k: int = 5):
    import faiss
    index, metadata = get_faiss_index(repo_id)
    if index.ntotal == 0:
        return []
        
    query_emb = get_embeddings([query])
    faiss.normalize_L2(query_emb)
    
    distances, indices = index.search(query_emb, top_k)
    
    results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        if idx != -1 and idx < len(metadata):
            results.append({
                "score": float(distances[0][i]),
                "metadata": metadata[idx]
            })
            
    return results
