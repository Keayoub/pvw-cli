import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button } from '@mui/material';
import { Policy as PolicyIcon, Add as AddIcon, Security as SecurityIcon } from '@mui/icons-material';

const GovernanceCenter: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Governance Center
        </Typography>
        <Button startIcon={<AddIcon />} variant="contained">
          New Policy
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <PolicyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Business Rules Engine
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Visual rule builder and policy management interface.
                Features include:
                • Drag-and-drop rule creation
                • Policy template library
                • Compliance monitoring
                • Exception handling
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Compliance Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Real-time compliance monitoring and reporting.
                Features include:
                • Compliance score tracking
                • Violation alerts
                • Audit trail
                • Regulatory reporting
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GovernanceCenter;
