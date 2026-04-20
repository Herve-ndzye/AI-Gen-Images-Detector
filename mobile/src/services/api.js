import axios from 'axios';

// Replace with your local machine IP so your phone can reach the backend
// Example: 'http://192.168.1.5:8000'
const BASE_URL = 'http://127.0.0.1:8000'; 

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
});

export const analyzeImage = async (uri) => {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: 'upload.jpg',
    type: 'image/jpeg',
  });

  try {
    const response = await api.post('/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};

export const chatWithAI = async (message, analysis_results) => {
  try {
    const response = await api.post('/chat', {
      message,
      analysis_results,
    });
    return response.data;
  } catch (error) {
    console.error('Chat failed:', error);
    throw error;
  }
};

export const getHistory = async () => {
  try {
    const response = await api.get('/history');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch history:', error);
    throw error;
  }
};

export default api;
