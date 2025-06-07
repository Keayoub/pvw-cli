import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Preview,
  PlayArrow,
  Download,
  Delete,
  CheckCircle,
  Error,
  Schedule,
  Refresh
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { AxiosProgressEvent } from 'axios';

import apiService, { UploadedFile, ProcessingJob } from '../services/enhancedApiService';

interface FileUploadProps {
  onFileProcessed?: (result: any) => void;
  allowedTypes?: string[];
  maxFileSize?: number;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileProcessed,
  allowedTypes = ['.csv', '.xlsx', '.xls', '.json', '.txt'],
  maxFileSize = 50 * 1024 * 1024 // 50MB
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [processingDialog, setProcessingDialog] = useState(false);
  const [processingOptions, setProcessingOptions] = useState({
    operation_type: '',
    target_entity_type: '',
    options: {}
  });
  const [alerts, setAlerts] = useState<Array<{ type: 'success' | 'error' | 'warning' | 'info'; message: string }>>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Supported processing operations
  const processingOperations = [
    { value: 'import_entities', label: 'Import Entities', description: 'Create entities from file data' },
    { value: 'bulk_classification', label: 'Bulk Classification', description: 'Apply classifications in bulk' },
    { value: 'data_quality_check', label: 'Data Quality Check', description: 'Analyze data quality metrics' },
    { value: 'lineage_discovery', label: 'Lineage Discovery', description: 'Discover data lineage relationships' },
    { value: 'metadata_extraction', label: 'Metadata Extraction', description: 'Extract comprehensive metadata' },
    { value: 'compliance_scan', label: 'Compliance Scan', description: 'Scan for compliance violations' },
    { value: 'data_profiling', label: 'Data Profiling', description: 'Generate detailed data profile' }
  ];

  const entityTypes = [
    'DataSet', 'Table', 'Column', 'Database', 'Schema', 'View', 'Process', 'API'
  ];

  // Dropzone configuration
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      if (file.size > maxFileSize) {
        addAlert('error', `File ${file.name} is too large. Maximum size is ${maxFileSize / 1024 / 1024}MB`);
        continue;
      }

      try {
        setLoading(true);
        const response = await apiService.uploadFile(file, (progressEvent: AxiosProgressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          }
        });

        const uploadedFile = response.data;
        setUploadedFiles(prev => [...prev, uploadedFile]);
        addAlert('success', `File ${file.name} uploaded successfully`);
        
        // Clear progress
        setUploadProgress(prev => {
          const newProgress = { ...prev };
          delete newProgress[file.name];
          return newProgress;
        });

      } catch (error: any) {
        addAlert('error', `Failed to upload ${file.name}: ${apiService.handleApiError(error)}`);
      } finally {
        setLoading(false);
      }
    }
  }, [maxFileSize]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: allowedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    multiple: true
  });

  const addAlert = (type: 'success' | 'error' | 'warning' | 'info', message: string) => {
    const newAlert = { type, message };
    setAlerts(prev => [...prev, newAlert]);
    setTimeout(() => {
      setAlerts(prev => prev.filter(alert => alert !== newAlert));
    }, 5000);
  };

  const loadUploadedFiles = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUploadedFiles();
      setUploadedFiles(response.data.files);
    } catch (error: any) {
      addAlert('error', `Failed to load files: ${apiService.handleApiError(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const previewFile = async (file: UploadedFile) => {
    try {
      setLoading(true);
      const response = await apiService.previewFile(file.file_id, 10);
      setPreviewData(response.data);
      setSelectedFile(file);
    } catch (error: any) {
      addAlert('error', `Failed to preview file: ${apiService.handleApiError(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (file: UploadedFile) => {
    try {
      const response = await apiService.downloadFile(file.file_id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file.original_filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      addAlert('error', `Failed to download file: ${apiService.handleApiError(error)}`);
    }
  };

  const deleteFile = async (file: UploadedFile) => {
    try {
      await apiService.deleteFile(file.file_id);
      setUploadedFiles(prev => prev.filter(f => f.file_id !== file.file_id));
      addAlert('success', 'File deleted successfully');
    } catch (error: any) {
      addAlert('error', `Failed to delete file: ${apiService.handleApiError(error)}`);
    }
  };

  const startProcessing = async () => {
    if (!selectedFile || !processingOptions.operation_type) {
      addAlert('error', 'Please select a file and processing operation');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.processFile(
        selectedFile.file_id,
        processingOptions.operation_type,
        processingOptions.target_entity_type || undefined,
        processingOptions.options
      );

      addAlert('success', `Processing started: ${response.data.job_id}`);
      setProcessingDialog(false);
      
      // Poll for status updates
      pollProcessingStatus(selectedFile.file_id);

    } catch (error: any) {
      addAlert('error', `Failed to start processing: ${apiService.handleApiError(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const pollProcessingStatus = async (fileId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await apiService.getProcessingStatus(fileId);
        const job = response.data;

        // Update file status in the list
        setUploadedFiles(prev => prev.map(file => 
          file.file_id === fileId 
            ? { ...file, processing_jobs: [job] }
            : file
        ));

        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(pollInterval);
          
          if (job.status === 'completed') {
            addAlert('success', 'File processing completed successfully');
            if (onFileProcessed && job.result) {
              onFileProcessed(job.result);
            }
          } else {
            addAlert('error', `File processing failed: ${job.error || 'Unknown error'}`);
          }
        }

      } catch (error) {
        // Silently handle polling errors
        clearInterval(pollInterval);
      }
    }, 2000);

    // Stop polling after 10 minutes
    setTimeout(() => clearInterval(pollInterval), 10 * 60 * 1000);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'warning';
      case 'queued': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'failed': return <Error />;
      case 'processing': return <Schedule />;
      case 'queued': return <Schedule />;
      default: return <InsertDriveFile />;
    }
  };

  // Load files on component mount
  React.useEffect(() => {
    loadUploadedFiles();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        File Upload & Processing
      </Typography>

      {/* Alerts */}
      {alerts.map((alert, index) => (
        <Alert key={index} severity={alert.type} sx={{ mb: 2 }}>
          {alert.message}
        </Alert>
      ))}

      {/* Upload Area */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'action.hover' : 'transparent',
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <input {...getInputProps()} />
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supported formats: {allowedTypes.join(', ')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Maximum file size: {formatFileSize(maxFileSize)}
            </Typography>
          </Box>

          {/* Upload Progress */}
          {Object.entries(uploadProgress).map(([filename, progress]) => (
            <Box key={filename} sx={{ mt: 2 }}>
              <Typography variant="body2">{filename}</Typography>
              <LinearProgress variant="determinate" value={progress} sx={{ mt: 1 }} />
              <Typography variant="caption" color="text.secondary">
                {progress}%
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Card>

      {/* Files List */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Uploaded Files</Typography>
            <Button startIcon={<Refresh />} onClick={loadUploadedFiles} disabled={loading}>
              Refresh
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>File Name</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Upload Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {uploadedFiles.map((file) => {
                  const job = file.processing_jobs?.[0];
                  return (
                    <TableRow key={file.file_id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <InsertDriveFile sx={{ mr: 1 }} />
                          {file.original_filename}
                        </Box>
                      </TableCell>
                      <TableCell>{formatFileSize(file.size)}</TableCell>
                      <TableCell>
                        {new Date(file.upload_time).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(job?.status || file.status)}
                          label={job?.status || file.status}
                          color={getStatusColor(job?.status || file.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {job && job.status === 'processing' && (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={job.progress}
                              sx={{ flexGrow: 1, mr: 1 }}
                            />
                            <Typography variant="caption">{job.progress}%</Typography>
                          </Box>
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Preview">
                            <IconButton size="small" onClick={() => previewFile(file)}>
                              <Preview />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Process">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedFile(file);
                                setProcessingDialog(true);
                              }}
                            >
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download">
                            <IconButton size="small" onClick={() => downloadFile(file)}>
                              <Download />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton size="small" color="error" onClick={() => deleteFile(file)}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* File Preview Dialog */}
      <Dialog open={!!previewData} onClose={() => setPreviewData(null)} maxWidth="lg" fullWidth>
        <DialogTitle>
          File Preview: {selectedFile?.original_filename}
        </DialogTitle>
        <DialogContent>
          {previewData && (
            <Box>
              {previewData.columns && (
                <TableContainer component={Paper} sx={{ mt: 2 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        {previewData.columns.map((col: string) => (
                          <TableCell key={col}>{col}</TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {previewData.data?.slice(0, 10).map((row: any, index: number) => (
                        <TableRow key={index}>
                          {previewData.columns.map((col: string) => (
                            <TableCell key={col}>{row[col]}</TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
              
              {previewData.lines && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Text Content:</Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    {previewData.lines.map((line: string, index: number) => (
                      <Typography key={index} variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {line}
                      </Typography>
                    ))}
                  </Paper>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewData(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Processing Options Dialog */}
      <Dialog open={processingDialog} onClose={() => setProcessingDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Process File: {selectedFile?.original_filename}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Processing Operation</InputLabel>
                <Select
                  value={processingOptions.operation_type}
                  onChange={(e) => setProcessingOptions(prev => ({
                    ...prev,
                    operation_type: e.target.value
                  }))}
                >
                  {processingOperations.map((op) => (
                    <MenuItem key={op.value} value={op.value}>
                      <Box>
                        <Typography variant="body1">{op.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {op.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {processingOptions.operation_type === 'import_entities' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Target Entity Type</InputLabel>
                  <Select
                    value={processingOptions.target_entity_type}
                    onChange={(e) => setProcessingOptions(prev => ({
                      ...prev,
                      target_entity_type: e.target.value
                    }))}
                  >
                    {entityTypes.map((type) => (
                      <MenuItem key={type} value={type}>{type}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProcessingDialog(false)}>Cancel</Button>
          <Button 
            onClick={startProcessing} 
            variant="contained" 
            disabled={!processingOptions.operation_type || loading}
          >
            Start Processing
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileUpload;
