import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Pagination,
  Toolbar,
  AppBar,
  InputAdornment
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Search,
  Storage,
  AccountTree,
  Security,
  Label,
  DataObject,
  ExpandMore,
  FilterList,
  Refresh,
  Download,
  Upload
} from '@mui/icons-material';

interface Entity {
  id: string;
  name: string;
  type: string;
  qualifiedName: string;
  owner?: string;
  description?: string;
  classifications: string[];
  attributes: Record<string, any>;
  lineage?: {
    upstream: string[];
    downstream: string[];
  };
  dataSource: string;
  createdAt: string;
  updatedAt: string;
  status: 'active' | 'archived' | 'deprecated';
  qualityScore?: number;
}

interface EntityType {
  name: string;
  displayName: string;
  description: string;
  category: string;
  attributeDefinitions: Array<{
    name: string;
    typeName: string;
    isOptional: boolean;
    cardinality: string;
  }>;
}

interface Classification {
  name: string;
  displayName: string;
  description: string;
  entityTypes: string[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`entities-tabpanel-${index}`}
      aria-labelledby={`entities-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const EntitiesManagement: React.FC = () => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [entityTypes, setEntityTypes] = useState<EntityType[]>([]);
  const [classifications, setClassifications] = useState<Classification[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [rowsPerPage] = useState(10);
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    classification: ''
  });

  // Mock data
  const mockEntities: Entity[] = [
    {
      id: '1',
      name: 'customers',
      type: 'DataSet',
      qualifiedName: 'mssql://server1/database1/dbo/customers',
      owner: 'data-team@company.com',
      description: 'Customer master data table containing customer information',
      classifications: ['PII', 'Confidential'],
      attributes: {
        rowCount: 150000,
        columnCount: 12,
        dataSize: '45MB',
        lastUpdated: '2025-06-07T09:30:00Z'
      },
      lineage: {
        upstream: ['customer_staging', 'customer_raw'],
        downstream: ['customer_analytics', 'customer_reports']
      },
      dataSource: 'SQL Server Production',
      createdAt: '2025-01-15T10:00:00Z',
      updatedAt: '2025-06-07T09:30:00Z',
      status: 'active',
      qualityScore: 92
    },
    {
      id: '2',
      name: 'products',
      type: 'DataSet',
      qualifiedName: 'mssql://server1/database1/dbo/products',
      owner: 'product-team@company.com',
      description: 'Product catalog with pricing and inventory data',
      classifications: ['Internal', 'Business'],
      attributes: {
        rowCount: 25000,
        columnCount: 8,
        dataSize: '12MB',
        lastUpdated: '2025-06-07T08:45:00Z'
      },
      lineage: {
        upstream: ['product_staging'],
        downstream: ['sales_analytics', 'inventory_reports']
      },
      dataSource: 'SQL Server Production',
      createdAt: '2025-02-01T14:30:00Z',
      updatedAt: '2025-06-07T08:45:00Z',
      status: 'active',
      qualityScore: 88
    },
    {
      id: '3',
      name: 'legacy_orders',
      type: 'DataSet',
      qualifiedName: 'oracle://legacy/orders',
      description: 'Legacy order data - scheduled for migration',
      classifications: ['Deprecated'],
      attributes: {
        rowCount: 500000,
        columnCount: 15,
        dataSize: '180MB',
        lastUpdated: '2025-05-15T12:00:00Z'
      },
      lineage: {
        upstream: [],
        downstream: ['order_archive']
      },
      dataSource: 'Oracle Legacy',
      createdAt: '2020-01-01T00:00:00Z',
      updatedAt: '2025-05-15T12:00:00Z',
      status: 'deprecated',
      qualityScore: 65
    }
  ];

  const mockEntityTypes: EntityType[] = [
    {
      name: 'DataSet',
      displayName: 'Data Set',
      description: 'A table or collection of data',
      category: 'DataAsset',
      attributeDefinitions: [
        { name: 'name', typeName: 'string', isOptional: false, cardinality: 'SINGLE' },
        { name: 'description', typeName: 'string', isOptional: true, cardinality: 'SINGLE' },
        { name: 'owner', typeName: 'string', isOptional: true, cardinality: 'SINGLE' }
      ]
    },
    {
      name: 'Column',
      displayName: 'Column',
      description: 'A column in a dataset',
      category: 'DataAsset',
      attributeDefinitions: [
        { name: 'name', typeName: 'string', isOptional: false, cardinality: 'SINGLE' },
        { name: 'dataType', typeName: 'string', isOptional: false, cardinality: 'SINGLE' },
        { name: 'isNullable', typeName: 'boolean', isOptional: true, cardinality: 'SINGLE' }
      ]
    }
  ];

  const mockClassifications: Classification[] = [
    {
      name: 'PII',
      displayName: 'Personally Identifiable Information',
      description: 'Data that can be used to identify a specific individual',
      entityTypes: ['DataSet', 'Column']
    },
    {
      name: 'Confidential',
      displayName: 'Confidential',
      description: 'Sensitive business data requiring restricted access',
      entityTypes: ['DataSet', 'Column']
    },
    {
      name: 'Public',
      displayName: 'Public',
      description: 'Data that can be freely shared',
      entityTypes: ['DataSet', 'Column']
    }
  ];

  useEffect(() => {
    setEntities(mockEntities);
    setEntityTypes(mockEntityTypes);
    setClassifications(mockClassifications);
  }, []);

  const fetchEntities = useCallback(async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call the backend API
      // const response = await fetch('/api/v1/entities');
      // const data = await response.json();
      // setEntities(data);
      setEntities(mockEntities);
    } catch (error) {
      console.error('Failed to fetch entities:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const openEntityDetails = (entity: Entity) => {
    setSelectedEntity(entity);
    setDetailsOpen(true);
  };

  const openEntityEdit = (entity: Entity) => {
    setSelectedEntity(entity);
    setEditOpen(true);
  };

  const handleDeleteEntity = async (entityId: string) => {
    // Implement delete functionality
    console.log('Delete entity:', entityId);
  };

  const getStatusColor = (status: Entity['status']) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'deprecated':
        return 'warning';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const filteredEntities = entities.filter(entity => {
    const matchesSearch = entity.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entity.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entity.qualifiedName.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !filters.type || entity.type === filters.type;
    const matchesStatus = !filters.status || entity.status === filters.status;
    const matchesClassification = !filters.classification || 
                                 entity.classifications.includes(filters.classification);

    return matchesSearch && matchesType && matchesStatus && matchesClassification;
  });

  const paginatedEntities = filteredEntities.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const renderEntitiesTable = () => (
    <Box>
      {/* Search and Filters */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search entities..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 300 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={filters.type}
            label="Type"
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            {entityTypes.map(type => (
              <MenuItem key={type.name} value={type.name}>
                {type.displayName}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filters.status}
            label="Status"
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="deprecated">Deprecated</MenuItem>
            <MenuItem value="archived">Archived</MenuItem>
          </Select>
        </FormControl>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchEntities}
        >
          Refresh
        </Button>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setEditOpen(true)}
        >
          Add Entity
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Classifications</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Quality Score</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedEntities.map((entity) => (
              <TableRow key={entity.id}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2">{entity.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {entity.qualifiedName}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    icon={<DataObject />}
                    label={entity.type}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {entity.classifications.map(classification => (
                      <Chip
                        key={classification}
                        label={classification}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </TableCell>
                <TableCell>{entity.owner || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={entity.status.toUpperCase()}
                    color={getStatusColor(entity.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {entity.qualityScore && (
                    <Chip
                      label={`${entity.qualityScore}%`}
                      color={getQualityScoreColor(entity.qualityScore) as any}
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton size="small" onClick={() => openEntityDetails(entity)}>
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton size="small" onClick={() => openEntityEdit(entity)}>
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton size="small" onClick={() => handleDeleteEntity(entity.id)}>
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
        <Pagination
          count={Math.ceil(filteredEntities.length / rowsPerPage)}
          page={page}
          onChange={(e, newPage) => setPage(newPage)}
        />
      </Box>
    </Box>
  );

  const renderEntityTypes = () => (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h6">Entity Types</Typography>
        <Button variant="contained" startIcon={<Add />}>
          Add Type
        </Button>
      </Box>
      {entityTypes.map(type => (
        <Accordion key={type.name}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <DataObject />
              <Box>
                <Typography variant="subtitle1">{type.displayName}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {type.description}
                </Typography>
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="subtitle2" gutterBottom>
              Attribute Definitions:
            </Typography>
            <List dense>
              {type.attributeDefinitions.map(attr => (
                <ListItem key={attr.name}>
                  <ListItemText
                    primary={attr.name}
                    secondary={`${attr.typeName} (${attr.cardinality}${attr.isOptional ? ', Optional' : ', Required'})`}
                  />
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );

  const renderClassifications = () => (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h6">Classifications</Typography>
        <Button variant="contained" startIcon={<Add />}>
          Add Classification
        </Button>
      </Box>
      <Grid container spacing={2}>
        {classifications.map(classification => (
          <Grid item xs={12} md={6} lg={4} key={classification.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Label sx={{ mr: 1 }} />
                  <Typography variant="h6">{classification.displayName}</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {classification.description}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  Applicable to:
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {classification.entityTypes.map(type => (
                    <Chip key={type} label={type} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange}>
          <Tab label="Entities" />
          <Tab label="Entity Types" />
          <Tab label="Classifications" />
        </Tabs>
      </Box>

      <TabPanel value={selectedTab} index={0}>
        {renderEntitiesTable()}
      </TabPanel>
      <TabPanel value={selectedTab} index={1}>
        {renderEntityTypes()}
      </TabPanel>
      <TabPanel value={selectedTab} index={2}>
        {renderClassifications()}
      </TabPanel>

      {/* Entity Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          {selectedEntity?.name} Details
        </DialogTitle>
        <DialogContent>
          {selectedEntity && (
            <Box sx={{ mt: 1 }}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" gutterBottom>Basic Information</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2">Qualified Name</Typography>
                      <Typography>{selectedEntity.qualifiedName}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2">Type</Typography>
                      <Typography>{selectedEntity.type}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2">Owner</Typography>
                      <Typography>{selectedEntity.owner || 'N/A'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="subtitle2">Data Source</Typography>
                      <Typography>{selectedEntity.dataSource}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2">Description</Typography>
                      <Typography>{selectedEntity.description || 'No description available'}</Typography>
                    </Grid>
                  </Grid>

                  {selectedEntity.lineage && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" gutterBottom>Lineage</Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="subtitle2">Upstream Dependencies</Typography>
                          <List dense>
                            {selectedEntity.lineage.upstream.map(dep => (
                              <ListItem key={dep}>
                                <ListItemIcon><AccountTree /></ListItemIcon>
                                <ListItemText primary={dep} />
                              </ListItem>
                            ))}
                          </List>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="subtitle2">Downstream Dependencies</Typography>
                          <List dense>
                            {selectedEntity.lineage.downstream.map(dep => (
                              <ListItem key={dep}>
                                <ListItemIcon><AccountTree /></ListItemIcon>
                                <ListItemText primary={dep} />
                              </ListItem>
                            ))}
                          </List>
                        </Grid>
                      </Grid>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>Metadata</Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Status</Typography>
                    <Chip
                      label={selectedEntity.status.toUpperCase()}
                      color={getStatusColor(selectedEntity.status) as any}
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2">Classifications</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
                      {selectedEntity.classifications.map(classification => (
                        <Chip
                          key={classification}
                          label={classification}
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>

                  {selectedEntity.qualityScore && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">Quality Score</Typography>
                      <Chip
                        label={`${selectedEntity.qualityScore}%`}
                        color={getQualityScoreColor(selectedEntity.qualityScore) as any}
                      />
                    </Box>
                  )}

                  <Typography variant="subtitle2">Attributes</Typography>
                  <List dense>
                    {Object.entries(selectedEntity.attributes).map(([key, value]) => (
                      <ListItem key={key}>
                        <ListItemText
                          primary={key}
                          secondary={typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => openEntityEdit(selectedEntity!)}>
            Edit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Entity Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedEntity ? 'Edit Entity' : 'Add New Entity'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Name"
                  defaultValue={selectedEntity?.name || ''}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    defaultValue={selectedEntity?.type || ''}
                    label="Type"
                  >
                    {entityTypes.map(type => (
                      <MenuItem key={type.name} value={type.name}>
                        {type.displayName}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Qualified Name"
                  defaultValue={selectedEntity?.qualifiedName || ''}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  defaultValue={selectedEntity?.description || ''}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Owner"
                  defaultValue={selectedEntity?.owner || ''}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    defaultValue={selectedEntity?.status || 'active'}
                    label="Status"
                  >
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="deprecated">Deprecated</MenuItem>
                    <MenuItem value="archived">Archived</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained">
            {selectedEntity ? 'Save Changes' : 'Create Entity'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EntitiesManagement;
