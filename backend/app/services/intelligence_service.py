import os
import json
import requests
import re
from ..core.config import settings


def sanitize_mermaid(chart: str) -> str:
    """Cleans up common AI-generated Mermaid syntax errors and discards trailing junk."""
    if not chart: return ""
    # 1. Normalize arrows
    chart = re.sub(r'(?<!-)>(?!-)', '-->', chart)
    chart = re.sub(r' -> ', ' --> ', chart)

    # 2. Rebuild clean diagram line by line
    lines = ["graph TD"]
    raw_lines = re.split(r'[\n;]+', chart)

    def clean_id(node_text):
        label = node_text
        match = re.search(r'\[(.*?)\]', node_text)
        if match:
            label = match.group(1).replace('"', '')
            node_id = re.sub(r'\[.*?\]', '', node_text).strip()
        else:
            node_id = node_text.strip().replace('"', '')

        safe_id = re.sub(r'[^a-zA-Z0-9]', '_', node_id).strip('_')
        if not safe_id: safe_id = "node_" + str(hash(node_id) % 1000)
        safe_id = f"id_{safe_id}"
        return f'{safe_id}["{label}"]'

    for line in raw_lines:
        line = line.strip()
        if not line or "graph " in line: continue

        if "-->" in line:
            parts = re.split(r'--+>', line)
            for i in range(len(parts)-1):
                left, right = parts[i].strip(), parts[i+1].strip()
                lines.append(f"  {clean_id(left)} --> {clean_id(right)}")
        else:
            lines.append(f"  {clean_id(line)}")

    return "\n".join(lines).strip()


def _query_hf(prompt: str, as_json: bool = False) -> str:
    """Query HuggingFace Router API."""
    api_url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    json_hint = "\nRespond ONLY with a raw JSON object. No markdown, no explanation." if as_json else ""
    
    payload = {
        "model": settings.HF_MODEL,
        "messages": [
            {"role": "user", "content": f"{prompt.strip()}{json_hint}"}
        ],
        "max_tokens": 1500,
        "temperature": 0.2,
        "stream": False
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"].strip()
    return str(data)


def analyze_repo_intelligence(repo_path: str, file_tree_summary: str):
    """
    Analyzes the repository using manifest files and file tree.
    Returns structured architecture, tech stack, flow chart, and summary.
    """
    # 1. Identify and read manifest files
    manifests = {}
    manifest_names = ['package.json', 'requirements.txt', 'go.mod', 'pom.xml',
                      'build.gradle', 'README.md', 'docker-compose.yml', 'Dockerfile']

    for root, _, files in os.walk(repo_path):
        rel_depth = os.path.relpath(root, repo_path).count(os.sep)
        if rel_depth > 1:
            continue
        for f in files:
            if f in manifest_names:
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                        manifests[f] = file.read(2048)
                except:
                    pass

    # 2. Build Prompt
    manifest_context = "\n".join([f"--- {name} ---\n{content}" for name, content in manifests.items()])

    prompt = f"""Analyze the following repository structure and manifest files.
Generate a JSON object strictly following this structure:
{{
  "architecture": "Concise description of the architecture (e.g. MVC, Client-Server, Layered)",
  "tech_stack": ["List", "of", "detected", "technologies"],
  "flow_chart": "A detailed Mermaid graph TD string mapping the repository's core logic flow",
  "deep_summary": "A 2-paragraph executive summary of what this code does and its main features"
}}

RULES for Mermaid flow_chart:
1. Start with 'graph TD'.
2. Use ONLY double arrows '-->' for connections. NEVER use single '->'.
3. Use snake_case for technical node IDs (no spaces, dots or commas) and use Brackets with Quotes for visible labels.
   Example: Audio_Preprocessing["Audio Preprocessing"] --> Feature_Extraction["Feature Extraction"]
4. Create a detailed map with 5-8 major components matching the file tree.

File Tree:
{file_tree_summary}

Manifest Context:
{manifest_context}

Return ONLY the raw JSON object. Do not include markdown code blocks."""

    # 3. Query HuggingFace
    try:
        raw_response = _query_hf(prompt, as_json=True)

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            raw_response = json_match.group(0)

        intelligence = json.loads(raw_response)

        # Apply defaults
        defaults = {
            "architecture": "Layered architecture",
            "tech_stack": [],
            "flow_chart": "graph TD\n  Repo --> Index",
            "deep_summary": "System analysis complete."
        }
        for key, val in defaults.items():
            if key not in intelligence or not intelligence[key]:
                intelligence[key] = val

        # Sanitize
        intelligence["flow_chart"] = sanitize_mermaid(intelligence["flow_chart"])
        return intelligence

    except Exception as e:
        print(f"Intelligence Generation Failed: {str(e)}")
        return {
            "architecture": "Detection paused",
            "tech_stack": [],
            "flow_chart": "graph TD\n  System --> Recovery_Mode",
            "deep_summary": "The AI is currently processing a large amount of project data. Please restart the backend and re-ingest to see the full architectural map."
        }
