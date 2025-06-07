import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  autoHide?: boolean;
  duration?: number;
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface UIState {
  // Navigation and layout
  sidebarOpen: boolean;
  currentPage: string;
  breadcrumbs: BreadcrumbItem[];
  
  // Notifications
  notifications: Notification[];
  
  // Modals and dialogs
  dialogs: {
    entityDetails: { open: boolean; entityGuid?: string };
    scanConfig: { open: boolean; scanId?: string };
    lineageSettings: { open: boolean };
    reportGenerator: { open: boolean };
  };
  
  // Loading states
  globalLoading: boolean;
  loadingMessage?: string;
  
  // Theme and preferences
  theme: 'light' | 'dark';
  density: 'comfortable' | 'compact';
  
  // Search
  globalSearch: {
    query: string;
    isOpen: boolean;
    results: any[];
    loading: boolean;
  };
  
  // Dashboard customization
  dashboardConfig: {
    widgets: string[];
    layout: any;
  };
  
  // Table preferences
  tablePreferences: Record<string, {
    pageSize: number;
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
    visibleColumns: string[];
  }>;
}

const initialState: UIState = {
  sidebarOpen: true,
  currentPage: 'dashboard',
  breadcrumbs: [{ label: 'Dashboard', path: '/dashboard' }],
  notifications: [],
  dialogs: {
    entityDetails: { open: false },
    scanConfig: { open: false },
    lineageSettings: { open: false },
    reportGenerator: { open: false },
  },
  globalLoading: false,
  theme: 'light',
  density: 'comfortable',
  globalSearch: {
    query: '',
    isOpen: false,
    results: [],
    loading: false,
  },
  dashboardConfig: {
    widgets: ['overview', 'scans', 'quality', 'lineage'],
    layout: {},
  },
  tablePreferences: {},
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Sidebar and navigation
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setCurrentPage: (state, action: PayloadAction<string>) => {
      state.currentPage = action.payload;
    },
    setBreadcrumbs: (state, action: PayloadAction<BreadcrumbItem[]>) => {
      state.breadcrumbs = action.payload;
    },
    
    // Notifications
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    // Dialogs
    openDialog: (state, action: PayloadAction<{ dialog: keyof UIState['dialogs']; data?: any }>) => {
      const { dialog, data } = action.payload;
      state.dialogs[dialog] = { open: true, ...data };
    },
    closeDialog: (state, action: PayloadAction<keyof UIState['dialogs']>) => {
      state.dialogs[action.payload] = { open: false };
    },
    
    // Loading states
    setGlobalLoading: (state, action: PayloadAction<{ loading: boolean; message?: string }>) => {
      state.globalLoading = action.payload.loading;
      state.loadingMessage = action.payload.message;
    },
    
    // Theme and preferences
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    setDensity: (state, action: PayloadAction<'comfortable' | 'compact'>) => {
      state.density = action.payload;
    },
    
    // Search
    setGlobalSearchQuery: (state, action: PayloadAction<string>) => {
      state.globalSearch.query = action.payload;
    },
    setGlobalSearchOpen: (state, action: PayloadAction<boolean>) => {
      state.globalSearch.isOpen = action.payload;
    },
    setGlobalSearchResults: (state, action: PayloadAction<any[]>) => {
      state.globalSearch.results = action.payload;
    },
    setGlobalSearchLoading: (state, action: PayloadAction<boolean>) => {
      state.globalSearch.loading = action.payload;
    },
    
    // Dashboard
    setDashboardConfig: (state, action: PayloadAction<Partial<UIState['dashboardConfig']>>) => {
      state.dashboardConfig = { ...state.dashboardConfig, ...action.payload };
    },
    
    // Table preferences
    setTablePreference: (state, action: PayloadAction<{ tableId: string; preferences: Partial<UIState['tablePreferences'][string]> }>) => {
      const { tableId, preferences } = action.payload;
      if (!state.tablePreferences[tableId]) {
        state.tablePreferences[tableId] = {
          pageSize: 25,
          visibleColumns: [],
        };
      }
      state.tablePreferences[tableId] = {
        ...state.tablePreferences[tableId],
        ...preferences,
      };
    },
  },
});

export const {
  toggleSidebar,
  setSidebarOpen,
  setCurrentPage,
  setBreadcrumbs,
  addNotification,
  removeNotification,
  clearNotifications,
  openDialog,
  closeDialog,
  setGlobalLoading,
  setTheme,
  setDensity,
  setGlobalSearchQuery,
  setGlobalSearchOpen,
  setGlobalSearchResults,
  setGlobalSearchLoading,
  setDashboardConfig,
  setTablePreference,
} = uiSlice.actions;

export default uiSlice.reducer;
