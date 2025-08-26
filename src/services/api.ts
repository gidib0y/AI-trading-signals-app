import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

// Create axios instance with base configuration
const api = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Markets
  getMarkets: () => api.get(API_ENDPOINTS.markets),
  scanMarkets: () => api.post(`${API_ENDPOINTS.markets}/scan`),
  getMarketData: (symbol: string) => api.get(`${API_ENDPOINTS.markets}/${symbol}`),
  getPriceHistory: (symbol: string, period: string = '1mo') => 
    api.get(`${API_ENDPOINTS.markets}/${symbol}/history?period=${period}`),

  // Signals
  getSignals: (params?: any) => api.get(API_ENDPOINTS.signals, { params }),
  generateSignal: (symbol: string) => api.post(`${API_ENDPOINTS.signals}/generate`, { symbol }),
  getSignal: (id: string) => api.get(`${API_ENDPOINTS.signals}/${id}`),
  getLatestSignal: (symbol: string) => api.get(`${API_ENDPOINTS.signals}/latest/${symbol}`),
  getSignalHistory: (symbol: string) => api.get(`${API_ENDPOINTS.signals}/history/${symbol}`),
  getDashboardSummary: () => api.get(`${API_ENDPOINTS.signals}/dashboard`),

  // Analysis
  getTechnicalAnalysis: (symbol: string) => api.get(`${API_ENDPOINTS.analysis}/${symbol}`),
  getIndicator: (symbol: string, indicator: string) => 
    api.get(`${API_ENDPOINTS.analysis}/${symbol}/indicator/${indicator}`),

  // Sentiment
  getSentiment: (symbol: string) => api.get(`${API_ENDPOINTS.sentiment}/${symbol}`),
  getNewsSentiment: (symbol: string) => api.get(`${API_ENDPOINTS.sentiment}/${symbol}/news`),
  getSocialSentiment: (symbol: string) => api.get(`${API_ENDPOINTS.sentiment}/${symbol}/social`),
  getFearGreedIndex: () => api.get(`${API_ENDPOINTS.sentiment}/fear-greed`),

  // Portfolio
  getPortfolio: () => api.get(API_ENDPOINTS.portfolio),
  addPosition: (data: any) => api.post(API_ENDPOINTS.portfolio, data),
  closePosition: (id: string) => api.put(`${API_ENDPOINTS.portfolio}/${id}/close`),
  getPosition: (id: string) => api.get(`${API_ENDPOINTS.portfolio}/${id}`),
  getPerformance: (period: string = '1y') => 
    api.get(`${API_ENDPOINTS.portfolio}/performance?period=${period}`),
  getWatchlist: () => api.get(`${API_ENDPOINTS.portfolio}/watchlist`),
};

export default api;

