import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../../services/apiService';

export interface Scan {
  id: string;
  name: string;
  description: string;
  dataSourceName: string;
  status: 'Running' | 'Completed' | 'Failed' | 'Cancelled' | 'Queued';
  scanRulesetName: string;
  createdAt: string;
  startTime?: string;
  endTime?: string;
  progress: number;
  totalAssets: number;
  processedAssets: number;
  errors: number;
  warnings: number;
}

export interface ScanTemplate {
  id: string;
  name: string;
  description: string;
  dataSourceType: string;
  scanRuleset: any;
  schedule?: {
    frequency: 'once' | 'daily' | 'weekly' | 'monthly';
    time: string;
    daysOfWeek?: number[];
  };
}

interface ScanningState {
  scans: Scan[];
  selectedScan: Scan | null;
  templates: ScanTemplate[];
  loading: boolean;
  error: string | null;
  scanLogs: Record<string, string[]>;
  realtimeUpdates: boolean;
  metrics: {
    totalScans: number;
    runningScans: number;
    completedScans: number;
    failedScans: number;
    avgScanTime: number;
  };
}

const initialState: ScanningState = {
  scans: [],
  selectedScan: null,
  templates: [],
  loading: false,
  error: null,
  scanLogs: {},
  realtimeUpdates: false,
  metrics: {
    totalScans: 0,
    runningScans: 0,
    completedScans: 0,
    failedScans: 0,
    avgScanTime: 0,
  },
};

// Async thunks
export const fetchScans = createAsyncThunk(
  'scanning/fetchScans',
  async () => {
    const response = await apiService.getScans();
    return response.data;
  }
);

export const fetchScanById = createAsyncThunk(
  'scanning/fetchScanById',
  async (scanId: string) => {
    const response = await apiService.getScan(scanId);
    return response.data;
  }
);

export const createScan = createAsyncThunk(
  'scanning/createScan',
  async (scanData: Partial<Scan>) => {
    const response = await apiService.createScan(scanData);
    return response.data;
  }
);

export const startScan = createAsyncThunk(
  'scanning/startScan',
  async (scanId: string) => {
    const response = await apiService.startScan(scanId);
    return response.data;
  }
);

export const stopScan = createAsyncThunk(
  'scanning/stopScan',
  async (scanId: string) => {
    const response = await apiService.stopScan(scanId);
    return response.data;
  }
);

export const fetchScanLogs = createAsyncThunk(
  'scanning/fetchScanLogs',
  async (scanId: string) => {
    const response = await apiService.getScanLogs(scanId);
    return { scanId, logs: response.data };
  }
);

export const fetchScanTemplates = createAsyncThunk(
  'scanning/fetchScanTemplates',
  async () => {
    const response = await apiService.getScanTemplates();
    return response.data;
  }
);

const scanningSlice = createSlice({
  name: 'scanning',
  initialState,
  reducers: {
    setSelectedScan: (state, action: PayloadAction<Scan | null>) => {
      state.selectedScan = action.payload;
    },
    updateScanProgress: (state, action: PayloadAction<{ scanId: string; progress: number; processedAssets: number }>) => {
      const scan = state.scans.find(s => s.id === action.payload.scanId);
      if (scan) {
        scan.progress = action.payload.progress;
        scan.processedAssets = action.payload.processedAssets;
      }
    },
    updateScanStatus: (state, action: PayloadAction<{ scanId: string; status: Scan['status'] }>) => {
      const scan = state.scans.find(s => s.id === action.payload.scanId);
      if (scan) {
        scan.status = action.payload.status;
        if (action.payload.status === 'Completed' || action.payload.status === 'Failed') {
          scan.endTime = new Date().toISOString();
        }
      }
    },
    setRealtimeUpdates: (state, action: PayloadAction<boolean>) => {
      state.realtimeUpdates = action.payload;
    },
    addScanLog: (state, action: PayloadAction<{ scanId: string; log: string }>) => {
      if (!state.scanLogs[action.payload.scanId]) {
        state.scanLogs[action.payload.scanId] = [];
      }
      state.scanLogs[action.payload.scanId].push(action.payload.log);
    },
    clearError: (state) => {
      state.error = null;
    },
    updateMetrics: (state, action: PayloadAction<Partial<ScanningState['metrics']>>) => {
      state.metrics = { ...state.metrics, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch scans
      .addCase(fetchScans.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchScans.fulfilled, (state, action) => {
        state.loading = false;
        state.scans = action.payload.scans || [];
        // Update metrics
        const scans = state.scans;
        state.metrics = {
          totalScans: scans.length,
          runningScans: scans.filter(s => s.status === 'Running').length,
          completedScans: scans.filter(s => s.status === 'Completed').length,
          failedScans: scans.filter(s => s.status === 'Failed').length,
          avgScanTime: action.payload.avgScanTime || 0,
        };
      })
      .addCase(fetchScans.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch scans';
      })
      // Fetch scan by ID
      .addCase(fetchScanById.fulfilled, (state, action) => {
        state.selectedScan = action.payload;
        const index = state.scans.findIndex(s => s.id === action.payload.id);
        if (index !== -1) {
          state.scans[index] = action.payload;
        }
      })
      // Create scan
      .addCase(createScan.fulfilled, (state, action) => {
        state.scans.unshift(action.payload);
        state.metrics.totalScans += 1;
      })
      // Start scan
      .addCase(startScan.fulfilled, (state, action) => {
        const index = state.scans.findIndex(s => s.id === action.payload.id);
        if (index !== -1) {
          state.scans[index] = action.payload;
        }
      })
      // Stop scan
      .addCase(stopScan.fulfilled, (state, action) => {
        const index = state.scans.findIndex(s => s.id === action.payload.id);
        if (index !== -1) {
          state.scans[index] = action.payload;
        }
      })
      // Fetch scan logs
      .addCase(fetchScanLogs.fulfilled, (state, action) => {
        state.scanLogs[action.payload.scanId] = action.payload.logs;
      })
      // Fetch scan templates
      .addCase(fetchScanTemplates.fulfilled, (state, action) => {
        state.templates = action.payload.templates || [];
      });
  },
});

export const {
  setSelectedScan,
  updateScanProgress,
  updateScanStatus,
  setRealtimeUpdates,
  addScanLog,
  clearError,
  updateMetrics,
} = scanningSlice.actions;

export default scanningSlice.reducer;
