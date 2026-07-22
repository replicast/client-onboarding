import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    // Get token from session storage (MSAL stores it there)
    const accounts = JSON.parse(sessionStorage.getItem('msal.account.keys') || '[]');
    if (accounts.length > 0) {
      const accountKey = accounts[0];
      const accountData = sessionStorage.getItem(accountKey);
      if (accountData) {
        const account = JSON.parse(accountData);
        const tokenKey = `msal.${account.homeAccountId}`;
        const tokenData = sessionStorage.getItem(tokenKey);
        if (tokenData) {
          const tokens = JSON.parse(tokenData);
          const accessToken = tokens.accessToken;
          if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
          }
        }
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Upload a file with progress tracking
 * @param {string} url - The API endpoint URL
 * @param {FormData} formData - FormData containing the file
 * @param {function} onProgress - Callback for upload progress (0-100)
 * @returns {Promise} - Axios response
 */
export const uploadFile = async (url, formData, onProgress) => {
  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });
};

export default api;
