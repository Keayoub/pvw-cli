import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
} from '@mui/material';
import {
  Search as SearchIcon,
  Storage as StorageIcon,
  TableChart as TableIcon,
  AccountTree as LineageIcon,
  FilterList as FilterIcon,
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon,
} from '@mui/icons-material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { fetchEntities, searchEntities, setFilters, setPagination } from '../../store/slices/entitiesSlice';

const DataExplorer: React.FC = () => {
  const dispatch = useDispatch();
  const { entities, searchResults, loading, filters, pagination } = useSelector(
    (state: RootState) => state.entities
  );
  
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('grid');

  useEffect(() => {
    dispatch(fetchEntities({ page: pagination.page, pageSize: pagination.pageSize }) as any);
  }, [dispatch, pagination.page, pagination.pageSize]);

  const handleSearch = () => {
    if (searchQuery.trim()) {
      dispatch(searchEntities(searchQuery) as any);
    }
  };

  const handleFilterChange = (filterType: string, value: any) => {
    dispatch(setFilters({ [filterType]: value }));
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    dispatch(setPagination({ page: value - 1 }));
  };

  const displayEntities = searchQuery ? searchResults : entities;

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Data Explorer
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton
            color={viewMode === 'list' ? 'primary' : 'default'}
            onClick={() => setViewMode('list')}
          >
            <ViewListIcon />
          </IconButton>
          <IconButton
            color={viewMode === 'grid' ? 'primary' : 'default'}
            onClick={() => setViewMode('grid')}
          >
            <ViewModuleIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search entities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleSearch}>
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={filters.typeName || ''}
                onChange={(e) => handleFilterChange('typeName', e.target.value)}
                label="Type"
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="DataSet">Data Set</MenuItem>
                <MenuItem value="Table">Table</MenuItem>
                <MenuItem value="Column">Column</MenuItem>
                <MenuItem value="Database">Database</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status || ''}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                label="Status"
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="DELETED">Deleted</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              fullWidth
            >
              More Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Loading entities...</Typography>
        </Box>
      ) : viewMode === 'grid' ? (
        <Grid container spacing={2}>
          {displayEntities.map((entity) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={entity.guid}>
              <Card sx={{ height: '100%', cursor: 'pointer', '&:hover': { elevation: 4 } }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StorageIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" noWrap>
                      {entity.displayText || entity.guid.substring(0, 8)}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {entity.typeName}
                  </Typography>
                  
                  <Chip
                    label={entity.status}
                    size="small"
                    color={entity.status === 'ACTIVE' ? 'success' : 'default'}
                    sx={{ mb: 1 }}
                  />
                  
                  {entity.classifications.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      {entity.classifications.slice(0, 2).map((classification, index) => (
                        <Chip
                          key={index}
                          label={classification.typeName}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>
                  )}
                  
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button size="small" startIcon={<LineageIcon />}>
                      Lineage
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper>
          <List>
            {displayEntities.map((entity, index) => (
              <React.Fragment key={entity.guid}>
                <ListItem sx={{ cursor: 'pointer' }}>
                  <ListItemIcon>
                    <TableIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={entity.displayText || entity.guid}
                    secondary={`${entity.typeName} • Created by ${entity.createdBy}`}
                  />
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                      label={entity.status}
                      size="small"
                      color={entity.status === 'ACTIVE' ? 'success' : 'default'}
                    />
                    <Button size="small" startIcon={<LineageIcon />}>
                      View Lineage
                    </Button>
                  </Box>
                </ListItem>
                {index < displayEntities.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      {/* Pagination */}
      {!searchQuery && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(pagination.total / pagination.pageSize)}
            page={pagination.page + 1}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
};

export default DataExplorer;
