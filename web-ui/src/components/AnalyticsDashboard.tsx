import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Alert,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  TrendingUp,
  Storage,
  Security,
  Speed,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  Download,
  Visibility
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';

interface AnalyticsData {
  overview: {
    totalEntities: number;
    totalDataSources: number;
    activeScans: number;
    dataQualityScore: number;
    complianceScore: number;
    lastUpdated: string;
  };
  trends: {
    date: string;
    entities: number;
    dataSources: number;
    scans: number;
    qualityScore: number;
  }[];
  dataQuality: {
    name: string;
    score: number;
    issues: number;
    trend: 'up' | 'down' | 'stable';
  }[];
  compliance: {
    regulation: string;
    score: number;
    status: 'compliant' | 'partial' | 'non-compliant';
    violations: number;
  }[];
  usage: {
    hour: number;
    apiCalls: number;
    searches: number;
    downloads: number;
  }[];
  topEntities: {
    name: string;
    type: string;
    accessCount: number;
    lastAccessed: string;
    qualityScore: number;
  }[];
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
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AnalyticsDashboard: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);

  // Mock data for demonstration
  const mockAnalyticsData: AnalyticsData = {
    overview: {
      totalEntities: 15847,
      totalDataSources: 42,
      activeScans: 8,
      dataQualityScore: 87,
      complianceScore: 92,
      lastUpdated: '2025-06-07T10:30:00Z'
    },
    trends: [
      { date: '2025-06-01', entities: 15200, dataSources: 38, scans: 12, qualityScore: 85 },
      { date: '2025-06-02', entities: 15350, dataSources: 39, scans: 10, qualityScore: 86 },
      { date: '2025-06-03', entities: 15480, dataSources: 40, scans: 15, qualityScore: 85 },
      { date: '2025-06-04', entities: 15620, dataSources: 41, scans: 8, qualityScore: 87 },
      { date: '2025-06-05', entities: 15730, dataSources: 41, scans: 6, qualityScore: 88 },
      { date: '2025-06-06', entities: 15800, dataSources: 42, scans: 9, qualityScore: 87 },
      { date: '2025-06-07', entities: 15847, dataSources: 42, scans: 8, qualityScore: 87 }
    ],
    dataQuality: [
      { name: 'Customer Data', score: 94, issues: 3, trend: 'up' },
      { name: 'Product Catalog', score: 88, issues: 8, trend: 'stable' },
      { name: 'Sales Transactions', score: 92, issues: 5, trend: 'up' },
      { name: 'Inventory Data', score: 79, issues: 15, trend: 'down' },
      { name: 'Financial Records', score: 96, issues: 2, trend: 'up' }
    ],
    compliance: [
      { regulation: 'GDPR', score: 94, status: 'compliant', violations: 2 },
      { regulation: 'CCPA', score: 89, status: 'partial', violations: 8 },
      { regulation: 'SOX', score: 97, status: 'compliant', violations: 1 },
      { regulation: 'HIPAA', score: 91, status: 'compliant', violations: 3 }
    ],
    usage: [
      { hour: 0, apiCalls: 45, searches: 12, downloads: 3 },
      { hour: 1, apiCalls: 32, searches: 8, downloads: 1 },
      { hour: 2, apiCalls: 28, searches: 5, downloads: 2 },
      { hour: 3, apiCalls: 25, searches: 4, downloads: 1 },
      { hour: 4, apiCalls: 30, searches: 6, downloads: 2 },
      { hour: 5, apiCalls: 38, searches: 9, downloads: 3 },
      { hour: 6, apiCalls: 65, searches: 18, downloads: 5 },
      { hour: 7, apiCalls: 120, searches: 35, downloads: 8 },
      { hour: 8, apiCalls: 180, searches: 52, downloads: 12 },
      { hour: 9, apiCalls: 220, searches: 68, downloads: 15 },
      { hour: 10, apiCalls: 195, searches: 58, downloads: 11 },
      { hour: 11, apiCalls: 210, searches: 62, downloads: 14 }
    ],
    topEntities: [
      { name: 'customers', type: 'DataSet', accessCount: 1247, lastAccessed: '2025-06-07T09:30:00Z', qualityScore: 94 },
      { name: 'orders', type: 'DataSet', accessCount: 986, lastAccessed: '2025-06-07T09:15:00Z', qualityScore: 89 },
      { name: 'products', type: 'DataSet', accessCount: 743, lastAccessed: '2025-06-07T09:45:00Z', qualityScore: 92 },
      { name: 'user_sessions', type: 'DataSet', accessCount: 612, lastAccessed: '2025-06-07T08:30:00Z', qualityScore: 78 },
      { name: 'financial_summary', type: 'DataSet', accessCount: 445, lastAccessed: '2025-06-07T10:00:00Z', qualityScore: 96 }
    ]
  };

  useEffect(() => {
    setAnalyticsData(mockAnalyticsData);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleTimeRangeChange = (newTimeRange: string) => {
    setTimeRange(newTimeRange);
    // In a real implementation, fetch new data based on time range
  };

  const refreshData = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call the backend API
      // const response = await fetch(`/api/v1/analytics?timeRange=${timeRange}`);
      // const data = await response.json();
      // setAnalyticsData(data);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalyticsData(mockAnalyticsData);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'success';
      case 'partial':
        return 'warning';
      case 'non-compliant':
        return 'error';
      default:
        return 'default';
    }
  };

  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return '#4caf50';
    if (score >= 70) return '#ff9800';
    return '#f44336';
  };

  const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'];

  if (!analyticsData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <LinearProgress sx={{ width: 200 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with Controls */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Analytics Dashboard</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => handleTimeRangeChange(e.target.value)}
            >
              <MenuItem value="1d">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshData}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Storage sx={{ color: 'primary.main', mr: 1, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Entities
                  </Typography>
                  <Typography variant="h5">
                    {analyticsData.overview.totalEntities.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Data Sources
                  </Typography>
                  <Typography variant="h5">
                    {analyticsData.overview.totalDataSources}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Speed sx={{ color: 'info.main', mr: 1, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Scans
                  </Typography>
                  <Typography variant="h5">
                    {analyticsData.overview.activeScans}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircle sx={{ color: 'success.main', mr: 1, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Data Quality
                  </Typography>
                  <Typography variant="h5">
                    {analyticsData.overview.dataQualityScore}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Security sx={{ color: 'warning.main', mr: 1, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Compliance
                  </Typography>
                  <Typography variant="h5">
                    {analyticsData.overview.complianceScore}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for Different Views */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="analytics tabs">
          <Tab label="Trends" />
          <Tab label="Data Quality" />
          <Tab label="Compliance" />
          <Tab label="Usage" />
          <Tab label="Top Entities" />
        </Tabs>
      </Box>

      {/* Trends Tab */}
      <TabPanel value={selectedTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Entity Growth
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={analyticsData.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Area
                      type="monotone"
                      dataKey="entities"
                      stroke="#1976d2"
                      fill="#1976d2"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Quality Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[80, 100]} />
                    <RechartsTooltip />
                    <Line
                      type="monotone"
                      dataKey="qualityScore"
                      stroke="#4caf50"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Scanning Activity
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="scans" fill="#ff9800" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Data Quality Tab */}
      <TabPanel value={selectedTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Quality by Dataset
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Dataset</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Issues</TableCell>
                        <TableCell>Trend</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analyticsData.dataQuality.map((item) => (
                        <TableRow key={item.name}>
                          <TableCell>{item.name}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <LinearProgress
                                variant="determinate"
                                value={item.score}
                                sx={{
                                  width: 100,
                                  mr: 1,
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: getQualityScoreColor(item.score)
                                  }
                                }}
                              />
                              <Typography variant="body2">{item.score}%</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={item.issues}
                              color={item.issues > 10 ? 'error' : item.issues > 5 ? 'warning' : 'success'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {item.trend === 'up' && <TrendingUp color="success" />}
                            {item.trend === 'down' && <TrendingUp sx={{ transform: 'rotate(180deg)' }} color="error" />}
                            {item.trend === 'stable' && <TrendingUp sx={{ transform: 'rotate(90deg)' }} color="disabled" />}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quality Score Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.dataQuality}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, score }) => `${name}: ${score}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="score"
                    >
                      {analyticsData.dataQuality.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Compliance Tab */}
      <TabPanel value={selectedTab} index={2}>
        <Grid container spacing={3}>
          {analyticsData.compliance.map((regulation) => (
            <Grid item xs={12} sm={6} md={3} key={regulation.regulation}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Security sx={{ mr: 1 }} />
                    <Typography variant="h6">{regulation.regulation}</Typography>
                  </Box>
                  <Typography variant="h4" sx={{ mb: 1 }}>
                    {regulation.score}%
                  </Typography>
                  <Chip
                    label={regulation.status.toUpperCase()}
                    color={getComplianceColor(regulation.status) as any}
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="body2" color="textSecondary">
                    {regulation.violations} violations found
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={regulation.score}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Usage Tab */}
      <TabPanel value={selectedTab} index={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Platform Usage (Last 24 Hours)
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={analyticsData.usage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" label={{ value: 'Hour', position: 'insideBottom', offset: -5 }} />
                <YAxis />
                <RechartsTooltip />
                <Area
                  type="monotone"
                  dataKey="apiCalls"
                  stackId="1"
                  stroke="#1976d2"
                  fill="#1976d2"
                  name="API Calls"
                />
                <Area
                  type="monotone"
                  dataKey="searches"
                  stackId="1"
                  stroke="#388e3c"
                  fill="#388e3c"
                  name="Searches"
                />
                <Area
                  type="monotone"
                  dataKey="downloads"
                  stackId="1"
                  stroke="#f57c00"
                  fill="#f57c00"
                  name="Downloads"
                />
                <Legend />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Top Entities Tab */}
      <TabPanel value={selectedTab} index={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Most Accessed Entities
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Entity Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Access Count</TableCell>
                    <TableCell>Last Accessed</TableCell>
                    <TableCell>Quality Score</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {analyticsData.topEntities.map((entity, index) => (
                    <TableRow key={entity.name}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="subtitle2">#{index + 1}</Typography>
                          <Typography sx={{ ml: 1 }}>{entity.name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={entity.type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>{entity.accessCount.toLocaleString()}</TableCell>
                      <TableCell>
                        {new Date(entity.lastAccessed).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${entity.qualityScore}%`}
                          color={entity.qualityScore >= 90 ? 'success' : entity.qualityScore >= 70 ? 'warning' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Entity">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>
    </Box>
  );
};

export default AnalyticsDashboard;
