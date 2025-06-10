import axios, { AxiosInstance, AxiosResponse } from 'axios';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Entity operations
  async getEntities(params?: any): Promise<AxiosResponse> {
    return this.client.get('/entities', { params });
  }

  async getEntity(guid: string): Promise<AxiosResponse> {
    return this.client.get(`/entities/${guid}`);
  }

  async createEntity(entityData: any): Promise<AxiosResponse> {
    return this.client.post('/entities', entityData);
  }

  async updateEntity(guid: string, entityData: any): Promise<AxiosResponse> {
    return this.client.put(`/entities/${guid}`, entityData);
  }

  async deleteEntity(guid: string): Promise<AxiosResponse> {
    return this.client.delete(`/entities/${guid}`);
  }

  async searchEntities(query: string): Promise<AxiosResponse> {
    return this.client.get('/search', { params: { query } });
  }

  // Scanning operations
  async getScans(): Promise<AxiosResponse> {
    return this.client.get('/scans');
  }

  async getScan(scanId: string): Promise<AxiosResponse> {
    return this.client.get(`/scans/${scanId}`);
  }

  async createScan(scanData: any): Promise<AxiosResponse> {
    return this.client.post('/scans', scanData);
  }

  async updateScan(scanId: string, scanData: any): Promise<AxiosResponse> {
    return this.client.put(`/scans/${scanId}`, scanData);
  }

  async deleteScan(scanId: string): Promise<AxiosResponse> {
    return this.client.delete(`/scans/${scanId}`);
  }

  async startScan(scanId: string): Promise<AxiosResponse> {
    return this.client.post(`/scans/${scanId}/start`);
  }

  async stopScan(scanId: string): Promise<AxiosResponse> {
    return this.client.post(`/scans/${scanId}/stop`);
  }

  async getScanLogs(scanId: string): Promise<AxiosResponse> {
    return this.client.get(`/scans/${scanId}/logs`);
  }

  async getScanTemplates(): Promise<AxiosResponse> {
    return this.client.get('/scan-templates');
  }

  // Lineage operations
  async getLineage(params: { entityGuid: string; direction: string; depth: number }): Promise<AxiosResponse> {
    return this.client.get(`/lineage/${params.entityGuid}`, {
      params: { direction: params.direction, depth: params.depth }
    });
  }

  async getImpactAnalysis(entityGuid: string): Promise<AxiosResponse> {
    return this.client.get(`/lineage/${entityGuid}/impact`);
  }

  async getEntityRelationships(entityGuid: string): Promise<AxiosResponse> {
    return this.client.get(`/entities/${entityGuid}/relationships`);
  }

  // Analytics operations
  async getAnalyticsMetrics(timeRange: string): Promise<AxiosResponse> {
    return this.client.get('/analytics/metrics', { params: { timeRange } });
  }

  async getChartData(chartType: string, timeRange: string): Promise<AxiosResponse> {
    return this.client.get(`/analytics/charts/${chartType}`, { params: { timeRange } });
  }

  async generateReport(reportConfig: any): Promise<AxiosResponse> {
    return this.client.post('/reports/generate', reportConfig);
  }

  async getReports(): Promise<AxiosResponse> {
    return this.client.get('/reports');
  }

  async downloadReport(reportId: string): Promise<AxiosResponse> {
    return this.client.get(`/reports/${reportId}/download`, { responseType: 'blob' });
  }

  // Governance operations
  async getGovernanceRules(): Promise<AxiosResponse> {
    return this.client.get('/governance/rules');
  }

  async createGovernanceRule(ruleData: any): Promise<AxiosResponse> {
    return this.client.post('/governance/rules', ruleData);
  }

  async updateGovernanceRule(ruleId: string, ruleData: any): Promise<AxiosResponse> {
    return this.client.put(`/governance/rules/${ruleId}`, ruleData);
  }

  async deleteGovernanceRule(ruleId: string): Promise<AxiosResponse> {
    return this.client.delete(`/governance/rules/${ruleId}`);
  }

  async getComplianceReport(): Promise<AxiosResponse> {
    return this.client.get('/governance/compliance');
  }

  // Classification operations
  async getClassifications(): Promise<AxiosResponse> {
    return this.client.get('/classifications');
  }

  async createClassification(classificationData: any): Promise<AxiosResponse> {
    return this.client.post('/classifications', classificationData);
  }

  async updateClassification(classificationId: string, classificationData: any): Promise<AxiosResponse> {
    return this.client.put(`/classifications/${classificationId}`, classificationData);
  }

  async deleteClassification(classificationId: string): Promise<AxiosResponse> {
    return this.client.delete(`/classifications/${classificationId}`);
  }

  // Glossary operations
  async getGlossaryTerms(): Promise<AxiosResponse> {
    return this.client.get('/glossary/terms');
  }

  async createGlossaryTerm(termData: any): Promise<AxiosResponse> {
    return this.client.post('/glossary/terms', termData);
  }

  async updateGlossaryTerm(termId: string, termData: any): Promise<AxiosResponse> {
    return this.client.put(`/glossary/terms/${termId}`, termData);
  }

  async deleteGlossaryTerm(termId: string): Promise<AxiosResponse> {
    return this.client.delete(`/glossary/terms/${termId}`);  }

  // System operations
  async getSystemHealth(): Promise<AxiosResponse> {
    return this.client.get('/system/health');
  }

  async getSystemMetrics(): Promise<AxiosResponse> {
    return this.client.get('/system/metrics');
  }

  async getAuditLogs(params?: any): Promise<AxiosResponse> {
    return this.client.get('/system/audit-logs', { params });
  }

  // User management
  async getUsers(): Promise<AxiosResponse> {
    return this.client.get('/users');
  }

  async createUser(userData: any): Promise<AxiosResponse> {
    return this.client.post('/users', userData);
  }

  async updateUser(userId: string, userData: any): Promise<AxiosResponse> {
    return this.client.put(`/users/${userId}`, userData);
  }

  async deleteUser(userId: string): Promise<AxiosResponse> {
    return this.client.delete(`/users/${userId}`);
  }

  async getCurrentUser(): Promise<AxiosResponse> {
    return this.client.get('/users/me');
  }

  // Authentication
  async login(credentials: { username: string; password: string }): Promise<AxiosResponse> {
    return this.client.post('/auth/login', credentials);
  }

  async logout(): Promise<AxiosResponse> {
    return this.client.post('/auth/logout');
  }

  async refreshToken(): Promise<AxiosResponse> {
    return this.client.post('/auth/refresh');
  }
}

export const apiService = new ApiService();
