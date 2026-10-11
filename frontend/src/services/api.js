import axios from 'axios';

export const API_BASE_URL = (() => {
  let url = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://nexadocs.onrender.com/api/v1' : 'http://localhost:8000/api/v1');
  if (url && url.includes('-backend.')) {
    url = url.replace('-backend.', '.');
  }
  return url;
})();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

// Interceptor for attaching JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nexadocs_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on unauthorized
      localStorage.removeItem('nexadocs_token');
    }
    return Promise.reject(error);
  }
);

/**
 * Distinguishes timeout/cold starts, CORS/network failures, HTTP 4xx, and HTTP 5xx responses.
 */
export function formatApiError(err, defaultAction = 'Authentication failed') {
  // 1. Client offline
  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    return {
      type: 'OFFLINE',
      message: 'You appear to be offline. Please check your internet connection.',
      status: null,
    };
  }

  // 2. Timeout / Cold start on Render free tier
  if (err.code === 'ECONNABORTED' || err.message?.toLowerCase().includes('timeout')) {
    return {
      type: 'TIMEOUT',
      message: 'Connection timed out. The Render backend may be waking up from idle (cold start). Please retry in a few seconds.',
      status: 408,
    };
  }

  // 3. Server HTTP response received
  if (err.response) {
    const status = err.response.status;
    let detail = err.response.data?.detail;

    if (Array.isArray(detail)) {
      detail = detail.map((d) => d.msg || (typeof d === 'string' ? d : JSON.stringify(d))).join('; ');
    } else if (typeof detail === 'object' && detail !== null) {
      detail = detail.message || JSON.stringify(detail);
    }

    if (status === 401) {
      return {
        type: 'UNAUTHORIZED',
        message: detail || 'Incorrect email or password. Please try again.',
        status,
      };
    }
    if (status === 400) {
      return {
        type: 'BAD_REQUEST',
        message: detail || 'Invalid request. Please check the entered information.',
        status,
      };
    }
    if (status === 403) {
      return {
        type: 'FORBIDDEN',
        message: detail || 'Access denied. You do not have permission.',
        status,
      };
    }
    if (status === 404) {
      return {
        type: 'NOT_FOUND',
        message: detail || 'Requested resource was not found on the server.',
        status,
      };
    }
    if (status === 422) {
      return {
        type: 'VALIDATION_ERROR',
        message: detail || 'Validation error: please check required fields.',
        status,
      };
    }
    if (status >= 500) {
      return {
        type: 'SERVER_ERROR',
        message: detail || `Server error (${status}): The NexaDocs API encountered an internal issue. Please retry shortly.`,
        status,
      };
    }

    return {
      type: 'HTTP_ERROR',
      message: detail || `Request failed with status code ${status}.`,
      status,
    };
  }

  // 4. Network Error (CORS blockage, DNS resolution failure, server unreachable)
  if (err.message === 'Network Error' || !err.response) {
    return {
      type: 'NETWORK_OR_CORS',
      message: 'Unable to reach NexaDocs API server. The Render backend may be spinning up from idle, or CORS/network blocked the request.',
      status: null,
    };
  }

  return {
    type: 'UNKNOWN',
    message: err.message || defaultAction,
    status: null,
  };
}

export default api;
