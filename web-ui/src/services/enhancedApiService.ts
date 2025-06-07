import axios, { AxiosInstance, AxiosResponse, AxiosProgressEvent } from 'axios';

// Type definitions for API responses
export interface EntityData {
  id: string;
  name: string;
  qualified_name: string;
  entity_type: string;
  description?: string;
  properties?: Record<string, any>;
  classifications?: string[];
  status: string;
  source_system?: string;
  created_at: string;
  updated_at: string;
}

export interface DataSourceData {
  id: string;
  name: string;
  source_type: string;
  connection_string: string;
  description?: string;
  config: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ScanData {
  id: string;
  name: string;
  data_source_id: string;
  scan_type: string;
  schedule?: string;
  config: Record<string, any>;
  status: string;
  last_run?: string;
  next_run?: string;
  created_at: string;
}

export interface LineageData {
  entities: EntityData[];
  relationships: Array<{
    from_entity: string;
    to_entity: string;
    relationship_type: string;
    attributes?: Record<string, any>;
  }>;
  metadata: {
    depth: number;
    direction: string;
    total_entities: number;
    total_relationships: number;
  };
}

export interface AnalyticsData {
  dashboard_metrics: Record<string, any>;
  scan_analytics: Record<string, any>;
  classification_analytics: Record<string, any>;
  data_quality_metrics: Record<string, any>;
  usage_analytics: Record<string, any>;
}

export interface GovernancePolicy {
  id: string;
  name: string;
  description: string;
  policy_type: string;
  rules: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Classification {
  id: string;
  name: string;
  display_name?: string;
  description?: string;
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UploadedFile {
  file_id: string;
  filename: string;
  original_filename: string;
  size: number;
  mime_type: string;
  upload_time: string;
  status: string;
  processing_jobs?: ProcessingJob[];
}

export interface ProcessingJob {
  job_id: string;
  file_id: string;
  operation_type: string;
  target_entity_type?: string;
  options: Record<string, any>;
  status: string;
  progress: number;
  result?: Record<string, any>;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface UserData {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  roles: string[];
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

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
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  async login(username: string, password: string): Promise<AxiosResponse<{ access_token: string; token_type: string; user: UserData }>> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }): Promise<AxiosResponse<UserData>> {
    return this.client.post('/auth/register', userData);
  }

  async refreshToken(): Promise<AxiosResponse<{ access_token: string; token_type: string }>> {
    return this.client.post('/auth/refresh');
  }

  async getCurrentUser(): Promise<AxiosResponse<UserData>> {
    return this.client.get('/auth/me');
  }

  async updatePassword(currentPassword: string, newPassword: string): Promise<AxiosResponse> {
    return this.client.put('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  // Entity endpoints
  async getEntities(params?: {
    page?: number;
    page_size?: number;
    entity_type?: string;
    search?: string;
  }): Promise<AxiosResponse<{ entities: EntityData[]; total_count: number; page: number; page_size: number }>> {
    return this.client.get('/entities', { params });
  }

  async getEntity(guid: string): Promise<AxiosResponse<EntityData>> {
    return this.client.get(`/entities/${guid}`);
  }

  async createEntity(entityData: Partial<EntityData>): Promise<AxiosResponse<EntityData>> {
    return this.client.post('/entities', entityData);
  }

  async updateEntity(guid: string, entityData: Partial<EntityData>): Promise<AxiosResponse<EntityData>> {
    return this.client.put(`/entities/${guid}`, entityData);
  }

  async deleteEntity(guid: string): Promise<AxiosResponse> {
    return this.client.delete(`/entities/${guid}`);
  }

  async searchEntities(query: string, filters?: Record<string, any>): Promise<AxiosResponse<{ entities: EntityData[]; total_count: number }>> {
    return this.client.post('/entities/search', { query, filters });
  }

  // Data source endpoints
  async getDataSources(params?: {
    page?: number;
    page_size?: number;
    source_type?: string;
  }): Promise<AxiosResponse<{ data_sources: DataSourceData[]; total_count: number }>> {
    return this.client.get('/data-sources', { params });
  }

  async getDataSource(id: string): Promise<AxiosResponse<DataSourceData>> {
    return this.client.get(`/data-sources/${id}`);
  }

  async createDataSource(dataSourceData: Partial<DataSourceData>): Promise<AxiosResponse<DataSourceData>> {
    return this.client.post('/data-sources', dataSourceData);
  }

  async updateDataSource(id: string, dataSourceData: Partial<DataSourceData>): Promise<AxiosResponse<DataSourceData>> {
    return this.client.put(`/data-sources/${id}`, dataSourceData);
  }

  async deleteDataSource(id: string): Promise<AxiosResponse> {
    return this.client.delete(`/data-sources/${id}`);
  }

  async testDataSourceConnection(id: string): Promise<AxiosResponse<{ success: boolean; message: string }>> {
    return this.client.post(`/data-sources/${id}/test-connection`);
  }

  // Scan endpoints
  async getScans(params?: {
    page?: number;
    page_size?: number;
    data_source_id?: string;
    status?: string;
  }): Promise<AxiosResponse<{ scans: ScanData[]; total_count: number }>> {
    return this.client.get('/scans', { params });
  }

  async getScan(id: string): Promise<AxiosResponse<ScanData>> {
    return this.client.get(`/scans/${id}`);
  }

  async createScan(scanData: Partial<ScanData>): Promise<AxiosResponse<ScanData>> {
    return this.client.post('/scans', scanData);
  }

  async updateScan(id: string, scanData: Partial<ScanData>): Promise<AxiosResponse<ScanData>> {
    return this.client.put(`/scans/${id}`, scanData);
  }

  async deleteScan(id: string): Promise<AxiosResponse> {
    return this.client.delete(`/scans/${id}`);
  }

  async runScan(id: string): Promise<AxiosResponse<{ message: string; scan_run_id: string }>> {
    return this.client.post(`/scans/${id}/run`);
  }

  async getScanResults(id: string): Promise<AxiosResponse<{ results: any[]; summary: Record<string, any> }>> {
    return this.client.get(`/scans/${id}/results`);
  }

  // Lineage endpoints
  async getEntityLineage(
    entityId: string,
    direction?: 'input' | 'output' | 'both',
    depth?: number
  ): Promise<AxiosResponse<LineageData>> {
    return this.client.get(`/lineage/entity/${entityId}`, {
      params: { direction, depth }
    });
  }

  async searchLineage(
    query: string,
    entityTypes?: string[]
  ): Promise<AxiosResponse<{ lineages: LineageData[]; total_count: number }>> {
    return this.client.post('/lineage/search', { query, entity_types: entityTypes });
  }

  async getLineageImpactAnalysis(
    entityId: string,
    changeType: string
  ): Promise<AxiosResponse<{ impacted_entities: EntityData[]; impact_score: number; recommendations: string[] }>> {
    return this.client.post(`/lineage/impact-analysis/${entityId}`, { change_type: changeType });
  }

  async createLineageRelationship(relationshipData: {
    from_entity: string;
    to_entity: string;
    relationship_type: string;
    attributes?: Record<string, any>;
  }): Promise<AxiosResponse> {
    return this.client.post('/lineage/relationships', relationshipData);
  }

  // Analytics endpoints
  async getDashboardMetrics(): Promise<AxiosResponse<AnalyticsData['dashboard_metrics']>> {
    return this.client.get('/analytics/dashboard');
  }

  async getScanAnalytics(timeRange?: string): Promise<AxiosResponse<AnalyticsData['scan_analytics']>> {
    return this.client.get('/analytics/scans', { params: { time_range: timeRange } });
  }

  async getClassificationAnalytics(): Promise<AxiosResponse<AnalyticsData['classification_analytics']>> {
    return this.client.get('/analytics/classifications');
  }

  async getDataQualityMetrics(entityId?: string): Promise<AxiosResponse<AnalyticsData['data_quality_metrics']>> {
    return this.client.get('/analytics/data-quality', { params: { entity_id: entityId } });
  }

  async getUsageAnalytics(timeRange?: string): Promise<AxiosResponse<AnalyticsData['usage_analytics']>> {
    return this.client.get('/analytics/usage', { params: { time_range: timeRange } });
  }

  async getAIRecommendations(context?: Record<string, any>): Promise<AxiosResponse<{ recommendations: any[] }>> {
    return this.client.post('/analytics/ai-recommendations', { context });
  }

  // Governance endpoints
  async getGovernancePolicies(params?: {
    page?: number;
    page_size?: number;
    policy_type?: string;
    status?: string;
  }): Promise<AxiosResponse<{ policies: GovernancePolicy[]; total_count: number }>> {
    return this.client.get('/governance/policies', { params });
  }

  async getGovernancePolicy(id: string): Promise<AxiosResponse<GovernancePolicy>> {
    return this.client.get(`/governance/policies/${id}`);
  }

  async createGovernancePolicy(policyData: Partial<GovernancePolicy>): Promise<AxiosResponse<GovernancePolicy>> {
    return this.client.post('/governance/policies', policyData);
  }

  async updateGovernancePolicy(id: string, policyData: Partial<GovernancePolicy>): Promise<AxiosResponse<GovernancePolicy>> {
    return this.client.put(`/governance/policies/${id}`, policyData);
  }

  async deleteGovernancePolicy(id: string): Promise<AxiosResponse> {
    return this.client.delete(`/governance/policies/${id}`);
  }

  async checkCompliance(entityId: string): Promise<AxiosResponse<{ compliant: boolean; violations: any[]; score: number }>> {
    return this.client.post(`/governance/compliance/check/${entityId}`);
  }

  async assignDataSteward(entityId: string, stewardId: string): Promise<AxiosResponse> {
    return this.client.post(`/governance/stewards/assign`, {
      entity_id: entityId,
      steward_id: stewardId
    });
  }

  // Classification endpoints
  async getClassifications(params?: {
    page?: number;
    page_size?: number;
  }): Promise<AxiosResponse<{ classifications: Classification[]; total_count: number }>> {
    return this.client.get('/classifications', { params });
  }

  async getClassification(id: string): Promise<AxiosResponse<Classification>> {
    return this.client.get(`/classifications/${id}`);
  }

  async createClassification(classificationData: Partial<Classification>): Promise<AxiosResponse<Classification>> {
    return this.client.post('/classifications', classificationData);
  }

  async updateClassification(id: string, classificationData: Partial<Classification>): Promise<AxiosResponse<Classification>> {
    return this.client.put(`/classifications/${id}`, classificationData);
  }

  async deleteClassification(id: string): Promise<AxiosResponse> {
    return this.client.delete(`/classifications/${id}`);
  }

  async applyClassification(entityId: string, classificationId: string, attributes?: Record<string, any>): Promise<AxiosResponse> {
    return this.client.post(`/classifications/apply`, {
      entity_id: entityId,
      classification_id: classificationId,
      attributes
    });
  }

  // File upload endpoints
  async uploadFile(
    file: File,
    onProgress?: (progressEvent: AxiosProgressEvent) => void
  ): Promise<AxiosResponse<UploadedFile>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    });
  }

  async getUploadedFiles(params?: {
    page?: number;
    page_size?: number;
    status_filter?: string;
  }): Promise<AxiosResponse<{ files: UploadedFile[]; total_count: number }>> {
    return this.client.get('/upload/files', { params });
  }

  async getFileInfo(fileId: string): Promise<AxiosResponse<UploadedFile>> {
    return this.client.get(`/upload/files/${fileId}`);
  }

  async previewFile(fileId: string, rows?: number): Promise<AxiosResponse<{
    columns?: string[];
    data?: any[];
    type?: string;
    lines?: string[];
    preview_rows?: number;
    total_rows?: number;
  }>> {
    return this.client.get(`/upload/files/${fileId}/preview`, { params: { rows } });
  }

  async processFile(
    fileId: string,
    operationType: string,
    targetEntityType?: string,
    options?: Record<string, any>
  ): Promise<AxiosResponse<{ job_id: string; message: string }>> {
    return this.client.post(`/upload/files/${fileId}/process`, {
      operation_type: operationType,
      target_entity_type: targetEntityType,
      options
    });
  }

  async getProcessingStatus(fileId: string): Promise<AxiosResponse<ProcessingJob>> {
    return this.client.get(`/upload/files/${fileId}/status`);
  }

  async downloadFile(fileId: string): Promise<AxiosResponse<Blob>> {
    return this.client.get(`/upload/files/${fileId}/download`, {
      responseType: 'blob'
    });
  }

  async deleteFile(fileId: string): Promise<AxiosResponse> {
    return this.client.delete(`/upload/files/${fileId}`);
  }

  // Health check endpoints
  async getHealthStatus(): Promise<AxiosResponse<{ status: string; details: Record<string, any> }>> {
    return this.client.get('/health');
  }

  async getDatabaseHealth(): Promise<AxiosResponse<{ status: string; connection_pool: Record<string, any> }>> {
    return this.client.get('/health/database');
  }

  async getCacheHealth(): Promise<AxiosResponse<{ status: string; redis_info: Record<string, any> }>> {
    return this.client.get('/health/cache');
  }

  // Utility methods
  setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  removeAuthToken(): void {
    localStorage.removeItem('auth_token');
  }

  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // Error handling helper
  handleApiError(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  }
}

export default new ApiService();
