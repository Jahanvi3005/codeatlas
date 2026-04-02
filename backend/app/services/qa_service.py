import os
import requests
from typing import Dict, Any
from .vector_service import search_index
from ..core.config import settings


def _query_hf(prompt: str) -> str:
    """Query HuggingFace Router API with a given prompt."""
    api_url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.HF_MODEL,
        "messages": [
            {"role": "user", "content": prompt.strip()}
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
        "stream": False
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        return str(data)

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 503:
            return "The AI model is currently loading. Please wait a moment and try again."
        return f"HuggingFace API error {status}: {e.response.text[:200]}"
    except Exception as e:
        return f"Unexpected error querying HuggingFace: {str(e)}"


def answer_query(repo_id: str, query: str) -> Dict[str, Any]:
    """
    Queries the vector database and structures the context to return a grounded response.
    Passes the context to HuggingFace Inference API to generate the final answer.
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
            "snippet": text[:200] + "..."
        })

        context_text += f"[{rank+1}] {path}:\n{text}\n\n"

    prompt = f"""You are CodeAtlas, an AI assistant helping a developer navigate their repository.
Use the following retrieved context chunks to answer the user's question accurately.
If the answer is not contained in the context, clearly state that you do not know based on the indexed files.

Context:
{context_text}

Question: {query}"""

    structured_answer = _query_hf(prompt)

    return {
        "answer": structured_answer,
        "sources": sources
    }
