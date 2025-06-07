import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../../services/apiService';

export interface AnalyticsMetric {
  name: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  unit?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

interface AnalyticsState {
  metrics: {
    overview: AnalyticsMetric[];
    dataQuality: AnalyticsMetric[];
    governance: AnalyticsMetric[];
    usage: AnalyticsMetric[];
  };
  charts: {
    entityTypes: ChartData | null;
    classifications: ChartData | null;
    scanTrends: ChartData | null;
    qualityTrends: ChartData | null;
    lineageComplexity: ChartData | null;
  };
  timeRange: '7d' | '30d' | '90d' | '1y';
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  autoRefresh: boolean;
  refreshInterval: number; // in seconds
}

const initialState: AnalyticsState = {
  metrics: {
    overview: [],
    dataQuality: [],
    governance: [],
    usage: [],
  },
  charts: {
    entityTypes: null,
    classifications: null,
    scanTrends: null,
    qualityTrends: null,
    lineageComplexity: null,
  },
  timeRange: '30d',
  loading: false,
  error: null,
  lastUpdated: null,
  autoRefresh: false,
  refreshInterval: 300, // 5 minutes
};

// Async thunks
export const fetchAnalyticsMetrics = createAsyncThunk(
  'analytics/fetchMetrics',
  async (timeRange: string) => {
    const response = await apiService.getAnalyticsMetrics(timeRange);
    return response.data;
  }
);

export const fetchChartData = createAsyncThunk(
  'analytics/fetchChartData',
  async (params: { chartType: string; timeRange: string }) => {
    const response = await apiService.getChartData(params.chartType, params.timeRange);
    return { chartType: params.chartType, data: response.data };
  }
);

export const generateReport = createAsyncThunk(
  'analytics/generateReport',
  async (reportConfig: { type: string; timeRange: string; filters?: any }) => {
    const response = await apiService.generateReport(reportConfig);
    return response.data;
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setTimeRange: (state, action: PayloadAction<AnalyticsState['timeRange']>) => {
      state.timeRange = action.payload;
    },
    setAutoRefresh: (state, action: PayloadAction<boolean>) => {
      state.autoRefresh = action.payload;
    },
    setRefreshInterval: (state, action: PayloadAction<number>) => {
      state.refreshInterval = action.payload;
    },
    updateMetric: (state, action: PayloadAction<{ category: keyof AnalyticsState['metrics']; metric: AnalyticsMetric }>) => {
      const { category, metric } = action.payload;
      const existingIndex = state.metrics[category].findIndex(m => m.name === metric.name);
      if (existingIndex !== -1) {
        state.metrics[category][existingIndex] = metric;
      } else {
        state.metrics[category].push(metric);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    setLastUpdated: (state) => {
      state.lastUpdated = new Date().toISOString();
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch analytics metrics
      .addCase(fetchAnalyticsMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalyticsMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.metrics = action.payload.metrics || state.metrics;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchAnalyticsMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch analytics metrics';
      })
      // Fetch chart data
      .addCase(fetchChartData.fulfilled, (state, action) => {
        const { chartType, data } = action.payload;
        if (chartType in state.charts) {
          (state.charts as any)[chartType] = data;
        }
      })
      .addCase(fetchChartData.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch chart data';
      })
      // Generate report
      .addCase(generateReport.fulfilled, (state, action) => {
        // Report generation successful - could trigger download or show success message
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to generate report';
      });
  },
});

export const {
  setTimeRange,
  setAutoRefresh,
  setRefreshInterval,
  updateMetric,
  clearError,
  setLastUpdated,
} = analyticsSlice.actions;

export default analyticsSlice.reducer;
