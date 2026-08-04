import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add request interceptor for error handling
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('API Request Timeout');
    } else if (error.response) {
      // Server responded with error status
      console.error('API Response Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('API Network Error: No response received');
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Sources
export const getSources = () => api.get('/api/sources');
export const syncSources = () => api.post('/api/sources/sync');

// Feedback
export const getFeedback = (params = {}) => api.get('/api/feedback', { params });

// Clustering
export const runClustering = (params = {}) => api.post('/api/clustering/run', null, { params });
export const runBERTopicClustering = (params = {}) => api.post('/api/clustering/bertopic', null, { params });
export const getClusteringQuality = () => api.get('/api/clustering/quality');
export const getClusters = () => api.get('/api/clusters');
export const getClusterDetail = (id) => api.get(`/api/clusters/${id}`);

// Roadmap
export const generateRoadmap = () => api.post('/api/roadmap/generate');
export const getRoadmap = () => api.get('/api/roadmap');

// Stats
export const getStats = () => api.get('/api/stats');

// Priority Analysis
export const predictImpact = (data) => api.post('/api/roadmap/predict-impact', data);
export const calculateCustomScore = (data) => api.post('/api/priority/custom-score', data);
export const getAtRiskCustomers = () => api.get('/api/priority/at-risk-customers');
export const getRoadmapExplanation = (id) => api.get(`/api/roadmap/${id}/explanation`);
export const getFormulaPresets = () => api.get('/api/priority/formulas/presets');
export const compareFormulas = (data) => api.post('/api/priority/formulas/compare', data);

// Imports
export const importZendesk = (data) => api.post('/api/import/zendesk', data);
export const importIntercom = (data) => api.post('/api/import/intercom', data);
export const importCSV = (formData) => api.post('/api/import/csv', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const getImportJob = (jobId) => api.get(`/api/import/job/${jobId}`);

// Jira Integration
export const createJiraIssue = (data) => api.post('/api/jira/create', data);
export const syncJiraIssue = (issueKey) => api.post(`/api/jira/sync/${issueKey}`);
export const getJiraIssues = (params) => api.get('/api/jira/issues', { params });

// Linear Integration
export const createLinearIssue = (data) => api.post('/api/linear/create', data);
export const syncLinearIssue = (issueId) => api.post(`/api/linear/sync/${issueId}`);
export const getLinearIssues = (params) => api.get('/api/linear/issues', { params });

export default api;
