import React, { useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Scanner as ScannerIcon,
  Policy as PolicyIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as StableIcon,
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../store/store';
import { fetchAnalyticsMetrics } from '../../store/slices/analyticsSlice';
import { fetchScans } from '../../store/slices/scanningSlice';
import { fetchEntities } from '../../store/slices/entitiesSlice';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
  icon: React.ReactNode;
  color?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  trend,
  icon,
  color = 'primary',
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon color="success" fontSize="small" />;
      case 'down':
        return <TrendingDownIcon color="error" fontSize="small" />;
      default:
        return <StableIcon color="disabled" fontSize="small" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
          <IconButton size="small">
            <RefreshIcon />
          </IconButton>
        </Box>
        
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {value}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {title}
        </Typography>
        
        {change !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {getTrendIcon()}
            <Typography
              variant="body2"
              sx={{ color: getTrendColor() }}
            >
              {change > 0 ? '+' : ''}{change}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              vs last period
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const { metrics, loading } = useSelector((state: RootState) => state.analytics);
  const { scans, metrics: scanMetrics } = useSelector((state: RootState) => state.scanning);
  const { entities } = useSelector((state: RootState) => state.entities);

  useEffect(() => {
    dispatch(fetchAnalyticsMetrics('30d') as any);
    dispatch(fetchScans() as any);
    dispatch(fetchEntities({ page: 0, pageSize: 10 }) as any);
  }, [dispatch]);

  // Mock data for charts
  const scanTrendData = [
    { name: 'Mon', scans: 12, successful: 10, failed: 2 },
    { name: 'Tue', scans: 15, successful: 14, failed: 1 },
    { name: 'Wed', scans: 8, successful: 7, failed: 1 },
    { name: 'Thu', scans: 18, successful: 16, failed: 2 },
    { name: 'Fri', scans: 22, successful: 20, failed: 2 },
    { name: 'Sat', scans: 5, successful: 5, failed: 0 },
    { name: 'Sun', scans: 3, successful: 3, failed: 0 },
  ];

  const entityTypeData = [
    { name: 'Tables', value: 1250, color: '#8884d8' },
    { name: 'Columns', value: 8500, color: '#82ca9d' },
    { name: 'Databases', value: 45, color: '#ffc658' },
    { name: 'Files', value: 2300, color: '#ff7300' },
    { name: 'Reports', value: 180, color: '#00ff00' },
  ];

  const qualityTrendData = [
    { name: 'Week 1', quality: 85, issues: 45 },
    { name: 'Week 2', quality: 88, issues: 38 },
    { name: 'Week 3', quality: 82, issues: 52 },
    { name: 'Week 4', quality: 91, issues: 28 },
  ];

  const recentScans = scans.slice(0, 5);
  const recentEntities = entities.slice(0, 5);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          variant="outlined"
          onClick={() => {
            dispatch(fetchAnalyticsMetrics('30d') as any);
            dispatch(fetchScans() as any);
          }}
        >
          Refresh Data
        </Button>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Entities"
            value="12,456"
            change={5.2}
            trend="up"
            icon={<StorageIcon fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Scans"
            value={scanMetrics.runningScans}
            change={-2.1}
            trend="down"
            icon={<ScannerIcon fontSize="large" />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Compliance Score"
            value="94%"
            change={1.8}
            trend="up"
            icon={<PolicyIcon fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Data Quality"
            value="89%"
            change={-0.5}
            trend="down"
            icon={<CheckCircleIcon fontSize="large" />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Scan Activity Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={scanTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="successful"
                    stackId="1"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    name="Successful"
                  />
                  <Area
                    type="monotone"
                    dataKey="failed"
                    stackId="1"
                    stroke="#ff7300"
                    fill="#ff7300"
                    name="Failed"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Entity Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={entityTypeData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {entityTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Quality Trends */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Quality Trends
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={qualityTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="quality"
                    stroke="#8884d8"
                    strokeWidth={3}
                    name="Quality Score (%)"
                  />
                  <Bar
                    yAxisId="right"
                    dataKey="issues"
                    fill="#ff7300"
                    name="Issues Found"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recent Scans
                </Typography>
                <Button
                  endIcon={<OpenInNewIcon />}
                  size="small"
                  href="/scans"
                >
                  View All
                </Button>
              </Box>
              
              <List>
                {recentScans.map((scan, index) => (
                  <React.Fragment key={scan.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {scan.status === 'Completed' ? (
                          <CheckCircleIcon color="success" />
                        ) : scan.status === 'Failed' ? (
                          <WarningIcon color="error" />
                        ) : (
                          <ScannerIcon color="primary" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={scan.name}
                        secondary={`${scan.dataSourceName} • ${scan.status}`}
                      />
                      <Chip
                        label={scan.status}
                        size="small"
                        color={
                          scan.status === 'Completed'
                            ? 'success'
                            : scan.status === 'Failed'
                            ? 'error'
                            : 'primary'
                        }
                      />
                    </ListItem>
                    {index < recentScans.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recently Modified Entities
                </Typography>
                <Button
                  endIcon={<OpenInNewIcon />}
                  size="small"
                  href="/explorer"
                >
                  Explore
                </Button>
              </Box>
              
              <List>
                {recentEntities.map((entity, index) => (
                  <React.Fragment key={entity.guid}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        <StorageIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={entity.displayText || entity.guid}
                        secondary={entity.typeName}
                      />
                      <Chip
                        label={entity.status}
                        size="small"
                        variant="outlined"
                      />
                    </ListItem>
                    {index < recentEntities.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
