// API Configuration
const API_CONFIG = {
  // Local development
  development: {
    baseURL: 'http://localhost:8000',
  },
  // Production deployment
  production: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-app-name.onrender.com',
  }
};

// Get current environment
const isDevelopment = process.env.NODE_ENV === 'development';
const config = isDevelopment ? API_CONFIG.development : API_CONFIG.production;

export const API_BASE_URL = config.baseURL;
export const API_ENDPOINTS = {
  markets: `${config.baseURL}/api/markets`,
  signals: `${config.baseURL}/api/signals`,
  analysis: `${config.baseURL}/api/analysis`,
  sentiment: `${config.baseURL}/api/sentiment`,
  portfolio: `${config.baseURL}/api/portfolio`,
};

