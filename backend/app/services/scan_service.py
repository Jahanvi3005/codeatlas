import os
import json
from .chunk_service import chunk_text
from ..core.config import settings

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".json", 
    ".txt", ".css", ".html", ".sh", ".yaml", ".yml"
}

def scan_and_chunk_repo(repo_path: str):
    """
    Scans the repository, extracts files, calculates metrics, and chunks text.
    Returns files_data for indexing.
    """
    files_data = []
    
    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                chunks = chunk_text(content)
                
                # Normalize relative path to forward slashes for the web tree
                web_path = rel_path.replace(os.sep, '/')
                
                files_data.append({
                    "path": web_path,
                    "extension": ext,
                    "size": os.path.getsize(file_path),
                    "content": content,
                    "chunks": chunks
                })
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")
                
    return files_data

def save_metadata(repo_id: str, repo_path: str, files_data: list):
    """
    Saves metrics and tree to disk as simple JSON for easy fetching.
    """
    metadata_dir = os.path.join(settings.DATA_DIR, repo_id)
    os.makedirs(metadata_dir, exist_ok=True)
    
    # 1. Generate Summary
    language_counts = {}
    total_size = 0
    for file in files_data:
        ext = file["extension"]
        language_counts[ext] = language_counts.get(ext, 0) + 1
        total_size += file["size"]
        
    summary = {
        "file_count": len(files_data),
        "language_counts": language_counts,
        "total_size_bytes": total_size
    }
    
    with open(os.path.join(metadata_dir, "summary.json"), 'w') as f:
        json.dump(summary, f)
        
    # 2. Generate Tree
    tree = {}
    for file in files_data:
        # Already normalized to / in scan_and_chunk_repo
        parts = file["path"].split('/')
        current = tree
        for part in parts[:-1]:
            if not part: continue # skip empty parts
            if part not in current or current[part] == "FILE":
                current[part] = {}
            current = current[part]
        current[parts[-1]] = "FILE"
        
    with open(os.path.join(metadata_dir, "tree.json"), 'w') as f:
        json.dump(tree, f)

def update_summary_with_intelligence(repo_id: str, intel: dict):
    """
    Merge AI analysis results into existing summary.
    """
    metadata_dir = os.path.join(settings.DATA_DIR, repo_id)
    summary_path = os.path.join(metadata_dir, "summary.json")
    
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            summary = json.load(f)
            
        summary.update(intel)
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f)

def load_summary(repo_id: str):
    path = os.path.join(settings.DATA_DIR, repo_id, "summary.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {"file_count": 0, "language_counts": {}, "total_size_bytes": 0}

def load_tree(repo_id: str):
    path = os.path.join(settings.DATA_DIR, repo_id, "tree.json")
    if not os.path.exists(path):
        return []
        
    with open(path, 'r') as f:
        raw_tree = json.load(f)
        
    def transform(name, content, current_path=""):
        node_path = os.path.join(current_path, name) if current_path else name
        if content == "FILE":
            return {"name": name, "path": node_path, "type": "file"}
        
        children = []
        for key, val in content.items():
            children.append(transform(key, val, node_path))
        
        # Sort so directories come first, then files alphabetically
        children.sort(key=lambda x: (x["type"] != "directory", x["name"]))
        
        return {
            "name": name, 
            "path": node_path, 
            "type": "directory", 
            "children": children
        }

    # The top level is the dict keys
    final_tree = []
    for key, val in raw_tree.items():
        final_tree.append(transform(key, val))
        
    final_tree.sort(key=lambda x: (x["type"] != "directory", x["name"]))
    return final_tree
