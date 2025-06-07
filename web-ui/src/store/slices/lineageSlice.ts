import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../../services/apiService';

export interface LineageNode {
  guid: string;
  typeName: string;
  displayText: string;
  attributes: Record<string, any>;
  isSource: boolean;
  isTarget: boolean;
  depth: number;
}

export interface LineageEdge {
  fromEntityId: string;
  toEntityId: string;
  relationshipId: string;
  label?: string;
}

export interface LineageGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
  baseEntityGuid: string;
  direction: 'INPUT' | 'OUTPUT' | 'BOTH';
  depth: number;
}

interface LineageState {
  currentLineage: LineageGraph | null;
  selectedNode: LineageNode | null;
  loading: boolean;
  error: string | null;
  impactAnalysis: {
    criticalPaths: string[][];
    affectedAssets: number;
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  } | null;
  visualConfig: {
    layout: 'hierarchical' | 'force' | 'circular';
    showLabels: boolean;
    groupByType: boolean;
    highlightCriticalPath: boolean;
  };
  filters: {
    entityTypes: string[];
    relationshipTypes: string[];
    maxDepth: number;
  };
}

const initialState: LineageState = {
  currentLineage: null,
  selectedNode: null,
  loading: false,
  error: null,
  impactAnalysis: null,
  visualConfig: {
    layout: 'hierarchical',
    showLabels: true,
    groupByType: false,
    highlightCriticalPath: false,
  },
  filters: {
    entityTypes: [],
    relationshipTypes: [],
    maxDepth: 3,
  },
};

// Async thunks
export const fetchLineage = createAsyncThunk(
  'lineage/fetchLineage',
  async (params: { 
    entityGuid: string; 
    direction: 'INPUT' | 'OUTPUT' | 'BOTH'; 
    depth: number 
  }) => {
    const response = await apiService.getLineage(params);
    return response.data;
  }
);

export const fetchImpactAnalysis = createAsyncThunk(
  'lineage/fetchImpactAnalysis',
  async (entityGuid: string) => {
    const response = await apiService.getImpactAnalysis(entityGuid);
    return response.data;
  }
);

export const fetchEntityRelationships = createAsyncThunk(
  'lineage/fetchEntityRelationships',
  async (entityGuid: string) => {
    const response = await apiService.getEntityRelationships(entityGuid);
    return response.data;
  }
);

const lineageSlice = createSlice({
  name: 'lineage',
  initialState,
  reducers: {
    setSelectedNode: (state, action: PayloadAction<LineageNode | null>) => {
      state.selectedNode = action.payload;
    },
    setVisualConfig: (state, action: PayloadAction<Partial<LineageState['visualConfig']>>) => {
      state.visualConfig = { ...state.visualConfig, ...action.payload };
    },
    setFilters: (state, action: PayloadAction<Partial<LineageState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearLineage: (state) => {
      state.currentLineage = null;
      state.selectedNode = null;
      state.impactAnalysis = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    addNodeToLineage: (state, action: PayloadAction<LineageNode>) => {
      if (state.currentLineage) {
        const existingIndex = state.currentLineage.nodes.findIndex(
          node => node.guid === action.payload.guid
        );
        if (existingIndex === -1) {
          state.currentLineage.nodes.push(action.payload);
        }
      }
    },
    removeNodeFromLineage: (state, action: PayloadAction<string>) => {
      if (state.currentLineage) {
        state.currentLineage.nodes = state.currentLineage.nodes.filter(
          node => node.guid !== action.payload
        );
        state.currentLineage.edges = state.currentLineage.edges.filter(
          edge => edge.fromEntityId !== action.payload && edge.toEntityId !== action.payload
        );
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch lineage
      .addCase(fetchLineage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLineage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentLineage = action.payload;
      })
      .addCase(fetchLineage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch lineage';
      })
      // Fetch impact analysis
      .addCase(fetchImpactAnalysis.fulfilled, (state, action) => {
        state.impactAnalysis = action.payload;
      })
      // Fetch entity relationships
      .addCase(fetchEntityRelationships.fulfilled, (state, action) => {
        // Update the current lineage with relationship data
        if (state.currentLineage && action.payload.relationships) {
          const newEdges = action.payload.relationships.map((rel: any) => ({
            fromEntityId: rel.end1.guid,
            toEntityId: rel.end2.guid,
            relationshipId: rel.guid,
            label: rel.typeName,
          }));
          state.currentLineage.edges = [...state.currentLineage.edges, ...newEdges];
        }
      });
  },
});

export const {
  setSelectedNode,
  setVisualConfig,
  setFilters,
  clearLineage,
  clearError,
  addNodeToLineage,
  removeNodeFromLineage,
} = lineageSlice.actions;

export default lineageSlice.reducer;
