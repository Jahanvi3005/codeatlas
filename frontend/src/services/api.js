import axios from 'axios';

// VITE_API_URL from Render is just the hostname (e.g. codeatlas-backend.onrender.com)
// In local dev it can be the full URL with /api already appended.
function buildBaseURL() {
  const raw = import.meta.env.VITE_API_URL;
  if (!raw) return 'http://localhost:8000/api';
  if (raw.startsWith('http')) return raw.replace(/\/$/, '') + '/api';
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
};

export default api;
