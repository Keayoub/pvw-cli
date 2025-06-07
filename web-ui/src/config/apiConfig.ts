// API Configuration for Enhanced Purview CLI v2.0
// Centralized configuration for backend API endpoints and settings

export interface ApiConfig {
  baseUrl: string;
  wsUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  endpoints: {
    auth: {
      login: string;
      logout: string;
      refresh: string;
      profile: string;
    };
    entities: {
      base: string;
      search: string;
      bulk: string;
      relationships: string;
      lineage: string;
    };
    analytics: {
      dashboard: string;
      metrics: string;
      reports: string;
      trends: string;
    };
    scanning: {
      base: string;
      sources: string;
      results: string;
      schedule: string;
    };
    upload: {
      base: string;
      files: string;
      process: string;
      status: string;
    };
    governance: {
      policies: string;
      compliance: string;
      classifications: string;
      glossary: string;
    };
    system: {
      health: string;
      status: string;
      logs: string;
      config: string;
    };
  };
}

// Environment-based configuration
const getApiConfig = (): ApiConfig => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  const isProduction = process.env.NODE_ENV === 'production';
  
  // Default configuration
  const defaultConfig: ApiConfig = {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
    timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000'),
    retryAttempts: parseInt(process.env.REACT_APP_RETRY_ATTEMPTS || '3'),
    retryDelay: parseInt(process.env.REACT_APP_RETRY_DELAY || '1000'),
    endpoints: {
      auth: {
        login: '/api/v1/auth/login',
        logout: '/api/v1/auth/logout', 
        refresh: '/api/v1/auth/refresh',
        profile: '/api/v1/auth/profile'
      },
      entities: {
        base: '/api/v1/entities',
        search: '/api/v1/entities/search',
        bulk: '/api/v1/entities/bulk',
        relationships: '/api/v1/entities/relationships',
        lineage: '/api/v1/lineage'
      },
      analytics: {
        dashboard: '/api/v1/analytics/dashboard',
        metrics: '/api/v1/analytics/metrics',
        reports: '/api/v1/analytics/reports',
        trends: '/api/v1/analytics/trends'
      },
      scanning: {
        base: '/api/v1/scanning',
        sources: '/api/v1/scanning/sources',
        results: '/api/v1/scanning/results',
        schedule: '/api/v1/scanning/schedule'
      },
      upload: {
        base: '/api/v1/upload',
        files: '/api/v1/upload/files',
        process: '/api/v1/upload/process',
        status: '/api/v1/upload/status'
      },
      governance: {
        policies: '/api/v1/governance/policies',
        compliance: '/api/v1/governance/compliance',
        classifications: '/api/v1/governance/classifications',
        glossary: '/api/v1/governance/glossary'
      },
      system: {
        health: '/health',
        status: '/api/v1/system/status',
        logs: '/api/v1/system/logs',
        config: '/api/v1/system/config'
      }
    }
  };

  // Development overrides
  if (isDevelopment) {
    return {
      ...defaultConfig,
      timeout: 60000, // Longer timeout for development
      retryAttempts: 1 // Fewer retries for faster feedback
    };
  }

  // Production overrides
  if (isProduction) {
    return {
      ...defaultConfig,
      baseUrl: process.env.REACT_APP_API_URL || 'https://your-production-api.com',
      wsUrl: process.env.REACT_APP_WS_URL || 'wss://your-production-api.com',
      timeout: 15000, // Shorter timeout for production
      retryAttempts: 5 // More retries for reliability
    };
  }

  return defaultConfig;
};

// Export the configuration
export const apiConfig = getApiConfig();

// Helper functions for URL construction
export const buildApiUrl = (endpoint: string): string => {
  return `${apiConfig.baseUrl}${endpoint}`;
};

export const buildWsUrl = (endpoint: string): string => {
  return `${apiConfig.wsUrl}${endpoint}`;
};

// API response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
  timestamp: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
  id?: string;
}

// Default headers for API requests
export const getDefaultHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // Add authorization header if token exists
  const token = localStorage.getItem('access_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

// API endpoints validation
export const validateEndpoint = (endpoint: string): boolean => {
  return endpoint.startsWith('/') && endpoint.length > 1;
};

export default apiConfig;
