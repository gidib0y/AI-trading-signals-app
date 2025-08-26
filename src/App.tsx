import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  CssBaseline,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useTheme,
  useMediaQuery,
  Badge,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  TrendingUp as SignalsIcon,
  Analytics as AnalysisIcon,
  SentimentSatisfied as SentimentIcon,
  AccountBalance as PortfolioIcon,
  Search as ScannerIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

// Import components
import Dashboard from './components/Dashboard';
import MarketScanner from './components/MarketScanner';
import TradingSignals from './components/TradingSignals';
import TechnicalAnalysis from './components/TechnicalAnalysis';
import SentimentAnalysis from './components/SentimentAnalysis';
import Portfolio from './components/Portfolio';

const drawerWidth = 280;

interface AppContentProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const AppContent: React.FC<AppContentProps> = ({ open, setOpen }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Market Scanner', icon: <ScannerIcon />, path: '/scanner' },
    { text: 'Trading Signals', icon: <SignalsIcon />, path: '/signals' },
    { text: 'Technical Analysis', icon: <AnalysisIcon />, path: '/analysis' },
    { text: 'Sentiment Analysis', icon: <SentimentIcon />, path: '/sentiment' },
    { text: 'Portfolio', icon: <PortfolioIcon />, path: '/portfolio' },
  ];

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      setOpen(false);
    }
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  const drawer = (
    <Box sx={{ width: drawerWidth }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          📈 Trading Signals Pro
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Advanced Market Analysis
        </Typography>
      </Box>
      
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => handleNavigation(item.path)}
            sx={{
              mb: 1,
              mx: 1,
              borderRadius: 2,
              backgroundColor: isActiveRoute(item.path) ? 'primary.main' : 'transparent',
              color: isActiveRoute(item.path) ? 'white' : 'text.primary',
              '&:hover': {
                backgroundColor: isActiveRoute(item.path) ? 'primary.dark' : 'action.hover',
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      
      <Box sx={{ position: 'absolute', bottom: 0, width: '100%', p: 2 }}>
        <Chip
          label="Live Market Data"
          color="success"
          size="small"
          sx={{ width: '100%' }}
        />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'background.paper',
          color: 'text.primary',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard'}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label="Market Open"
              color="success"
              size="small"
              variant="outlined"
            />
            <IconButton color="inherit" size="large">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit" size="large">
              <SettingsIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      
      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={open}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              backgroundColor: 'background.paper',
              borderRight: 1,
              borderColor: 'divider',
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
        }}
      >
        <Container maxWidth="xl">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scanner" element={<MarketScanner />} />
            <Route path="/signals" element={<TradingSignals />} />
            <Route path="/analysis" element={<TechnicalAnalysis />} />
            <Route path="/sentiment" element={<SentimentAnalysis />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

const App: React.FC = () => {
  const [open, setOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    if (!isMobile) {
      setOpen(true);
    }
  }, [isMobile]);

  return (
    <Router>
      <AppContent open={open} setOpen={setOpen} />
    </Router>
  );
};

export default App;

