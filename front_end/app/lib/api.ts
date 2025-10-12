// API Configuration for Freshtify Frontend
const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://your-production-api.com"
    : "http://localhost:8000";

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/v1/health`,
  MODELS: `${API_BASE_URL}/api/v1/models`,
  PRODUCTS: `${API_BASE_URL}/api/v1/products`,
  ESTIMATE_STOCK: `${API_BASE_URL}/api/v1/estimate-stock`,
  ESTIMATE_STOCK_BATCH: `${API_BASE_URL}/api/v1/estimate-stock-batch`,
  ESTIMATE_STOCK_INTEGRATED: `${API_BASE_URL}/api/v1/estimate-stock-integrated`,
} as const;

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 300000, // 5 minutes for AI processing
  HEADERS: {
    "Content-Type": "multipart/form-data",
  },
} as const;
