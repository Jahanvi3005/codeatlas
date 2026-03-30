import os
import requests
from typing import Dict, Any
from .vector_service import search_index
from ..core.config import settings

def _query_ollama(prompt: str) -> str:
    """Helper to query the local Ollama daemon via REST payload."""
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.ConnectionError:
        return f"Error connecting to Ollama: Could not reach {url}. Is your Ollama daemon running?"
    except requests.exceptions.HTTPError as e:
        return f"Ollama HTTP error: {e.response.status_code} - perhaps the model '{settings.OLLAMA_MODEL}' is not pulled locally."
    except Exception as e:
        return f"Unexpected error querying Ollama: {str(e)}"

def answer_query(repo_id: str, query: str) -> Dict[str, Any]:
    """
    Queries the vector database and structures the context to return a grounded response.
    Passes the context to Ollama to generate the final chat answer.
    """
    results = search_index(repo_id, query, top_k=5)
    
    if not results:
        return {
            "answer": "I couldn't find any relevant code chunks in the indexed repository to answer your question.",
            "sources": []
        }
        
    context_text = ""
    sources = []
    
    for rank, res in enumerate(results):
        meta = res["metadata"]
        path = meta.get("path", "Unknown Source")
        source_type = meta.get("source_type", "unknown")
        text = meta.get("text", "")
        
        sources.append({
            "path": path,
            "type": source_type,
            "snippet": text[:200] + "..." # Snippet for the UI reference
        })
        
        context_text += f"[{rank+1}] {path}:\n{text}\n\n"
        
    prompt = f"""
You are CodeAtlas, an AI assistant helping a developer navigate their repository.
Use the following retrieved context chunks to answer the user's question accurately.
If the answer is not contained in the context, clearly state that you do not know based on the indexed files.

Context:
{context_text}

Question: {query}
"""

    structured_answer = _query_ollama(prompt)
        
    return {
        "answer": structured_answer,
        "sources": sources
    }
