import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Button } from '@mui/material';
import { AccountTree as LineageIcon, ZoomIn as ZoomInIcon, ZoomOut as ZoomOutIcon } from '@mui/icons-material';

const LineageViewer: React.FC = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Lineage Viewer
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button startIcon={<ZoomInIcon />}>Zoom In</Button>
          <Button startIcon={<ZoomOutIcon />}>Zoom Out</Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Lineage Controls
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive lineage visualization controls will be implemented here.
                Features include:
                • Direction selection (upstream/downstream)
                • Depth control
                • Entity type filtering
                • Layout options
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={9}>
          <Paper sx={{ p: 3, minHeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box sx={{ textAlign: 'center' }}>
              <LineageIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Lineage Visualization
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive D3.js-powered lineage graph will be rendered here.
                This will show entity relationships, data flow, and impact analysis.
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LineageViewer;
