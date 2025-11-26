import axios from 'axios';

// API base URL - all endpoints use /api prefix for consistency
const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// Root stats (no /api prefix - separate endpoint)
export const getRootStats = async () => {
  const res = await fetch('/stats');
  if (!res.ok) throw new Error('Failed to load root stats');
  return res.json();
};

// Legal database stats
export const getLegalStats = () => api.get('/legal/stats');

// Creditor endpoints
export const getCreditor = (name) => api.get(`/creditor/${encodeURIComponent(name)}`);
export const getCreditors = () => api.get('/creditors');

// GPR calculation endpoints
export const calculateGPR = (data) => api.post('/gpr/calculate', data);
export const verifyGPR = (data) => api.post('/gpr/verify', data);

// Legacy simple analysis endpoint (no user metadata persistence)
export const analyzeContractSimple = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/contract/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Full workflow analysis with user fields
export const analyzeContractFull = (file, fields) => {
  const formData = new FormData();
  formData.append('file', file);
  Object.entries(fields).forEach(([k, v]) => formData.append(k, v || ''));
  return api.post('/analyze-contract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Complaint export
export const exportComplaintPdf = async (complaintId) => {
  const res = await fetch(`${API_BASE}/complaints/${complaintId}/export`);
  if (!res.ok) throw new Error('Failed to export complaint');
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `complaint_${complaintId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export default api;
