import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
  Button,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change_pct: number;
  trend: string;
}

interface SignalData {
  symbol: string;
  signal_type: string;
  confidence_score: number;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [signals, setSignals] = useState<SignalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Simulated data for demonstration
  const mockMarketData: MarketData[] = [
    { symbol: 'SPY', name: 'S&P 500', price: 456.78, change_pct: 0.85, trend: 'UP' },
    { symbol: 'QQQ', name: 'NASDAQ 100', price: 389.45, change_pct: -0.32, trend: 'DOWN' },
    { symbol: 'IWM', name: 'Russell 2000', price: 189.23, change_pct: 1.45, trend: 'UP' },
    { symbol: 'DIA', name: 'Dow Jones', price: 34567.89, change_pct: 0.67, trend: 'UP' },
  ];

  const mockSignals: SignalData[] = [
    { symbol: 'AAPL', signal_type: 'BUY', confidence_score: 85, timestamp: '2024-01-15T10:30:00Z' },
    { symbol: 'GOOGL', signal_type: 'SELL', confidence_score: 78, timestamp: '2024-01-15T09:45:00Z' },
    { symbol: 'TSLA', signal_type: 'HOLD', confidence_score: 72, timestamp: '2024-01-15T08:15:00Z' },
    { symbol: 'NVDA', signal_type: 'BUY', confidence_score: 91, timestamp: '2024-01-15T07:30:00Z' },
  ];

  const mockChartData = [
    { time: '09:00', value: 100 },
    { time: '10:00', value: 102 },
    { time: '11:00', value: 98 },
    { time: '12:00', value: 105 },
    { time: '13:00', value: 103 },
    { time: '14:00', value: 107 },
    { time: '15:00', value: 106 },
    { time: '16:00', value: 108 },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setMarketData(mockMarketData);
      setSignals(mockSignals);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLastUpdate(new Date());
      setLoading(false);
    }, 1000);
  };

  const getTrendColor = (trend: string) => {
    return trend === 'UP' ? 'success' : trend === 'DOWN' ? 'error' : 'warning';
  };

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      case 'HOLD': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Market overview and trading insights
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Refresh Data
          </Button>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>

      {/* Market Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Market Overview
          </Typography>
        </Grid>
        {marketData.map((market) => (
          <Grid item xs={12} sm={6} md={3} key={market.symbol}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="h6" component="div">
                    {market.symbol}
                  </Typography>
                  <Chip
                    label={market.trend}
                    color={getTrendColor(market.trend) as any}
                    size="small"
                    icon={market.trend === 'UP' ? <TrendingUp /> : <TrendingDown />}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {market.name}
                </Typography>
                <Typography variant="h5" component="div" sx={{ mb: 1 }}>
                  ${market.price.toLocaleString()}
                </Typography>
                <Typography
                  variant="body2"
                  color={market.change_pct >= 0 ? 'success.main' : 'error.main'}
                  sx={{ fontWeight: 'bold' }}
                >
                  {market.change_pct >= 0 ? '+' : ''}{market.change_pct}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Signals */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recent Trading Signals
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<ViewIcon />}
                >
                  View All
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {signals.map((signal, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      borderRadius: 1,
                      backgroundColor: 'action.hover',
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {signal.symbol}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(signal.timestamp).toLocaleString()}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Chip
                        label={signal.signal_type}
                        color={getSignalColor(signal.signal_type) as any}
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary">
                        {signal.confidence_score}% confidence
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Portfolio Performance
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h4" color="success.main" gutterBottom>
                  +12.5%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This month
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Total Value: $125,450
                </Typography>
                <Typography variant="body2" gutterBottom>
                  P&L: +$13,890
                </Typography>
                <Typography variant="body2">
                  Positions: 8
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                fullWidth
                sx={{ mt: 2 }}
              >
                Add Position
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Market Trend Chart */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Trend (Today)
              </Typography>
              <Box sx={{ height: 300, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#00c853"
                      strokeWidth={2}
                      dot={{ fill: '#00c853', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="contained" color="primary">
            Scan Markets
          </Button>
          <Button variant="outlined">
            Generate Signals
          </Button>
          <Button variant="outlined">
            View Analysis
          </Button>
          <Button variant="outlined">
            Portfolio Review
          </Button>
        </Box>
      </Box>

      {/* System Status */}
      <Box sx={{ mt: 4 }}>
        <Alert severity="success" sx={{ mb: 2 }}>
          All systems operational. Market data is being updated in real-time.
        </Alert>
        <Alert severity="info">
          Next market scan scheduled in 2 minutes. Last scan completed successfully.
        </Alert>
      </Box>
    </Box>
  );
};

export default Dashboard;

