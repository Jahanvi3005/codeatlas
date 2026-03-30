import os
import json
import requests
from ..core.config import settings

def analyze_repo_intelligence(repo_path: str, file_tree_summary: str):
    """
    Analyzes the repository using manifest files and file tree.
    Returns structured architecture, tech stack, flow chart, and summary.
    """
    # 1. Identify and read manifest files
    manifests = {}
    manifest_names = ['package.json', 'requirements.txt', 'go.mod', 'pom.xml', 'build.gradle', 'README.md', 'docker-compose.yml', 'Dockerfile']
    
    for root, _, files in os.walk(repo_path):
        # Only look at top levels for manifests
        rel_depth = os.path.relpath(root, repo_path).count(os.sep)
        if rel_depth > 1:
            continue
            
        for f in files:
            if f in manifest_names:
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                        # Only take first 2KB of each manifest for context
                        manifests[f] = file.read(2048)
                except:
                    pass

    # 2. Build Prompt
    manifest_context = "\n".join([f"--- {name} ---\n{content}" for name, content in manifests.items()])
    
    prompt = f"""
Analyze the following repository structure and manifest files. 
Generate a JSON object strictly following this structure:
{{
  "architecture": "Concise description of the architecture (e.g. MVC, Client-Server, Layered)",
  "tech_stack": ["List", "of", "detected", "technologies"],
  "flow_chart": "A simple Mermaid graph TD string (e.g., graph TD; A-->B; B-->C;)",
  "deep_summary": "A 2-paragraph executive summary of what this code does and its main features"
}}

File Tree:
{file_tree_summary}

Manifest Context:
{manifest_context}

Return ONLY the raw JSON object. Do not include markdown code blocks.
"""

    # 3. Query Ollama
    url = f"{settings.OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        raw_response = data.get("response", "").strip()
        
        # Robust extraction if the model used markdown backticks
        if "```" in raw_response:
            # Try to get content between ```json and ```
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            else:
                raw_response = raw_response.split("```")[1].split("```")[0].strip()
        
        intelligence = json.loads(raw_response)
        
        # Basic validation of fields
        defaults = {
            "architecture": "Layered architecture",
            "tech_stack": [],
            "flow_chart": "graph TD\n  Repo --> Index",
            "deep_summary": "No summary generated."
        }
        for key, val in defaults.items():
            if key not in intelligence or not intelligence[key]:
                intelligence[key] = val
                
        return intelligence
    except Exception as e:
        print(f"Intelligence analysis failed: {str(e)}")
        return {
            "architecture": "Detection failed",
            "tech_stack": [],
            "flow_chart": "graph TD\n  Start --> Error",
            "deep_summary": "Failed to generate AI summary."
        }
