import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sources
export const getSources = () => api.get('/api/sources');
export const syncSources = () => api.post('/api/sources/sync');

// Feedback
export const getFeedback = (params = {}) => api.get('/api/feedback', { params });

// Clustering
export const runClustering = (params = {}) => api.post('/api/clustering/run', null, { params });
export const getClusters = () => api.get('/api/clusters');
export const getClusterDetail = (id) => api.get(`/api/clusters/${id}`);

// Roadmap
export const generateRoadmap = () => api.post('/api/roadmap/generate');
export const getRoadmap = () => api.get('/api/roadmap');

// Stats
export const getStats = () => api.get('/api/stats');

export default api;
