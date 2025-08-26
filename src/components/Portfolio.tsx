import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const Portfolio: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Portfolio
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Portfolio tracking, position management, and performance analysis
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Portfolio Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This component will include portfolio tracking, position management, P&L analysis, and performance metrics.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Portfolio;

