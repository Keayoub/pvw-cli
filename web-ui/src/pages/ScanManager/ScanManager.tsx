import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button, Chip } from '@mui/material';
import { Scanner as ScannerIcon, PlayArrow as PlayIcon, Stop as StopIcon, Add as AddIcon } from '@mui/icons-material';

const ScanManager: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Scan Manager
        </Typography>
        <Button startIcon={<AddIcon />} variant="contained">
          New Scan
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Scan Configuration
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Visual scan configuration wizard will be implemented here.
                Features include:
                • Data source selection
                • Scan rule configuration
                • Schedule management
                • Template library
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Scans
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {[1, 2, 3].map((scan) => (
                <Card key={scan} variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="h6">
                          Production Database Scan #{scan}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          SQL Server • Started 2 hours ago
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip 
                          label={scan === 1 ? "Running" : scan === 2 ? "Completed" : "Failed"} 
                          color={scan === 1 ? "primary" : scan === 2 ? "success" : "error"}
                        />
                        <Button startIcon={scan === 1 ? <StopIcon /> : <PlayIcon />} size="small">
                          {scan === 1 ? "Stop" : "Restart"}
                        </Button>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ScanManager;
