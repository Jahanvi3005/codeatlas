import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from ..core.config import settings

# Initialize model
try:
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    dimension = model.get_sentence_embedding_dimension()
except Exception as e:
    print(f"Warning: Failed to load embeddings model: {e}")
    # Fallback to a mock for fast tests if downloading fails
    dimension = 384

def get_faiss_index(repo_id: str):
    """
    Returns the loaded FAISS index and metadata for a repo.
    """
    repo_data_dir = os.path.join(settings.DATA_DIR, repo_id)
    index_path = os.path.join(repo_data_dir, "faiss_index.bin")
    meta_path = os.path.join(repo_data_dir, "faiss_meta.json")
    
    if os.path.exists(index_path) and os.path.exists(meta_path):
        index = faiss.read_index(index_path)
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        return index, metadata
        
    # Return empty if doesn't exist
    index = faiss.IndexFlatL2(dimension)
    return index, []

def save_faiss_index(repo_id: str, index, metadata):
    repo_data_dir = os.path.join(settings.DATA_DIR, repo_id)
    os.makedirs(repo_data_dir, exist_ok=True)
    
    faiss.write_index(index, os.path.join(repo_data_dir, "faiss_index.bin"))
    with open(os.path.join(repo_data_dir, "faiss_meta.json"), 'w') as f:
        json.dump(metadata, f)

def index_chunks(repo_id: str, files_data: list):
    """
    Indexes the file chunks into FAISS and stores the metadata
    """
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
        
    embeddings = model.encode(texts_to_embed, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings)
    metadata.extend(new_metadata)
    
    save_faiss_index(repo_id, index, metadata)
    
def index_scrape(repo_id: str, url: str, title: str, chunks: list):
    """
    Indexes newly scraped external docs into the repo's FAISS index.
    """
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
        
    embeddings = model.encode(texts_to_embed, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings)
    metadata.extend(new_metadata)
    
    save_faiss_index(repo_id, index, metadata)

def search_index(repo_id: str, query: str, top_k: int = 5):
    index, metadata = get_faiss_index(repo_id)
    if index.ntotal == 0:
        return []
        
    query_emb = model.encode([query], convert_to_numpy=True)
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
