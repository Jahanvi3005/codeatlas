from ..core.config import settings

def chunk_text(text: str) -> list[str]:
    """
    Implements a simple sliding window semantic chunking.
    We split by newlines, then group into chunks of rough character sizes.
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        if current_length + len(line) > settings.CHUNK_SIZE and current_chunk:
            chunks.append("\n".join(current_chunk))
            # overlap logic
            overlap_length = 0
            overlap_chunk = []
            for prev_line in reversed(current_chunk):
                if overlap_length + len(prev_line) > settings.CHUNK_OVERLAP:
                    break
                overlap_chunk.insert(0, prev_line)
                overlap_length += len(prev_line)
                
            current_chunk = overlap_chunk
            current_length = overlap_length
        
        current_chunk.append(line)
        current_length += len(line) + 1 # +1 for newline
        
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks
