// API Configuration
// For production: Set VITE_API_URL in Vercel environment variables
// For local dev: Falls back to localhost:8080
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export default API_BASE_URL;
