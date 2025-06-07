import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Alert,
  LinearProgress,
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Refresh,
  FileDownload,
  Visibility,
  Delete,
  CheckCircle,
  Error,
  Schedule,
  ExpandMore,
  Analytics,
  Storage,
  Security,
  NetworkCheck
} from '@mui/icons-material';

interface ProcessingJob {
  id: string;
  fileName: string;
  operation: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  completedAt?: string;
  resultSummary?: {
    entitiesProcessed: number;
    classificationsApplied: number;
    issuesFound: number;
    dataQualityScore: number;
  };
  errorMessage?: string;
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
      id={`processing-tabpanel-${index}`}
      aria-labelledby={`processing-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DataProcessingDashboard: React.FC = () => {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<ProcessingJob | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Mock data for demonstration
  const mockJobs: ProcessingJob[] = [
    {
      id: '1',
      fileName: 'customer_data.csv',
      operation: 'Entity Import',
      status: 'completed',
      progress: 100,
      createdAt: '2025-06-07T10:30:00Z',
      completedAt: '2025-06-07T10:35:00Z',
      resultSummary: {
        entitiesProcessed: 15420,
        classificationsApplied: 8,
        issuesFound: 12,
        dataQualityScore: 92
      }
    },
    {
      id: '2',
      fileName: 'product_catalog.xlsx',
      operation: 'Data Quality Check',
      status: 'processing',
      progress: 65,
      createdAt: '2025-06-07T11:00:00Z'
    },
    {
      id: '3',
      fileName: 'sales_transactions.json',
      operation: 'Lineage Discovery',
      status: 'pending',
      progress: 0,
      createdAt: '2025-06-07T11:15:00Z'
    }
  ];

  useEffect(() => {
    // Initialize with mock data
    setJobs(mockJobs);
    // Set up polling for real-time updates
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = useCallback(async () => {
    try {
      // In a real implementation, this would call the backend API
      // const response = await fetch('/api/v1/processing/jobs');
      // const data = await response.json();
      // setJobs(data);
      
      // For now, simulate progress updates
      setJobs(prevJobs =>
        prevJobs.map(job => {
          if (job.status === 'processing' && job.progress < 100) {
            return { ...job, progress: Math.min(100, job.progress + Math.random() * 10) };
          }
          return job;
        })
      );
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    }
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const getStatusIcon = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <Schedule color="primary" />;
      case 'failed':
        return <Error color="error" />;
      default:
        return <Schedule color="disabled" />;
    }
  };

  const getStatusColor = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'primary';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleJobAction = (action: string, jobId: string) => {
    console.log(`${action} job ${jobId}`);
    // Implement job actions (pause, resume, cancel, etc.)
  };

  const openJobDetails = (job: ProcessingJob) => {
    setSelectedJob(job);
    setDetailsOpen(true);
  };

  const renderJobsTable = (filteredJobs: ProcessingJob[]) => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Status</TableCell>
            <TableCell>File Name</TableCell>
            <TableCell>Operation</TableCell>
            <TableCell>Progress</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredJobs.map((job) => (
            <TableRow key={job.id}>
              <TableCell>
                <Tooltip title={job.status}>
                  <Chip
                    icon={getStatusIcon(job.status)}
                    label={job.status.toUpperCase()}
                    color={getStatusColor(job.status) as any}
                    size="small"
                  />
                </Tooltip>
              </TableCell>
              <TableCell>{job.fileName}</TableCell>
              <TableCell>{job.operation}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 100 }}>
                  <LinearProgress
                    variant="determinate"
                    value={job.progress}
                    sx={{ flexGrow: 1, mr: 1 }}
                  />
                  <Typography variant="body2">{job.progress}%</Typography>
                </Box>
              </TableCell>
              <TableCell>
                {new Date(job.createdAt).toLocaleString()}
              </TableCell>
              <TableCell>
                <Tooltip title="View Details">
                  <IconButton size="small" onClick={() => openJobDetails(job)}>
                    <Visibility />
                  </IconButton>
                </Tooltip>
                {job.status === 'processing' && (
                  <Tooltip title="Pause">
                    <IconButton size="small" onClick={() => handleJobAction('pause', job.id)}>
                      <Pause />
                    </IconButton>
                  </Tooltip>
                )}
                {job.status === 'completed' && job.resultSummary && (
                  <Tooltip title="Download Results">
                    <IconButton size="small" onClick={() => handleJobAction('download', job.id)}>
                      <FileDownload />
                    </IconButton>
                  </Tooltip>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const completedJobs = jobs.filter(job => job.status === 'completed');
  const processingJobs = jobs.filter(job => job.status === 'processing');
  const pendingJobs = jobs.filter(job => job.status === 'pending');
  const failedJobs = jobs.filter(job => job.status === 'failed');

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h4">
                    {completedJobs.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Schedule sx={{ color: 'primary.main', mr: 1 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Processing
                  </Typography>
                  <Typography variant="h4">
                    {processingJobs.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Schedule sx={{ color: 'warning.main', mr: 1 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pending
                  </Typography>
                  <Typography variant="h4">
                    {pendingJobs.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Error sx={{ color: 'error.main', mr: 1 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Failed
                  </Typography>
                  <Typography variant="h4">
                    {failedJobs.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content with Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={selectedTab} onChange={handleTabChange} aria-label="processing jobs tabs">
            <Tab label={
              <Badge badgeContent={processingJobs.length} color="primary">
                Processing
              </Badge>
            } />
            <Tab label={
              <Badge badgeContent={pendingJobs.length} color="warning">
                Pending
              </Badge>
            } />
            <Tab label={
              <Badge badgeContent={completedJobs.length} color="success">
                Completed
              </Badge>
            } />
            <Tab label={
              <Badge badgeContent={failedJobs.length} color="error">
                Failed
              </Badge>
            } />
          </Tabs>
        </Box>
        <TabPanel value={selectedTab} index={0}>
          {renderJobsTable(processingJobs)}
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          {renderJobsTable(pendingJobs)}
        </TabPanel>
        <TabPanel value={selectedTab} index={2}>
          {renderJobsTable(completedJobs)}
        </TabPanel>
        <TabPanel value={selectedTab} index={3}>
          {renderJobsTable(failedJobs)}
        </TabPanel>
      </Card>

      {/* Job Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Job Details: {selectedJob?.fileName}
        </DialogTitle>
        <DialogContent>
          {selectedJob && (
            <Box sx={{ mt: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Operation
                  </Typography>
                  <Typography>{selectedJob.operation}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Status
                  </Typography>
                  <Chip
                    icon={getStatusIcon(selectedJob.status)}
                    label={selectedJob.status.toUpperCase()}
                    color={getStatusColor(selectedJob.status) as any}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Created
                  </Typography>
                  <Typography>{new Date(selectedJob.createdAt).toLocaleString()}</Typography>
                </Grid>
                {selectedJob.completedAt && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Completed
                    </Typography>
                    <Typography>{new Date(selectedJob.completedAt).toLocaleString()}</Typography>
                  </Grid>
                )}
              </Grid>

              {selectedJob.resultSummary && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Results Summary
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Storage sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                          <Typography variant="h5">
                            {selectedJob.resultSummary.entitiesProcessed.toLocaleString()}
                          </Typography>
                          <Typography color="textSecondary">
                            Entities Processed
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Security sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                          <Typography variant="h5">
                            {selectedJob.resultSummary.classificationsApplied}
                          </Typography>
                          <Typography color="textSecondary">
                            Classifications Applied
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Error sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                          <Typography variant="h5">
                            {selectedJob.resultSummary.issuesFound}
                          </Typography>
                          <Typography color="textSecondary">
                            Issues Found
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Analytics sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                          <Typography variant="h5">
                            {selectedJob.resultSummary.dataQualityScore}%
                          </Typography>
                          <Typography color="textSecondary">
                            Data Quality Score
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {selectedJob.errorMessage && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {selectedJob.errorMessage}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          {selectedJob?.status === 'completed' && (
            <Button variant="contained" startIcon={<FileDownload />}>
              Download Results
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataProcessingDashboard;
