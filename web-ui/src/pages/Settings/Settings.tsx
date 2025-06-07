import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Alert,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Save as SaveIcon,
  RestartAlt as ResetIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as ThemeIcon,
  Api as ApiIcon,
  Storage as DataIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { updatePreferences, resetPreferences } from '../../store/slices/uiSlice';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Settings: React.FC = () => {
  const dispatch = useAppDispatch();
  const { preferences } = useAppSelector((state) => state.ui);
  const [currentTab, setCurrentTab] = useState(0);
  const [saveMessage, setSaveMessage] = useState('');
  const [apiEndpoints, setApiEndpoints] = useState<string[]>([
    'https://api.purview.microsoft.com',
    'https://catalog.purview.azure.com'
  ]);
  const [newEndpoint, setNewEndpoint] = useState('');

  const [settings, setSettings] = useState({
    // General Settings
    theme: preferences.theme || 'light',
    language: 'en',
    autoRefresh: true,
    refreshInterval: 30,
    
    // Notification Settings
    emailNotifications: true,
    pushNotifications: true,
    scanCompletionNotify: true,
    errorNotifications: true,
    weeklyReports: false,
    
    // Data Settings
    defaultPageSize: 25,
    maxExportRows: 10000,
    cacheTimeout: 300,
    enableDataPreview: true,
    previewRowLimit: 100,
    
    // Security Settings
    sessionTimeout: 480,
    enableMFA: false,
    auditLogging: true,
    encryptLocalStorage: true,
    
    // API Settings
    apiTimeout: 30,
    retryAttempts: 3,
    enableApiCache: true,
    apiCacheTimeout: 180,
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = () => {
    dispatch(updatePreferences(settings));
    setSaveMessage('Settings saved successfully!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleResetSettings = () => {
    dispatch(resetPreferences());
    setSaveMessage('Settings reset to defaults!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleAddEndpoint = () => {
    if (newEndpoint && !apiEndpoints.includes(newEndpoint)) {
      setApiEndpoints([...apiEndpoints, newEndpoint]);
      setNewEndpoint('');
    }
  };

  const handleRemoveEndpoint = (endpoint: string) => {
    setApiEndpoints(apiEndpoints.filter(e => e !== endpoint));
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      {saveMessage && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {saveMessage}
        </Alert>
      )}

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={currentTab} onChange={handleTabChange} aria-label="settings tabs">
            <Tab icon={<ThemeIcon />} label="General" />
            <Tab icon={<NotificationsIcon />} label="Notifications" />
            <Tab icon={<DataIcon />} label="Data & Performance" />
            <Tab icon={<SecurityIcon />} label="Security" />
            <Tab icon={<ApiIcon />} label="API Configuration" />
          </Tabs>
        </Box>

        {/* General Settings */}
        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Appearance" />
                <CardContent>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={settings.theme}
                      onChange={(e) => handleSettingChange('theme', e.target.value)}
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="auto">Auto</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                      <MenuItem value="de">German</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Auto-Refresh" />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoRefresh}
                        onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                      />
                    }
                    label="Enable auto-refresh"
                  />
                  
                  {settings.autoRefresh && (
                    <TextField
                      fullWidth
                      type="number"
                      label="Refresh Interval (seconds)"
                      value={settings.refreshInterval}
                      onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                      margin="normal"
                      inputProps={{ min: 10, max: 300 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Notification Settings */}
        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Notification Channels" />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.emailNotifications}
                        onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                      />
                    }
                    label="Email Notifications"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.pushNotifications}
                        onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                      />
                    }
                    label="Push Notifications"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Notification Types" />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.scanCompletionNotify}
                        onChange={(e) => handleSettingChange('scanCompletionNotify', e.target.checked)}
                      />
                    }
                    label="Scan Completion"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.errorNotifications}
                        onChange={(e) => handleSettingChange('errorNotifications', e.target.checked)}
                      />
                    }
                    label="Error Notifications"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.weeklyReports}
                        onChange={(e) => handleSettingChange('weeklyReports', e.target.checked)}
                      />
                    }
                    label="Weekly Reports"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Data & Performance Settings */}
        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Data Display" />
                <CardContent>
                  <TextField
                    fullWidth
                    type="number"
                    label="Default Page Size"
                    value={settings.defaultPageSize}
                    onChange={(e) => handleSettingChange('defaultPageSize', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 10, max: 100 }}
                  />
                  
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Export Rows"
                    value={settings.maxExportRows}
                    onChange={(e) => handleSettingChange('maxExportRows', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 1000, max: 100000 }}
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.enableDataPreview}
                        onChange={(e) => handleSettingChange('enableDataPreview', e.target.checked)}
                      />
                    }
                    label="Enable Data Preview"
                  />
                  
                  {settings.enableDataPreview && (
                    <TextField
                      fullWidth
                      type="number"
                      label="Preview Row Limit"
                      value={settings.previewRowLimit}
                      onChange={(e) => handleSettingChange('previewRowLimit', parseInt(e.target.value))}
                      margin="normal"
                      inputProps={{ min: 10, max: 1000 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Caching" />
                <CardContent>
                  <TextField
                    fullWidth
                    type="number"
                    label="Cache Timeout (seconds)"
                    value={settings.cacheTimeout}
                    onChange={(e) => handleSettingChange('cacheTimeout', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 60, max: 3600 }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Security Settings */}
        <TabPanel value={currentTab} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Authentication" />
                <CardContent>
                  <TextField
                    fullWidth
                    type="number"
                    label="Session Timeout (minutes)"
                    value={settings.sessionTimeout}
                    onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 15, max: 1440 }}
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.enableMFA}
                        onChange={(e) => handleSettingChange('enableMFA', e.target.checked)}
                      />
                    }
                    label="Enable Multi-Factor Authentication"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Data Protection" />
                <CardContent>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.auditLogging}
                        onChange={(e) => handleSettingChange('auditLogging', e.target.checked)}
                      />
                    }
                    label="Enable Audit Logging"
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.encryptLocalStorage}
                        onChange={(e) => handleSettingChange('encryptLocalStorage', e.target.checked)}
                      />
                    }
                    label="Encrypt Local Storage"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* API Configuration */}
        <TabPanel value={currentTab} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="API Settings" />
                <CardContent>
                  <TextField
                    fullWidth
                    type="number"
                    label="API Timeout (seconds)"
                    value={settings.apiTimeout}
                    onChange={(e) => handleSettingChange('apiTimeout', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 5, max: 120 }}
                  />
                  
                  <TextField
                    fullWidth
                    type="number"
                    label="Retry Attempts"
                    value={settings.retryAttempts}
                    onChange={(e) => handleSettingChange('retryAttempts', parseInt(e.target.value))}
                    margin="normal"
                    inputProps={{ min: 0, max: 10 }}
                  />
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.enableApiCache}
                        onChange={(e) => handleSettingChange('enableApiCache', e.target.checked)}
                      />
                    }
                    label="Enable API Caching"
                  />
                  
                  {settings.enableApiCache && (
                    <TextField
                      fullWidth
                      type="number"
                      label="API Cache Timeout (seconds)"
                      value={settings.apiCacheTimeout}
                      onChange={(e) => handleSettingChange('apiCacheTimeout', parseInt(e.target.value))}
                      margin="normal"
                      inputProps={{ min: 30, max: 3600 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="API Endpoints" />
                <CardContent>
                  <Box sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      label="Add New Endpoint"
                      value={newEndpoint}
                      onChange={(e) => setNewEndpoint(e.target.value)}
                      InputProps={{
                        endAdornment: (
                          <IconButton onClick={handleAddEndpoint} disabled={!newEndpoint}>
                            <AddIcon />
                          </IconButton>
                        )
                      }}
                    />
                  </Box>
                  
                  <List>
                    {apiEndpoints.map((endpoint, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={endpoint} />
                        <ListItemSecondaryAction>
                          <IconButton 
                            edge="end" 
                            onClick={() => handleRemoveEndpoint(endpoint)}
                            disabled={apiEndpoints.length <= 1}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <Divider />
        
        <Box sx={{ p: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={<ResetIcon />}
            onClick={handleResetSettings}
          >
            Reset to Defaults
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
          >
            Save Settings
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Settings;
