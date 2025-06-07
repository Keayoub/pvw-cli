import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../../services/apiService';

export interface Entity {
  guid: string;
  typeName: string;
  displayText: string;
  status: string;
  createdBy: string;
  updatedBy: string;
  createTime: number;
  updateTime: number;
  attributes: Record<string, any>;
  classifications: any[];
  meanings: any[];
}

interface EntitiesState {
  entities: Entity[];
  selectedEntity: Entity | null;
  loading: boolean;
  error: string | null;
  searchResults: Entity[];
  searchLoading: boolean;
  filters: {
    typeName?: string;
    classification?: string;
    status?: string;
  };
  pagination: {
    page: number;
    pageSize: number;
    total: number;
  };
}

const initialState: EntitiesState = {
  entities: [],
  selectedEntity: null,
  loading: false,
  error: null,
  searchResults: [],
  searchLoading: false,
  filters: {},
  pagination: {
    page: 0,
    pageSize: 25,
    total: 0,
  },
};

// Async thunks
export const fetchEntities = createAsyncThunk(
  'entities/fetchEntities',
  async (params: { page?: number; pageSize?: number; filters?: any }) => {
    const response = await apiService.getEntities(params);
    return response.data;
  }
);

export const fetchEntityByGuid = createAsyncThunk(
  'entities/fetchEntityByGuid',
  async (guid: string) => {
    const response = await apiService.getEntity(guid);
    return response.data;
  }
);

export const searchEntities = createAsyncThunk(
  'entities/searchEntities',
  async (query: string) => {
    const response = await apiService.searchEntities(query);
    return response.data;
  }
);

export const createEntity = createAsyncThunk(
  'entities/createEntity',
  async (entityData: Partial<Entity>) => {
    const response = await apiService.createEntity(entityData);
    return response.data;
  }
);

export const updateEntity = createAsyncThunk(
  'entities/updateEntity',
  async ({ guid, data }: { guid: string; data: Partial<Entity> }) => {
    const response = await apiService.updateEntity(guid, data);
    return response.data;
  }
);

const entitiesSlice = createSlice({
  name: 'entities',
  initialState,
  reducers: {
    setSelectedEntity: (state, action: PayloadAction<Entity | null>) => {
      state.selectedEntity = action.payload;
    },
    setFilters: (state, action: PayloadAction<any>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setPagination: (state, action: PayloadAction<Partial<typeof initialState.pagination>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch entities
      .addCase(fetchEntities.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEntities.fulfilled, (state, action) => {
        state.loading = false;
        state.entities = action.payload.entities || [];
        state.pagination.total = action.payload.total || 0;
      })
      .addCase(fetchEntities.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch entities';
      })
      // Fetch entity by GUID
      .addCase(fetchEntityByGuid.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEntityByGuid.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedEntity = action.payload;
      })
      .addCase(fetchEntityByGuid.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch entity';
      })
      // Search entities
      .addCase(searchEntities.pending, (state) => {
        state.searchLoading = true;
      })
      .addCase(searchEntities.fulfilled, (state, action) => {
        state.searchLoading = false;
        state.searchResults = action.payload.entities || [];
      })
      .addCase(searchEntities.rejected, (state, action) => {
        state.searchLoading = false;
        state.error = action.error.message || 'Search failed';
      })
      // Create entity
      .addCase(createEntity.fulfilled, (state, action) => {
        state.entities.unshift(action.payload);
      })
      // Update entity
      .addCase(updateEntity.fulfilled, (state, action) => {
        const index = state.entities.findIndex(e => e.guid === action.payload.guid);
        if (index !== -1) {
          state.entities[index] = action.payload;
        }
        if (state.selectedEntity?.guid === action.payload.guid) {
          state.selectedEntity = action.payload;
        }
      });
  },
});

export const {
  setSelectedEntity,
  setFilters,
  clearFilters,
  setPagination,
  clearError,
} = entitiesSlice.actions;

export default entitiesSlice.reducer;
