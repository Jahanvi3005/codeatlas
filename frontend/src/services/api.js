import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
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
