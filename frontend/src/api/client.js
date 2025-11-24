import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

export const getStats = () => api.get('/stats');

export const getCreditor = (name) => api.get(`/creditor/${encodeURIComponent(name)}`);

export const calculateGPR = (data) => api.post('/gpr/calculate', data);

export const verifyGPR = (data) => api.post('/gpr/verify', data);

export const analyzeContract = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/contract/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export default api;
