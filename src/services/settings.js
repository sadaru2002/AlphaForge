import apiService from './api';

const settingsService = {
  async getSettings() {
    try {
      const response = await apiService.get('/api/settings');
      return response.data;
    } catch (error) {
      console.error('Error fetching settings:', error);
      throw error;
    }
  },

  async updateSettings(settings) {
    try {
      const response = await apiService.put('/api/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  },

  async testApiConnection(credentials) {
    try {
      const response = await apiService.post('/api/test-connection', credentials);
      return response.data;
    } catch (error) {
      console.error('Error testing API connection:', error);
      throw error;
    }
  },

  async toggleBot(enabled) {
    try {
      const response = await apiService.post('/api/bot/toggle', { enabled });
      return response.data;
    } catch (error) {
      console.error('Error toggling bot:', error);
      throw error;
    }
  }
};

export default settingsService;