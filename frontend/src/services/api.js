import axios from 'axios';

// Build the API base URL from the environment variable
function buildBaseURL() {
  const raw = import.meta.env.VITE_API_URL;
  if (!raw) {
    // In production single-container (HF Spaces), use relative path
    if (import.meta.env.PROD) return '/api';
    return 'http://localhost:8000/api';
  }
  // Relative path (e.g. /api) — use as-is
  if (raw.startsWith('/')) return raw;
  // Full URL with protocol
  if (raw.startsWith('http')) return raw.replace(/\/$/, '');
  // Just a hostname (e.g. from Render)
  return `https://${raw}/api`;
}

const api = axios.create({
  baseURL: buildBaseURL(),
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': '69420',
    'cf-no-browser-verify': 'true'
  }
});

export const repoApi = {
  ingest: (url) => api.post('/repositories/ingest', { url }),
  getStatus: (id) => api.get(`/repositories/${id}/status`),
  getSummary: (id) => api.get(`/repositories/${id}/summary`),
  getTree: (id) => api.get(`/repositories/${id}/tree`),
};

export const chatApi = {
  query: (repository_id, query) => api.post('/chat/query', { repository_id, query }),
};

export const scrapeApi = {
  scrapeDocs: (repository_id, url) => api.post('/scrape/docs', { repository_id, url }),
  getSources: (repository_id) => api.get(`/scrape/docs/${repository_id}`),
};

export default api;
