import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  IconButton,
  Paper,
  Typography,
  Chip,
  Avatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  LinearProgress,
  Tooltip,
  Badge,
  Divider
} from '@mui/material';
import {
  Policy as PolicyIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Description as DescriptionIcon,
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Assessment as AssessmentIcon,
  Gavel as GavelIcon,
  Shield as ShieldIcon,
  DataUsage as DataUsageIcon
} from '@mui/icons-material';
import { enhancedApiService, GovernancePolicy, Entity, ComplianceCheck, PolicyType, PolicyStatus } from '../services/enhancedApiService';

interface GovernanceWorkflowProps {
  entities?: Entity[];
}

interface PolicyFormData {
  name: string;
  description: string;
  type: PolicyType;
  rules: any;
  entities: string[];
  data_steward_id?: string;
  is_active: boolean;
  enforcement_level: 'warning' | 'blocking';
  schedule?: string;
}

const GovernanceWorkflow: React.FC<GovernanceWorkflowProps> = ({ entities = [] }) => {
  const [policies, setPolicies] = useState<GovernancePolicy[]>([]);
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  
  // Dialog states
  const [openPolicyDialog, setOpenPolicyDialog] = useState(false);
  const [openComplianceDialog, setOpenComplianceDialog] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState<GovernancePolicy | null>(null);
  const [selectedCompliance, setSelectedCompliance] = useState<ComplianceCheck | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form state
  const [policyFormData, setPolicyFormData] = useState<PolicyFormData>({
    name: '',
    description: '',
    type: 'data_classification',
    rules: {},
    entities: [],
    is_active: true,
    enforcement_level: 'warning'
  });
  
  // Workflow states
  const [activeStep, setActiveStep] = useState(0);
  const [workflowData, setWorkflowData] = useState({
    selectedEntities: [] as string[],
    selectedPolicies: [] as string[],
    complianceResults: [] as any[]
  });
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [policiesData, complianceData] = await Promise.all([
        enhancedApiService.getPolicies(),
        enhancedApiService.getComplianceChecks()
      ]);
      setPolicies(policiesData);
      setComplianceChecks(complianceData);
    } catch (err) {
      setError('Failed to load governance data');
      console.error('Error loading governance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePolicy = () => {
    setSelectedPolicy(null);
    setIsEditing(false);
    setPolicyFormData({
      name: '',
      description: '',
      type: 'data_classification',
      rules: {},
      entities: [],
      is_active: true,
      enforcement_level: 'warning'
    });
    setOpenPolicyDialog(true);
  };

  const handleEditPolicy = (policy: GovernancePolicy) => {
    setSelectedPolicy(policy);
    setIsEditing(true);
    setPolicyFormData({
      name: policy.name,
      description: policy.description,
      type: policy.type,
      rules: policy.rules,
      entities: policy.entities || [],
      data_steward_id: policy.data_steward_id,
      is_active: policy.is_active,
      enforcement_level: policy.enforcement_level || 'warning',
      schedule: policy.schedule
    });
    setOpenPolicyDialog(true);
  };

  const handleSubmitPolicy = async () => {
    try {
      if (!policyFormData.name || !policyFormData.description) {
        showSnackbar('Please fill in all required fields', 'error');
        return;
      }

      const policyData = {
        name: policyFormData.name,
        description: policyFormData.description,
        type: policyFormData.type,
        rules: policyFormData.rules,
        entities: policyFormData.entities,
        data_steward_id: policyFormData.data_steward_id,
        is_active: policyFormData.is_active,
        enforcement_level: policyFormData.enforcement_level,
        schedule: policyFormData.schedule
      };

      if (isEditing && selectedPolicy) {
        await enhancedApiService.updatePolicy(selectedPolicy.id, policyData);
        showSnackbar('Policy updated successfully', 'success');
      } else {
        await enhancedApiService.createPolicy(policyData);
        showSnackbar('Policy created successfully', 'success');
      }

      setOpenPolicyDialog(false);
      loadData();
    } catch (err) {
      showSnackbar('Failed to save policy', 'error');
      console.error('Error saving policy:', err);
    }
  };

  const handleRunComplianceCheck = async (policyId: string) => {
    try {
      await enhancedApiService.runComplianceCheck({
        policy_id: policyId,
        entity_ids: workflowData.selectedEntities
      });
      showSnackbar('Compliance check started', 'success');
      setTimeout(loadData, 2000); // Refresh data after a delay
    } catch (err) {
      showSnackbar('Failed to run compliance check', 'error');
      console.error('Error running compliance check:', err);
    }
  };

  const handleBulkComplianceCheck = async () => {
    try {
      const promises = workflowData.selectedPolicies.map(policyId =>
        enhancedApiService.runComplianceCheck({
          policy_id: policyId,
          entity_ids: workflowData.selectedEntities
        })
      );
      
      await Promise.all(promises);
      showSnackbar('Bulk compliance checks started', 'success');
      setTimeout(loadData, 2000);
    } catch (err) {
      showSnackbar('Failed to run bulk compliance checks', 'error');
      console.error('Error running bulk compliance checks:', err);
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'warning' | 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const getPolicyStatusColor = (status: PolicyStatus) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'draft': return 'warning';
      default: return 'default';
    }
  };

  const getComplianceStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant': return <CheckCircleIcon color="success" />;
      case 'non_compliant': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'pending': return <ScheduleIcon color="action" />;
      default: return <ScheduleIcon color="action" />;
    }
  };

  const workflowSteps = [
    'Select Entities',
    'Choose Policies',
    'Run Compliance Checks',
    'Review Results',
    'Apply Governance'
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading governance data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Data Governance Workflow
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreatePolicy}
        >
          Create Policy
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={selectedTab} onChange={(e, v) => setSelectedTab(v)}>
            <Tab label="Workflow" />
            <Tab label="Policies" />
            <Tab label="Compliance" />
            <Tab label="Analytics" />
          </Tabs>
        </Box>

        {/* Workflow Tab */}
        {selectedTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Governance Workflow
            </Typography>
            <Stepper activeStep={activeStep} orientation="vertical">
              {workflowSteps.map((label, index) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                  <StepContent>
                    {index === 0 && (
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          Select the entities you want to apply governance policies to:
                        </Typography>
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                          {entities.slice(0, 6).map((entity) => (
                            <Grid item xs={12} sm={6} md={4} key={entity.id}>
                              <Card 
                                variant="outlined" 
                                sx={{ 
                                  cursor: 'pointer',
                                  border: workflowData.selectedEntities.includes(entity.id) ? '2px solid' : '1px solid',
                                  borderColor: workflowData.selectedEntities.includes(entity.id) ? 'primary.main' : 'divider'
                                }}
                                onClick={() => {
                                  const newSelected = workflowData.selectedEntities.includes(entity.id)
                                    ? workflowData.selectedEntities.filter(id => id !== entity.id)
                                    : [...workflowData.selectedEntities, entity.id];
                                  setWorkflowData({ ...workflowData, selectedEntities: newSelected });
                                }}
                              >
                                <CardContent>
                                  <Typography variant="subtitle2">{entity.name}</Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    {entity.type}
                                  </Typography>
                                </CardContent>
                              </Card>
                            </Grid>
                          ))}
                        </Grid>
                        <Box sx={{ mt: 2 }}>
                          <Button
                            variant="contained"
                            onClick={() => setActiveStep(1)}
                            disabled={workflowData.selectedEntities.length === 0}
                          >
                            Next
                          </Button>
                        </Box>
                      </Box>
                    )}
                    
                    {index === 1 && (
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          Select the policies to apply:
                        </Typography>
                        <List>
                          {policies.slice(0, 5).map((policy) => (
                            <ListItem
                              key={policy.id}
                              button
                              onClick={() => {
                                const newSelected = workflowData.selectedPolicies.includes(policy.id)
                                  ? workflowData.selectedPolicies.filter(id => id !== policy.id)
                                  : [...workflowData.selectedPolicies, policy.id];
                                setWorkflowData({ ...workflowData, selectedPolicies: newSelected });
                              }}
                            >
                              <ListItemIcon>
                                <PolicyIcon 
                                  color={workflowData.selectedPolicies.includes(policy.id) ? 'primary' : 'action'}
                                />
                              </ListItemIcon>
                              <ListItemText
                                primary={policy.name}
                                secondary={policy.description}
                              />
                              <ListItemSecondaryAction>
                                <Chip
                                  label={policy.type}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                        </List>
                        <Box sx={{ mt: 2 }}>
                          <Button sx={{ mr: 1 }} onClick={() => setActiveStep(0)}>
                            Back
                          </Button>
                          <Button
                            variant="contained"
                            onClick={() => setActiveStep(2)}
                            disabled={workflowData.selectedPolicies.length === 0}
                          >
                            Next
                          </Button>
                        </Box>
                      </Box>
                    )}
                    
                    {index === 2 && (
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          Run compliance checks for selected entities and policies:
                        </Typography>
                        <Alert severity="info" sx={{ mb: 2 }}>
                          {workflowData.selectedEntities.length} entities selected, {workflowData.selectedPolicies.length} policies selected
                        </Alert>
                        <Box sx={{ mt: 2 }}>
                          <Button sx={{ mr: 1 }} onClick={() => setActiveStep(1)}>
                            Back
                          </Button>
                          <Button
                            variant="contained"
                            startIcon={<PlayArrowIcon />}
                            onClick={() => {
                              handleBulkComplianceCheck();
                              setActiveStep(3);
                            }}
                          >
                            Run Compliance Checks
                          </Button>
                        </Box>
                      </Box>
                    )}
                    
                    {index === 3 && (
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          Review compliance check results:
                        </Typography>
                        <Grid container spacing={2} sx={{ mt: 1 }}>
                          {complianceChecks.slice(0, 4).map((check) => (
                            <Grid item xs={12} sm={6} key={check.id}>
                              <Card variant="outlined">
                                <CardContent>
                                  <Box display="flex" alignItems="center" mb={1}>
                                    {getComplianceStatusIcon(check.status)}
                                    <Typography variant="subtitle2" sx={{ ml: 1 }}>
                                      {check.policy_name}
                                    </Typography>
                                  </Box>
                                  <Typography variant="body2" color="text.secondary">
                                    Status: {check.status}
                                  </Typography>
                                  <LinearProgress
                                    variant="determinate"
                                    value={check.compliance_score || 0}
                                    sx={{ mt: 1 }}
                                  />
                                </CardContent>
                              </Card>
                            </Grid>
                          ))}
                        </Grid>
                        <Box sx={{ mt: 2 }}>
                          <Button sx={{ mr: 1 }} onClick={() => setActiveStep(2)}>
                            Back
                          </Button>
                          <Button
                            variant="contained"
                            onClick={() => setActiveStep(4)}
                          >
                            Apply Governance
                          </Button>
                        </Box>
                      </Box>
                    )}
                    
                    {index === 4 && (
                      <Box>
                        <Typography variant="body2" gutterBottom>
                          Apply governance actions based on compliance results:
                        </Typography>
                        <Alert severity="success">
                          Governance workflow completed successfully!
                        </Alert>
                        <Box sx={{ mt: 2 }}>
                          <Button
                            variant="contained"
                            onClick={() => {
                              setActiveStep(0);
                              setWorkflowData({
                                selectedEntities: [],
                                selectedPolicies: [],
                                complianceResults: []
                              });
                            }}
                          >
                            Start New Workflow
                          </Button>
                        </Box>
                      </Box>
                    )}
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Box>
        )}

        {/* Policies Tab */}
        {selectedTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              {policies.map((policy) => (
                <Grid item xs={12} md={6} lg={4} key={policy.id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                        <Typography variant="h6" component="h3">
                          {policy.name}
                        </Typography>
                        <Chip
                          label={policy.status}
                          color={getPolicyStatusColor(policy.status)}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {policy.description}
                      </Typography>
                      <Box display="flex" alignItems="center" mt={2}>
                        <Chip
                          icon={<PolicyIcon />}
                          label={policy.type.replace('_', ' ')}
                          size="small"
                          variant="outlined"
                        />
                        {policy.enforcement_level && (
                          <Chip
                            icon={<SecurityIcon />}
                            label={policy.enforcement_level}
                            size="small"
                            variant="outlined"
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Box>
                      {policy.data_steward && (
                        <Box display="flex" alignItems="center" mt={1}>
                          <PersonIcon fontSize="small" color="action" />
                          <Typography variant="body2" sx={{ ml: 0.5 }}>
                            Steward: {policy.data_steward}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                    <CardActions>
                      <Button size="small" onClick={() => handleEditPolicy(policy)}>
                        Edit
                      </Button>
                      <Button size="small" onClick={() => handleRunComplianceCheck(policy.id)}>
                        Run Check
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Compliance Tab */}
        {selectedTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Timeline>
              {complianceChecks.map((check, index) => (
                <TimelineItem key={check.id}>
                  <TimelineSeparator>
                    <TimelineDot color={check.status === 'compliant' ? 'success' : 'error'}>
                      {getComplianceStatusIcon(check.status)}
                    </TimelineDot>
                    {index < complianceChecks.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="start">
                          <Box>
                            <Typography variant="subtitle1">
                              {check.policy_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Checked on {new Date(check.checked_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                          <Chip
                            label={check.status}
                            color={check.status === 'compliant' ? 'success' : 'error'}
                            size="small"
                          />
                        </Box>
                        {check.compliance_score !== undefined && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="body2" gutterBottom>
                              Compliance Score: {check.compliance_score}%
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={check.compliance_score}
                              color={check.compliance_score >= 80 ? 'success' : 'warning'}
                            />
                          </Box>
                        )}
                        {check.violations && check.violations.length > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="body2" gutterBottom>
                              Violations:
                            </Typography>
                            <List dense>
                              {check.violations.slice(0, 3).map((violation, idx) => (
                                <ListItem key={idx}>
                                  <ListItemIcon>
                                    <ErrorIcon color="error" fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={violation.description}
                                    secondary={`Severity: ${violation.severity}`}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </Box>
        )}

        {/* Analytics Tab */}
        {selectedTab === 3 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <PolicyIcon color="primary" />
                      <Box sx={{ ml: 2 }}>
                        <Typography variant="h4">{policies.length}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Policies
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <CheckCircleIcon color="success" />
                      <Box sx={{ ml: 2 }}>
                        <Typography variant="h4">
                          {complianceChecks.filter(c => c.status === 'compliant').length}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Compliant Checks
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <ErrorIcon color="error" />
                      <Box sx={{ ml: 2 }}>
                        <Typography variant="h4">
                          {complianceChecks.filter(c => c.status === 'non_compliant').length}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Non-Compliant
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center">
                      <AssessmentIcon color="info" />
                      <Box sx={{ ml: 2 }}>
                        <Typography variant="h4">
                          {Math.round(
                            complianceChecks.reduce((acc, c) => acc + (c.compliance_score || 0), 0) /
                            Math.max(complianceChecks.length, 1)
                          )}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Avg Compliance
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Policy Dialog */}
      <Dialog open={openPolicyDialog} onClose={() => setOpenPolicyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {isEditing ? 'Edit Policy' : 'Create New Policy'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Policy Name"
                value={policyFormData.name}
                onChange={(e) => setPolicyFormData({ ...policyFormData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={policyFormData.description}
                onChange={(e) => setPolicyFormData({ ...policyFormData, description: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Policy Type</InputLabel>
                <Select
                  value={policyFormData.type}
                  onChange={(e) => setPolicyFormData({ ...policyFormData, type: e.target.value as PolicyType })}
                  label="Policy Type"
                >
                  <MenuItem value="data_classification">Data Classification</MenuItem>
                  <MenuItem value="data_retention">Data Retention</MenuItem>
                  <MenuItem value="data_quality">Data Quality</MenuItem>
                  <MenuItem value="access_control">Access Control</MenuItem>
                  <MenuItem value="privacy">Privacy</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Enforcement Level</InputLabel>
                <Select
                  value={policyFormData.enforcement_level}
                  onChange={(e) => setPolicyFormData({ ...policyFormData, enforcement_level: e.target.value as 'warning' | 'blocking' })}
                  label="Enforcement Level"
                >
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="blocking">Blocking</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPolicyDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmitPolicy} variant="contained">
            {isEditing ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default GovernanceWorkflow;
