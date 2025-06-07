import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tabs,
  Tab,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Refresh,
  CheckCircle,
  Error,
  Warning,
  Info,
  Settings,
  Timeline,
  Speed,
  Memory,
  Storage,
  Cloud,
  PlayArrow,
  Stop,
  RestartAlt
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'critical';
  total_workers: number;
  active_workers: number;
  total_tasks: number;
  failed_tasks: number;
  queue_backlog: number;
  avg_response_time: number;
  uptime: string;
  last_check: string;
}

interface WorkerMetrics {
  worker_name: string;
  is_active: boolean;
  tasks_processed: number;
  current_load: number;
  memory_usage: number;
  cpu_usage: number;
  last_heartbeat: string;
  queues: string[];
}

interface TaskMetrics {
  task_name: string;
  total_executed: number;
  successful: number;
  failed: number;
  retried: number;
  avg_execution_time: number;
  min_execution_time: number;
  max_execution_time: number;
  last_execution: string;
  failure_rate: number;
}

interface QueueMetrics {
  queue_name: string;
  pending_tasks: number;
  processing_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  avg_wait_time: number;
  throughput: number;
}

interface Alert {
  type: 'critical' | 'warning' | 'info' | 'error';
  message: string;
  recommendation: string;
}

interface HealthReport {
  timestamp: string;
  system_health: SystemHealth;
  task_metrics: Record<string, TaskMetrics>;
  worker_metrics: Record<string, WorkerMetrics>;
  queue_metrics: Record<string, QueueMetrics>;
  alerts: Alert[];
  recommendations: string[];
}

const SystemMonitoring: React.FC = () => {
  const [healthReport, setHealthReport] = useState<HealthReport | null>(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds
  const [selectedTab, setSelectedTab] = useState(0);
  const [alertDialog, setAlertDialog] = useState(false);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState<WorkerMetrics | null>(null);

  // Colors for charts
  const chartColors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe'];

  const fetchHealthReport = useCallback(async () => {
    try {
      setLoading(true);
      
      // In a real implementation, this would call the monitoring API
      // For now, we'll simulate the data structure
      const mockReport: HealthReport = {
        timestamp: new Date().toISOString(),
        system_health: {
          status: 'healthy',
          total_workers: 4,
          active_workers: 4,
          total_tasks: 1250,
          failed_tasks: 15,
          queue_backlog: 5,
          avg_response_time: 2.3,
          uptime: '2 days, 14 hours',
          last_check: new Date().toISOString()
        },
        task_metrics: {
          'file_processing.import_entities': {
            task_name: 'file_processing.import_entities',
            total_executed: 450,
            successful: 442,
            failed: 8,
            retried: 3,
            avg_execution_time: 15.2,
            min_execution_time: 2.1,
            max_execution_time: 45.6,
            last_execution: new Date().toISOString(),
            failure_rate: 0.018
          },
          'file_processing.data_quality_check': {
            task_name: 'file_processing.data_quality_check',
            total_executed: 320,
            successful: 315,
            failed: 5,
            retried: 2,
            avg_execution_time: 8.7,
            min_execution_time: 1.2,
            max_execution_time: 28.3,
            last_execution: new Date().toISOString(),
            failure_rate: 0.016
          },
          'data_operations.analytics_update': {
            task_name: 'data_operations.analytics_update',
            total_executed: 480,
            successful: 478,
            failed: 2,
            retried: 1,
            avg_execution_time: 5.1,
            min_execution_time: 1.8,
            max_execution_time: 12.4,
            last_execution: new Date().toISOString(),
            failure_rate: 0.004
          }
        },
        worker_metrics: {
          'file_processing_worker@host1': {
            worker_name: 'file_processing_worker@host1',
            is_active: true,
            tasks_processed: 325,
            current_load: 2,
            memory_usage: 45.2,
            cpu_usage: 12.5,
            last_heartbeat: new Date().toISOString(),
            queues: ['file_processing', 'high_priority']
          },
          'data_operations_worker@host1': {
            worker_name: 'data_operations_worker@host1',
            is_active: true,
            tasks_processed: 198,
            current_load: 1,
            memory_usage: 32.1,
            cpu_usage: 8.2,
            last_heartbeat: new Date().toISOString(),
            queues: ['data_operations', 'analytics']
          },
          'maintenance_worker@host1': {
            worker_name: 'maintenance_worker@host1',
            is_active: true,
            tasks_processed: 45,
            current_load: 0,
            memory_usage: 18.5,
            cpu_usage: 2.1,
            last_heartbeat: new Date().toISOString(),
            queues: ['maintenance', 'low_priority']
          },
          'bulk_operations_worker@host1': {
            worker_name: 'bulk_operations_worker@host1',
            is_active: true,
            tasks_processed: 682,
            current_load: 3,
            memory_usage: 78.9,
            cpu_usage: 25.3,
            last_heartbeat: new Date().toISOString(),
            queues: ['bulk_operations']
          }
        },
        queue_metrics: {
          'file_processing': {
            queue_name: 'file_processing',
            pending_tasks: 3,
            processing_tasks: 2,
            completed_tasks: 445,
            failed_tasks: 8,
            avg_wait_time: 1.2,
            throughput: 15.2
          },
          'data_operations': {
            queue_name: 'data_operations',
            pending_tasks: 1,
            processing_tasks: 1,
            completed_tasks: 196,
            failed_tasks: 2,
            avg_wait_time: 0.8,
            throughput: 12.8
          },
          'maintenance': {
            queue_name: 'maintenance',
            pending_tasks: 0,
            processing_tasks: 0,
            completed_tasks: 45,
            failed_tasks: 0,
            avg_wait_time: 0.3,
            throughput: 2.1
          },
          'bulk_operations': {
            queue_name: 'bulk_operations',
            pending_tasks: 1,
            processing_tasks: 3,
            completed_tasks: 678,
            failed_tasks: 4,
            avg_wait_time: 2.1,
            throughput: 18.9
          }
        },
        alerts: [
          {
            type: 'warning',
            message: 'High memory usage detected on bulk_operations_worker',
            recommendation: 'Consider reducing concurrency or restarting the worker'
          },
          {
            type: 'info',
            message: 'File processing queue has low backlog',
            recommendation: 'System is running efficiently'
          }
        ],
        recommendations: [
          'Consider scaling up bulk operations worker memory',
          'Monitor file processing queue during peak hours',
          'Schedule maintenance tasks during low usage periods'
        ]
      };

      setHealthReport(mockReport);
      
      // Add to historical data (simulate)
      setHistoricalData(prev => {
        const newData = {
          timestamp: Date.now(),
          active_workers: mockReport.system_health.active_workers,
          queue_backlog: mockReport.system_health.queue_backlog,
          avg_response_time: mockReport.system_health.avg_response_time,
          failed_tasks: mockReport.system_health.failed_tasks
        };
        return [...prev.slice(-23), newData]; // Keep last 24 data points
      });

    } catch (error) {
      console.error('Failed to fetch health report:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    fetchHealthReport();

    if (autoRefresh) {
      const interval = setInterval(fetchHealthReport, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [fetchHealthReport, autoRefresh, refreshInterval]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle color="success" />;
      case 'degraded': return <Warning color="warning" />;
      case 'critical': return <Error color="error" />;
      default: return <Info />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      case 'error': return <Error color="error" />;
      case 'info': return <Info color="info" />;
      default: return <Info />;
    }
  };

  const formatUptime = (uptime: string) => {
    return uptime;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!healthReport) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <LinearProgress sx={{ width: 200 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">System Monitoring</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
          />
          <Button
            startIcon={<Refresh />}
            onClick={fetchHealthReport}
            disabled={loading}
            variant="outlined"
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* System Health Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {getStatusIcon(healthReport.system_health.status)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  System Status
                </Typography>
              </Box>
              <Chip
                label={healthReport.system_health.status.toUpperCase()}
                color={getStatusColor(healthReport.system_health.status) as any}
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                Uptime: {formatUptime(healthReport.system_health.uptime)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Cloud color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Workers
                </Typography>
              </Box>
              <Typography variant="h4">
                {healthReport.system_health.active_workers}/{healthReport.system_health.total_workers}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Workers
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Storage color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Queue Backlog
                </Typography>
              </Box>
              <Typography variant="h4">
                {healthReport.system_health.queue_backlog}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending Tasks
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Speed color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Response Time
                </Typography>
              </Box>
              <Typography variant="h4">
                {healthReport.system_health.avg_response_time.toFixed(1)}s
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts */}
      {healthReport.alerts.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Alerts
            </Typography>
            {healthReport.alerts.map((alert, index) => (
              <Alert
                key={index}
                severity={alert.type}
                sx={{ mb: 1 }}
                action={
                  <Button size="small" onClick={() => setAlertDialog(true)}>
                    View Details
                  </Button>
                }
              >
                {alert.message}
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Tabs for different views */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)}>
            <Tab label="Workers" />
            <Tab label="Tasks" />
            <Tab label="Queues" />
            <Tab label="Performance" />
          </Tabs>
        </Box>

        <CardContent>
          {/* Workers Tab */}
          {selectedTab === 0 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Worker Name</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Tasks Processed</TableCell>
                    <TableCell>Current Load</TableCell>
                    <TableCell>Memory Usage</TableCell>
                    <TableCell>CPU Usage</TableCell>
                    <TableCell>Queues</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.values(healthReport.worker_metrics).map((worker) => (
                    <TableRow key={worker.worker_name}>
                      <TableCell>{worker.worker_name}</TableCell>
                      <TableCell>
                        <Chip
                          icon={worker.is_active ? <CheckCircle /> : <Error />}
                          label={worker.is_active ? 'Active' : 'Inactive'}
                          color={worker.is_active ? 'success' : 'error'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{worker.tasks_processed}</TableCell>
                      <TableCell>{worker.current_load}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={worker.memory_usage}
                            sx={{ flexGrow: 1, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {worker.memory_usage.toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={worker.cpu_usage}
                            sx={{ flexGrow: 1, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {worker.cpu_usage.toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {worker.queues.map((queue) => (
                          <Chip key={queue} label={queue} size="small" sx={{ mr: 0.5 }} />
                        ))}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<Info />}
                          onClick={() => {
                            setSelectedWorker(worker);
                            setDetailsDialog(true);
                          }}
                        >
                          Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Tasks Tab */}
          {selectedTab === 1 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Task Name</TableCell>
                    <TableCell>Total Executed</TableCell>
                    <TableCell>Success Rate</TableCell>
                    <TableCell>Avg Execution Time</TableCell>
                    <TableCell>Last Execution</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.values(healthReport.task_metrics).map((task) => (
                    <TableRow key={task.task_name}>
                      <TableCell>{task.task_name}</TableCell>
                      <TableCell>{task.total_executed}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={(1 - task.failure_rate) * 100}
                            color={task.failure_rate < 0.05 ? 'success' : task.failure_rate < 0.1 ? 'warning' : 'error'}
                            sx={{ flexGrow: 1, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {((1 - task.failure_rate) * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{task.avg_execution_time.toFixed(2)}s</TableCell>
                      <TableCell>{formatTimestamp(task.last_execution)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Queues Tab */}
          {selectedTab === 2 && (
            <Grid container spacing={3}>
              {Object.values(healthReport.queue_metrics).map((queue) => (
                <Grid item xs={12} md={6} key={queue.queue_name}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {queue.queue_name}
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Pending
                          </Typography>
                          <Typography variant="h4">{queue.pending_tasks}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Processing
                          </Typography>
                          <Typography variant="h4">{queue.processing_tasks}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Completed
                          </Typography>
                          <Typography variant="body1">{queue.completed_tasks}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Failed
                          </Typography>
                          <Typography variant="body1">{queue.failed_tasks}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Avg Wait Time
                          </Typography>
                          <Typography variant="body1">{queue.avg_wait_time.toFixed(1)}s</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Throughput
                          </Typography>
                          <Typography variant="body1">{queue.throughput.toFixed(1)}/min</Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}

          {/* Performance Tab */}
          {selectedTab === 3 && historicalData.length > 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Active Workers Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Line
                      type="monotone"
                      dataKey="active_workers"
                      stroke="#8884d8"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Queue Backlog Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Area
                      type="monotone"
                      dataKey="queue_backlog"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Response Time Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historicalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="timestamp"
                      tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Line
                      type="monotone"
                      dataKey="avg_response_time"
                      stroke="#ffc658"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Alert Details Dialog */}
      <Dialog open={alertDialog} onClose={() => setAlertDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>System Alerts & Recommendations</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            Active Alerts
          </Typography>
          <List>
            {healthReport.alerts.map((alert, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {getAlertIcon(alert.type)}
                </ListItemIcon>
                <ListItemText
                  primary={alert.message}
                  secondary={alert.recommendation}
                />
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <List>
            {healthReport.recommendations.map((recommendation, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Info color="info" />
                </ListItemIcon>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Worker Details Dialog */}
      <Dialog open={detailsDialog} onClose={() => setDetailsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Worker Details: {selectedWorker?.worker_name}
        </DialogTitle>
        <DialogContent>
          {selectedWorker && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Status
                </Typography>
                <Chip
                  icon={selectedWorker.is_active ? <CheckCircle /> : <Error />}
                  label={selectedWorker.is_active ? 'Active' : 'Inactive'}
                  color={selectedWorker.is_active ? 'success' : 'error'}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Tasks Processed
                </Typography>
                <Typography variant="body1">{selectedWorker.tasks_processed}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Current Load
                </Typography>
                <Typography variant="body1">{selectedWorker.current_load} tasks</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Last Heartbeat
                </Typography>
                <Typography variant="body1">
                  {formatTimestamp(selectedWorker.last_heartbeat)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  Memory Usage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={selectedWorker.memory_usage}
                    sx={{ flexGrow: 1, mr: 1 }}
                  />
                  <Typography variant="body2">
                    {selectedWorker.memory_usage.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  CPU Usage
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress
                    variant="determinate"
                    value={selectedWorker.cpu_usage}
                    sx={{ flexGrow: 1, mr: 1 }}
                  />
                  <Typography variant="body2">
                    {selectedWorker.cpu_usage.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Assigned Queues
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedWorker.queues.map((queue) => (
                    <Chip key={queue} label={queue} />
                  ))}
                </Box>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button startIcon={<RestartAlt />} color="warning">
            Restart Worker
          </Button>
          <Button onClick={() => setDetailsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemMonitoring;
