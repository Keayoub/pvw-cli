import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { Analytics as AnalyticsIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';

const Analytics: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        Analytics & Reporting
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Advanced Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ML-powered insights and predictive analytics.
                Features include:
                • Usage pattern analysis
                • Anomaly detection
                • Quality predictions
                • Recommendation engine
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Custom Reports
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive report builder and dashboard customization.
                Features include:
                • Drag-and-drop report builder
                • Custom dashboard creation
                • Scheduled reporting
                • Export capabilities
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
