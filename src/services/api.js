import axios from 'axios';
import API_BASE_URL from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const apiService = {
  // Health check
  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get system status
  getStatus: async () => {
    const response = await api.get('/api/status');
    return response.data;
  },

  // Get all signals
  getSignals: async () => {
    const response = await api.get('/api/signals');
    return response.data;
  },

  // Get signal by ID
  getSignalById: async (id) => {
    const response = await api.get(`/api/signals/${id}`);
    return response.data;
  },

  // Generate new signals
  generateSignals: async () => {
    const response = await api.post('/api/signals/generate');
    return response.data;
  },

  // Get journal entries
  getJournalEntries: async () => {
    const response = await api.get('/api/journal');
    return response.data;
  },

  // Create journal entry
  createJournalEntry: async (entry) => {
    const response = await api.post('/api/journal', entry);
    return response.data;
  },

  // Update journal entry
  updateJournalEntry: async (id, entry) => {
    const response = await api.put(`/api/journal/${id}`, entry);
    return response.data;
  },

  // Delete journal entry
  deleteJournalEntry: async (id) => {
    const response = await api.delete(`/api/journal/${id}`);
    return response.data;
  },

  // Get statistics
  getStatistics: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  },
};

export default apiService;
