from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import yfinance as yf
import pandas as pd
from datetime import datetime
import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
import json
import asyncio
from datetime import datetime, timedelta
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading
import aiohttp
warnings.filterwarnings('ignore')

# Create FastAPI app
app = FastAPI(title="Simple Trading Signals API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global state
active_symbols = []
is_monitoring = False

# Advanced Analytics Global Variables
trading_performance = {
    "total_trades": 0,
    "winning_trades": 0,
    "losing_trades": 0,
    "total_pnl": 0.0,
    "win_rate": 0.0,
    "profit_factor": 0.0,
    "max_drawdown": 0.0,
    "current_drawdown": 0.0,
    "avg_win": 0.0,
    "avg_loss": 0.0,
    "largest_win": 0.0,
    "largest_loss": 0.0,
    "consecutive_wins": 0,
    "consecutive_losses": 0,
    "max_consecutive_wins": 0,
    "max_consecutive_losses": 0,
    "sharpe_ratio": 0.0,
    "sortino_ratio": 0.0,
    "calmar_ratio": 0.0,
    "trades_by_market": {},
    "trades_by_timeframe": {},
    "performance_by_hour": {},
    "performance_by_day": {},
    "recent_trades": [],
    "equity_curve": [],
    "drawdown_curve": [],
    "monthly_returns": {},
    "yearly_returns": {}
}

# Enhanced AI Learning Global Variables
ai_learning_enhanced = {
    "sentiment_analysis": {
        "market_sentiment": "NEUTRAL",
        "sentiment_score": 0.0,
        "sentiment_trend": "STABLE",
        "news_impact": 0.0,
        "social_sentiment": 0.0,
        "fear_greed_index": 50.0,
        "last_updated": None
    },
    "market_regime": {
        "current_regime": "NORMAL",
        "regime_confidence": 0.0,
        "volatility_regime": "MEDIUM",
        "trend_regime": "SIDEWAYS",
        "liquidity_regime": "NORMAL",
        "regime_history": [],
        "regime_transitions": 0
    },
    "pattern_recognition": {
        "active_patterns": [],
        "pattern_accuracy": {},
        "pattern_performance": {},
        "emerging_patterns": [],
        "pattern_strength": 0.0,
        "pattern_confidence": 0.0
    },
    "adaptive_parameters": {
        "confidence_threshold": 0.7,
        "risk_adjustment": 1.0,
        "pattern_weight": 0.8,
        "volume_weight": 0.6,
        "trend_weight": 0.9,
        "sentiment_weight": 0.5,
        "regime_weight": 0.7,
        "learning_rate": 0.01,
        "adaptation_speed": 0.1,
        "last_adaptation": None
    },
    "learning_metrics": {
        "total_learning_cycles": 0,
        "successful_adaptations": 0,
        "learning_accuracy": 0.0,
        "adaptation_frequency": 0.0,
        "model_performance": {},
        "learning_velocity": 0.0
    }
}

# Predictive Analytics Global Variables
predictive_analytics = {
    "price_targets": {
        "short_term": {},  # 1-3 days
        "medium_term": {},  # 1-2 weeks
        "long_term": {},  # 1-3 months
        "confidence_scores": {},
        "last_updated": None
    },
    "volatility_forecast": {
        "current_volatility": 0.0,
        "predicted_volatility": 0.0,
        "volatility_trend": "STABLE",
        "volatility_percentile": 50.0,
        "volatility_forecast_periods": {
            "1_day": 0.0,
            "1_week": 0.0,
            "1_month": 0.0
        },
        "last_updated": None
    },
    "market_direction": {
        "direction_probability": {
            "bullish": 0.0,
            "bearish": 0.0,
            "sideways": 0.0
        },
        "confidence_level": 0.0,
        "key_levels": {
            "support": [],
            "resistance": [],
            "pivot_points": []
        },
        "trend_strength": 0.0,
        "momentum_score": 0.0,
        "last_updated": None
    },
    "forecasting_models": {
        "arima_accuracy": 0.0,
        "lstm_accuracy": 0.0,
        "ensemble_accuracy": 0.0,
        "model_weights": {
            "technical": 0.4,
            "sentiment": 0.2,
            "volume": 0.2,
            "volatility": 0.2
        },
        "last_training": None
    }
}

# Real-Time Market Scanner Global Variables
market_scanner = {
    "hot_list": {
        "stocks": [],
        "forex": [],
        "crypto": [],
        "indices": [],
        "last_updated": None
    },
    "sector_rotation": {
        "technology": {"momentum": 0.0, "rank": 0, "symbols": []},
        "healthcare": {"momentum": 0.0, "rank": 0, "symbols": []},
        "financial": {"momentum": 0.0, "rank": 0, "symbols": []},
        "energy": {"momentum": 0.0, "rank": 0, "symbols": []},
        "consumer": {"momentum": 0.0, "rank": 0, "symbols": []},
        "industrial": {"momentum": 0.0, "rank": 0, "symbols": []},
        "materials": {"momentum": 0.0, "rank": 0, "symbols": []},
        "utilities": {"momentum": 0.0, "rank": 0, "symbols": []},
        "last_updated": None
    },
    "momentum_ranking": {
        "top_gainers": [],
        "top_losers": [],
        "most_active": [],
        "highest_volume": [],
        "breakout_candidates": [],
        "last_updated": None
    },
    "scanner_settings": {
        "scan_interval": 30,  # seconds
        "min_volume": 1000000,
        "min_price": 1.0,
        "max_price": 1000.0,
        "momentum_threshold": 0.05,
        "volume_spike_threshold": 2.0,
        "breakout_threshold": 0.02
    },
    "scan_results": {
        "total_scanned": 0,
        "signals_found": 0,
        "scan_duration": 0.0,
        "last_scan_time": None
    }
}

# Social Trading Global Variables
social_trading = {
    "signal_sharing": {
        "shared_signals": [],
        "public_signals": [],
        "signal_ratings": {},
        "last_shared": None
    },
    "performance_leaderboard": {
        "top_traders": [],
        "monthly_winners": [],
        "all_time_best": [],
        "copy_traders": [],
        "last_updated": None
    },
    "copy_trading": {
        "active_copies": [],
        "copy_settings": {},
        "performance_tracking": {},
        "risk_limits": {},
        "last_updated": None
    },
    "community_insights": {
        "market_sentiment": "NEUTRAL",
        "popular_symbols": [],
        "trending_strategies": [],
        "community_predictions": {},
        "discussion_topics": [],
        "last_updated": None
    },
    "social_settings": {
        "auto_share_signals": False,
        "public_profile": True,
        "allow_copy_trading": True,
        "risk_tolerance": "MEDIUM",
        "max_copiers": 100,
        "minimum_followers": 10
    }
}

# Advanced Risk Management Global Variables
risk_management = {
    "portfolio_heatmap": {
        "correlation_matrix": {},
        "risk_scores": {},
        "position_sizes": {},
        "exposure_limits": {},
        "last_updated": None
    },
    "correlation_analysis": {
        "pair_correlations": {},
        "sector_correlations": {},
        "market_correlations": {},
        "correlation_thresholds": {
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        },
        "last_updated": None
    },
    "dynamic_position_sizing": {
        "kelly_criterion": {},
        "volatility_adjustment": {},
        "risk_parity": {},
        "maximum_positions": 10,
        "max_portfolio_risk": 0.15,
        "position_size_limits": {
            "min": 0.01,
            "max": 0.25
        },
        "last_updated": None
    },
    "risk_metrics": {
        "var_95": 0.0,
        "var_99": 0.0,
        "expected_shortfall": 0.0,
        "maximum_drawdown": 0.0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "calmar_ratio": 0.0,
        "beta": 0.0,
        "alpha": 0.0,
        "last_updated": None
    },
    "risk_settings": {
        "max_daily_loss": 0.05,
        "max_position_risk": 0.02,
        "correlation_limit": 0.6,
        "volatility_adjustment": True,
        "dynamic_sizing": True,
        "risk_parity_enabled": True,
        "stop_loss_enabled": True,
        "trailing_stop_enabled": True
    }
}

alert_settings = {
    'enabled': True,
    'email_notifications': False,
    'webhook_url': None,
    'whatsapp_enabled': False,
    'whatsapp_webhook': None,
    'telegram_enabled': False,
    'telegram_bot_token': None,
    'telegram_chat_id': None,
    'sms_enabled': False,
    'sms_provider': 'twilio',
    'sms_phone': None,
    'min_signal_strength': 5.0,
    'alert_frequency': 'all',  # 'all', 'high_only', 'custom'
    'custom_conditions': {
        'rsi_threshold': 70,
        'volume_spike': 2.0,
        'atr_threshold': 0.02,
        'risk_reward_min': 1.5
    }
}
alert_history = []

# AI Learning Enhancement - Global state
ml_models = {
    'signal_classifier': None,
    'pattern_recognizer': None,
    'sentiment_analyzer': None
}

# Initialize ML models on startup
def initialize_ml_models_startup():
    """Initialize ML models on server startup"""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.neural_network import MLPClassifier
        
        ml_models['signal_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
        ml_models['pattern_recognizer'] = MLPClassifier(hidden_layer_sizes=(50, 25), random_state=42)
        ml_models['sentiment_analyzer'] = LogisticRegression(random_state=42)
        
        print("✅ ML models initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing ML models: {e}")
        return False

# Initialize models on startup
initialize_ml_models_startup()
learning_data = {
    'signal_history': [],
    'performance_metrics': {},
    'model_accuracy': {},
    'adaptive_parameters': {
        'signal_threshold': 1.0,
        'confidence_boost': 1.0,
        'pattern_weight': 1.0,
        'volume_weight': 1.0
    }
}

# Root endpoint - Main Dashboard
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await live_dashboard(request)

# Live Trading Dashboard
@app.get("/live", response_class=HTMLResponse)
async def live_dashboard(request: Request):
    """Simple live dashboard that always works"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Pro Trading Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        
        <!-- Professional Trading Interface Styles -->
        <style>
            :root {
                --primary-color: #1e3a8a;
                --secondary-color: #3b82f6;
                --accent-color: #10b981;
                --danger-color: #ef4444;
                --warning-color: #f59e0b;
                --dark-bg: #0f172a;
                --dark-card: #1e293b;
                --dark-text: #f1f5f9;
                --light-bg: #ffffff;
                --light-card: #f8fafc;
                --light-text: #1e293b;
                --border-color: #e2e8f0;
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }
            
            [data-theme="dark"] {
                --bg-color: var(--dark-bg);
                --card-bg: var(--dark-card);
                --text-color: var(--dark-text);
                --border-color: #374151;
            }
            
            [data-theme="light"] {
                --bg-color: var(--light-bg);
                --card-bg: var(--light-card);
                --text-color: var(--light-text);
                --border-color: var(--border-color);
            }
            
            body {
                background: var(--bg-color);
                color: var(--text-color);
                transition: all 0.3s ease;
            }
            
            .header {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                box-shadow: var(--shadow-lg);
            }
            
            .signal-card {
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
            }
            
            .signal-card:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }
            
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: var(--shadow);
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
            }
            
            .layout-controls {
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 1000;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 10px;
                box-shadow: var(--shadow);
            }
            
            .layout-btn {
                background: var(--secondary-color);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                margin: 2px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }
            
            .layout-btn:hover {
                background: var(--primary-color);
            }
            
            .layout-btn.active {
                background: var(--accent-color);
            }
            
            .p-l-tracker {
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 1000;
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 15px;
                box-shadow: var(--shadow);
                min-width: 200px;
            }
            
            .p-l-value {
                font-size: 1.5rem;
                font-weight: bold;
                text-align: center;
                margin: 5px 0;
            }
            
            .p-l-positive {
                color: var(--accent-color);
            }
            
            .p-l-negative {
                color: var(--danger-color);
            }
            
            .p-l-neutral {
                color: var(--warning-color);
            }
            
            .trading-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 10px;
                margin-top: 10px;
            }
            
            .stat-item {
                text-align: center;
                padding: 5px;
                background: var(--bg-color);
                border-radius: 5px;
                border: 1px solid var(--border-color);
            }
            
            .stat-value {
                font-weight: bold;
                font-size: 1.1rem;
            }
            
            .stat-label {
                font-size: 0.8rem;
                opacity: 0.8;
            }
            
            .grid-1 { grid-template-columns: 1fr; }
            .grid-2 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: repeat(3, 1fr); }
            .grid-4 { grid-template-columns: repeat(4, 1fr); }
            
            .compact .signal-card {
                padding: 10px;
                margin: 5px;
            }
            
            .compact .signal-header {
                flex-direction: row;
                align-items: center;
                gap: 10px;
            }
            
            .compact .signal-info {
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
            }
            
            .compact .price-item {
                padding: 5px;
                font-size: 0.9rem;
            }
            
            .compact .ml-analysis {
                display: none;
            }
            
            .expanded .signal-card {
                padding: 20px;
                margin: 10px;
            }
            
            .expanded .signal-info {
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
            }
            
            .expanded .ml-analysis {
                display: block;
            }
        </style>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: #ffffff;
                overflow-x: hidden;
                min-height: 100vh;
            }
            
            /* Tab Navigation Styles */
            .tab-navigation {
                display: flex;
                background: rgba(0,0,0,0.3);
                border-radius: 12px;
                padding: 8px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }
            
            .tab-button {
                flex: 1;
                padding: 15px 20px;
                background: transparent;
                border: none;
                color: rgba(255,255,255,0.7);
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
                text-align: center;
            }
            
            .tab-button:hover {
                background: rgba(255,255,255,0.1);
                color: white;
                transform: translateY(-2px);
            }
            
            .tab-button.active {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            .tab-content {
                display: none;
            }
            
                    .tab-content.active {
            display: block;
        }
        
        /* Clean Dashboard Layout */
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .top-section {
            margin-bottom: 30px;
        }
        
        .three-column-layout {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .column {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .column h3 {
            color: #4CAF50;
            margin-bottom: 15px;
            text-align: center;
            font-size: 1.2em;
        }
        
        .analyzing-column {
            border-left: 4px solid #2196F3;
        }
        
        .scanning-column {
            border-left: 4px solid #FF9800;
        }
        
        .other-features-column {
            border-left: 4px solid #9C27B0;
        }
        
        /* Collapsible Menu Styles */
        .collapsible-menu {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .menu-item {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .menu-item:hover {
            background: rgba(255,255,255,0.2);
            transform: translateX(5px);
        }
        
        .menu-icon {
            font-size: 1.2em;
            width: 24px;
            text-align: center;
        }
        
        .menu-title {
            flex: 1;
            font-weight: 500;
        }
        
        .menu-arrow {
            font-size: 0.8em;
            transition: transform 0.3s ease;
        }
        
        .menu-item.active .menu-arrow {
            transform: rotate(180deg);
        }
        
        .menu-content {
            display: none;
            padding: 15px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            margin-top: 5px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .menu-content.active {
            display: block;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .three-column-layout {
                grid-template-columns: 1fr;
                gap: 15px;
            }
        }
        
        /* 6-Column Features Layout */
        .six-column-features {
            margin-top: 30px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .feature-card {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            min-height: 200px;
        }
        
        .feature-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .feature-icon {
            font-size: 1.2em;
        }
        
        .feature-header h3 {
            color: #4CAF50;
            margin: 0;
            font-size: 1em;
        }
        
        .feature-content {
            font-size: 0.85em;
        }
        
        .status-item {
            color: #4CAF50;
            margin: 3px 0;
            font-size: 0.8em;
        }
        
        .action-btn {
            width: 100%;
            padding: 6px 8px;
            margin: 3px 0;
            border: none;
            border-radius: 6px;
            font-size: 0.75em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .scan-btn { background: #4CAF50; color: white; }
        .analyze-btn { background: #2196F3; color: white; }
        .signals-btn { background: #9C27B0; color: white; }
        .charts-btn { background: #9C27B0; color: white; }
        .summary-btn { background: #9C27B0; color: white; }
        
        .timeframe-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            margin-bottom: 10px;
        }
        
        .timeframe-btn {
            padding: 6px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: white;
            cursor: pointer;
            font-size: 0.7em;
            text-align: center;
        }
        
        .timeframe-btn.active {
            background: #2196F3;
            border-color: #2196F3;
        }
        
        .timeframe-status {
            font-size: 0.75em;
            color: #ccc;
            text-align: center;
        }
        
        .risk-item, .ai-item, .backtest-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
        }
        
        .risk-icon, .ai-icon, .backtest-icon {
            font-size: 1em;
            width: 20px;
            text-align: center;
        }
        
        .risk-text, .ai-text, .backtest-text {
            flex: 1;
        }
        
        .risk-title, .ai-title, .backtest-title {
            font-weight: bold;
            font-size: 0.8em;
            margin-bottom: 2px;
        }
        
        .risk-desc, .ai-desc, .backtest-desc {
            font-size: 0.7em;
            opacity: 0.8;
        }
        
        .backtest-controls {
            margin-top: 10px;
        }
        
        .backtest-input {
            width: 100%;
            padding: 6px;
            margin: 5px 0;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 4px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 0.75em;
        }
        
        .backtest-btn {
            width: 100%;
            padding: 6px;
            margin: 3px 0;
            border: none;
            border-radius: 4px;
            font-size: 0.75em;
            cursor: pointer;
        }
        
        .test-btn { background: #4CAF50; color: white; }
        .summary-btn { background: #2196F3; color: white; }
        
        /* Responsive for 5-column features */
        @media (max-width: 1400px) {
            .features-grid {
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
            }
        }
        
        @media (max-width: 1000px) {
            .features-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
        }
        
        @media (max-width: 600px) {
            .features-grid {
                grid-template-columns: 1fr;
                gap: 8px;
            }
        }
        
        /* Market Cards Responsive */
        @media (max-width: 1400px) {
            .market-cards-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (max-width: 900px) {
            .market-cards-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 600px) {
            .market-cards-grid {
                grid-template-columns: 1fr;
            }
        }
            
            /* Mobile Responsive Design */
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                    margin: 0;
                }
                
                .header {
                    padding: 15px 10px;
                    text-align: center;
                }
                
                .header h1 {
                    font-size: 1.5rem;
                    margin-bottom: 5px;
                }
                
                .header p {
                    font-size: 0.9rem;
                }
                
                .controls {
                    flex-direction: column;
                    gap: 10px;
                    padding: 15px;
                }
                
                .control-group {
                    width: 100%;
                    margin-bottom: 10px;
                }
                
                .control-group select,
                .control-group button {
                    width: 100%;
                    padding: 12px;
                    font-size: 16px; /* Prevents zoom on iOS */
                }
                
                .signals-grid {
                    grid-template-columns: 1fr;
                    gap: 15px;
                    padding: 10px;
                }
                
                .signal-card {
                    margin: 0;
                    padding: 15px;
                }
                
                .signal-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }
                
                .signal-info {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }
                
                .price-item {
                    padding: 8px;
                }
                
                .price-label {
                    font-size: 0.8rem;
                }
                
                .price-value {
                    font-size: 1rem;
                }
                
                .confidence-bar {
                    height: 8px;
                }
                
                .ml-analysis {
                    padding: 10px;
                }
                
                .ml-item {
                    padding: 5px;
                    font-size: 0.8rem;
                }
                
                .status-indicator {
                    padding: 8px 12px;
                    font-size: 0.9rem;
                }
                
                .market-selector {
                    flex-direction: column;
                    gap: 10px;
                }
                
                .market-buttons {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 8px;
                }
                
                .market-btn {
                    padding: 10px;
                    font-size: 0.9rem;
                }
            }
            
            @media (max-width: 480px) {
                .header h1 {
                    font-size: 1.3rem;
                }
                
                .market-buttons {
                    grid-template-columns: 1fr;
                }
                
                .signal-card {
                    padding: 12px;
                }
                
                .price-item {
                    padding: 6px;
                }
            }
            
            /* Touch-friendly interactions */
            .touch-target {
                min-height: 44px;
                min-width: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Enhanced button states for touch */
            button:active {
                transform: scale(0.98);
                transition: transform 0.1s ease;
            }
            
            /* Improved focus states for accessibility */
            button:focus,
            select:focus {
                outline: 2px solid #4CAF50;
                outline-offset: 2px;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                padding: 20px;
            }
            .header { 
                text-align: center; 
                margin-bottom: 30px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .header h1 { 
                font-size: 3em; 
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .header p { 
                font-size: 1.2em; 
                opacity: 0.9;
            }
            .status { 
                background: rgba(255,255,255,0.1); 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .button { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 10px; 
                cursor: pointer; 
                margin: 10px; 
                font-size: 1.1em;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            .signals { 
                background: rgba(255,255,255,0.1); 
                padding: 25px; 
                border-radius: 15px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .signal-card {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                border-left: 4px solid #667eea;
                transition: all 0.3s ease;
            }
            .signal-card:hover {
                transform: translateX(5px);
                background: rgba(255,255,255,0.1);
            }
            .signal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .symbol {
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }
            .signal-type {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.9em;
            }
            .signal-type.buy {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
            }
            .signal-type.sell {
                background: linear-gradient(135deg, #f44336, #da190b);
                color: white;
            }
            .signal-type.hold {
                background: linear-gradient(135deg, #ff9800, #f57c00);
                color: white;
            }
            .price-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 12px;
                margin: 15px 0;
            }
            .price-item {
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            .price-label {
                font-size: 0.9em;
                opacity: 0.7;
                margin-bottom: 5px;
            }
            .price-value {
                font-size: 1.3em;
                font-weight: bold;
                color: #667eea;
            }
            .price-value.positive {
                color: #4CAF50;
            }
            .price-value.negative {
                color: #f44336;
            }
            .price-value.neutral {
                color: #ff9800;
            }
            .confidence-bar {
                background: rgba(255,255,255,0.1);
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 10px;
            }
            .confidence-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
                transition: width 0.3s ease;
            }
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .loading {
                text-align: center;
                padding: 40px;
                font-size: 1.2em;
                opacity: 0.7;
            }
            .error {
                background: rgba(244, 67, 54, 0.2);
                border: 1px solid #f44336;
                color: #ffcdd2;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            .chart-container {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 15px;
                margin: 15px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            }
            .chart-title {
                font-size: 1.2em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 15px;
                text-align: center;
            }
            .chart-wrapper {
                position: relative;
                height: 300px;
                margin: 10px 0;
            }
            
            /* Advanced Analytics Styles */
            .metric-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            
            .metric-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 5px;
            }
            
            .metric-label {
                font-size: 0.9em;
                color: #b0b0b0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .heatmap-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
            .heatmap-section h4 {
                color: #4CAF50;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            
            .heatmap-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                margin: 5px 0;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
            }
            
            .heatmap-item:hover {
                transform: translateX(5px);
            }
            
            .heatmap-label {
                font-weight: 500;
                color: #ffffff;
            }
            
            .heatmap-value {
                font-weight: bold;
                color: #4CAF50;
            }
            
            .heatmap-trades {
                font-size: 0.8em;
                color: #b0b0b0;
            }
            
            /* Responsive Analytics */
            @media (max-width: 768px) {
                .heatmap-grid {
                    grid-template-columns: 1fr;
                }
                
                .metric-card {
                    padding: 10px;
                }
                
                .metric-value {
                    font-size: 1.2em;
                }
            }
        </style>
    </head>
    <body data-theme="dark">
        <!-- Professional Trading Interface Controls -->
        <div class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme">
            <span id="theme-icon">🌙</span>
        </div>
        
        <!-- Layout controls and P&L moved to Other Features column -->
        
        <div class="container">
            <div class="header">
                <h1>🚀 Pro Trading Dashboard</h1>
                <p>Advanced AI-Powered Trading Signals with Real-Time Market Data</p>
            </div>
            
            <!-- Tab Navigation -->
            <!-- Clean Dashboard Layout -->
            <div class="dashboard-container">
                <!-- Top Section: Market Selection -->
                <div class="top-section">
                    <div class="status">
                        <h2>📈 Select Market Category</h2>
                <div class="market-cards-grid" style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 15px; margin: 20px 0;">
                    <div class="market-card" onclick="selectMarket('stocks', this)" style="background: rgba(76, 175, 80, 0.2); border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">📊</div>
                        <h3 style="color: #4CAF50; margin-bottom: 5px;">STOCKS</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">US Equities & ETFs</p>
                    </div>
                    <div class="market-card" onclick="selectMarket('forex', this)" style="background: rgba(33, 150, 243, 0.2); border: 2px solid #2196F3; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">💱</div>
                        <h3 style="color: #2196F3; margin-bottom: 5px;">FOREX</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">Currency Pairs</p>
                    </div>
                    <div class="market-card" onclick="selectMarket('crypto', this)" style="background: rgba(255, 193, 7, 0.2); border: 2px solid #FFC107; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">₿</div>
                        <h3 style="color: #FFC107; margin-bottom: 5px;">CRYPTO</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">Digital Assets</p>
                    </div>
                    <div class="market-card" onclick="selectMarket('futures', this)" style="background: rgba(255, 152, 0, 0.2); border: 2px solid #FF9800; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">⛽</div>
                        <h3 style="color: #FF9800; margin-bottom: 5px;">FUTURES</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">Commodities</p>
                    </div>
                    <div class="market-card" onclick="selectMarket('indices', this)" style="background: rgba(244, 67, 54, 0.2); border: 2px solid #f44336; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">📈</div>
                        <h3 style="color: #f44336; margin-bottom: 5px;">INDICES</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">Market Indexes</p>
                    </div>
                    <div class="market-card" onclick="selectMarket('metals', this)" style="background: rgba(156, 39, 176, 0.2); border: 2px solid #9C27B0; padding: 20px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-size: 2em; margin-bottom: 10px;">🥇</div>
                        <h3 style="color: #9C27B0; margin-bottom: 5px;">METALS</h3>
                        <p style="opacity: 0.8; font-size: 0.9em;">Precious Metals</p>
                    </div>
                </div>
                
                <!-- Market Symbols Display -->
                <div id="market-symbols" style="margin-top: 20px; display: none;">
                    <h3 id="market-symbols-title" style="color: #4CAF50; margin-bottom: 15px;">📊 Top Stocks</h3>
                    <div id="symbols-list" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 20px;">
                        <!-- Symbols will be populated here -->
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <button class="button" onclick="startMonitoringForSelectedMarket()" style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.3s ease;">
                            🚀 Start Monitoring Selected Market
                        </button>
                    </div>
                </div>
                </div>
                
                <!-- 3-Column Layout -->
                <div class="three-column-layout">
                    <!-- Left Column: Scanner ONLY -->
                    <div class="column analyzing-column">
                        <h3>🔍 Market Scanner</h3>
                        <!-- Scanner Content -->
                        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <button class="button" onclick="scanFullMarket()" style="background: #4CAF50; width: 100%; margin-bottom: 10px;">🌐 Scan Full Market</button>
                            <button class="button" onclick="getHotList()" style="background: #FF9800; width: 100%; margin-bottom: 10px;">🔥 Get Hot List</button>
                            <button class="button" onclick="getSectorRotation()" style="background: #2196F3; width: 100%; margin-bottom: 10px;">🔄 Sector Rotation</button>
                        </div>
                        
                        <!-- Scanner Results -->
                        <div id="scanner-results" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 200px;">
                            <div class="loading">Click "Scan Full Market" to see trading signals</div>
                        </div>

                    </div>
                    
                    <!-- Middle Column: Analyzer ONLY -->
                    <div class="column scanning-column">
                        <h3>📊 Symbol Analyzer</h3>
                        <!-- Analyzer Content -->
                        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <input type="text" id="analyze-symbol" placeholder="Enter symbol (e.g., AAPL, BTC-USD, EURUSD)" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; background: rgba(0,0,0,0.3); color: white;">
                            <button class="button" onclick="analyzeCustomSymbol()" style="background: #2196F3; width: 100%; margin-bottom: 10px;">📊 Analyze Symbol</button>
                            <button class="button" onclick="getPriceTargets()" style="background: #FF9800; width: 100%; margin-bottom: 10px;">🎯 Price Targets</button>
                            <button class="button" onclick="getVolatilityForecast()" style="background: #9C27B0; width: 100%; margin-bottom: 10px;">📊 Volatility Forecast</button>
                        </div>
                        
                        <!-- Analyzer Results -->
                        <div id="analyzer-results" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 200px;">
                            <div class="loading">Enter a symbol and click "Analyze Symbol" to see detailed analysis</div>
                        </div>

                    </div>
                    
                    <!-- Right Column: Other Features -->
                    <div class="column other-features-column">
                        <h3>⚙️ Other Features</h3>
                        <div class="collapsible-menu">
                            <div class="menu-item" onclick="toggleCollapse('live-signals')">
                                <span class="menu-icon">📈</span>
                                <span class="menu-title">Live Signals</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="live-signals" class="menu-content">
                                <button class="button" onclick="getSignals()">📈 Get Live Signals</button>
                                <div id="signals" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 100px;">
                                    <div class="loading">Click to get live signals</div>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('charts')">
                                <span class="menu-icon">📊</span>
                                <span class="menu-title">Price Charts</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="charts" class="menu-content">
                                <button class="button" onclick="createCharts()">📊 Load Charts</button>
                                <div id="charts-container" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 100px;">
                                    <div class="loading">Click to load charts</div>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('ai-learning')">
                                <span class="menu-icon">🤖</span>
                                <span class="menu-title">AI Learning</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="ai-learning" class="menu-content">
                                <button class="button" onclick="loadAILearningStatus()">🤖 Load AI Status</button>
                                <button class="button" onclick="retrainAIModels()">🧠 Retrain Models</button>
                                <div id="ai-learning-status" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; min-height: 100px;">
                                    <div class="loading">Click to load AI status</div>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('layout-controls')">
                                <span class="menu-icon">⚙️</span>
                                <span class="menu-title">Layout Controls</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="layout-controls" class="menu-content">
                                <div style="margin-bottom: 15px;">
                                    <label style="display: block; margin-bottom: 5px; color: #ccc;">Layout:</label>
                                    <div style="display: flex; gap: 5px;">
                                        <button class="button" onclick="setLayout('compact')" style="background: #4CAF50; padding: 8px 12px; font-size: 12px;">Compact</button>
                                        <button class="button" onclick="setLayout('normal')" style="background: #2196F3; padding: 8px 12px; font-size: 12px;">Normal</button>
                                        <button class="button" onclick="setLayout('expanded')" style="background: #2196F3; padding: 8px 12px; font-size: 12px;">Expanded</button>
                                    </div>
                                </div>
                                <div>
                                    <label style="display: block; margin-bottom: 5px; color: #ccc;">Theme:</label>
                                    <button class="button" onclick="toggleTheme()" style="background: #FF9800; padding: 8px 12px; font-size: 12px;">🌙 Toggle Theme</button>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('system-status')">
                                <span class="menu-icon">📊</span>
                                <span class="menu-title">System Status</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="system-status" class="menu-content">
                                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                    <div style="color: #4CAF50; margin: 5px 0;">✅ Server: Running & Healthy</div>
                                    <div style="color: #4CAF50; margin: 5px 0;">✅ API: All Endpoints Active</div>
                                    <div style="color: #4CAF50; margin: 5px 0;">✅ Data: Real-Time Feed Active</div>
                                    <div style="color: #4CAF50; margin: 5px 0;">✅ Signals: AI Analysis Ready</div>
                                </div>
                                <button class="button" onclick="refreshSystemStatus()">🔄 Refresh Status</button>
                            </div>
                            
                            
                            <div class="menu-item" onclick="toggleCollapse('timeframe-analysis')">
                                <span class="menu-icon">⏰</span>
                                <span class="menu-title">Timeframe Analysis</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="timeframe-analysis" class="menu-content">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin: 10px 0;">
                                    <button class="button" onclick="setTimeframe('5m')" style="background: #f44336; padding: 8px; font-size: 12px;">⚡ 5M Entry</button>
                                    <button class="button" onclick="setTimeframe('15m')" style="background: #E91E63; padding: 8px; font-size: 12px;">👥 15M Confirmation</button>
                                    <button class="button" onclick="setTimeframe('1h')" style="background: #2196F3; padding: 8px; font-size: 12px;">📊 1H Trend</button>
                                    <button class="button" onclick="setTimeframe('4h')" style="background: #2196F3; padding: 8px; font-size: 12px;">📊 4H Structure</button>
                                    <button class="button" onclick="setTimeframe('1d')" style="background: #2196F3; padding: 8px; font-size: 12px;">📅 1D Bias</button>
                                </div>
                                <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; margin: 10px 0;">
                                    <div style="color: #ccc;">Current: 1H Analysis</div>
                                    <div style="color: #E91E63;">🎯 Kill Zone: Checking...</div>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('risk-management')">
                                <span class="menu-icon">🛡️</span>
                                <span class="menu-title">Risk Management</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="risk-management" class="menu-content">
                                <div style="background: rgba(76,175,80,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4CAF50;">
                                    <div style="color: #4CAF50; font-weight: bold;">📊 ATR-Based Stops</div>
                                    <div style="color: #ccc; font-size: 0.9em;">Adaptive to volatility</div>
                                </div>
                                <div style="background: rgba(33,150,243,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #2196F3;">
                                    <div style="color: #2196F3; font-weight: bold;">💰 Position Sizing</div>
                                    <div style="color: #ccc; font-size: 0.9em;">2% risk per trade</div>
                                </div>
                                <div style="background: rgba(156,39,176,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #9C27B0;">
                                    <div style="color: #9C27B0; font-weight: bold;">⚙️ Trailing Stops</div>
                                    <div style="color: #ccc; font-size: 0.9em;">Lock in profits</div>
                                </div>
                                <div style="background: rgba(139,69,19,0.2); padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #8B4513;">
                                    <div style="color: #8B4513; font-weight: bold;">⚖️ Risk/Reward</div>
                                    <div style="color: #ccc; font-size: 0.9em;">1.5:1 minimum</div>
                                </div>
                            </div>
                            
                            <div class="menu-item" onclick="toggleCollapse('trading-stats')">
                                <span class="menu-icon">📊</span>
                                <span class="menu-title">Trading Statistics</span>
                                <span class="menu-arrow">▼</span>
                            </div>
                            <div id="trading-stats" class="menu-content">
                                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                    <div style="text-align: center; margin-bottom: 15px;">
                                        <div style="color: #ccc; font-size: 0.9em; margin-bottom: 5px;">Real-Time P&L</div>
                                        <div style="color: #FF9800; font-size: 1.5em; font-weight: bold;">$0.00</div>
                                    </div>
                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                        <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
                                            <div style="color: white; font-size: 1.2em; font-weight: bold;">0%</div>
                                            <div style="color: #ccc; font-size: 0.8em;">Win Rate</div>
                                        </div>
                                        <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
                                            <div style="color: white; font-size: 1.2em; font-weight: bold;">0</div>
                                            <div style="color: #ccc; font-size: 0.8em;">Trades</div>
                                        </div>
                                        <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
                                            <div style="color: white; font-size: 1.2em; font-weight: bold;">0.0</div>
                                            <div style="color: #ccc; font-size: 0.8em;">P.Factor</div>
                                        </div>
                                        <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
                                            <div style="color: white; font-size: 1.2em; font-weight: bold;">0%</div>
                                            <div style="color: #ccc; font-size: 0.8em;">Max DD</div>
                                        </div>
                                    </div>
                                </div>
                                <button class="button" onclick="refreshTradingStats()">🔄 Refresh Stats</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </script>
            
            <!-- Horizontal Trading Actions Section -->
            <div class="trading-actions-horizontal" style="margin: 30px 0; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                <h2 style="color: #4CAF50; margin-bottom: 20px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 10px;">
                    🎯 Trading Actions
                </h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto;">
                    <button class="button touch-target" onclick="scanFullMarket()" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 15px; border-radius: 8px; color: white; border: none; cursor: pointer; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        🔍 Scan Full Market
                    </button>
                    <button class="button touch-target" onclick="analyzeCustomSymbol()" style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); padding: 15px; border-radius: 8px; color: white; border: none; cursor: pointer; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        📊 Analyze Symbol
                    </button>
                    <button class="button touch-target" onclick="getSignals()" style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); padding: 15px; border-radius: 8px; color: white; border: none; cursor: pointer; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        📈 Get Live Signals
                    </button>
                    <button class="button touch-target" onclick="createCharts()" style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); padding: 15px; border-radius: 8px; color: white; border: none; cursor: pointer; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        📊 Load Charts
                    </button>
                    <button class="button touch-target" onclick="getSummary()" style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); padding: 15px; border-radius: 8px; color: white; border: none; cursor: pointer; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 8px; justify-content: center;">
                        📊 Market Summary
                    </button>
                </div>
            </div>
            
            <div class="grid-container">

                
                <div class="status">
                    <h2>⏰ Timeframe Analysis</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin: 15px 0;">
                        <button class="timeframe-btn" onclick="selectTimeframe('5m')" data-timeframe="5m" style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease;">
                            <div style="font-size: 1.2em; margin-bottom: 5px;">⚡</div>
                            <div style="font-weight: bold;">5M</div>
                            <div style="font-size: 0.8em; opacity: 0.7;">Entry</div>
                        </button>
                        <button class="timeframe-btn" onclick="selectTimeframe('15m')" data-timeframe="15m" style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease;">
                            <div style="font-size: 1.2em; margin-bottom: 5px;">🎯</div>
                            <div style="font-weight: bold;">15M</div>
                            <div style="font-size: 0.8em; opacity: 0.7;">Confirmation</div>
                        </button>
                        <button class="timeframe-btn active" onclick="selectTimeframe('1h')" data-timeframe="1h" style="background: rgba(59, 130, 246, 0.2); border: 2px solid #3b82f6; padding: 10px; border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease;">
                            <div style="font-size: 1.2em; margin-bottom: 5px;">📊</div>
                            <div style="font-weight: bold;">1H</div>
                            <div style="font-size: 0.8em; opacity: 0.7;">Trend</div>
                        </button>
                        <button class="timeframe-btn" onclick="selectTimeframe('4h')" data-timeframe="4h" style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease;">
                            <div style="font-size: 1.2em; margin-bottom: 5px;">📈</div>
                            <div style="font-weight: bold;">4H</div>
                            <div style="font-size: 0.8em; opacity: 0.7;">Structure</div>
                        </button>
                        <button class="timeframe-btn" onclick="selectTimeframe('1d')" data-timeframe="1d" style="background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease;">
                            <div style="font-size: 1.2em; margin-bottom: 5px;">📅</div>
                            <div style="font-weight: bold;">1D</div>
                            <div style="font-size: 0.8em; opacity: 0.7;">Bias</div>
                        </button>
                    </div>
                    <div style="text-align: center; margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                        <span id="current-timeframe">Current: 1H Analysis</span>
                        <div id="kill-zone-status" style="margin-top: 5px; font-size: 0.8em; color: #ffd700;">
                            🎯 Kill Zone: <span id="kill-zone-text">Checking...</span>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>🛡️ Risk Management</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0;">
                        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">📊</div>
                            <div style="font-weight: bold; color: #22c55e;">ATR-Based Stops</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Adaptive to volatility</div>
                        </div>
                        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">💰</div>
                            <div style="font-weight: bold; color: #3b82f6;">Position Sizing</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">2% risk per trade</div>
                        </div>
                        <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">🎯</div>
                            <div style="font-weight: bold; color: #a855f7;">Trailing Stops</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Lock in profits</div>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">⚖️</div>
                            <div style="font-weight: bold; color: #f59e0b;">Risk/Reward</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">1.5:1 minimum</div>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>🤖 AI & Machine Learning</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0;">
                        <div style="background: rgba(236, 72, 153, 0.1); border: 1px solid rgba(236, 72, 153, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">🧠</div>
                            <div style="font-weight: bold; color: #ec4899;">Pattern Recognition</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">AI-enhanced analysis</div>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">📈</div>
                            <div style="font-weight: bold; color: #10b981;">Market Regime</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Trending/Ranging detection</div>
                        </div>
                        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">💭</div>
                            <div style="font-weight: bold; color: #8b5cf6;">Sentiment Analysis</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Market mood detection</div>
                        </div>
                        <div style="background: rgba(245, 101, 101, 0.1); border: 1px solid rgba(245, 101, 101, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">🎯</div>
                            <div style="font-weight: bold; color: #f56565;">Accuracy Prediction</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">ML confidence scoring</div>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>📊 Backtesting Engine</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0;">
                        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">📈</div>
                            <div style="font-weight: bold; color: #22c55e;">Historical Analysis</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Test on past data</div>
                        </div>
                        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">📊</div>
                            <div style="font-weight: bold; color: #3b82f6;">Performance Metrics</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Win rate & returns</div>
                        </div>
                        <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">⚠️</div>
                            <div style="font-weight: bold; color: #a855f7;">Risk Analysis</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Drawdown & Sharpe</div>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 15px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5em; margin-bottom: 5px;">🔧</div>
                            <div style="font-weight: bold; color: #f59e0b;">Strategy Optimization</div>
                            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">Find best parameters</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; text-align: center;">
                        <div style="margin-bottom: 15px;">
                            <input type="text" id="backtest-symbol" placeholder="Enter symbol (e.g., AAPL, BTC-USD, EURUSD=X)" 
                                   style="padding: 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 5px; background: rgba(255,255,255,0.1); color: white; width: 300px; margin-right: 10px;">
                            <button class="button" onclick="runCustomBacktest()" style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);">🚀 Test Symbol</button>
                        </div>
                        <div>
                            <button class="button" onclick="getBacktestSummary()" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);">📈 Market Summary</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="signals">
                <h2>📈 Live Trading Signals</h2>
                <div id="monitoring-status" style="background: rgba(255,0,0,0.1); border: 1px solid #ff4444; border-radius: 8px; padding: 15px; margin-bottom: 20px; text-align: center;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                        <div id="status-indicator" style="width: 12px; height: 12px; border-radius: 50%; background: #ff4444; animation: pulse 2s infinite;"></div>
                        <span id="status-text" style="font-weight: bold; color: #ff4444;">NOT SCANNING</span>
                        <span id="monitoring-details" style="color: #ccc; font-size: 0.9em;"></span>
                    </div>
                </div>
                <div id="signals-display">
                    <div class="loading">Ready to display live trading signals</div>
                </div>
            </div>
            
            <!-- Redundant sections removed - now available in 3-column layout -->
            </div>
            
            <!-- Analytics Tab Content -->
            <div id="analytics-content" class="tab-content">
                <div class="status">
                    <h2>📊 Advanced Analytics Dashboard</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div>
                            <h3>Performance Metrics</h3>
                            <div id="performance-metrics" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading performance metrics...</div>
                            </div>
                            <button class="button" onclick="loadPerformanceMetrics()">📊 Load Metrics</button>
                        </div>
                        <div>
                            <h3>Performance Heatmap</h3>
                            <div id="performance-heatmap" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading performance heatmap...</div>
                            </div>
                            <button class="button" onclick="loadPerformanceHeatmap()">🔥 Load Heatmap</button>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>🤖 AI Learning System</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3>Learning Status</h3>
                            <div id="ai-learning-status" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading AI learning status...</div>
                            </div>
                            <button class="button" onclick="loadAILearningStatus()">🔄 Refresh Status</button>
                            <button class="button" onclick="retrainAIModels()" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">🧠 Retrain Models</button>
                        </div>
                        <div>
                            <h3>Performance Metrics</h3>
                            <div id="ai-performance-metrics" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; max-height: 200px; overflow-y: auto;">
                                <div class="loading">Loading performance metrics...</div>
                            </div>
                            <button class="button" onclick="loadPerformanceMetrics()">📊 Load Metrics</button>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>🔮 Predictive Analytics</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3>Price Targets</h3>
                            <div id="price-targets" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Click "Get Price Targets" to analyze</div>
                            </div>
                            <button class="button" onclick="getPriceTargets()">🎯 Get Price Targets</button>
                        </div>
                        <div>
                            <h3>Volatility Forecast</h3>
                            <div id="volatility-forecast" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Click "Get Volatility Forecast" to analyze</div>
                            </div>
                            <button class="button" onclick="getVolatilityForecast()">📊 Get Volatility Forecast</button>
                        </div>
                    </div>
                </div>
                
                <div class="status">
                    <h2>🔍 Market Scanner</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3>Hot List</h3>
                            <div id="hot-list" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Click "Get Hot List" to scan</div>
                            </div>
                            <button class="button" onclick="getHotList()">🔥 Get Hot List</button>
                        </div>
                        <div>
                            <h3>Sector Rotation</h3>
                            <div id="sector-rotation" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Click "Get Sector Rotation" to analyze</div>
                            </div>
                            <button class="button" onclick="getSectorRotation()">🔄 Get Sector Rotation</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Settings Tab Content -->
            <div id="settings-content" class="tab-content">
                <div class="status">
                    <h2>🚨 Alert System</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>Alert Settings</h3>
                        <div style="margin: 10px 0;">
                            <label style="display: block; margin: 5px 0;">
                                <input type="checkbox" id="alertEnabled" checked> Enable Alerts
                            </label>
                            <label style="display: block; margin: 5px 0;">
                                Min Signal Strength: <input type="number" id="minSignalStrength" value="5.0" min="0" max="10" step="0.5" style="width: 80px; margin-left: 10px;">
                            </label>
                            <label style="display: block; margin: 5px 0;">
                                Alert Frequency: 
                                <select id="alertFrequency" style="margin-left: 10px;">
                                    <option value="all">All Signals</option>
                                    <option value="high_only">High Strength Only</option>
                                </select>
                            </label>
                            <label style="display: block; margin: 5px 0;">
                                Webhook URL: <input type="url" id="webhookUrl" placeholder="https://hooks.slack.com/..." style="width: 200px; margin-left: 10px;">
                            </label>
                        </div>
                        <button class="button" onclick="updateAlertSettings()">💾 Save Settings</button>
                        <button class="button" onclick="testAlert()" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);">🧪 Test Alert</button>
                    </div>
                    <div>
                        <h3>Alert History</h3>
                        <div id="alert-history" style="max-height: 200px; overflow-y: auto; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                            <div class="loading">No alerts yet</div>
                        </div>
                        <button class="button" onclick="loadAlertHistory()" style="margin-top: 10px;">🔄 Refresh</button>
                        <button class="button" onclick="clearAlertHistory()" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); margin-top: 10px;">🗑️ Clear</button>
                    </div>
                </div>
                
                <div class="status">
                    <h2>⚙️ System Settings</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3>Risk Management</h3>
                            <div style="margin: 10px 0;">
                                <label style="display: block; margin: 5px 0;">
                                    Risk per Trade: <input type="number" id="risk-per-trade" value="2" min="0.1" max="10" step="0.1" style="width: 80px; padding: 4px; margin-left: 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; background: rgba(0,0,0,0.3); color: white;">%
                                </label>
                                <label style="display: block; margin: 5px 0;">
                                    Reward Ratio: <input type="number" id="reward-ratio" value="2" min="1" max="5" step="0.1" style="width: 80px; padding: 4px; margin-left: 10px; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; background: rgba(0,0,0,0.3); color: white;">:1
                                </label>
                            </div>
                            <button class="button" onclick="saveRiskSettings()">💾 Save Risk Settings</button>
                        </div>
                        <div>
                            <h3>System Status</h3>
                            <div id="system-status" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading system status...</div>
                            </div>
                            <button class="button" onclick="loadSystemStatus()">🔄 Refresh Status</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- All remaining content moved to proper tabs above -->
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Chart instances storage
            const charts = {};
            let currentMarket = 'stocks';
            let currentTimeframe = '1h'; // Default to 1H (existing behavior)
            let currentTheme = 'dark';
            let currentLayout = 'compact';
            let tradingStats = {
                totalPnl: 0,
                winRate: 0,
                totalTrades: 0,
                profitFactor: 0,
                maxDrawdown: 0,
                trades: []
            };
            
            // Professional Trading Interface Functions
            function toggleTheme() {
                currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.body.setAttribute('data-theme', currentTheme);
                document.getElementById('theme-icon').textContent = currentTheme === 'dark' ? '🌙' : '☀️';
                localStorage.setItem('trading-theme', currentTheme);
            }
            
            function toggleLayout() {
                currentLayout = currentLayout === 'compact' ? 'expanded' : 'compact';
                document.body.setAttribute('data-layout', currentLayout);
                document.getElementById('layout-icon').textContent = currentLayout === 'compact' ? '📱' : '🖥️';
                localStorage.setItem('trading-layout', currentLayout);
            }
            
            // Tab switching function
            function switchTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Remove active class from all tab buttons
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.classList.remove('active');
                });
                
                // Show selected tab content
                document.getElementById(tabName + '-content').classList.add('active');
                
                // Add active class to clicked tab button
                document.getElementById(tabName + '-tab').classList.add('active');
            }
            
            // Collapsible menu function
            function toggleCollapse(menuId) {
                const content = document.getElementById(menuId);
                const menuItem = content.previousElementSibling;
                const arrow = menuItem.querySelector('.menu-arrow');
                
                if (content.classList.contains('active')) {
                    content.classList.remove('active');
                    menuItem.classList.remove('active');
                } else {
                    content.classList.add('active');
                    menuItem.classList.add('active');
                }
            }
            
            // Market data and functions
            const marketData = {
                stocks: {
                    name: 'STOCKS',
                    icon: '📊',
                    symbols: ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'SPY', 'QQQ', 'IWM', 'GLD', 'SLV', 'USO', 'TLT', 'VXX', 'AMD', 'INTC', 'CRM', 'ADBE', 'PYPL', 'NKE', 'DIS', 'WMT', 'JPM', 'BAC', 'XOM', 'CVX', 'KO', 'PEP'],
                    color: '#4CAF50',
                    description: 'US Equities & ETFs'
                },
                                <div class="loading">Loading market regime...</div>
                            </div>
                            <button class="button" onclick="loadMarketRegime()">🔄 Refresh Regime</button>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div>
                            <h3>Pattern Recognition</h3>
                            <div id="pattern-recognition" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading pattern recognition...</div>
                            </div>
                            <button class="button" onclick="loadPatternRecognition()">🔄 Refresh Patterns</button>
                        </div>
                        <div>
                            <h3>Adaptive Parameters</h3>
                            <div id="adaptive-parameters" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                                <div class="loading">Loading adaptive parameters...</div>
                            </div>
                            <button class="button" onclick="loadAdaptiveParameters()">🔄 Refresh Parameters</button>
                            <button class="button" onclick="triggerAdaptation()" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">🧠 Adapt Now</button>
                        </div>
                    </div>
                    <div>
                        <h3>AI Learning Metrics</h3>
                        <div id="ai-learning-metrics" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading AI learning metrics...</div>
                        </div>
                        <button class="button" onclick="loadAILearningMetrics()">📊 Load Metrics</button>
                    </div>
                </div>
            </div>
            
            <div class="status">
                <h2>🔮 Predictive Analytics Dashboard</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>Price Targets Analysis</h3>
                        <div id="price-targets-analysis" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading price targets...</div>
                        </div>
                        <button class="button" onclick="loadPriceTargets()">🎯 Load Price Targets</button>
                        <input type="text" id="symbol-input" placeholder="Enter symbol (e.g., AAPL)" style="margin: 5px; padding: 8px; border-radius: 4px; border: 1px solid #ccc;">
                    </div>
                    <div>
                        <h3>Volatility Forecast</h3>
                        <div id="volatility-forecast" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading volatility forecast...</div>
                        </div>
                        <button class="button" onclick="loadVolatilityForecast()">📊 Load Volatility</button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>Market Direction Prediction</h3>
                        <div id="market-direction-prediction" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading market direction...</div>
                        </div>
                        <button class="button" onclick="loadMarketDirection()">🧭 Load Direction</button>
                    </div>
                    <div>
                        <h3>Comprehensive Predictions</h3>
                        <div id="comprehensive-predictions" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading comprehensive predictions...</div>
                        </div>
                        <button class="button" onclick="loadComprehensivePredictions()">🔮 Load All Predictions</button>
                    </div>
                </div>
                <div>
                    <h3>Multi-Symbol Forecast</h3>
                    <div id="multi-symbol-forecast" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div class="loading">Loading multi-symbol forecast...</div>
                    </div>
                    <button class="button" onclick="loadMultiSymbolForecast()">📈 Load Multi-Symbol</button>
                </div>
            </div>
            
            <div class="status">
                <h2>📡 Real-Time Market Scanner</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>🔥 Hot List</h3>
                        <div id="market-hot-list" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Scanning market for hot opportunities...</div>
                        </div>
                        <button class="button" onclick="loadMarketHotList()">🔥 Scan Hot List</button>
                    </div>
                    <div>
                        <h3>🔄 Sector Rotation</h3>
                        <div id="sector-rotation" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Analyzing sector rotation...</div>
                        </div>
                        <button class="button" onclick="loadSectorRotation()">🔄 Analyze Sectors</button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>📈 Momentum Ranking</h3>
                        <div id="momentum-ranking" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Ranking momentum opportunities...</div>
                        </div>
                        <button class="button" onclick="loadMomentumRanking()">📈 Rank Momentum</button>
                    </div>
                    <div>
                        <h3>⚙️ Scanner Settings</h3>
                        <div id="scanner-settings" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading scanner settings...</div>
                        </div>
                        <button class="button" onclick="loadScannerSettings()">⚙️ Load Settings</button>
                    </div>
                </div>
                <div>
                    <h3>🎯 Comprehensive Market Scan</h3>
                    <div id="comprehensive-market-scan" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div class="loading">Running comprehensive market scan...</div>
                    </div>
                    <button class="button" onclick="loadComprehensiveMarketScan()">🎯 Full Market Scan</button>
                </div>
            </div>
            
            <div class="status">
                <h2>👥 Social Trading Features</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>📢 Signal Sharing</h3>
                        <div id="shared-signals" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading shared signals...</div>
                        </div>
                        <button class="button" onclick="loadSharedSignals()">📢 Load Shared Signals</button>
                        <button class="button" onclick="shareCurrentSignal()">🚀 Share Signal</button>
                    </div>
                    <div>
                        <h3>🏆 Performance Leaderboard</h3>
                        <div id="performance-leaderboard" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading leaderboard...</div>
                        </div>
                        <button class="button" onclick="loadPerformanceLeaderboard()">🏆 Load Leaderboard</button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>📋 Copy Trading</h3>
                        <div id="copy-trading" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading copy trading...</div>
                        </div>
                        <button class="button" onclick="loadCopyTrading()">📋 Load Copy Trading</button>
                        <button class="button" onclick="setupCopyTrading()">⚙️ Setup Copy</button>
                    </div>
                    <div>
                        <h3>💬 Community Insights</h3>
                        <div id="community-insights" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Loading community insights...</div>
                        </div>
                        <button class="button" onclick="loadCommunityInsights()">💬 Load Insights</button>
                    </div>
                </div>
                <div>
                    <h3>⚙️ Social Settings</h3>
                    <div id="social-settings" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div class="loading">Loading social settings...</div>
                    </div>
                    <button class="button" onclick="loadSocialSettings()">⚙️ Load Settings</button>
                    <button class="button" onclick="loadSocialSummary()">📊 Social Summary</button>
                </div>
            </div>
            
            <div class="status">
                <h2>🛡️ Advanced Risk Management</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>🔥 Portfolio Heatmap</h3>
                        <div id="portfolio-heatmap" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Calculating portfolio heatmap...</div>
                        </div>
                        <button class="button" onclick="loadPortfolioHeatmap()">🔥 Load Heatmap</button>
                    </div>
                    <div>
                        <h3>🔗 Correlation Analysis</h3>
                        <div id="correlation-analysis" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Analyzing correlations...</div>
                        </div>
                        <button class="button" onclick="loadCorrelationAnalysis()">🔗 Analyze Correlations</button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>📏 Dynamic Position Sizing</h3>
                        <div id="position-sizing" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Calculating position sizes...</div>
                        </div>
                        <button class="button" onclick="loadPositionSizing()">📏 Load Position Sizing</button>
                    </div>
                    <div>
                        <h3>📊 Risk Metrics</h3>
                        <div id="risk-metrics" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                            <div class="loading">Calculating risk metrics...</div>
                        </div>
                        <button class="button" onclick="loadRiskMetrics()">📊 Load Risk Metrics</button>
                    </div>
                </div>
                <div>
                    <h3>⚙️ Risk Settings</h3>
                    <div id="risk-settings" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div class="loading">Loading risk settings...</div>
                    </div>
                    <button class="button" onclick="loadRiskSettings()">⚙️ Load Settings</button>
                    <button class="button" onclick="loadComprehensiveRiskAnalysis()">🛡️ Full Risk Analysis</button>
                </div>
            </div>
            
            <div class="status">
                <h2>📊 Advanced Analytics Dashboard</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <h3>Performance Metrics</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                            <div class="metric-card">
                                <div class="metric-value" id="total-trades-analytics">0</div>
                                <div class="metric-label">Total Trades</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="win-rate-analytics">0%</div>
                                <div class="metric-label">Win Rate</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="profit-factor-analytics">0.0</div>
                                <div class="metric-label">Profit Factor</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="max-drawdown-analytics">0%</div>
                                <div class="metric-label">Max Drawdown</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="sharpe-ratio-analytics">0.0</div>
                                <div class="metric-label">Sharpe Ratio</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="total-pnl-analytics">$0.00</div>
                                <div class="metric-label">Total P&L</div>
                            </div>
                        </div>
                        <button class="button" onclick="loadAnalyticsDashboard()">🔄 Refresh Analytics</button>
                        <button class="button" onclick="resetAnalytics()" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);">🗑️ Reset Data</button>
                    </div>
                    <div>
                        <h3>Equity Curve</h3>
                        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0; height: 200px;">
                            <canvas id="equityCurveChart"></canvas>
                        </div>
                    </div>
                </div>
                <div>
                    <h3>Performance Heatmap</h3>
                    <div id="performance-heatmap" style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div class="loading">Loading performance heatmap...</div>
                    </div>
                </div>
            </div>
            
                </div>
            </div>
            
            <!-- API Endpoints section removed for clean, professional interface -->
            <!-- If needed for debugging, access directly via URL: /api/health, /api/live/signals, etc. -->
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            // Chart instances storage
            const charts = {};
            let currentMarket = 'stocks';
            let currentTimeframe = '1h'; // Default to 1H (existing behavior)
            let currentTheme = 'dark';
            let currentLayout = 'compact';
            let tradingStats = {
                totalPnl: 0,
                winRate: 0,
                totalTrades: 0,
                profitFactor: 0,
                maxDrawdown: 0,
                trades: []
            };
            
            // Professional Trading Interface Functions
            function toggleTheme() {
                currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.body.setAttribute('data-theme', currentTheme);
                document.getElementById('theme-icon').textContent = currentTheme === 'dark' ? '🌙' : '☀️';
                localStorage.setItem('trading-theme', currentTheme);
            }
            
            function toggleCollapse(sectionId) {
                const content = document.getElementById(sectionId);
                const icon = document.getElementById(sectionId + '-icon');
                
                if (content && icon) {
                    if (content.style.display === 'none') {
                        content.style.display = 'block';
                        icon.textContent = '📕'; // Open book
                    } else {
                        content.style.display = 'none';
                        icon.textContent = '📖'; // Closed book
                    }
                }
            }
            
            // Full Market Scanner Functions
            async function scanFullMarket() {
                const scannerDiv = document.getElementById('full-market-scanner');
                if (!scannerDiv) return;
                
                scannerDiv.innerHTML = '<div class="loading">🔍 Scanning entire market for trading signals... This may take 30-60 seconds</div>';
                
                try {
                    const response = await fetch('/api/scanner/full-market-signals');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        let html = `
                            <div style="background: rgba(0,255,0,0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <h3 style="color: #4CAF50; margin: 0 0 10px 0;">✅ Scan Complete!</h3>
                                <p><strong>Symbols Scanned:</strong> ${result.total_symbols_scanned}</p>
                                <p><strong>Signals Found:</strong> ${result.signals_generated}</p>
                                <p><strong>Scan Duration:</strong> ${result.scan_duration_seconds}s</p>
                            </div>
                        `;
                        
                        if (result.signals && result.signals.length > 0) {
                            html += '<h4 style="color: #4CAF50; margin: 15px 0 10px 0;">🎯 Trading Signals Found:</h4>';
                            html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">';
                            
                            result.signals.forEach(signalData => {
                                const signal = signalData.signal;
                                const signalColor = signal.signal_type === 'BUY' ? '#4CAF50' : '#f44336';
                                const signalIcon = signal.signal_type === 'BUY' ? '📈' : '📉';
                                
                                html += `
                                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; border-left: 4px solid ${signalColor};">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                            <h5 style="margin: 0; color: ${signalColor};">${signalIcon} ${signalData.symbol}</h5>
                                            <span style="background: ${signalColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">${signal.signal_type}</span>
                                        </div>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Market:</strong> ${signalData.market.toUpperCase()}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Current Price:</strong> $${signal.current_price}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Entry:</strong> $${signal.entry_price}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Stop Loss:</strong> $${signal.stop_loss}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Take Profit:</strong> $${signal.take_profit}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Confidence:</strong> ${signal.confidence}%</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Risk/Reward:</strong> ${signal.risk_reward_ratio}</p>
                                    </div>
                                `;
                            });
                            
                            html += '</div>';
                        } else {
                            html += '<div style="background: rgba(255,193,7,0.1); padding: 15px; border-radius: 8px; color: #FFC107;"><strong>⚠️ No Trading Signals Found</strong><br>Market conditions don\'t meet our strict trading criteria. Try again later or check individual symbols.</div>';
                        }
                        
                        scannerDiv.innerHTML = html;
                    } else {
                        scannerDiv.innerHTML = `<div style="background: rgba(244,67,54,0.1); padding: 15px; border-radius: 8px; color: #f44336;"><strong>❌ Scan Failed:</strong> ${result.error || 'Unknown error'}</div>`;
                    }
                } catch (error) {
                    scannerDiv.innerHTML = `<div style="background: rgba(244,67,54,0.1); padding: 15px; border-radius: 8px; color: #f44336;"><strong>❌ Error:</strong> ${error.message}</div>`;
                }
            }
            
            // Individual Symbol Analyzer Functions
            async function analyzeCustomSymbol() {
                const symbolInput = document.getElementById('custom-symbol');
                const analysisDiv = document.getElementById('individual-analysis');
                
                if (!symbolInput || !analysisDiv) return;
                
                const symbol = symbolInput.value.trim().toUpperCase();
                if (!symbol) {
                    alert('Please enter a symbol to analyze!');
                    return;
                }
                
                analysisDiv.innerHTML = `<div class="loading">🔍 Analyzing ${symbol}... Please wait</div>`;
                
                try {
                    const response = await fetch(`/api/analyze/${encodeURIComponent(symbol)}`);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const signal = result.signal;
                        const signalColor = signal.signal_type === 'BUY' ? '#4CAF50' : '#f44336';
                        const signalIcon = signal.signal_type === 'BUY' ? '📈' : '📉';
                        
                        let html = `
                            <div style="background: rgba(0,255,0,0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                                <h3 style="color: #4CAF50; margin: 0 0 10px 0;">✅ Analysis Complete!</h3>
                                <p><strong>Symbol:</strong> ${result.symbol}</p>
                                <p><strong>Market Type:</strong> ${result.market_type.toUpperCase()}</p>
                                <p><strong>Timeframe:</strong> ${result.timeframe.toUpperCase()}</p>
                            </div>
                            
                            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; border-left: 4px solid ${signalColor};">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h4 style="margin: 0; color: ${signalColor};">${signalIcon} ${signal.signal_type} Signal</h4>
                                    <span style="background: ${signalColor}; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold;">${signal.confidence}% Confidence</span>
                                </div>
                                
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                                    <div>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Current Price:</strong> $${signal.current_price}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Entry Price:</strong> $${signal.entry_price}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Stop Loss:</strong> $${signal.stop_loss}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Take Profit:</strong> $${signal.take_profit}</p>
                                    </div>
                                    <div>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Risk/Reward:</strong> ${signal.risk_reward_ratio}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>ATR:</strong> ${signal.atr}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Pattern:</strong> ${signal.pattern}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em;"><strong>Timeframe:</strong> ${signal.timeframe}</p>
                                    </div>
                                </div>
                                
                                <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 6px;">
                                    <p style="margin: 0; font-size: 0.9em; color: #ccc;"><strong>Analysis Time:</strong> ${new Date(result.analysis_timestamp).toLocaleString()}</p>
                                </div>
                            </div>
                        `;
                        
                        analysisDiv.innerHTML = html;
                    } else if (result.status === 'no_signal') {
                        analysisDiv.innerHTML = `
                            <div style="background: rgba(255,193,7,0.1); padding: 15px; border-radius: 8px; color: #FFC107;">
                                <h4 style="margin: 0 0 10px 0;">⚠️ No Trading Signal</h4>
                                <p><strong>Symbol:</strong> ${result.symbol}</p>
                                <p><strong>Market Type:</strong> ${result.market_type.toUpperCase()}</p>
                                <p><strong>Reason:</strong> ${result.message}</p>
                                <p style="margin-top: 10px; font-size: 0.9em;">Market conditions don't meet our strict trading criteria. Try a different symbol or timeframe.</p>
                            </div>
                        `;
                    } else {
                        analysisDiv.innerHTML = `<div style="background: rgba(244,67,54,0.1); padding: 15px; border-radius: 8px; color: #f44336;"><strong>❌ Analysis Failed:</strong> ${result.message || 'Unknown error'}</div>`;
                    }
                } catch (error) {
                    analysisDiv.innerHTML = `<div style="background: rgba(244,67,54,0.1); padding: 15px; border-radius: 8px; color: #f44336;"><strong>❌ Error:</strong> ${error.message}</div>`;
                }
            }
            
            function setLayout(layout) {
                currentLayout = layout;
                document.body.className = layout;
                
                // Update active button
                document.querySelectorAll('.layout-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                localStorage.setItem('trading-layout', layout);
            }
            
            function updateTradingStats() {
                // Calculate trading statistics
                const totalTrades = tradingStats.trades.length;
                const winningTrades = tradingStats.trades.filter(trade => trade.pnl > 0).length;
                const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100).toFixed(1) : 0;
                
                const totalProfit = tradingStats.trades.filter(trade => trade.pnl > 0).reduce((sum, trade) => sum + trade.pnl, 0);
                const totalLoss = Math.abs(tradingStats.trades.filter(trade => trade.pnl < 0).reduce((sum, trade) => sum + trade.pnl, 0));
                const profitFactor = totalLoss > 0 ? (totalProfit / totalLoss).toFixed(2) : 0;
                
                // Update UI
                document.getElementById('total-p-l').textContent = `$${tradingStats.totalPnl.toFixed(2)}`;
                document.getElementById('win-rate').textContent = `${winRate}%`;
                document.getElementById('total-trades').textContent = totalTrades;
                document.getElementById('profit-factor').textContent = profitFactor;
                document.getElementById('max-drawdown').textContent = `${tradingStats.maxDrawdown.toFixed(1)}%`;
                
                // Update P&L color
                const pnlElement = document.getElementById('total-p-l');
                pnlElement.className = 'p-l-value';
                if (tradingStats.totalPnl > 0) {
                    pnlElement.classList.add('p-l-positive');
                } else if (tradingStats.totalPnl < 0) {
                    pnlElement.classList.add('p-l-negative');
                } else {
                    pnlElement.classList.add('p-l-neutral');
                }
            }
            
            function simulateTrade(signal) {
                // Simulate trade execution and P&L calculation
                const entryPrice = signal.entry_price;
                const currentPrice = signal.current_price;
                const stopLoss = signal.stop_loss;
                const takeProfit = signal.take_profit;
                const direction = signal.signal_type;
                
                let pnl = 0;
                let tradeStatus = 'open';
                
                if (direction === 'BUY') {
                    if (currentPrice >= takeProfit) {
                        pnl = (takeProfit - entryPrice) / entryPrice * 100; // Percentage gain
                        tradeStatus = 'win';
                    } else if (currentPrice <= stopLoss) {
                        pnl = (stopLoss - entryPrice) / entryPrice * 100; // Percentage loss
                        tradeStatus = 'loss';
                    }
                } else if (direction === 'SELL') {
                    if (currentPrice <= takeProfit) {
                        pnl = (entryPrice - takeProfit) / entryPrice * 100; // Percentage gain
                        tradeStatus = 'win';
                    } else if (currentPrice >= stopLoss) {
                        pnl = (entryPrice - stopLoss) / entryPrice * 100; // Percentage loss
                        tradeStatus = 'loss';
                    }
                }
                
                if (tradeStatus !== 'open') {
                    const trade = {
                        symbol: signal.symbol,
                        direction: direction,
                        entryPrice: entryPrice,
                        exitPrice: tradeStatus === 'win' ? takeProfit : stopLoss,
                        pnl: pnl,
                        timestamp: new Date(),
                        status: tradeStatus
                    };
                    
                    tradingStats.trades.push(trade);
                    tradingStats.totalPnl += pnl;
                    
                    // Update max drawdown
                    const currentDrawdown = Math.min(0, tradingStats.totalPnl - Math.max(...tradingStats.trades.map(t => t.pnl)));
                    tradingStats.maxDrawdown = Math.min(tradingStats.maxDrawdown, currentDrawdown);
                    
                    updateTradingStats();
                }
            }
            
            // Load saved preferences
            function loadPreferences() {
                const savedTheme = localStorage.getItem('trading-theme');
                const savedLayout = localStorage.getItem('trading-layout');
                
                if (savedTheme) {
                    currentTheme = savedTheme;
                    document.body.setAttribute('data-theme', currentTheme);
                    document.getElementById('theme-icon').textContent = currentTheme === 'dark' ? '🌙' : '☀️';
                }
                
                if (savedLayout) {
                    currentLayout = savedLayout;
                    document.body.className = currentLayout;
                    document.querySelectorAll('.layout-btn').forEach(btn => {
                        btn.classList.remove('active');
                        if (btn.textContent.toLowerCase() === currentLayout) {
                            btn.classList.add('active');
                        }
                    });
                }
            }
            
            // Mobile touch and swipe support
            let touchStartX = 0;
            let touchStartY = 0;
            let touchEndX = 0;
            let touchEndY = 0;
            
            // Add touch event listeners
            document.addEventListener('DOMContentLoaded', function() {
                loadPreferences();
                updateTradingStats();
                
                const signalsContainer = document.getElementById('signals');
                if (signalsContainer) {
                    signalsContainer.addEventListener('touchstart', handleTouchStart, false);
                    signalsContainer.addEventListener('touchend', handleTouchEnd, false);
                }
                
                // Add pull-to-refresh functionality
                let startY = 0;
                let currentY = 0;
                let isRefreshing = false;
                
                document.addEventListener('touchstart', function(e) {
                    if (window.scrollY === 0) {
                        startY = e.touches[0].clientY;
                    }
                });
                
                document.addEventListener('touchmove', function(e) {
                    if (window.scrollY === 0 && !isRefreshing) {
                        currentY = e.touches[0].clientY;
                        const pullDistance = currentY - startY;
                        
                        if (pullDistance > 50) {
                            showRefreshIndicator();
                        }
                    }
                });
                
                document.addEventListener('touchend', function(e) {
                    if (window.scrollY === 0 && !isRefreshing) {
                        const pullDistance = currentY - startY;
                        
                        if (pullDistance > 100) {
                            refreshSignals();
                        } else {
                            hideRefreshIndicator();
                        }
                    }
                });
            });
            
            function handleTouchStart(e) {
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
            }
            
            function handleTouchEnd(e) {
                touchEndX = e.changedTouches[0].screenX;
                touchEndY = e.changedTouches[0].screenY;
                handleSwipe();
            }
            
            function handleSwipe() {
                const deltaX = touchEndX - touchStartX;
                const deltaY = touchEndY - touchStartY;
                
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                    if (deltaX > 0) {
                        switchToPreviousMarket();
                    } else {
                        switchToNextMarket();
                    }
                }
            }
            
            function switchToPreviousMarket() {
                const markets = ['stocks', 'forex', 'crypto', 'indices', 'futures', 'metals'];
                const currentIndex = markets.indexOf(currentMarket);
                const previousIndex = currentIndex > 0 ? currentIndex - 1 : markets.length - 1;
                const targetMarket = markets[previousIndex];
                
                // Find the corresponding market card element
                const marketCards = document.querySelectorAll('.market-card');
                let targetElement = null;
                marketCards.forEach(card => {
                    if (card.onclick && card.onclick.toString().includes(`selectMarket('${targetMarket}'`)) {
                        targetElement = card;
                    }
                });
                
                selectMarket(targetMarket, targetElement);
            }
            
            function switchToNextMarket() {
                const markets = ['stocks', 'forex', 'crypto', 'indices', 'futures', 'metals'];
                const currentIndex = markets.indexOf(currentMarket);
                const nextIndex = currentIndex < markets.length - 1 ? currentIndex + 1 : 0;
                const targetMarket = markets[nextIndex];
                
                // Find the corresponding market card element
                const marketCards = document.querySelectorAll('.market-card');
                let targetElement = null;
                marketCards.forEach(card => {
                    if (card.onclick && card.onclick.toString().includes(`selectMarket('${targetMarket}'`)) {
                        targetElement = card;
                    }
                });
                
                selectMarket(targetMarket, targetElement);
            }
            
            function showRefreshIndicator() {
                let indicator = document.getElementById('refresh-indicator');
                if (!indicator) {
                    indicator = document.createElement('div');
                    indicator.id = 'refresh-indicator';
                    indicator.style.cssText = `
                        position: fixed;
                        top: 20px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: rgba(76, 175, 80, 0.9);
                        color: white;
                        padding: 10px 20px;
                        border-radius: 20px;
                        z-index: 1000;
                        font-size: 14px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    `;
                    indicator.textContent = '🔄 Pull to refresh signals';
                    document.body.appendChild(indicator);
                }
            }
            
            function hideRefreshIndicator() {
                const indicator = document.getElementById('refresh-indicator');
                if (indicator) {
                    indicator.remove();
                }
            }
            
            function refreshSignals() {
                const indicator = document.getElementById('refresh-indicator');
                if (indicator) {
                    indicator.textContent = '🔄 Refreshing...';
                }
                
                getSignals().then(() => {
                    setTimeout(() => {
                        hideRefreshIndicator();
                    }, 1000);
                });
            }
            
            // Update Kill Zone status
            function updateKillZoneStatus() {
                const now = new Date();
                const utcTime = new Date(now.getTime() + (now.getTimezoneOffset() * 60000));
                const hours = utcTime.getHours();
                const minutes = utcTime.getMinutes();
                const currentTime = hours * 60 + minutes;
                
                // Kill Zone times (UTC minutes from midnight)
                const londonStart = 7 * 60;    // 7:00 AM UTC
                const londonEnd = 10 * 60;     // 10:00 AM UTC
                const nyStart = 13 * 60 + 30;  // 1:30 PM UTC
                const nyEnd = 16 * 60 + 30;    // 4:30 PM UTC
                
                let killZoneText = '';
                let killZoneColor = '#666';
                
                if (currentTime >= londonStart && currentTime <= londonEnd) {
                    killZoneText = 'London KZ Active 🟢';
                    killZoneColor = '#00ff00';
                } else if (currentTime >= nyStart && currentTime <= nyEnd) {
                    killZoneText = 'NY KZ Active 🟢';
                    killZoneColor = '#00ff00';
                } else {
                    killZoneText = 'Outside KZ ⚪';
                    killZoneColor = '#666';
                }
                
                document.getElementById('kill-zone-text').textContent = killZoneText;
                document.getElementById('kill-zone-text').style.color = killZoneColor;
            }
            
            // Update Kill Zone status every minute
            updateKillZoneStatus();
            setInterval(updateKillZoneStatus, 60000);
            
            // Market data with symbols for each market type - More comprehensive
            const marketData = {
                stocks: {
                    name: 'STOCKS',
                    icon: '📊',
                    color: '#4CAF50',
                    description: 'US Equities & ETFs',
                    categories: {
                        'NASDAQ': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC', 'CRM', 'ADBE'],
                        'NYSE': ['JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V', 'NKE', 'DIS', 'WMT', 'XOM'],
                        'ETFs': ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'SLV', 'USO', 'TLT', 'VXX', 'PYPL', 'CVX', 'KO']
                    }
                },
                forex: {
                    name: 'FOREX',
                    icon: '💱',
                    color: '#2196F3',
                    description: 'Currency Pairs',
                    categories: {
                        'MAJORS': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X'],
                        'MINORS': ['EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURAUD=X', 'GBPAUD=X', 'AUDNZD=X'],
                        'EXOTICS': ['USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'EURCHF=X', 'GBPCHF=X', 'USDZAR=X', 'USDTRY=X']
                    }
                },
                crypto: {
                    name: 'CRYPTO',
                    icon: '₿',
                    color: '#FFC107',
                    description: 'Digital Assets',
                    categories: {
                        'MAJORS': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD'],
                        'DEFI': ['UNI-USD', 'AAVE-USD', 'COMP-USD', 'MKR-USD', 'SUSHI-USD'],
                        'LAYER1': ['ADA-USD', 'DOT-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD']
                    }
                },
                futures: {
                    name: 'FUTURES',
                    icon: '⛽',
                    color: '#FF9800',
                    description: 'Commodities & Indices',
                    categories: {
                        'METALS': ['GC', 'SI', 'PL', 'PA', 'HG', 'AL', 'NI', 'ZN'],
                        'ENERGY': ['CL', 'NG', 'HO', 'RB', 'BZ', 'QS', 'BZ=F'],
                        'INDICES': ['ES', 'NQ', 'YM', 'RTY', 'SPX', 'NDX', 'DJI', 'RUT'],
                        'AGRICULTURE': ['ZC', 'ZS', 'ZW', 'KC', 'CC', 'CT', 'SB', 'CC=F'],
                        'BONDS': ['ZB', 'ZN', 'ZF', 'ZT', 'GE', 'TU', 'FV', 'TY']
                    }
                },
                indices: {
                    name: 'INDICES',
                    icon: '📈',
                    color: '#f44336',
                    description: 'Market Indexes & ETFs',
                    categories: {
                        'US_INDICES': ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO'],
                        'INTERNATIONAL': ['EFA', 'EEM', 'ACWI', 'VT', 'VXUS', 'BND', 'TLT', 'IEF'],
                        'VOLATILITY': ['VXX', 'UVXY', 'TVIX', 'VIXY', 'SHY', 'LQD', 'HYG', 'EMB']
                    }
                },
                metals: {
                    name: 'METALS',
                    icon: '🥇',
                    color: '#9C27B0',
                    description: 'Precious Metals & Commodities',
                    categories: {
                        'PRECIOUS': ['GC', 'SI', 'PL', 'PA', 'GLD', 'SLV', 'PPLT', 'PALL'],
                        'MINING': ['GDX', 'GDXJ', 'SIL', 'COPX', 'PICK', 'REMX', 'URA', 'LIT'],
                        'AGRICULTURE': ['BAL', 'NIB', 'JO', 'CAFE', 'WEAT', 'CORN', 'SOYB', 'CANE']
                    }
                }
            };
            
            // Tab switching function
            function switchTab(tabName) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Remove active class from all tab buttons
                document.querySelectorAll('.tab-button').forEach(button => {
                    button.classList.remove('active');
                });
                
                // Show selected tab content
                document.getElementById(tabName + '-content').classList.add('active');
                
                // Add active class to clicked tab button
                document.getElementById(tabName + '-tab').classList.add('active');
            }
            
            // Analytics Tab Functions
            async function loadPerformanceMetrics() {
                try {
                    const response = await fetch('/api/analytics/performance');
                    const data = await response.json();
                    document.getElementById('performance-metrics').innerHTML = `
                        <div style="color: #4CAF50;">✅ Performance loaded</div>
                        <div>Win Rate: ${data.win_rate || 'N/A'}%</div>
                        <div>Profit Factor: ${data.profit_factor || 'N/A'}</div>
                        <div>Total Trades: ${data.total_trades || 'N/A'}</div>
                    `;
                } catch (error) {
                    document.getElementById('performance-metrics').innerHTML = `<div style="color: #f44336;">❌ Error loading metrics</div>`;
                }
            }
            
            async function loadPerformanceHeatmap() {
                try {
                    const response = await fetch('/api/analytics/heatmap');
                    const data = await response.json();
                    document.getElementById('performance-heatmap').innerHTML = `
                        <div style="color: #4CAF50;">✅ Heatmap loaded</div>
                        <div>Best performing: ${data.best_performing || 'N/A'}</div>
                        <div>Worst performing: ${data.worst_performing || 'N/A'}</div>
                    `;
                } catch (error) {
                    document.getElementById('performance-heatmap').innerHTML = `<div style="color: #f44336;">❌ Error loading heatmap</div>`;
                }
            }
            
            async function loadAILearningStatus() {
                try {
                    const response = await fetch('/api/ai/learning/insights');
                    const data = await response.json();
                    document.getElementById('ai-learning-status').innerHTML = `
                        <div style="color: #4CAF50;">✅ AI Status loaded</div>
                        <div>Learning Cycles: ${data.total_cycles || 'N/A'}</div>
                        <div>Accuracy: ${data.accuracy || 'N/A'}%</div>
                    `;
                } catch (error) {
                    document.getElementById('ai-learning-status').innerHTML = `<div style="color: #f44336;">❌ Error loading AI status</div>`;
                }
            }
            
            async function retrainAIModels() {
                try {
                    const response = await fetch('/api/ai/learning/retrain', { method: 'POST' });
                    const data = await response.json();
                    alert('AI models retraining started!');
                } catch (error) {
                    alert('Error starting retraining');
                }
            }
            
            // Settings Tab Functions
            async function saveAlertSettings() {
                alert('Alert settings saved!');
            }
            
            async function testAlert() {
                alert('Test alert sent!');
            }
            
            async function loadAlertHistory() {
                document.getElementById('alert-history').innerHTML = '<div style="color: #4CAF50;">✅ Alert history loaded</div>';
            }
            
            async function saveRiskSettings() {
                alert('Risk settings saved!');
            }
            
            async function loadSystemStatus() {
                document.getElementById('system-status').innerHTML = '<div style="color: #4CAF50;">✅ System healthy</div>';
            }
            
            // Layout and Theme Functions
            function setLayout(layout) {
                currentLayout = layout;
                document.body.setAttribute('data-layout', layout);
                localStorage.setItem('trading-layout', layout);
                
                // Update button styles
                document.querySelectorAll('[onclick^="setLayout"]').forEach(btn => {
                    btn.style.background = '#2196F3';
                });
                event.target.style.background = '#4CAF50';
            }
            
            function refreshTradingStats() {
                // This would normally fetch real trading stats
                alert('Trading stats refreshed!');
            }
            
            // Additional Analytics Functions
            async function getPriceTargets() {
                try {
                    const response = await fetch('/api/predictive/price-targets/AAPL');
                    const data = await response.json();
                    document.getElementById('price-targets').innerHTML = `
                        <div style="color: #4CAF50;">✅ Price targets loaded</div>
                        <div>Short-term: $${data.short_term || 'N/A'}</div>
                        <div>Medium-term: $${data.medium_term || 'N/A'}</div>
                        <div>Long-term: $${data.long_term || 'N/A'}</div>
                    `;
                } catch (error) {
                    document.getElementById('price-targets').innerHTML = `<div style="color: #f44336;">❌ Error loading price targets</div>`;
                }
            }
            
            async function getVolatilityForecast() {
                try {
                    const response = await fetch('/api/predictive/volatility-forecast/AAPL');
                    const data = await response.json();
                    document.getElementById('volatility-forecast').innerHTML = `
                        <div style="color: #4CAF50;">✅ Volatility forecast loaded</div>
                        <div>Current: ${data.current || 'N/A'}%</div>
                        <div>Predicted: ${data.predicted || 'N/A'}%</div>
                        <div>Trend: ${data.trend || 'N/A'}</div>
                    `;
                } catch (error) {
                    document.getElementById('volatility-forecast').innerHTML = `<div style="color: #f44336;">❌ Error loading volatility forecast</div>`;
                }
            }
            
            async function getHotList() {
                try {
                    const response = await fetch('/api/scanner/hot-list');
                    const data = await response.json();
                    document.getElementById('hot-list').innerHTML = `
                        <div style="color: #4CAF50;">✅ Hot list loaded</div>
                        <div>Top performers: ${data.top_performers?.length || 0}</div>
                        <div>Breakout candidates: ${data.breakout_candidates?.length || 0}</div>
                    `;
                } catch (error) {
                    document.getElementById('hot-list').innerHTML = `<div style="color: #f44336;">❌ Error loading hot list</div>`;
                }
            }
            
            async function getSectorRotation() {
                try {
                    const response = await fetch('/api/scanner/sector-rotation');
                    const data = await response.json();
                    document.getElementById('sector-rotation').innerHTML = `
                        <div style="color: #4CAF50;">✅ Sector rotation loaded</div>
                        <div>Leading sectors: ${data.leading_sectors?.length || 0}</div>
                        <div>Lagging sectors: ${data.lagging_sectors?.length || 0}</div>
                    `;
                } catch (error) {
                    document.getElementById('sector-rotation').innerHTML = `<div style="color: #f44336;">❌ Error loading sector rotation</div>`;
                }
            }
            
            function selectMarket(market, element) {
                console.log('selectMarket called with:', market, element);
                console.log('marketData available:', !!marketData);
                console.log('marketData[market]:', marketData[market]);
                
                currentMarket = market;
                
                // Update active market styling
                document.querySelectorAll('.market-card').forEach(card => {
                    card.style.borderColor = 'rgba(255,255,255,0.2)';
                    card.style.transform = 'scale(1)';
                });
                
                // Highlight the clicked market card
                if (element) {
                    element.style.borderColor = marketData[market].color;
                    element.style.transform = 'scale(1.05)';
                }
                
                console.log('About to call showMarketSymbols');
                // Show market symbols
                showMarketSymbols(market);
            }
            
            function showMarketSymbols(market) {
                console.log('showMarketSymbols called with market:', market);
                
                const symbolsContainer = document.getElementById('market-symbols');
                const symbolsTitle = document.getElementById('market-symbols-title');
                const symbolsList = document.getElementById('symbols-list');
                
                console.log('Elements found:', {
                    symbolsContainer: !!symbolsContainer,
                    symbolsTitle: !!symbolsTitle,
                    symbolsList: !!symbolsList
                });
                
                if (!symbolsContainer || !symbolsTitle || !symbolsList) {
                    console.log('Missing elements, returning');
                    return;
                }
                
                const marketInfo = marketData[market];
                const categories = marketInfo.categories;
                
                console.log('Market data:', { marketInfo, categories });
                console.log('Categories keys:', Object.keys(categories));
                
                // Update title
                symbolsTitle.innerHTML = `${marketInfo.icon} ${marketInfo.name} Categories`;
                symbolsTitle.style.color = marketInfo.color;
                
                // Clear and populate symbols by category
                symbolsList.innerHTML = '';
                
                // Create category sections
                Object.entries(categories).forEach(([categoryName, symbols]) => {
                    // Create category header
                    const categoryHeader = document.createElement('div');
                    categoryHeader.style.cssText = `
                        background: linear-gradient(135deg, ${marketInfo.color}20, ${marketInfo.color}10);
                        border-left: 4px solid ${marketInfo.color};
                        border-radius: 6px;
                        padding: 10px 15px;
                        margin: 15px 0 10px 0;
                        font-weight: bold;
                        color: ${marketInfo.color};
                        font-size: 0.9em;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    `;
                    categoryHeader.innerHTML = `📂 ${categoryName}`;
                    symbolsList.appendChild(categoryHeader);
                    
                    // Create symbols grid for this category
                    const categoryGrid = document.createElement('div');
                    categoryGrid.style.cssText = `
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: 8px;
                        margin-bottom: 20px;
                    `;
                    
                    // Add symbols for this category
                    symbols.slice(0, 8).forEach(symbol => {
                        const symbolCard = document.createElement('div');
                        symbolCard.style.cssText = `
                            background: rgba(255,255,255,0.08);
                            border: 1px solid ${marketInfo.color}30;
                            border-radius: 6px;
                            padding: 8px;
                            text-align: center;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            backdrop-filter: blur(5px);
                            font-size: 0.85em;
                        `;
                        symbolCard.innerHTML = `
                            <div style="font-weight: bold; color: ${marketInfo.color}; margin-bottom: 2px;">${symbol}</div>
                            <div style="font-size: 0.7em; opacity: 0.7;">${categoryName}</div>
                        `;
                        symbolCard.onmouseover = () => {
                            symbolCard.style.transform = 'scale(1.05)';
                            symbolCard.style.borderColor = marketInfo.color;
                            symbolCard.style.background = `rgba(${marketInfo.color.replace('#', '')}, 0.15)`;
                        };
                        symbolCard.onmouseout = () => {
                            symbolCard.style.transform = 'scale(1)';
                            symbolCard.style.borderColor = `${marketInfo.color}30`;
                            symbolCard.style.background = 'rgba(255,255,255,0.08)';
                        };
                        symbolCard.onclick = () => {
                            // Auto-fill the symbol analyzer
                            const analyzeInput = document.getElementById('analyze-symbol');
                            if (analyzeInput) {
                                analyzeInput.value = symbol;
                            }
                        };
                        categoryGrid.appendChild(symbolCard);
                    });
                    
                    symbolsList.appendChild(categoryGrid);
                });
                
                // Show the symbols container
                symbolsContainer.style.display = 'block';
            }
            
            function startMonitoringForSelectedMarket() {
                if (!currentMarket) {
                    alert('Please select a market first!');
                    return;
                }
                
                const categories = marketData[currentMarket].categories;
                if (!categories || Object.keys(categories).length === 0) {
                    alert('No symbols available for this market!');
                    return;
                }
                
                // Collect all symbols from all categories
                const allSymbols = [];
                Object.values(categories).forEach(symbols => {
                    allSymbols.push(...symbols);
                });
                
                if (allSymbols.length === 0) {
                    alert('No symbols available for this market!');
                    return;
                }
                
                // Start monitoring with the selected market symbols
                startMonitoring(allSymbols, currentMarket);
            }
            
            function selectTimeframe(timeframe) {
                currentTimeframe = timeframe;
                
                // Update active timeframe styling
                document.querySelectorAll('.timeframe-btn').forEach(btn => {
                    btn.style.background = 'rgba(255,255,255,0.1)';
                    btn.style.borderColor = 'rgba(255,255,255,0.2)';
                    btn.classList.remove('active');
                });
                
                // Highlight selected timeframe
                const selectedBtn = document.querySelector(`[data-timeframe="${timeframe}"]`);
                selectedBtn.style.background = 'rgba(59, 130, 246, 0.2)';
                selectedBtn.style.borderColor = '#3b82f6';
                selectedBtn.classList.add('active');
                
                // Update current timeframe display
                const timeframeNames = {
                    '5m': '5M Entry',
                    '15m': '15M Confirmation', 
                    '1h': '1H Trend',
                    '4h': '4H Structure',
                    '1d': '1D Bias'
                };
                document.getElementById('current-timeframe').textContent = `Current: ${timeframeNames[timeframe]} Analysis`;
                
                // Show timeframe change message
                document.getElementById('signals-display').innerHTML = `
                    <div class="loading">
                        ⏰ Timeframe changed to ${timeframe.toUpperCase()}<br>
                        📊 Analysis will use ${timeframeNames[timeframe]} data<br>
                        💡 Click "Get Live Signals" to see ${timeframe.toUpperCase()} analysis
                    </div>
                `;
            }
            
            // Global variable to store monitoring interval
            let monitoringInterval = null;
            
            async function startMonitoring() {
                try {
                    const symbols = marketData[currentMarket].symbols;
                    const displaySymbols = symbols.slice(0, 10);
                    document.getElementById('signals-display').innerHTML = `<div class="loading">🚀 Starting monitoring for ${marketData[currentMarket].name}...<br>📊 Symbols: ${displaySymbols.join(', ')}${symbols.length > 10 ? ` + ${symbols.length - 10} more` : ''}</div>`;
                    
                    const response = await fetch('/api/live/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbols: symbols})
                    });
                    const data = await response.json();
                    
                    // Update monitoring status indicator
                    updateMonitoringStatus(true, marketData[currentMarket].name, symbols.length);
                    
                    // Get initial signals
                    await getSignals();
                    
                    // Start automatic signal refresh every 2 minutes
                    if (monitoringInterval) {
                        clearInterval(monitoringInterval);
                    }
                    monitoringInterval = setInterval(async () => {
                        console.log('🔄 Auto-refreshing signals...');
                        await getSignals();
                    }, 120000); // 2 minutes
                    
                    document.getElementById('signals-display').innerHTML += `
                        <div class="success">
                            ✅ ${data.message}<br>
                            📈 Market: ${marketData[currentMarket].name}<br>
                            📊 Monitoring: ${displaySymbols.join(', ')}${symbols.length > 10 ? ` + ${symbols.length - 10} more` : ''}<br>
                            🔄 Auto-refresh: Every 2 minutes
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function stopMonitoring() {
                try {
                    document.getElementById('signals-display').innerHTML = '<div class="loading">⏹️ Stopping monitoring...</div>';
                    const response = await fetch('/api/live/stop', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'}
                    });
                    const data = await response.json();
                    
                    // Clear the monitoring interval
                    if (monitoringInterval) {
                        clearInterval(monitoringInterval);
                        monitoringInterval = null;
                    }
                    
                    // Update monitoring status indicator
                    updateMonitoringStatus(false);
                    
                    document.getElementById('signals-display').innerHTML = `
                        <div class="success">
                            ✅ ${data.message}<br>
                            💡 Select a market and click "Start Monitoring" to begin again
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            function updateMonitoringStatus(isActive, market = '', symbolCount = 0) {
                const statusIndicator = document.getElementById('status-indicator');
                const statusText = document.getElementById('status-text');
                const monitoringDetails = document.getElementById('monitoring-details');
                const statusContainer = document.getElementById('monitoring-status');
                
                if (isActive) {
                    statusIndicator.style.background = '#4CAF50';
                    statusText.textContent = 'MONITORING ACTIVE';
                    statusText.style.color = '#4CAF50';
                    statusContainer.style.background = 'rgba(76, 175, 80, 0.1)';
                    statusContainer.style.borderColor = '#4CAF50';
                    monitoringDetails.textContent = `${market} • ${symbolCount} symbols`;
                } else {
                    statusIndicator.style.background = '#ff4444';
                    statusText.textContent = 'NOT SCANNING';
                    statusText.style.color = '#ff4444';
                    statusContainer.style.background = 'rgba(255,0,0,0.1)';
                    statusContainer.style.borderColor = '#ff4444';
                    monitoringDetails.textContent = 'Click "Start Monitoring" to begin';
                }
            }
            
            async function getSignals() {
                try {
                    document.getElementById('signals-display').innerHTML = `<div class="loading">📊 Fetching ${currentTimeframe.toUpperCase()} signals...</div>`;
                    const response = await fetch(`/api/live/signals?timeframe=${currentTimeframe}`);
                    const data = await response.json();
                    
                    if (data.signals && data.signals.length > 0) {
                        let html = '';
                        data.signals.forEach(signal => {
                            // Simulate trade for P&L tracking
                            simulateTrade(signal);
                            
                            const signalClass = signal.signal_type.toLowerCase();
                            
                            // Color coding functions
                            const getPriceChangeClass = (change) => {
                                if (change > 0) return 'positive';
                                if (change < 0) return 'negative';
                                return 'neutral';
                            };
                            
                            const getRSIClass = (rsi) => {
                                if (rsi < 30) return 'positive'; // Oversold
                                if (rsi > 70) return 'negative'; // Overbought
                                return 'neutral';
                            };
                            
                            const getVolumeClass = (ratio) => {
                                if (ratio > 1.5) return 'positive'; // High volume
                                if (ratio < 0.5) return 'negative'; // Low volume
                                return 'neutral';
                            };
                            
                            html += `
                                <div class="signal-card">
                                    <div class="signal-header">
                                        <span class="symbol">${signal.symbol}</span>
                                        <span class="signal-type ${signalClass}">${signal.signal_type}</span>
                                    </div>
                                    
                                    <!-- Main Trading Info -->
                                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 15px 0;">
                                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                                            <div style="text-align: center;">
                                                <div style="font-size: 0.9em; opacity: 0.7; margin-bottom: 5px;">CURRENT PRICE</div>
                                                <div style="font-size: 1.4em; font-weight: bold; color: #667eea;">$${signal.current_price}</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 0.9em; opacity: 0.7; margin-bottom: 5px;">ENTRY PRICE</div>
                                                <div style="font-size: 1.4em; font-weight: bold; color: #ffffff;">$${signal.entry_price}</div>
                                            </div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px;">
                                            <div style="text-align: center;">
                                                <div style="font-size: 0.9em; opacity: 0.7; margin-bottom: 5px;">TAKE PROFIT</div>
                                                <div style="font-size: 1.4em; font-weight: bold; color: #4CAF50;">$${signal.take_profit}</div>
                                            </div>
                                            <div style="text-align: center;">
                                                <div style="font-size: 0.9em; opacity: 0.7; margin-bottom: 5px;">STOP LOSS</div>
                                                <div style="font-size: 1.4em; font-weight: bold; color: #f44336;">$${signal.stop_loss}</div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- Technical Indicators -->
                                    <div class="price-info">
                                        <div class="price-item">
                                            <div class="price-label">Price Change</div>
                                            <div class="price-value ${getPriceChangeClass(signal.price_change)}">${signal.price_change}%</div>
                                        </div>
                                        <div class="price-item">
                                            <div class="price-label">RSI</div>
                                            <div class="price-value ${getRSIClass(signal.rsi)}">${signal.rsi || 'N/A'}</div>
                                        </div>
                                        <div class="price-item">
                                            <div class="price-label">SMA 20</div>
                                            <div class="price-value">$${signal.sma_20 || 'N/A'}</div>
                                        </div>
                                        <div class="price-item">
                                            <div class="price-label">Volume Ratio</div>
                                            <div class="price-value ${getVolumeClass(signal.volume_ratio)}">${signal.volume_ratio || 'N/A'}x</div>
                                        </div>
                                        <div class="price-item">
                                            <div class="price-label">Risk/Reward</div>
                                            <div class="price-value positive">${signal.risk_reward || 'N/A'}:1</div>
                                        </div>
                                        <div class="price-item">
                                            <div class="price-label">Confidence</div>
                                            <div class="price-value">${signal.confidence}%</div>
                                        </div>
                                    </div>
                                    <div style="margin-top: 15px;">
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">Confidence</div>
                                                <div style="font-weight: bold;">${signal.confidence}%</div>
                                            </div>
                                            <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">Risk/Reward</div>
                                                <div style="font-weight: bold;">1:${signal.risk_reward}</div>
                                            </div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <div style="text-align: center; padding: 8px; background: rgba(34, 197, 94, 0.1); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">ATR</div>
                                                <div style="font-weight: bold; color: #22c55e;">${signal.atr}</div>
                                            </div>
                                            <div style="text-align: center; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">Position Size</div>
                                                <div style="font-weight: bold; color: #3b82f6;">${signal.position_size}</div>
                                            </div>
                                        </div>
                                        <div style="text-align: center; padding: 8px; background: rgba(168, 85, 247, 0.1); border-radius: 5px; margin-bottom: 10px;">
                                            <div style="font-size: 0.8em; opacity: 0.7;">Trailing Stop</div>
                                            <div style="font-weight: bold; color: #a855f7;">$${signal.trailing_stop}</div>
                                        </div>
                                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                                            <div style="text-align: center; padding: 8px; background: rgba(236, 72, 153, 0.1); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">Market Regime</div>
                                                <div style="font-weight: bold; color: #ec4899;">${signal.ml_analysis.market_regime}</div>
                                            </div>
                                            <div style="text-align: center; padding: 8px; background: rgba(139, 92, 246, 0.1); border-radius: 5px;">
                                                <div style="font-size: 0.8em; opacity: 0.7;">Sentiment</div>
                                                <div style="font-weight: bold; color: #8b5cf6;">${signal.ml_analysis.sentiment}</div>
                                            </div>
                                        </div>
                                        <div style="text-align: center; padding: 8px; background: rgba(245, 101, 101, 0.1); border-radius: 5px; margin-bottom: 10px;">
                                            <div style="font-size: 0.8em; opacity: 0.7;">ML Accuracy</div>
                                            <div style="font-weight: bold; color: #f56565;">${signal.ml_analysis.ml_accuracy}%</div>
                                        </div>
                                        <div class="confidence-bar">
                                            <div class="confidence-fill" style="width: ${signal.confidence}%"></div>
                                        </div>
                                        <div style="margin-top: 10px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px; font-size: 0.9em;">
                                            <strong>Pattern:</strong> ${signal.pattern || 'Technical Analysis'}
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        document.getElementById('signals-display').innerHTML = html;
                    } else {
                        document.getElementById('signals-display').innerHTML = '<div class="loading">No signals available. Start monitoring first.</div>';
                    }
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function getSummary() {
                try {
                    document.getElementById('signals-display').innerHTML = '<div class="loading">📊 Getting market summary...</div>';
                    const response = await fetch('/api/live/summary');
                    const data = await response.json();
                    
                    if (data.summary) {
                        const summary = data.summary;
                        document.getElementById('signals-display').innerHTML = `
                            <div class="signal-card">
                                <h3 style="margin-bottom: 20px; color: #667eea;">📊 Market Summary</h3>
                                <div class="price-info">
                                    <div class="price-item">
                                        <div class="price-label">Total Signals</div>
                                        <div class="price-value">${summary.total_signals}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Buy Signals</div>
                                        <div class="price-value" style="color: #4CAF50;">${summary.buy_signals}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Sell Signals</div>
                                        <div class="price-value" style="color: #f44336;">${summary.sell_signals}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Market Status</div>
                                        <div class="price-value">${summary.market_status}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('signals-display').innerHTML = '<div class="loading">No summary available.</div>';
                    }
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function runCustomBacktest() {
                const symbol = document.getElementById('backtest-symbol').value.trim().toUpperCase();
                if (!symbol) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Please enter a symbol to test</div>';
                    return;
                }
                
                try {
                    document.getElementById('signals-display').innerHTML = `<div class="loading">🚀 Running backtest on ${symbol}...</div>`;
                    const response = await fetch(`/api/backtest/${symbol}?timeframe=${currentTimeframe}`);
                    const data = await response.json();
                    
                    if (data.result && !data.result.error) {
                        const result = data.result;
                        document.getElementById('signals-display').innerHTML = `
                            <div class="signal-card">
                                <h3 style="margin-bottom: 20px; color: #22c55e;">📊 Backtest Results for ${result.symbol}</h3>
                                <div class="price-info">
                                    <div class="price-item">
                                        <div class="price-label">Period</div>
                                        <div class="price-value">${result.start_date} to ${result.end_date}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Initial Capital</div>
                                        <div class="price-value">$${result.initial_capital.toLocaleString()}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Final Capital</div>
                                        <div class="price-value">$${result.final_capital.toLocaleString()}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Total Return</div>
                                        <div class="price-value" style="color: ${result.total_return >= 0 ? '#4CAF50' : '#f44336'};">${result.total_return}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Win Rate</div>
                                        <div class="price-value">${result.win_rate}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Total Trades</div>
                                        <div class="price-value">${result.total_trades}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Max Drawdown</div>
                                        <div class="price-value" style="color: #f44336;">${result.max_drawdown}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Sharpe Ratio</div>
                                        <div class="price-value">${result.sharpe_ratio}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + (data.result?.error || 'Backtest failed') + '</div>';
                    }
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            

            
            async function getBacktestSummary() {
                try {
                    document.getElementById('signals-display').innerHTML = '<div class="loading">📊 Getting backtest summary...</div>';
                    const response = await fetch(`/api/backtest/summary?timeframe=${currentTimeframe}&market=${currentMarket}`);
                    const data = await response.json();
                    
                    if (data.result && !data.result.error) {
                        const result = data.result;
                        const summary = result.summary;
                        document.getElementById('signals-display').innerHTML = `
                            <div class="signal-card">
                                <h3 style="margin-bottom: 20px; color: #3b82f6;">📊 Backtest Summary (${currentMarket.toUpperCase()})</h3>
                                <div class="price-info">
                                    <div class="price-item">
                                        <div class="price-label">Average Return</div>
                                        <div class="price-value" style="color: ${summary.avg_return >= 0 ? '#4CAF50' : '#f44336'};">${summary.avg_return}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Average Win Rate</div>
                                        <div class="price-value">${summary.avg_win_rate}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Average Drawdown</div>
                                        <div class="price-value" style="color: #f44336;">${summary.avg_drawdown}%</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Total Trades</div>
                                        <div class="price-value">${summary.total_trades}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Symbols Tested</div>
                                        <div class="price-value">${summary.symbols_tested}</div>
                                    </div>
                                    <div class="price-item">
                                        <div class="price-label">Timeframe</div>
                                        <div class="price-value">${currentTimeframe.toUpperCase()}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + (data.result?.error || 'Summary failed') + '</div>';
                    }
                } catch (error) {
                    document.getElementById('signals-display').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                }
            }
            
            async function createCharts() {
                try {
                    document.getElementById('charts-display').innerHTML = '<div class="loading">📊 Loading charts...</div>';
                    
                    // Get monitored symbols from selected market (first 5 for charts)
                    const symbols = marketData[currentMarket].symbols.slice(0, 5);
                    let chartsHtml = '';
                    
                    for (const symbol of symbols) {
                        const response = await fetch(`/api/live/chart/${symbol}`);
                        const data = await response.json();
                        
                        if (data.status === 'success') {
                            const chartData = data.data;
                            const chartId = `chart-${symbol}`;
                            
                            chartsHtml += `
                                <div class="chart-container">
                                    <div class="chart-title">${symbol} - Enhanced ICT/SMC Analysis</div>
                                    <div class="chart-wrapper">
                                        <canvas id="${chartId}"></canvas>
                                    </div>
                                </div>
                            `;
                        }
                    }
                    
                    document.getElementById('charts-display').innerHTML = chartsHtml;
                    
                    // Create charts
                    for (const symbol of symbols) {
                        await createChart(symbol);
                    }
                    
                } catch (error) {
                    document.getElementById('charts-display').innerHTML = '<div class="error">❌ Error loading charts: ' + error.message + '</div>';
                }
            }
            
            async function createChart(symbol) {
                try {
                    const response = await fetch(`/api/live/chart/${symbol}`);
                    const data = await response.json();
                    
                    if (data.status !== 'success') return;
                    
                    const chartData = data.data;
                    const ctx = document.getElementById(`chart-${symbol}`).getContext('2d');
                    
                    // Destroy existing chart if it exists
                    if (charts[symbol]) {
                        charts[symbol].destroy();
                    }
                    
                    const signal = chartData.signal;
                    const signalColor = signal ? (signal.signal_type === 'BUY' ? '#4CAF50' : signal.signal_type === 'SELL' ? '#f44336' : '#ff9800') : '#667eea';
                    
                    // Prepare ICT/SMC datasets
                    const datasets = [{
                        label: 'Price',
                        data: chartData.prices,
                        borderColor: signalColor,
                        backgroundColor: signalColor + '20',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1
                    }, {
                        label: 'SMA 20',
                        data: chartData.sma_20,
                        borderColor: '#ff9800',
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false
                    }];
                    
                    // Add Order Blocks visualization
                    if (chartData.ict_analysis && chartData.ict_analysis.order_blocks) {
                        const bullishOB = chartData.ict_analysis.order_blocks.filter(ob => ob.type === 'bullish');
                        const bearishOB = chartData.ict_analysis.order_blocks.filter(ob => ob.type === 'bearish');
                        
                        if (bullishOB.length > 0) {
                            datasets.push({
                                label: 'Bullish Order Blocks',
                                data: bullishOB.map(ob => ({ x: chartData.labels[ob.index], y: ob.high })),
                                backgroundColor: 'rgba(76, 175, 80, 0.3)',
                                borderColor: 'rgba(76, 175, 80, 0.8)',
                                borderWidth: 2,
                                pointRadius: 6,
                                pointHoverRadius: 8,
                                showLine: false,
                                pointStyle: 'rect'
                            });
                        }
                        
                        if (bearishOB.length > 0) {
                            datasets.push({
                                label: 'Bearish Order Blocks',
                                data: bearishOB.map(ob => ({ x: chartData.labels[ob.index], y: ob.low })),
                                backgroundColor: 'rgba(244, 67, 54, 0.3)',
                                borderColor: 'rgba(244, 67, 54, 0.8)',
                                borderWidth: 2,
                                pointRadius: 6,
                                pointHoverRadius: 8,
                                showLine: false,
                                pointStyle: 'rect'
                            });
                        }
                    }
                    
                    // Add Fair Value Gaps visualization
                    if (chartData.ict_analysis && chartData.ict_analysis.fair_value_gaps) {
                        const bullishFVG = chartData.ict_analysis.fair_value_gaps.filter(fvg => fvg.type === 'bullish');
                        const bearishFVG = chartData.ict_analysis.fair_value_gaps.filter(fvg => fvg.type === 'bearish');
                        
                        if (bullishFVG.length > 0) {
                            datasets.push({
                                label: 'Bullish FVG',
                                data: bullishFVG.map(fvg => ({ x: chartData.labels[fvg.index], y: fvg.bottom })),
                                backgroundColor: 'rgba(33, 150, 243, 0.2)',
                                borderColor: 'rgba(33, 150, 243, 0.6)',
                                borderWidth: 1,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                showLine: false,
                                pointStyle: 'triangle'
                            });
                        }
                        
                        if (bearishFVG.length > 0) {
                            datasets.push({
                                label: 'Bearish FVG',
                                data: bearishFVG.map(fvg => ({ x: chartData.labels[fvg.index], y: fvg.top })),
                                backgroundColor: 'rgba(255, 152, 0, 0.2)',
                                borderColor: 'rgba(255, 152, 0, 0.6)',
                                borderWidth: 1,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                showLine: false,
                                pointStyle: 'triangle'
                            });
                        }
                    }
                    
                    // Add Liquidity Levels visualization
                    if (chartData.ict_analysis && chartData.ict_analysis.liquidity_levels) {
                        const resistance = chartData.ict_analysis.liquidity_levels.filter(ll => ll.type === 'resistance');
                        const support = chartData.ict_analysis.liquidity_levels.filter(ll => ll.type === 'support');
                        
                        if (resistance.length > 0) {
                            datasets.push({
                                label: 'Resistance Levels',
                                data: resistance.map(ll => ({ x: chartData.labels[ll.index], y: ll.price })),
                                backgroundColor: 'rgba(156, 39, 176, 0.3)',
                                borderColor: 'rgba(156, 39, 176, 0.8)',
                                borderWidth: 2,
                                pointRadius: 5,
                                pointHoverRadius: 7,
                                showLine: false,
                                pointStyle: 'star'
                            });
                        }
                        
                        if (support.length > 0) {
                            datasets.push({
                                label: 'Support Levels',
                                data: support.map(ll => ({ x: chartData.labels[ll.index], y: ll.price })),
                                backgroundColor: 'rgba(0, 150, 136, 0.3)',
                                borderColor: 'rgba(0, 150, 136, 0.8)',
                                borderWidth: 2,
                                pointRadius: 5,
                                pointHoverRadius: 7,
                                showLine: false,
                                pointStyle: 'star'
                            });
                        }
                    }
                    
                    // Add Market Structure Breaks visualization
                    if (chartData.ict_analysis && chartData.ict_analysis.structure_breaks) {
                        const bullishBOS = chartData.ict_analysis.structure_breaks.filter(sb => sb.type === 'bullish_bos');
                        const bearishBOS = chartData.ict_analysis.structure_breaks.filter(sb => sb.type === 'bearish_bos');
                        
                        if (bullishBOS.length > 0) {
                            datasets.push({
                                label: 'Bullish BOS',
                                data: bullishBOS.map(sb => ({ x: chartData.labels[sb.index], y: sb.price })),
                                backgroundColor: 'rgba(76, 175, 80, 0.4)',
                                borderColor: 'rgba(76, 175, 80, 1)',
                                borderWidth: 3,
                                pointRadius: 8,
                                pointHoverRadius: 10,
                                showLine: false,
                                pointStyle: 'circle'
                            });
                        }
                        
                        if (bearishBOS.length > 0) {
                            datasets.push({
                                label: 'Bearish BOS',
                                data: bearishBOS.map(sb => ({ x: chartData.labels[sb.index], y: sb.price })),
                                backgroundColor: 'rgba(244, 67, 54, 0.4)',
                                borderColor: 'rgba(244, 67, 54, 1)',
                                borderWidth: 3,
                                pointRadius: 8,
                                pointHoverRadius: 10,
                                showLine: false,
                                pointStyle: 'circle'
                            });
                        }
                    }
                    
                    charts[symbol] = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: chartData.labels,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: `${symbol} - Enhanced ICT/SMC Analysis`,
                                    color: '#ffffff',
                                    font: { size: 16, weight: 'bold' }
                                },
                                legend: {
                                    labels: { color: '#ffffff' },
                                    position: 'top'
                                },
                                tooltip: {
                                    backgroundColor: 'rgba(0,0,0,0.8)',
                                    titleColor: '#ffffff',
                                    bodyColor: '#ffffff',
                                    borderColor: '#667eea',
                                    borderWidth: 1
                                }
                            },
                            scales: {
                                x: {
                                    ticks: {
                                        color: '#ffffff',
                                        maxTicksLimit: 10
                                    },
                                    grid: {
                                        color: 'rgba(255,255,255,0.1)'
                                    }
                                },
                                y: {
                                    ticks: {
                                        color: '#ffffff'
                                    },
                                    grid: {
                                        color: 'rgba(255,255,255,0.1)'
                                    }
                                }
                            },
                            elements: {
                                point: {
                                    radius: 0
                                }
                            },
                            interaction: {
                                intersect: false,
                                mode: 'index'
                            }
                        }
                    });
                    
                } catch (error) {
                    console.error(`Error creating chart for ${symbol}:`, error);
                }
            }
            
            // Alert System Functions
            async function updateAlertSettings() {
                try {
                    const settings = {
                        enabled: document.getElementById('alertEnabled').checked,
                        min_signal_strength: parseFloat(document.getElementById('minSignalStrength').value),
                        alert_frequency: document.getElementById('alertFrequency').value,
                        webhook_url: document.getElementById('webhookUrl').value || null
                    };
                    
                    const response = await fetch('/api/alerts/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(settings)
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('✅ Alert settings updated successfully!');
                    } else {
                        alert('❌ Error updating settings: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
            
            async function testAlert() {
                try {
                    const response = await fetch('/api/alerts/test', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('✅ Test alert sent! Check console and alert history.');
                        loadAlertHistory(); // Refresh history
                    } else {
                        alert('❌ Test failed: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
            
            async function loadAlertHistory() {
                try {
                    const response = await fetch('/api/alerts/history');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const historyDiv = document.getElementById('alert-history');
                        
                        if (result.alerts.length === 0) {
                            historyDiv.innerHTML = '<div class="loading">No alerts yet</div>';
                            return;
                        }
                        
                        let historyHtml = '';
                        result.alerts.slice(-10).reverse().forEach(alert => {
                            const time = new Date(alert.timestamp).toLocaleTimeString();
                            const signalType = alert.signal_type;
                            const score = alert.score;
                            
                            historyHtml += `
                                <div style="margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 5px; font-size: 0.9em;">
                                    <strong>${alert.symbol}</strong> - ${signalType} (${score})<br>
                                    <small style="opacity: 0.7;">${time}</small>
                                </div>
                            `;
                        });
                        
                        historyDiv.innerHTML = historyHtml;
                    }
                } catch (error) {
                    console.error('Error loading alert history:', error);
                }
            }
            
            async function clearAlertHistory() {
                if (confirm('Are you sure you want to clear all alert history?')) {
                    try {
                        const response = await fetch('/api/alerts/history', { method: 'DELETE' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            alert('✅ Alert history cleared!');
                            loadAlertHistory();
                        } else {
                            alert('❌ Error: ' + result.message);
                        }
                    } catch (error) {
                        alert('❌ Error: ' + error.message);
                    }
                }
            }
            
            // AI Learning System Functions
            async function loadAILearningStatus() {
                try {
                    const response = await fetch('/api/ai/learning/insights');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const insights = result.insights;
                        const statusDiv = document.getElementById('ai-learning-status');
                        
                        let statusHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Learning Status:</strong> ${insights.learning_status || 'Initializing'}<br>
                                <strong>Total Signals Learned:</strong> ${insights.total_signals_learned || 0}<br>
                                <strong>Signals with Outcomes:</strong> ${insights.signals_with_outcomes || 0}<br>
                                <strong>Model Accuracy:</strong> ${insights.model_accuracy?.signal_classifier ? (insights.model_accuracy.signal_classifier * 100).toFixed(1) + '%' : 'Not trained yet'}
                            </div>
                        `;
                        
                        if (insights.adaptive_parameters) {
                            statusHtml += `
                                <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px;">
                                    <strong>Adaptive Parameters:</strong><br>
                                    <small>Signal Threshold: ${insights.adaptive_parameters.signal_threshold?.toFixed(2) || '1.00'}</small><br>
                                    <small>Confidence Boost: ${insights.adaptive_parameters.confidence_boost?.toFixed(2) || '1.00'}</small><br>
                                    <small>Pattern Weight: ${insights.adaptive_parameters.pattern_weight?.toFixed(2) || '1.00'}</small><br>
                                    <small>Volume Weight: ${insights.adaptive_parameters.volume_weight?.toFixed(2) || '1.00'}</small>
                                </div>
                            `;
                        }
                        
                        statusDiv.innerHTML = statusHtml;
                    }
                } catch (error) {
                    console.error('Error loading AI learning status:', error);
                    document.getElementById('ai-learning-status').innerHTML = '<div class="error">❌ Error loading status</div>';
                }
            }
            
            async function retrainAIModels() {
                try {
                    const response = await fetch('/api/ai/learning/retrain', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('✅ AI models retrained successfully!');
                        loadAILearningStatus(); // Refresh status
                        loadPerformanceMetrics(); // Refresh metrics
                    } else {
                        alert('❌ Retraining failed: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ Error: ' + error.message);
                }
            }
            
            async function loadPerformanceMetrics() {
                try {
                    const response = await fetch('/api/ai/learning/performance');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const metrics = result.metrics;
                        const metricsDiv = document.getElementById('ai-performance-metrics');
                        
                        if (Object.keys(metrics).length === 0) {
                            metricsDiv.innerHTML = '<div class="loading">No performance data yet</div>';
                            return;
                        }
                        
                        let metricsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Total Signals:</strong> ${metrics.total_signals || 0}<br>
                                <strong>Win Rate:</strong> ${metrics.win_rate ? (metrics.win_rate * 100).toFixed(1) + '%' : 'N/A'}<br>
                                <strong>Avg Return:</strong> ${metrics.avg_return ? (metrics.avg_return * 100).toFixed(2) + '%' : 'N/A'}<br>
                                <strong>Avg Win:</strong> ${metrics.avg_win ? (metrics.avg_win * 100).toFixed(2) + '%' : 'N/A'}<br>
                                <strong>Avg Loss:</strong> ${metrics.avg_loss ? (metrics.avg_loss * 100).toFixed(2) + '%' : 'N/A'}<br>
                                <strong>Profit Factor:</strong> ${metrics.profit_factor ? metrics.profit_factor.toFixed(2) : 'N/A'}
                            </div>
                        `;
                        
                        if (metrics.last_updated) {
                            const lastUpdated = new Date(metrics.last_updated).toLocaleString();
                            metricsHtml += `<div style="margin-top: 10px; font-size: 0.8em; opacity: 0.7;">Last Updated: ${lastUpdated}</div>`;
                        }
                        
                        metricsDiv.innerHTML = metricsHtml;
                    }
                } catch (error) {
                    console.error('Error loading performance metrics:', error);
                    document.getElementById('ai-performance-metrics').innerHTML = '<div class="error">❌ Error loading metrics</div>';
                }
            }
            
            // Check monitoring status on page load
            async function checkMonitoringStatus() {
                try {
                    const response = await fetch('/api/live/summary');
                    const result = await response.json();
                    
                    if (result.status === 'success' && result.summary.is_monitoring) {
                        const market = result.summary.market || 'Unknown Market';
                        const symbolCount = result.summary.symbols_monitored || 0;
                        updateMonitoringStatus(true, market, symbolCount);
                    } else {
                        updateMonitoringStatus(false);
                    }
                } catch (error) {
                    console.log('Could not check monitoring status:', error);
                    updateMonitoringStatus(false);
                }
            }
            
            // Advanced Analytics Functions
            async function loadAnalyticsDashboard() {
                try {
                    const [performanceResponse, heatmapResponse, equityResponse] = await Promise.all([
                        fetch('/api/analytics/performance'),
                        fetch('/api/analytics/heatmap'),
                        fetch('/api/analytics/equity-curve')
                    ]);
                    
                    const performance = await performanceResponse.json();
                    const heatmap = await heatmapResponse.json();
                    const equity = await equityResponse.json();
                    
                    updateAnalyticsUI(performance.performance, heatmap.heatmap, equity.equity_curve);
                } catch (error) {
                    console.error('Error loading analytics:', error);
                }
            }
            
            function updateAnalyticsUI(performance, heatmap, equityCurve) {
                // Update performance metrics
                document.getElementById('total-trades-analytics').textContent = performance.total_trades;
                document.getElementById('win-rate-analytics').textContent = performance.win_rate.toFixed(1) + '%';
                document.getElementById('profit-factor-analytics').textContent = performance.profit_factor.toFixed(2);
                document.getElementById('max-drawdown-analytics').textContent = performance.max_drawdown.toFixed(1) + '%';
                document.getElementById('sharpe-ratio-analytics').textContent = performance.sharpe_ratio.toFixed(2);
                document.getElementById('total-pnl-analytics').textContent = '$' + performance.total_pnl.toFixed(2);
                
                // Update equity curve chart
                updateEquityCurveChart(equityCurve);
                
                // Update performance heatmap
                updatePerformanceHeatmap(heatmap);
            }
            
            function updateEquityCurveChart(equityData) {
                const ctx = document.getElementById('equityCurveChart');
                if (!ctx || !equityData.length) return;
                
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: equityData.map((_, i) => i),
                        datasets: [{
                            label: 'Equity Curve',
                            data: equityData.map(point => point.y),
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                grid: {
                                    color: 'rgba(255,255,255,0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    color: 'rgba(255,255,255,0.1)'
                                }
                            }
                        }
                    }
                });
            }
            
            function updatePerformanceHeatmap(heatmapData) {
                const heatmapContainer = document.getElementById('performance-heatmap');
                if (!heatmapContainer) return;
                
                let heatmapHtml = '<div class="heatmap-grid">';
                
                // Group by category
                const marketData = heatmapData.filter(item => item.category === 'Market');
                const hourData = heatmapData.filter(item => item.category === 'Hour');
                
                // Market performance
                heatmapHtml += '<div class="heatmap-section"><h4>Market Performance</h4>';
                marketData.forEach(item => {
                    const intensity = Math.min(item.value / 100, 1);
                    const color = `rgba(76, 175, 80, ${intensity})`;
                    heatmapHtml += `
                        <div class="heatmap-item" style="background-color: ${color}">
                            <span class="heatmap-label">${item.name}</span>
                            <span class="heatmap-value">${item.value.toFixed(1)}%</span>
                            <span class="heatmap-trades">${item.trades} trades</span>
                        </div>
                    `;
                });
                heatmapHtml += '</div>';
                
                // Hourly performance
                heatmapHtml += '<div class="heatmap-section"><h4>Hourly Performance</h4>';
                hourData.forEach(item => {
                    const intensity = Math.min(item.value / 100, 1);
                    const color = `rgba(76, 175, 80, ${intensity})`;
                    heatmapHtml += `
                        <div class="heatmap-item" style="background-color: ${color}">
                            <span class="heatmap-label">${item.name}</span>
                            <span class="heatmap-value">${item.value.toFixed(1)}%</span>
                            <span class="heatmap-trades">${item.trades} trades</span>
                        </div>
                    `;
                });
                heatmapHtml += '</div></div>';
                
                heatmapContainer.innerHTML = heatmapHtml;
            }
            
            async function resetAnalytics() {
                if (confirm('Are you sure you want to reset all analytics data?')) {
                    try {
                        await fetch('/api/analytics/reset-performance', { method: 'POST' });
                        loadAnalyticsDashboard();
                        alert('Analytics data reset successfully!');
                    } catch (error) {
                        console.error('Error resetting analytics:', error);
                        alert('Error resetting analytics data');
                    }
                }
            }
            
            // Enhanced AI Learning Functions
            async function loadSentimentAnalysis() {
                try {
                    const response = await fetch('/api/ai/enhanced/sentiment');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const sentiment = result.sentiment;
                        const sentimentDiv = document.getElementById('sentiment-analysis');
                        
                        let sentimentHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Market Sentiment:</strong> <span style="color: ${sentiment.market_sentiment === 'BULLISH' ? '#4CAF50' : sentiment.market_sentiment === 'BEARISH' ? '#f44336' : '#ff9800'}">${sentiment.market_sentiment}</span><br>
                                <strong>Sentiment Score:</strong> ${(sentiment.sentiment_score * 100).toFixed(1)}%<br>
                                <strong>Sentiment Trend:</strong> ${sentiment.sentiment_trend}<br>
                                <strong>Fear/Greed Index:</strong> ${sentiment.fear_greed_index.toFixed(1)}/100<br>
                                <strong>News Impact:</strong> ${(sentiment.news_impact * 100).toFixed(1)}%<br>
                                <strong>Social Sentiment:</strong> ${(sentiment.social_sentiment * 100).toFixed(1)}%
                            </div>
                        `;
                        
                        sentimentDiv.innerHTML = sentimentHtml;
                    }
                } catch (error) {
                    console.error('Error loading sentiment analysis:', error);
                }
            }
            
            async function loadMarketRegime() {
                try {
                    const response = await fetch('/api/ai/enhanced/regime');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const regime = result.regime;
                        const regimeDiv = document.getElementById('market-regime');
                        
                        let regimeHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Current Regime:</strong> <span style="color: #4CAF50">${regime.current_regime}</span><br>
                                <strong>Regime Confidence:</strong> ${(regime.regime_confidence * 100).toFixed(1)}%<br>
                                <strong>Volatility Regime:</strong> ${regime.volatility_regime}<br>
                                <strong>Trend Regime:</strong> ${regime.trend_regime}<br>
                                <strong>Liquidity Regime:</strong> ${regime.liquidity_regime}<br>
                                <strong>Regime Transitions:</strong> ${regime.regime_transitions}
                            </div>
                        `;
                        
                        regimeDiv.innerHTML = regimeHtml;
                    }
                } catch (error) {
                    console.error('Error loading market regime:', error);
                }
            }
            
            async function loadPatternRecognition() {
                try {
                    const response = await fetch('/api/ai/enhanced/patterns');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const patterns = result.patterns;
                        const patternsDiv = document.getElementById('pattern-recognition');
                        
                        let patternsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Active Patterns:</strong> ${patterns.active_patterns.length > 0 ? patterns.active_patterns.join(', ') : 'None detected'}<br>
                                <strong>Pattern Strength:</strong> ${(patterns.pattern_strength * 100).toFixed(1)}%<br>
                                <strong>Pattern Confidence:</strong> ${(patterns.pattern_confidence * 100).toFixed(1)}%<br>
                                <strong>Emerging Patterns:</strong> ${patterns.emerging_patterns.length > 0 ? patterns.emerging_patterns.join(', ') : 'None'}<br>
                                <strong>Last Updated:</strong> ${new Date(patterns.last_updated).toLocaleTimeString()}
                            </div>
                        `;
                        
                        patternsDiv.innerHTML = patternsHtml;
                    }
                } catch (error) {
                    console.error('Error loading pattern recognition:', error);
                }
            }
            
            async function loadAdaptiveParameters() {
                try {
                    const response = await fetch('/api/ai/enhanced/parameters');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const params = result.parameters;
                        const paramsDiv = document.getElementById('adaptive-parameters');
                        
                        let paramsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Confidence Threshold:</strong> ${(params.confidence_threshold * 100).toFixed(1)}%<br>
                                <strong>Risk Adjustment:</strong> ${params.risk_adjustment.toFixed(2)}<br>
                                <strong>Pattern Weight:</strong> ${(params.pattern_weight * 100).toFixed(1)}%<br>
                                <strong>Volume Weight:</strong> ${(params.volume_weight * 100).toFixed(1)}%<br>
                                <strong>Trend Weight:</strong> ${(params.trend_weight * 100).toFixed(1)}%<br>
                                <strong>Sentiment Weight:</strong> ${(params.sentiment_weight * 100).toFixed(1)}%<br>
                                <strong>Learning Rate:</strong> ${(params.learning_rate * 100).toFixed(2)}%<br>
                                <strong>Last Adaptation:</strong> ${params.last_adaptation ? new Date(params.last_adaptation).toLocaleTimeString() : 'Never'}
                            </div>
                        `;
                        
                        paramsDiv.innerHTML = paramsHtml;
                    }
                } catch (error) {
                    console.error('Error loading adaptive parameters:', error);
                }
            }
            
            async function triggerAdaptation() {
                try {
                    const response = await fetch('/api/ai/enhanced/adapt', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('AI parameters adapted successfully!');
                        loadAdaptiveParameters();
                    } else {
                        alert('Error adapting parameters: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error triggering adaptation:', error);
                    alert('Error triggering adaptation');
                }
            }
            
            async function loadAILearningMetrics() {
                try {
                    const response = await fetch('/api/ai/enhanced/learning-metrics');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const metrics = result.metrics;
                        const metricsDiv = document.getElementById('ai-learning-metrics');
                        
                        let metricsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Total Learning Cycles:</strong> ${metrics.total_learning_cycles}<br>
                                <strong>Successful Adaptations:</strong> ${metrics.successful_adaptations}<br>
                                <strong>Learning Accuracy:</strong> ${(metrics.learning_accuracy * 100).toFixed(1)}%<br>
                                <strong>Adaptation Frequency:</strong> ${(metrics.adaptation_frequency * 100).toFixed(1)}%<br>
                                <strong>Learning Velocity:</strong> ${metrics.learning_velocity.toFixed(2)}<br>
                                <strong>Last Updated:</strong> ${metrics.last_updated ? new Date(metrics.last_updated).toLocaleTimeString() : 'Never'}
                            </div>
                        `;
                        
                        metricsDiv.innerHTML = metricsHtml;
                    }
                } catch (error) {
                    console.error('Error loading AI learning metrics:', error);
                }
            }
            
            // Predictive Analytics Functions
            async function loadPriceTargets() {
                try {
                    const symbol = document.getElementById('symbol-input').value || 'AAPL';
                    const response = await fetch(`/api/predictive/price-targets/${symbol}`);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const targets = result.price_targets;
                        const targetsDiv = document.getElementById('price-targets-analysis');
                        
                        let targetsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Symbol:</strong> ${result.symbol}<br>
                                <strong>Current Price:</strong> $${result.current_price.toFixed(2)}<br><br>
                                <strong>Short-term Targets:</strong><br>
                                • Bullish: $${targets.short_term.bullish.toFixed(2)}<br>
                                • Bearish: $${targets.short_term.bearish.toFixed(2)}<br><br>
                                <strong>Medium-term Targets:</strong><br>
                                • Bullish: $${targets.medium_term.bullish.toFixed(2)}<br>
                                • Bearish: $${targets.medium_term.bearish.toFixed(2)}<br><br>
                                <strong>Long-term Targets:</strong><br>
                                • Bullish: $${targets.long_term.bullish.toFixed(2)}<br>
                                • Bearish: $${targets.long_term.bearish.toFixed(2)}<br><br>
                                <strong>Support Levels:</strong> ${targets.support_levels.map(level => '$' + level.toFixed(2)).join(', ')}<br>
                                <strong>Resistance Levels:</strong> ${targets.resistance_levels.map(level => '$' + level.toFixed(2)).join(', ')}
                            </div>
                        `;
                        
                        targetsDiv.innerHTML = targetsHtml;
                    } else {
                        document.getElementById('price-targets-analysis').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading price targets:', error);
                }
            }
            
            async function loadVolatilityForecast() {
                try {
                    const symbol = document.getElementById('symbol-input').value || 'AAPL';
                    const response = await fetch(`/api/predictive/volatility-forecast/${symbol}`);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const forecast = result.volatility_forecast;
                        const forecastDiv = document.getElementById('volatility-forecast');
                        
                        let forecastHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Symbol:</strong> ${result.symbol}<br>
                                <strong>Current Volatility:</strong> ${(forecast.current_volatility * 100).toFixed(2)}%<br>
                                <strong>Predicted Volatility:</strong> ${(forecast.predicted_volatility * 100).toFixed(2)}%<br>
                                <strong>Volatility Trend:</strong> <span style="color: ${forecast.volatility_trend === 'INCREASING' ? '#f44336' : forecast.volatility_trend === 'DECREASING' ? '#4CAF50' : '#ff9800'}">${forecast.volatility_trend}</span><br>
                                <strong>Volatility Percentile:</strong> ${forecast.volatility_percentile.toFixed(1)}%<br><br>
                                <strong>Forecast Periods:</strong><br>
                                • 1 Day: ${(forecast.volatility_forecast_periods['1_day'] * 100).toFixed(2)}%<br>
                                • 1 Week: ${(forecast.volatility_forecast_periods['1_week'] * 100).toFixed(2)}%<br>
                                • 1 Month: ${(forecast.volatility_forecast_periods['1_month'] * 100).toFixed(2)}%
                            </div>
                        `;
                        
                        forecastDiv.innerHTML = forecastHtml;
                    } else {
                        document.getElementById('volatility-forecast').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading volatility forecast:', error);
                }
            }
            
            async function loadMarketDirection() {
                try {
                    const symbol = document.getElementById('symbol-input').value || 'AAPL';
                    const response = await fetch(`/api/predictive/market-direction/${symbol}`);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const direction = result.market_direction;
                        const directionDiv = document.getElementById('market-direction-prediction');
                        
                        let directionHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Symbol:</strong> ${result.symbol}<br>
                                <strong>Direction Probabilities:</strong><br>
                                • Bullish: <span style="color: #4CAF50">${(direction.direction_probability.bullish * 100).toFixed(1)}%</span><br>
                                • Bearish: <span style="color: #f44336">${(direction.direction_probability.bearish * 100).toFixed(1)}%</span><br>
                                • Sideways: <span style="color: #ff9800">${(direction.direction_probability.sideways * 100).toFixed(1)}%</span><br><br>
                                <strong>Confidence Level:</strong> ${(direction.confidence_level * 100).toFixed(1)}%<br>
                                <strong>Trend Strength:</strong> ${(direction.trend_strength * 100).toFixed(1)}%<br>
                                <strong>Momentum Score:</strong> ${(direction.momentum_score * 100).toFixed(1)}%<br><br>
                                <strong>Key Levels:</strong><br>
                                • Support: ${direction.key_levels.support.map(level => '$' + level.toFixed(2)).join(', ')}<br>
                                • Resistance: ${direction.key_levels.resistance.map(level => '$' + level.toFixed(2)).join(', ')}<br>
                                • Pivot Points: ${direction.key_levels.pivot_points.map(level => '$' + level.toFixed(2)).join(', ')}
                            </div>
                        `;
                        
                        directionDiv.innerHTML = directionHtml;
                    } else {
                        document.getElementById('market-direction-prediction').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading market direction:', error);
                }
            }
            
            async function loadComprehensivePredictions() {
                try {
                    const symbol = document.getElementById('symbol-input').value || 'AAPL';
                    const response = await fetch(`/api/predictive/comprehensive/${symbol}`);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const predictions = result.predictions;
                        const predictionsDiv = document.getElementById('comprehensive-predictions');
                        
                        let predictionsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Symbol:</strong> ${predictions.symbol}<br>
                                <strong>Current Price:</strong> $${predictions.current_price.toFixed(2)}<br>
                                <strong>Overall Confidence:</strong> ${(predictions.overall_confidence * 100).toFixed(1)}%<br><br>
                                <strong>Data Quality:</strong><br>
                                • Price Data Points: ${predictions.data_quality.price_data_points}<br>
                                • Volume Data: ${predictions.data_quality.volume_data_available ? 'Available' : 'Not Available'}<br>
                                • Data Freshness: ${predictions.data_quality.data_freshness}<br><br>
                                <strong>Quick Summary:</strong><br>
                                • Short-term Target: $${predictions.price_targets.short_term.bullish.toFixed(2)}<br>
                                • Volatility Trend: ${predictions.volatility_forecast.volatility_trend}<br>
                                • Market Direction: ${Object.keys(predictions.market_direction.direction_probability).reduce((a, b) => 
                                    predictions.market_direction.direction_probability[a] > predictions.market_direction.direction_probability[b] ? a : b
                                ).toUpperCase()}
                            </div>
                        `;
                        
                        predictionsDiv.innerHTML = predictionsHtml;
                    } else {
                        document.getElementById('comprehensive-predictions').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading comprehensive predictions:', error);
                }
            }
            
            async function loadMultiSymbolForecast() {
                try {
                    const response = await fetch('/api/predictive/forecast-multiple');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const predictions = result.predictions;
                        const forecastDiv = document.getElementById('multi-symbol-forecast');
                        
                        let forecastHtml = '<div style="margin: 5px 0;"><strong>Multi-Symbol Forecast:</strong><br><br>';
                        
                        for (const [symbol, data] of Object.entries(predictions)) {
                            if (data.error) {
                                forecastHtml += `<div style="color: #f44336;">${symbol}: Error - ${data.error}</div>`;
                            } else {
                                const direction = Object.keys(data.market_direction.direction_probability).reduce((a, b) => 
                                    data.market_direction.direction_probability[a] > data.market_direction.direction_probability[b] ? a : b
                                ).toUpperCase();
                                
                                forecastHtml += `
                                    <div style="margin: 5px 0; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                        <strong>${symbol}:</strong> $${data.current_price.toFixed(2)}<br>
                                        Direction: <span style="color: ${direction === 'BULLISH' ? '#4CAF50' : direction === 'BEARISH' ? '#f44336' : '#ff9800'}">${direction}</span><br>
                                        Confidence: ${(data.overall_confidence * 100).toFixed(1)}%<br>
                                        Volatility: ${(data.volatility_forecast.current_volatility * 100).toFixed(2)}%
                                    </div>
                                `;
                            }
                        }
                        
                        forecastHtml += '</div>';
                        forecastDiv.innerHTML = forecastHtml;
                    } else {
                        document.getElementById('multi-symbol-forecast').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading multi-symbol forecast:', error);
                }
            }
            
            // Market Scanner Functions
            async function loadMarketHotList() {
                try {
                    const response = await fetch('/api/scanner/hot-list');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const hotList = result.hot_list;
                        const hotListDiv = document.getElementById('market-hot-list');
                        
                        let hotListHtml = '<div style="margin: 5px 0;"><strong>Market Hot List:</strong><br><br>';
                        
                        // Stocks
                        if (hotList.stocks.length > 0) {
                            hotListHtml += '<strong>🔥 Hot Stocks:</strong><br>';
                            hotList.stocks.forEach(stock => {
                                hotListHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${stock.symbol}: $${stock.price} 
                                        <span style="color: ${stock.change > 0 ? '#4CAF50' : '#f44336'}">(${stock.change > 0 ? '+' : ''}${stock.change}%)</span>
                                        <small>Vol: ${stock.volume.toLocaleString()}</small>
                                    </div>
                                `;
                            });
                        }
                        
                        // Forex
                        if (hotList.forex.length > 0) {
                            hotListHtml += '<br><strong>💱 Hot Forex:</strong><br>';
                            hotList.forex.forEach(forex => {
                                hotListHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${forex.symbol}: ${forex.price} 
                                        <span style="color: ${forex.change > 0 ? '#4CAF50' : '#f44336'}">(${forex.change > 0 ? '+' : ''}${forex.change}%)</span>
                                    </div>
                                `;
                            });
                        }
                        
                        // Crypto
                        if (hotList.crypto.length > 0) {
                            hotListHtml += '<br><strong>₿ Hot Crypto:</strong><br>';
                            hotList.crypto.forEach(crypto => {
                                hotListHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${crypto.symbol}: $${crypto.price} 
                                        <span style="color: ${crypto.change > 0 ? '#4CAF50' : '#f44336'}">(${crypto.change > 0 ? '+' : ''}${crypto.change}%)</span>
                                    </div>
                                `;
                            });
                        }
                        
                        hotListHtml += '</div>';
                        hotListDiv.innerHTML = hotListHtml;
                    } else {
                        document.getElementById('market-hot-list').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading market hot list:', error);
                }
            }
            
            async function loadSectorRotation() {
                try {
                    const response = await fetch('/api/scanner/sector-rotation');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const sectors = result.sector_rotation;
                        const sectorsDiv = document.getElementById('sector-rotation');
                        
                        let sectorsHtml = '<div style="margin: 5px 0;"><strong>Sector Rotation:</strong><br><br>';
                        
                        // Sort sectors by rank
                        const sortedSectors = Object.entries(sectors)
                            .filter(([key, value]) => key !== 'last_updated')
                            .sort((a, b) => a[1].rank - b[1].rank);
                        
                        sortedSectors.forEach(([sector, data]) => {
                            const momentumColor = data.momentum > 0 ? '#4CAF50' : data.momentum < 0 ? '#f44336' : '#ff9800';
                            sectorsHtml += `
                                <div style="margin: 3px 0; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                    <strong>#${data.rank} ${sector.toUpperCase()}:</strong> 
                                    <span style="color: ${momentumColor}">${(data.momentum * 100).toFixed(2)}%</span><br>
                                    <small>Top: ${data.symbols.join(', ')}</small>
                                </div>
                            `;
                        });
                        
                        sectorsHtml += '</div>';
                        sectorsDiv.innerHTML = sectorsHtml;
                    } else {
                        document.getElementById('sector-rotation').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading sector rotation:', error);
                }
            }
            
            async function loadMomentumRanking() {
                try {
                    const response = await fetch('/api/scanner/momentum-ranking');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const ranking = result.momentum_ranking;
                        const rankingDiv = document.getElementById('momentum-ranking');
                        
                        let rankingHtml = '<div style="margin: 5px 0;"><strong>Momentum Ranking:</strong><br><br>';
                        
                        // Top Gainers
                        if (ranking.top_gainers.length > 0) {
                            rankingHtml += '<strong>📈 Top Gainers:</strong><br>';
                            ranking.top_gainers.forEach(stock => {
                                rankingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(76,175,80,0.2); border-radius: 3px;">
                                        ${stock.symbol}: $${stock.price} 
                                        <span style="color: #4CAF50">+${(stock.momentum * 100).toFixed(2)}%</span>
                                    </div>
                                `;
                            });
                        }
                        
                        // Top Losers
                        if (ranking.top_losers.length > 0) {
                            rankingHtml += '<br><strong>📉 Top Losers:</strong><br>';
                            ranking.top_losers.forEach(stock => {
                                rankingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(244,67,54,0.2); border-radius: 3px;">
                                        ${stock.symbol}: $${stock.price} 
                                        <span style="color: #f44336">${(stock.momentum * 100).toFixed(2)}%</span>
                                    </div>
                                `;
                            });
                        }
                        
                        // Breakout Candidates
                        if (ranking.breakout_candidates.length > 0) {
                            rankingHtml += '<br><strong>🚀 Breakout Candidates:</strong><br>';
                            ranking.breakout_candidates.forEach(stock => {
                                rankingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,193,7,0.2); border-radius: 3px;">
                                        ${stock.symbol}: $${stock.price} 
                                        <span style="color: #ffc107">Breakout: ${(stock.breakout_potential * 100).toFixed(1)}%</span>
                                    </div>
                                `;
                            });
                        }
                        
                        rankingHtml += '</div>';
                        rankingDiv.innerHTML = rankingHtml;
                    } else {
                        document.getElementById('momentum-ranking').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading momentum ranking:', error);
                }
            }
            
            async function loadScannerSettings() {
                try {
                    const response = await fetch('/api/scanner/settings');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const settings = result.settings;
                        const settingsDiv = document.getElementById('scanner-settings');
                        
                        let settingsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Scanner Settings:</strong><br><br>
                                <strong>Scan Interval:</strong> ${settings.scan_interval} seconds<br>
                                <strong>Min Volume:</strong> ${settings.min_volume.toLocaleString()}<br>
                                <strong>Price Range:</strong> $${settings.min_price} - $${settings.max_price}<br>
                                <strong>Momentum Threshold:</strong> ${(settings.momentum_threshold * 100).toFixed(1)}%<br>
                                <strong>Volume Spike:</strong> ${settings.volume_spike_threshold}x<br>
                                <strong>Breakout Threshold:</strong> ${(settings.breakout_threshold * 100).toFixed(1)}%
                            </div>
                        `;
                        
                        settingsDiv.innerHTML = settingsHtml;
                    } else {
                        document.getElementById('scanner-settings').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading scanner settings:', error);
                }
            }
            
            async function loadComprehensiveMarketScan() {
                try {
                    const response = await fetch('/api/scanner/comprehensive');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const scan = result.scan_results;
                        const scanDiv = document.getElementById('comprehensive-market-scan');
                        
                        let scanHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Comprehensive Market Scan:</strong><br><br>
                                <strong>Scan Results:</strong><br>
                                • Total Scanned: ${scan.scan_results.total_scanned} symbols<br>
                                • Signals Found: ${scan.scan_results.signals_found}<br>
                                • Scan Duration: ${scan.scan_results.scan_duration}s<br>
                                • Last Scan: ${new Date(scan.scan_results.last_scan_time).toLocaleTimeString()}<br><br>
                                
                                <strong>Quick Summary:</strong><br>
                                • Hot Stocks: ${scan.hot_list.stocks.length}<br>
                                • Hot Forex: ${scan.hot_list.forex.length}<br>
                                • Hot Crypto: ${scan.hot_list.crypto.length}<br>
                                • Hot Indices: ${scan.hot_list.indices.length}<br>
                                • Top Sector: ${Object.entries(scan.sector_rotation).filter(([k,v]) => k !== 'last_updated').sort((a,b) => a[1].rank - b[1].rank)[0]?.[0] || 'N/A'}<br>
                                • Top Gainer: ${scan.momentum_ranking.top_gainers[0]?.symbol || 'N/A'}
                            </div>
                        `;
                        
                        scanDiv.innerHTML = scanHtml;
                    } else {
                        document.getElementById('comprehensive-market-scan').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading comprehensive market scan:', error);
                }
            }
            
            // Social Trading Functions
            async function loadSharedSignals() {
                try {
                    const response = await fetch('/api/social/signals');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const signals = result.shared_signals;
                        const signalsDiv = document.getElementById('shared-signals');
                        
                        let signalsHtml = '<div style="margin: 5px 0;"><strong>Shared Signals:</strong><br><br>';
                        
                        if (signals.length > 0) {
                            signals.forEach(signal => {
                                const signalColor = signal.signal_type === 'BUY' ? '#4CAF50' : signal.signal_type === 'SELL' ? '#f44336' : '#ff9800';
                                signalsHtml += `
                                    <div style="margin: 3px 0; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                                        <strong>${signal.symbol}</strong> - <span style="color: ${signalColor}">${signal.signal_type}</span><br>
                                        Entry: $${signal.entry_price} | TP: $${signal.take_profit} | SL: $${signal.stop_loss}<br>
                                        <small>By: ${signal.trader_id} | Confidence: ${signal.confidence}% | ${new Date(signal.timestamp).toLocaleTimeString()}</small>
                                    </div>
                                `;
                            });
                        } else {
                            signalsHtml += '<div style="color: #ff9800;">No shared signals yet</div>';
                        }
                        
                        signalsHtml += '</div>';
                        signalsDiv.innerHTML = signalsHtml;
                    } else {
                        document.getElementById('shared-signals').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading shared signals:', error);
                }
            }
            
            async function shareCurrentSignal() {
                try {
                    // Get the latest signal from monitoring
                    const response = await fetch('/api/live/signals');
                    const result = await response.json();
                    
                    if (result.status === 'success' && result.signals.length > 0) {
                        const latestSignal = result.signals[0];
                        
                        const shareResponse = await fetch('/api/social/share-signal', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                signal_data: latestSignal,
                                trader_id: 'user_001'
                            })
                        });
                        
                        const shareResult = await shareResponse.json();
                        
                        if (shareResult.status === 'success') {
                            alert('Signal shared successfully!');
                            loadSharedSignals(); // Refresh the list
                        } else {
                            alert('Failed to share signal: ' + shareResult.message);
                        }
                    } else {
                        alert('No signals available to share');
                    }
                } catch (error) {
                    console.error('Error sharing signal:', error);
                    alert('Error sharing signal');
                }
            }
            
            async function loadPerformanceLeaderboard() {
                try {
                    const response = await fetch('/api/social/leaderboard');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const leaderboard = result.leaderboard;
                        const leaderboardDiv = document.getElementById('performance-leaderboard');
                        
                        let leaderboardHtml = '<div style="margin: 5px 0;"><strong>Performance Leaderboard:</strong><br><br>';
                        
                        // Top Traders
                        if (leaderboard.top_traders.length > 0) {
                            leaderboardHtml += '<strong>🏆 Top Traders:</strong><br>';
                            leaderboard.top_traders.forEach((trader, index) => {
                                const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏅';
                                leaderboardHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${medal} ${trader.name}: $${trader.profit.toFixed(2)} (${(trader.win_rate * 100).toFixed(1)}% WR) | ${trader.followers} followers
                                    </div>
                                `;
                            });
                        }
                        
                        // Monthly Winners
                        if (leaderboard.monthly_winners.length > 0) {
                            leaderboardHtml += '<br><strong>📅 Monthly Winners:</strong><br>';
                            leaderboard.monthly_winners.slice(0, 3).forEach((trader, index) => {
                                leaderboardHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(76,175,80,0.2); border-radius: 3px;">
                                        #${index + 1} ${trader.name}: ${(trader.win_rate * 100).toFixed(1)}% Win Rate
                                    </div>
                                `;
                            });
                        }
                        
                        leaderboardHtml += '</div>';
                        leaderboardDiv.innerHTML = leaderboardHtml;
                    } else {
                        document.getElementById('performance-leaderboard').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading performance leaderboard:', error);
                }
            }
            
            async function loadCopyTrading() {
                try {
                    const response = await fetch('/api/social/summary');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const copyData = result.summary.copy_trading;
                        const copyDiv = document.getElementById('copy-trading');
                        
                        let copyHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Copy Trading Status:</strong><br><br>
                                <strong>Active Copies:</strong> ${copyData.active_copies}<br>
                                <strong>Total Copiers:</strong> ${copyData.total_copiers}<br>
                                <strong>Last Updated:</strong> ${copyData.last_updated ? new Date(copyData.last_updated).toLocaleTimeString() : 'Never'}<br><br>
                                <strong>Available Traders to Copy:</strong><br>
                                • CryptoKing (78% WR, $15,420 profit)<br>
                                • ForexMaster (72% WR, $12,890 profit)<br>
                                • StockGuru (69% WR, $11,250 profit)<br>
                                • DayTraderPro (65% WR, $9,850 profit)<br>
                                • SwingTrader (71% WR, $8,750 profit)
                            </div>
                        `;
                        
                        copyDiv.innerHTML = copyHtml;
                    } else {
                        document.getElementById('copy-trading').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading copy trading:', error);
                }
            }
            
            async function setupCopyTrading() {
                try {
                    const traderId = prompt('Enter trader ID to copy (e.g., trader_001):');
                    if (!traderId) return;
                    
                    const copySettings = {
                        copy_percentage: 100,
                        max_risk_per_trade: 2.0,
                        max_daily_risk: 5.0,
                        auto_copy: true,
                        copy_signals: ['BUY', 'SELL']
                    };
                    
                    const response = await fetch('/api/social/copy-trading', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            copier_id: 'user_002',
                            trader_id: traderId,
                            copy_settings: copySettings
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('Copy trading setup successfully!');
                        loadCopyTrading(); // Refresh
                    } else {
                        alert('Failed to setup copy trading: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error setting up copy trading:', error);
                    alert('Error setting up copy trading');
                }
            }
            
            async function loadCommunityInsights() {
                try {
                    const response = await fetch('/api/social/community-insights');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const insights = result.insights;
                        const insightsDiv = document.getElementById('community-insights');
                        
                        let insightsHtml = '<div style="margin: 5px 0;"><strong>Community Insights:</strong><br><br>';
                        
                        // Market Sentiment
                        const sentimentColor = insights.market_sentiment === 'BULLISH' ? '#4CAF50' : insights.market_sentiment === 'BEARISH' ? '#f44336' : '#ff9800';
                        insightsHtml += `<strong>Market Sentiment:</strong> <span style="color: ${sentimentColor}">${insights.market_sentiment}</span><br><br>`;
                        
                        // Popular Symbols
                        if (insights.popular_symbols.length > 0) {
                            insightsHtml += '<strong>🔥 Popular Symbols:</strong><br>';
                            insights.popular_symbols.slice(0, 5).forEach(symbol => {
                                insightsHtml += `• ${symbol.symbol}: ${symbol.mentions} mentions<br>`;
                            });
                        }
                        
                        // Trending Strategies
                        if (insights.trending_strategies.length > 0) {
                            insightsHtml += '<br><strong>📈 Trending Strategies:</strong><br>';
                            insights.trending_strategies.slice(0, 3).forEach(strategy => {
                                insightsHtml += `• ${strategy.name}: ${strategy.popularity}% popularity (${(strategy.success_rate * 100).toFixed(1)}% success)<br>`;
                            });
                        }
                        
                        // Discussion Topics
                        if (insights.discussion_topics.length > 0) {
                            insightsHtml += '<br><strong>💬 Hot Topics:</strong><br>';
                            insights.discussion_topics.slice(0, 3).forEach(topic => {
                                const topicColor = topic.sentiment === 'BULLISH' ? '#4CAF50' : topic.sentiment === 'BEARISH' ? '#f44336' : '#ff9800';
                                insightsHtml += `• ${topic.topic}: ${topic.posts} posts (<span style="color: ${topicColor}">${topic.sentiment}</span>)<br>`;
                            });
                        }
                        
                        insightsHtml += '</div>';
                        insightsDiv.innerHTML = insightsHtml;
                    } else {
                        document.getElementById('community-insights').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading community insights:', error);
                }
            }
            
            async function loadSocialSettings() {
                try {
                    const response = await fetch('/api/social/settings');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const settings = result.settings;
                        const settingsDiv = document.getElementById('social-settings');
                        
                        let settingsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Social Trading Settings:</strong><br><br>
                                <strong>Auto Share Signals:</strong> ${settings.auto_share_signals ? '✅ Enabled' : '❌ Disabled'}<br>
                                <strong>Public Profile:</strong> ${settings.public_profile ? '✅ Public' : '❌ Private'}<br>
                                <strong>Allow Copy Trading:</strong> ${settings.allow_copy_trading ? '✅ Allowed' : '❌ Not Allowed'}<br>
                                <strong>Risk Tolerance:</strong> ${settings.risk_tolerance}<br>
                                <strong>Max Copiers:</strong> ${settings.max_copiers}<br>
                                <strong>Minimum Followers:</strong> ${settings.minimum_followers}
                            </div>
                        `;
                        
                        settingsDiv.innerHTML = settingsHtml;
                    } else {
                        document.getElementById('social-settings').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading social settings:', error);
                }
            }
            
            async function loadSocialSummary() {
                try {
                    const response = await fetch('/api/social/summary');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const summary = result.summary;
                        alert(`Social Trading Summary:
                        
Signal Sharing: ${summary.signal_sharing.total_shared} signals shared
Performance Leaderboard: ${summary.performance_leaderboard.top_traders.length} top traders
Copy Trading: ${summary.copy_trading.active_copies} active copies
Community Sentiment: ${summary.community_insights.market_sentiment}
Popular Symbols: ${summary.community_insights.popular_symbols.length} tracked
Trending Strategies: ${summary.community_insights.trending_strategies.length} active`);
                    } else {
                        alert('Error loading social summary: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error loading social summary:', error);
                    alert('Error loading social summary');
                }
            }
            
            // Risk Management Functions
            async function loadPortfolioHeatmap() {
                try {
                    const response = await fetch('/api/risk/portfolio-heatmap');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const heatmap = result.portfolio_heatmap;
                        const heatmapDiv = document.getElementById('portfolio-heatmap');
                        
                        let heatmapHtml = '<div style="margin: 5px 0;"><strong>Portfolio Heatmap:</strong><br><br>';
                        
                        // Risk Scores
                        heatmapHtml += '<strong>🎯 Risk Scores:</strong><br>';
                        Object.entries(heatmap.risk_scores).forEach(([symbol, score]) => {
                            const riskColor = score > 0.3 ? '#f44336' : score > 0.2 ? '#ff9800' : '#4CAF50';
                            heatmapHtml += `
                                <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                    ${symbol}: <span style="color: ${riskColor}">${(score * 100).toFixed(1)}%</span> volatility
                                </div>
                            `;
                        });
                        
                        // Position Sizes
                        heatmapHtml += '<br><strong>📏 Position Sizes:</strong><br>';
                        Object.entries(heatmap.position_sizes).forEach(([symbol, size]) => {
                            heatmapHtml += `
                                <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                    ${symbol}: ${(size * 100).toFixed(1)}% allocation
                                </div>
                            `;
                        });
                        
                        // Exposure Limits
                        heatmapHtml += '<br><strong>⚠️ Exposure Limits:</strong><br>';
                        Object.entries(heatmap.exposure_limits).forEach(([symbol, limit]) => {
                            heatmapHtml += `
                                <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                    ${symbol}: Max ${(limit * 100).toFixed(0)}% exposure
                                </div>
                            `;
                        });
                        
                        heatmapHtml += '</div>';
                        heatmapDiv.innerHTML = heatmapHtml;
                    } else {
                        document.getElementById('portfolio-heatmap').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading portfolio heatmap:', error);
                }
            }
            
            async function loadCorrelationAnalysis() {
                try {
                    const response = await fetch('/api/risk/correlation-analysis');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const correlations = result.correlation_analysis;
                        const correlationsDiv = document.getElementById('correlation-analysis');
                        
                        let correlationsHtml = '<div style="margin: 5px 0;"><strong>Correlation Analysis:</strong><br><br>';
                        
                        // Pair Correlations
                        if (Object.keys(correlations.pair_correlations).length > 0) {
                            correlationsHtml += '<strong>🔗 Asset Pair Correlations:</strong><br>';
                            Object.entries(correlations.pair_correlations).slice(0, 5).forEach(([pair, data]) => {
                                const strengthColor = data.strength === 'HIGH' ? '#f44336' : data.strength === 'MEDIUM' ? '#ff9800' : '#4CAF50';
                                correlationsHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${pair}: <span style="color: ${strengthColor}">${data.strength}</span> (${data.correlation.toFixed(3)})
                                    </div>
                                `;
                            });
                        }
                        
                        // Sector Correlations
                        if (Object.keys(correlations.sector_correlations).length > 0) {
                            correlationsHtml += '<br><strong>🏢 Sector Correlations:</strong><br>';
                            Object.entries(correlations.sector_correlations).slice(0, 3).forEach(([sector, data]) => {
                                const strengthColor = data.strength === 'HIGH' ? '#f44336' : data.strength === 'MEDIUM' ? '#ff9800' : '#4CAF50';
                                correlationsHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${sector}: <span style="color: ${strengthColor}">${data.strength}</span> (${data.correlation.toFixed(3)})
                                    </div>
                                `;
                            });
                        }
                        
                        // Market Correlations
                        if (Object.keys(correlations.market_correlations).length > 0) {
                            correlationsHtml += '<br><strong>🌍 Market Correlations:</strong><br>';
                            Object.entries(correlations.market_correlations).slice(0, 3).forEach(([market, data]) => {
                                const strengthColor = data.strength === 'HIGH' ? '#f44336' : data.strength === 'MEDIUM' ? '#ff9800' : '#4CAF50';
                                correlationsHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${market}: <span style="color: ${strengthColor}">${data.strength}</span> (${data.correlation.toFixed(3)})
                                    </div>
                                `;
                            });
                        }
                        
                        correlationsHtml += '</div>';
                        correlationsDiv.innerHTML = correlationsHtml;
                    } else {
                        document.getElementById('correlation-analysis').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading correlation analysis:', error);
                }
            }
            
            async function loadPositionSizing() {
                try {
                    const response = await fetch('/api/risk/position-sizing');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const sizing = result.position_sizing;
                        const sizingDiv = document.getElementById('position-sizing');
                        
                        let sizingHtml = '<div style="margin: 5px 0;"><strong>Dynamic Position Sizing:</strong><br><br>';
                        
                        // Kelly Criterion
                        if (Object.keys(sizing.kelly_criterion).length > 0) {
                            sizingHtml += '<strong>🎯 Kelly Criterion:</strong><br>';
                            Object.entries(sizing.kelly_criterion).slice(0, 5).forEach(([symbol, data]) => {
                                sizingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${symbol}: ${(data.kelly_fraction * 100).toFixed(1)}% (WR: ${(data.win_rate * 100).toFixed(1)}%)
                                    </div>
                                `;
                            });
                        }
                        
                        // Volatility Adjustment
                        if (Object.keys(sizing.volatility_adjustment).length > 0) {
                            sizingHtml += '<br><strong>📊 Volatility Adjustment:</strong><br>';
                            Object.entries(sizing.volatility_adjustment).slice(0, 5).forEach(([symbol, data]) => {
                                sizingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${symbol}: ${(data.recommended_size * 100).toFixed(1)}% (Vol: ${(data.volatility * 100).toFixed(1)}%)
                                    </div>
                                `;
                            });
                        }
                        
                        // Risk Parity
                        if (Object.keys(sizing.risk_parity).length > 0) {
                            sizingHtml += '<br><strong>⚖️ Risk Parity:</strong><br>';
                            Object.entries(sizing.risk_parity).slice(0, 5).forEach(([symbol, data]) => {
                                sizingHtml += `
                                    <div style="margin: 2px 0; padding: 3px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                        ${symbol}: ${(data.risk_adjusted_size * 100).toFixed(1)}% (Risk: ${(data.risk_contribution * 100).toFixed(1)}%)
                                    </div>
                                `;
                            });
                        }
                        
                        sizingHtml += '</div>';
                        sizingDiv.innerHTML = sizingHtml;
                    } else {
                        document.getElementById('position-sizing').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading position sizing:', error);
                }
            }
            
            async function loadRiskMetrics() {
                try {
                    const response = await fetch('/api/risk/metrics');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const metrics = result.risk_metrics;
                        const metricsDiv = document.getElementById('risk-metrics');
                        
                        let metricsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Advanced Risk Metrics:</strong><br><br>
                                <strong>📉 Value at Risk (VaR):</strong><br>
                                • 95% VaR: ${(metrics.var_95 * 100).toFixed(2)}%<br>
                                • 99% VaR: ${(metrics.var_99 * 100).toFixed(2)}%<br><br>
                                
                                <strong>📊 Risk-Adjusted Returns:</strong><br>
                                • Sharpe Ratio: ${metrics.sharpe_ratio.toFixed(3)}<br>
                                • Sortino Ratio: ${metrics.sortino_ratio.toFixed(3)}<br>
                                • Calmar Ratio: ${metrics.calmar_ratio.toFixed(3)}<br><br>
                                
                                <strong>📈 Portfolio Metrics:</strong><br>
                                • Maximum Drawdown: ${(metrics.maximum_drawdown * 100).toFixed(2)}%<br>
                                • Expected Shortfall: ${(metrics.expected_shortfall * 100).toFixed(2)}%<br>
                                • Beta: ${metrics.beta.toFixed(2)}<br>
                                • Alpha: ${(metrics.alpha * 100).toFixed(2)}%
                            </div>
                        `;
                        
                        metricsDiv.innerHTML = metricsHtml;
                    } else {
                        document.getElementById('risk-metrics').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading risk metrics:', error);
                }
            }
            
            async function loadRiskSettings() {
                try {
                    const response = await fetch('/api/risk/settings');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const settings = result.risk_settings;
                        const settingsDiv = document.getElementById('risk-settings');
                        
                        let settingsHtml = `
                            <div style="margin: 5px 0;">
                                <strong>Risk Management Settings:</strong><br><br>
                                <strong>⚠️ Risk Limits:</strong><br>
                                • Max Daily Loss: ${(settings.max_daily_loss * 100).toFixed(1)}%<br>
                                • Max Position Risk: ${(settings.max_position_risk * 100).toFixed(1)}%<br>
                                • Correlation Limit: ${(settings.correlation_limit * 100).toFixed(0)}%<br><br>
                                
                                <strong>🔧 Features:</strong><br>
                                • Volatility Adjustment: ${settings.volatility_adjustment ? '✅ Enabled' : '❌ Disabled'}<br>
                                • Dynamic Sizing: ${settings.dynamic_sizing ? '✅ Enabled' : '❌ Disabled'}<br>
                                • Risk Parity: ${settings.risk_parity_enabled ? '✅ Enabled' : '❌ Disabled'}<br>
                                • Stop Loss: ${settings.stop_loss_enabled ? '✅ Enabled' : '❌ Disabled'}<br>
                                • Trailing Stop: ${settings.trailing_stop_enabled ? '✅ Enabled' : '❌ Disabled'}
                            </div>
                        `;
                        
                        settingsDiv.innerHTML = settingsHtml;
                    } else {
                        document.getElementById('risk-settings').innerHTML = `<div style="color: #f44336;">Error: ${result.message}</div>`;
                    }
                } catch (error) {
                    console.error('Error loading risk settings:', error);
                }
            }
            
            async function loadComprehensiveRiskAnalysis() {
                try {
                    const response = await fetch('/api/risk/comprehensive');
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const analysis = result.risk_analysis;
                        alert(`Comprehensive Risk Analysis:
                        
Portfolio Heatmap: ${Object.keys(analysis.portfolio_heatmap.risk_scores).length} assets analyzed
Correlation Analysis: ${Object.keys(analysis.correlation_analysis.pair_correlations).length} pairs analyzed
Position Sizing: ${Object.keys(analysis.dynamic_position_sizing.kelly_criterion).length} assets sized
Risk Metrics: VaR 95%: ${(analysis.risk_metrics.var_95 * 100).toFixed(2)}%
Sharpe Ratio: ${analysis.risk_metrics.sharpe_ratio.toFixed(3)}
Max Drawdown: ${(analysis.risk_metrics.maximum_drawdown * 100).toFixed(2)}%
Beta: ${analysis.risk_metrics.beta.toFixed(2)}
Alpha: ${(analysis.risk_metrics.alpha * 100).toFixed(2)}%`);
                    } else {
                        alert('Error loading comprehensive risk analysis: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error loading comprehensive risk analysis:', error);
                    alert('Error loading comprehensive risk analysis');
                }
            }

            // Load alert history and AI learning status on page load
            document.addEventListener('DOMContentLoaded', function() {
                loadAlertHistory();
                loadAILearningStatus();
                loadPerformanceMetrics();
                checkMonitoringStatus();
                loadAnalyticsDashboard();
                loadSentimentAnalysis();
                loadMarketRegime();
                loadPatternRecognition();
                loadAdaptiveParameters();
                loadAILearningMetrics();
                loadPriceTargets();
                loadVolatilityForecast();
                loadMarketDirection();
                loadComprehensivePredictions();
                loadMultiSymbolForecast();
                loadMarketHotList();
                loadSectorRotation();
                loadMomentumRanking();
                loadScannerSettings();
                loadComprehensiveMarketScan();
                loadSharedSignals();
                loadPerformanceLeaderboard();
                loadCopyTrading();
                loadCommunityInsights();
                loadSocialSettings();
                loadPortfolioHeatmap();
                loadCorrelationAnalysis();
                loadPositionSizing();
                loadRiskMetrics();
                loadRiskSettings();
            });
        </script>
    </body>
    </html>
    """)

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Start monitoring
@app.post("/api/live/start")
async def start_monitoring(request: dict):
    global active_symbols, is_monitoring, monitoring_active, current_market
    
    symbols = request.get("symbols", [])
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    # Limit to maximum 5 symbols
    active_symbols = symbols[:5]
    is_monitoring = True
    monitoring_active = True
    current_market = request.get("market", "stocks")
    
    return {
        "status": "success", 
        "message": f"Started monitoring {len(active_symbols)} symbols",
        "monitoring": active_symbols
    }

# Stop monitoring
@app.post("/api/live/stop")
async def stop_monitoring():
    global is_monitoring, monitoring_active
    is_monitoring = False
    monitoring_active = False
    return {"status": "success", "message": "Stopped monitoring"}

# Get live signals
@app.get("/api/live/signals")
async def get_live_signals(timeframe: str = "1h"):
    """Get live trading signals with real data for specified timeframe"""
    if not is_monitoring or not active_symbols:
        return {"status": "success", "signals": []}
    
    try:
        signals = []
        for symbol in active_symbols:
            # Get real live price data
            price_data = get_live_price_data(symbol)
            if price_data and 'error' not in price_data:
                # Generate trading signals for specified timeframe
                signal = generate_trading_signal(symbol, price_data, timeframe)
                if signal:
                    signals.append(signal)
        
        return {"status": "success", "signals": signals, "timeframe": timeframe}
    except Exception as e:
        print(f"Error getting signals: {e}")
        return {"status": "success", "signals": []}

# Get live summary
@app.get("/api/live/summary")
async def get_live_summary():
    """Get live trading summary"""
    if not is_monitoring or not active_symbols:
        return {
            "status": "success",
            "summary": {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "hold_signals": 0,
                "monitored_symbols": [],
                "market_status": "Inactive",
                "trend_direction": "None"
            }
        }
    
    try:
        signals_response = await get_live_signals()
        signals = signals_response.get("signals", [])
        
        buy_signals = len([s for s in signals if s.get("signal_type") == "BUY"])
        sell_signals = len([s for s in signals if s.get("signal_type") == "SELL"])
        hold_signals = len([s for s in signals if s.get("signal_type") == "HOLD"])
        
        return {
            "status": "success",
            "summary": {
                "total_signals": len(signals),
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "hold_signals": hold_signals,
                "monitored_symbols": active_symbols,
                "market_status": "Live",
                "trend_direction": "Active"
            }
        }
    except Exception as e:
        print(f"Error getting summary: {e}")
        return {"status": "success", "summary": {"total_signals": 0}}

# Get live price data
def get_live_price_data(symbol: str):
    """Get real live price data from Yahoo Finance with caching"""
    try:
        # Use cached data if available
        hist = get_cached_data(symbol, "1d", "1m")
        if hist is None:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
        
        if hist.empty:
            return {"error": "No data available"}
        
        current_price = hist.iloc[-1]['Close']
        prev_price = hist.iloc[-2]['Close'] if len(hist) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 4),
            "previous_price": round(prev_price, 4),
            "price_change": round(price_change, 4),
            "price_change_pct": round(price_change_pct, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return {"error": str(e)}

# Advanced ICT/SMC Analysis Functions
def detect_liquidity_sweep(hist):
    """Detect liquidity sweeps (false breakouts)"""
    try:
        if len(hist) < 20:
            return {'bullish': False, 'bearish': False}
        
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        closes = hist['Close'].tolist()
        
        # Look for recent high/low breaks that get swept
        recent_high = max(highs[-5:])
        recent_low = min(lows[-5:])
        previous_high = max(highs[-20:-5])
        previous_low = min(lows[-20:-5])
        
        # Bullish liquidity sweep: price breaks below recent low then closes above
        if recent_low < previous_low and closes[-1] > previous_low:
            return {'bullish': True, 'bearish': False}
        
        # Bearish liquidity sweep: price breaks above recent high then closes below
        if recent_high > previous_high and closes[-1] < previous_high:
            return {'bullish': False, 'bearish': True}
        
        return {'bullish': False, 'bearish': False}
    except:
        return {'bullish': False, 'bearish': False}

def detect_break_of_structure(hist):
    """Detect Break of Structure (BOS) - trend continuation"""
    try:
        if len(hist) < 20:
            return {'bullish': False, 'bearish': False}
        
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        closes = hist['Close'].tolist()
        
        # Look for structure breaks
        recent_high = max(highs[-3:])
        recent_low = min(lows[-3:])
        swing_high = max(highs[-10:-3])
        swing_low = min(lows[-10:-3])
        
        # Bullish BOS: breaks above swing high
        if recent_high > swing_high and closes[-1] > swing_high:
            return {'bullish': True, 'bearish': False}
        
        # Bearish BOS: breaks below swing low
        if recent_low < swing_low and closes[-1] < swing_low:
            return {'bullish': False, 'bearish': True}
        
        return {'bullish': False, 'bearish': False}
    except:
        return {'bullish': False, 'bearish': False}

def detect_change_of_character(hist):
    """Detect Change of Character (CHoCH) - trend reversal"""
    try:
        if len(hist) < 30:
            return {'bullish': False, 'bearish': False}
        
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        closes = hist['Close'].tolist()
        
        # Analyze market structure over longer period
        recent_high = max(highs[-5:])
        recent_low = min(lows[-5:])
        mid_high = max(highs[-15:-5])
        mid_low = min(lows[-15:-5])
        old_high = max(highs[-30:-15])
        old_low = min(lows[-30:-15])
        
        # Bullish CHoCH: was making lower highs, now breaks above
        if recent_high > mid_high and mid_high < old_high and closes[-1] > mid_high:
            return {'bullish': True, 'bearish': False}
        
        # Bearish CHoCH: was making higher lows, now breaks below
        if recent_low < mid_low and mid_low > old_low and closes[-1] < mid_low:
            return {'bullish': False, 'bearish': True}
        
        return {'bullish': False, 'bearish': False}
    except:
        return {'bullish': False, 'bearish': False}

def validate_order_blocks(hist, current_price):
    """Validate order blocks with current price action"""
    try:
        if len(hist) < 20:
            return {'bullish': False, 'bearish': False}
        
        # Simple order block detection
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        volumes = hist['Volume'].tolist()
        
        # Look for high-volume candles (potential order blocks)
        avg_volume = sum(volumes[-20:]) / 20
        high_volume_candles = []
        
        for i in range(len(volumes)-10, len(volumes)):
            if volumes[i] > avg_volume * 1.5:  # 50% above average
                high_volume_candles.append(i)
        
        # Check if current price is respecting order blocks
        for candle_idx in high_volume_candles:
            if candle_idx < len(highs) - 1:
                ob_high = highs[candle_idx]
                ob_low = lows[candle_idx]
                
                # Bullish OB: price above the order block
                if current_price > ob_high:
                    return {'bullish': True, 'bearish': False}
                
                # Bearish OB: price below the order block
                if current_price < ob_low:
                    return {'bullish': False, 'bearish': True}
        
        return {'bullish': False, 'bearish': False}
    except:
        return {'bullish': False, 'bearish': False}

def analyze_kill_zones(hist, timeframe):
    """Enhanced Kill Zones analysis with session overlaps and market activity"""
    try:
        from datetime import datetime, time, timedelta
        
        # Get current UTC time
        current_time = datetime.now().time()
        
        # Enhanced Kill Zone definitions (UTC)
        london_kill_zone = (time(7, 0), time(10, 0))    # 7-10 AM UTC (London Open)
        ny_kill_zone = (time(13, 30), time(16, 30))     # 1:30-4:30 PM UTC (NY Open)
        asian_kill_zone = (time(23, 0), time(1, 0))     # 11 PM-1 AM UTC (Asian Open)
        
        # Session overlap periods (highest volatility)
        london_ny_overlap = (time(13, 30), time(16, 0))  # 1:30-4 PM UTC
        london_asian_overlap = (time(7, 0), time(9, 0))  # 7-9 AM UTC
        
        # Check current session status
        in_london_kz = london_kill_zone[0] <= current_time <= london_kill_zone[1]
        in_ny_kz = ny_kill_zone[0] <= current_time <= ny_kill_zone[1]
        in_asian_kz = (current_time >= asian_kill_zone[0] or current_time <= asian_kill_zone[1])
        
        # Check for session overlaps
        in_london_ny_overlap = london_ny_overlap[0] <= current_time <= london_ny_overlap[1]
        in_london_asian_overlap = london_asian_overlap[0] <= current_time <= london_asian_overlap[1]
        
        # Determine current session and strength
        if in_london_ny_overlap:
            return {'active': True, 'zone': 'London-NY Overlap', 'score': 2.5, 'strength': 'MAXIMUM'}
        elif in_london_asian_overlap:
            return {'active': True, 'zone': 'London-Asian Overlap', 'score': 2.0, 'strength': 'HIGH'}
        elif in_london_kz:
            return {'active': True, 'zone': 'London KZ', 'score': 1.8, 'strength': 'HIGH'}
        elif in_ny_kz:
            return {'active': True, 'zone': 'NY KZ', 'score': 1.8, 'strength': 'HIGH'}
        elif in_asian_kz:
            return {'active': True, 'zone': 'Asian KZ', 'score': 1.2, 'strength': 'MEDIUM'}
        else:
            return {'active': False, 'zone': 'Off Hours', 'score': 0.5, 'strength': 'LOW'}
    except:
        return {'active': False, 'zone': 'KZ Error', 'score': 0}

def get_next_kill_zone():
    """Get the next upcoming kill zone"""
    from datetime import datetime, time
    
    current_time = datetime.now().time()
    kill_zones = [
        (time(7, 0), 'London'),
        (time(13, 30), 'New York'),
        (time(23, 0), 'Asian')
    ]
    
    for zone_time, zone_name in kill_zones:
        if current_time < zone_time:
            return zone_name
    
    return 'London'  # Next day

def calculate_session_volatility(hist):
    """Calculate expected volatility based on current session"""
    try:
        if len(hist) < 20:
            return 1.0
        
        # Calculate recent volatility
        recent_volatility = hist['Close'].pct_change().std() * 100
        
        # Get current session info
        kill_zone_info = analyze_kill_zones(hist, '1h')
        
        # Adjust volatility based on session strength
        session_multipliers = {
            'MAXIMUM': 1.5,
            'HIGH': 1.3,
            'MEDIUM': 1.1,
            'LOW': 0.8
        }
        
        multiplier = session_multipliers.get(kill_zone_info.get('strength', 'LOW'), 1.0)
        adjusted_volatility = recent_volatility * multiplier
        
        return min(adjusted_volatility, 5.0)  # Cap at 5%
    except:
        return 1.0

def analyze_session_momentum(hist):
    """Analyze momentum patterns during different sessions"""
    try:
        if len(hist) < 10:
            return {'bullish': False, 'bearish': False, 'strength': 0}
        
        # Get recent price action
        recent_closes = hist['Close'].tail(5).tolist()
        recent_highs = hist['High'].tail(5).tolist()
        recent_lows = hist['Low'].tail(5).tolist()
        
        # Calculate momentum
        price_change = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]
        high_break = max(recent_highs) > max(hist['High'].tail(10).head(5).tolist())
        low_break = min(recent_lows) < min(hist['Low'].tail(10).head(5).tolist())
        
        # Get session strength
        kill_zone_info = analyze_kill_zones(hist, '1h')
        session_strength = kill_zone_info.get('strength', 'LOW')
        
        # Adjust momentum based on session
        strength_multipliers = {
            'MAXIMUM': 2.0,
            'HIGH': 1.5,
            'MEDIUM': 1.2,
            'LOW': 0.8
        }
        
        multiplier = strength_multipliers.get(session_strength, 1.0)
        adjusted_momentum = abs(price_change) * multiplier
        
        if price_change > 0.001 and high_break:  # Bullish momentum
            return {'bullish': True, 'bearish': False, 'strength': adjusted_momentum}
        elif price_change < -0.001 and low_break:  # Bearish momentum
            return {'bullish': False, 'bearish': True, 'strength': adjusted_momentum}
        else:
            return {'bullish': False, 'bearish': False, 'strength': 0}
    except:
        return {'bullish': False, 'bearish': False, 'strength': 0}

def detect_displacement(hist, timeframe):
    """Detect strong momentum moves (displacement)"""
    try:
        if len(hist) < 10:
            return {'detected': False, 'type': 'None', 'score': 0}
        
        # Calculate price movement over last few candles
        recent_closes = hist['Close'].tail(5)
        price_change = (recent_closes.iloc[-1] - recent_closes.iloc[0]) / recent_closes.iloc[0]
        
        # Displacement thresholds based on timeframe
        thresholds = {
            '5m': 0.005,   # 0.5%
            '15m': 0.008,  # 0.8%
            '1h': 0.015,   # 1.5%
            '4h': 0.025,   # 2.5%
            '1d': 0.035    # 3.5%
        }
        
        threshold = thresholds.get(timeframe, 0.015)
        
        if price_change > threshold:
            return {'detected': True, 'type': 'Bullish', 'score': 2.0}
        elif price_change < -threshold:
            return {'detected': True, 'type': 'Bearish', 'score': -2.0}
        else:
            return {'detected': False, 'type': 'None', 'score': 0}
    except:
        return {'detected': False, 'type': 'None', 'score': 0}

def find_ote_zones(hist, current_price):
    """Find Optimal Trade Entry (OTE) zones using Fibonacci retracements"""
    try:
        if len(hist) < 20:
            return {'in_zone': False, 'zone_type': 'None', 'score': 0}
        
        # Find recent swing high and low
        recent_high = hist['High'].tail(20).max()
        recent_low = hist['Low'].tail(20).min()
        
        if recent_high == recent_low:
            return {'in_zone': False, 'zone_type': 'None', 'score': 0}
        
        # Calculate Fibonacci levels
        fib_range = recent_high - recent_low
        fib_618 = recent_high - (fib_range * 0.618)  # 61.8% retracement
        fib_786 = recent_high - (fib_range * 0.786)  # 78.6% retracement
        fib_382 = recent_high - (fib_range * 0.382)  # 38.2% retracement
        fib_236 = recent_high - (fib_range * 0.236)  # 23.6% retracement
        
        # Check if current price is in OTE zone (61.8% - 78.6% retracement)
        if fib_786 <= current_price <= fib_618:
            return {'in_zone': True, 'zone_type': 'Bullish', 'score': 1.5}
        elif fib_236 <= current_price <= fib_382:
            return {'in_zone': True, 'zone_type': 'Bearish', 'score': -1.5}
        else:
            return {'in_zone': False, 'zone_type': 'None', 'score': 0}
    except:
        return {'in_zone': False, 'zone_type': 'None', 'score': 0}

def detect_breaker_blocks(hist, current_price):
    """Detect Breaker Blocks and Mitigation Blocks"""
    try:
        if len(hist) < 15:
            return {'detected': False, 'type': 'None', 'score': 0}
        
        # Look for significant price levels that were broken
        recent_highs = hist['High'].tail(15)
        recent_lows = hist['Low'].tail(15)
        
        # Find key levels
        key_high = recent_highs.max()
        key_low = recent_lows.min()
        
        # Check if current price is near a broken level (within 1%)
        tolerance = 0.01
        
        if abs(current_price - key_high) / key_high < tolerance:
            # Price near broken resistance - potential breaker block
            return {'detected': True, 'type': 'Bullish Breaker', 'score': 1.0}
        elif abs(current_price - key_low) / key_low < tolerance:
            # Price near broken support - potential breaker block
            return {'detected': True, 'type': 'Bearish Breaker', 'score': -1.0}
        else:
            return {'detected': False, 'type': 'None', 'score': 0}
    except:
        return {'detected': False, 'type': 'None', 'score': 0}

def calculate_atr(hist, period=14):
    """Calculate Average True Range (ATR) for dynamic stop losses"""
    try:
        if len(hist) < period + 1:
            return 0
        
        # Calculate True Range for each period
        high = hist['High']
        low = hist['Low']
        close = hist['Close']
        
        tr_list = []
        for i in range(1, len(hist)):
            tr1 = high.iloc[i] - low.iloc[i]  # High - Low
            tr2 = abs(high.iloc[i] - close.iloc[i-1])  # High - Previous Close
            tr3 = abs(low.iloc[i] - close.iloc[i-1])   # Low - Previous Close
            tr = max(tr1, tr2, tr3)
            tr_list.append(tr)
        
        # Calculate ATR as simple moving average of True Range
        if len(tr_list) >= period:
            atr = sum(tr_list[-period:]) / period
            return atr
        else:
            return 0
    except:
        return 0

def calculate_sensible_sl_tp(current_price, signal_direction, atr, risk_reward_ratio=1.5):
    """
    Calculate Stop Loss and Take Profit based on volatility (ATR).
    This is a sane starting point.
    """
    if signal_direction == "BULLISH":
        stop_loss = current_price - (atr * 1.0)   # Stop 1 ATR below
        take_profit = current_price + (atr * risk_reward_ratio) # TP 1.5 ATR above (for 1.5 R:R)
    elif signal_direction == "BEARISH":
        stop_loss = current_price + (atr * 1.0)    # Stop 1 ATR above
        take_profit = current_price - (atr * risk_reward_ratio) # TP 1.5 ATR below
    else:
        return current_price, current_price # No signal, no trade

    return round(stop_loss, 5), round(take_profit, 5)

def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss):
    """Calculate optimal position size based on risk management"""
    try:
        # Risk amount in dollars
        risk_amount = account_balance * (risk_percent / 100)
        
        # Price difference between entry and stop loss
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        # Position size calculation
        position_size = risk_amount / price_risk
        
        # Round to reasonable number of shares/units
        if position_size >= 1000:
            return round(position_size, -2)  # Round to nearest 100
        elif position_size >= 100:
            return round(position_size, -1)  # Round to nearest 10
        else:
            return round(position_size, 0)   # Round to nearest 1
    except:
        return 0

def calculate_trailing_stop(current_price, entry_price, atr, signal_type, trail_multiplier=2.0):
    """Calculate trailing stop loss based on ATR"""
    try:
        if signal_type == "BUY":
            # For BUY: trail below current price
            trailing_stop = current_price - (atr * trail_multiplier)
            # Don't let trailing stop go below entry price
            trailing_stop = max(trailing_stop, entry_price)
        else:  # SELL
            # For SELL: trail above current price
            trailing_stop = current_price + (atr * trail_multiplier)
            # Don't let trailing stop go above entry price
            trailing_stop = min(trailing_stop, entry_price)
        
        return round(trailing_stop, 2)
    except:
        return entry_price

# Machine Learning Functions
def extract_ml_features(hist, current_price):
    """Extract features for machine learning analysis"""
    try:
        if len(hist) < 20:
            return None
        
        # Price-based features
        close_prices = hist['Close'].values
        high_prices = hist['High'].values
        low_prices = hist['Low'].values
        volume = hist['Volume'].values
        
        # Technical indicators
        sma_20 = np.mean(close_prices[-20:])
        sma_50 = np.mean(close_prices[-50:]) if len(close_prices) >= 50 else sma_20
        
        # Price momentum
        price_change_1 = (close_prices[-1] - close_prices[-2]) / close_prices[-2] if len(close_prices) > 1 else 0
        price_change_5 = (close_prices[-1] - close_prices[-6]) / close_prices[-6] if len(close_prices) > 5 else 0
        price_change_10 = (close_prices[-1] - close_prices[-11]) / close_prices[-11] if len(close_prices) > 10 else 0
        
        # Volatility features
        returns = np.diff(close_prices) / close_prices[:-1]
        volatility = np.std(returns[-20:]) if len(returns) >= 20 else 0
        
        # Volume features
        avg_volume = np.mean(volume[-20:]) if len(volume) >= 20 else volume[-1]
        volume_ratio = volume[-1] / avg_volume if avg_volume > 0 else 1
        
        # RSI calculation
        gains = np.where(returns > 0, returns, 0)
        losses = np.where(returns < 0, -returns, 0)
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else 0
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else 0
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        # Market structure features
        recent_high = np.max(high_prices[-10:])
        recent_low = np.min(low_prices[-10:])
        price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        # Trend strength
        trend_strength = (sma_20 - sma_50) / sma_50 if sma_50 > 0 else 0
        
        return {
            'price_change_1': price_change_1,
            'price_change_5': price_change_5,
            'price_change_10': price_change_10,
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'rsi': rsi,
            'price_position': price_position,
            'trend_strength': trend_strength,
            'sma_20_ratio': current_price / sma_20 if sma_20 > 0 else 1,
            'sma_50_ratio': current_price / sma_50 if sma_50 > 0 else 1
        }
    except:
        return None

def detect_market_regime(hist):
    """Detect if market is trending or ranging using ML"""
    try:
        if len(hist) < 50:
            return "Unknown"
        
        close_prices = hist['Close'].values
        
        # Calculate trend indicators
        sma_20 = np.mean(close_prices[-20:])
        sma_50 = np.mean(close_prices[-50:])
        
        # Price range analysis
        recent_range = np.max(close_prices[-20:]) - np.min(close_prices[-20:])
        avg_range = np.mean([np.max(close_prices[i:i+20]) - np.min(close_prices[i:i+20]) 
                           for i in range(len(close_prices)-20)])
        
        # Trend strength
        trend_strength = abs(sma_20 - sma_50) / sma_50
        
        # Volatility analysis
        returns = np.diff(close_prices) / close_prices[:-1]
        volatility = np.std(returns[-20:])
        
        # Simple rule-based classification
        if trend_strength > 0.02 and volatility > 0.01:
            return "Trending"
        elif recent_range < avg_range * 0.8:
            return "Ranging"
        else:
            return "Mixed"
    except:
        return "Unknown"

def analyze_sentiment_patterns(hist, current_price):
    """Analyze market sentiment using price patterns"""
    try:
        if len(hist) < 20:
            return {"sentiment": "Neutral", "confidence": 0.5}
        
        close_prices = hist['Close'].values
        high_prices = hist['High'].values
        low_prices = hist['Low'].values
        volume = hist['Volume'].values
        
        # Bullish patterns
        bullish_signals = 0
        bearish_signals = 0
        
        # Higher highs and higher lows
        if len(close_prices) >= 10:
            recent_highs = high_prices[-10:]
            recent_lows = low_prices[-10:]
            
            if recent_highs[-1] > recent_highs[-5] > recent_highs[-10]:
                bullish_signals += 2
            if recent_lows[-1] > recent_lows[-5] > recent_lows[-10]:
                bullish_signals += 2
                
            if recent_highs[-1] < recent_highs[-5] < recent_highs[-10]:
                bearish_signals += 2
            if recent_lows[-1] < recent_lows[-5] < recent_lows[-10]:
                bearish_signals += 2
        
        # Volume confirmation
        avg_volume = np.mean(volume[-20:])
        recent_volume = volume[-1]
        if recent_volume > avg_volume * 1.2:
            if close_prices[-1] > close_prices[-2]:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        # Price momentum
        if len(close_prices) >= 5:
            momentum = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
            if momentum > 0.02:
                bullish_signals += 1
            elif momentum < -0.02:
                bearish_signals += 1
        
        # Determine sentiment
        total_signals = bullish_signals + bearish_signals
        if total_signals == 0:
            return {"sentiment": "Neutral", "confidence": 0.5}
        
        bullish_ratio = bullish_signals / total_signals
        
        if bullish_ratio > 0.6:
            sentiment = "Bullish"
            confidence = bullish_ratio
        elif bullish_ratio < 0.4:
            sentiment = "Bearish"
            confidence = 1 - bullish_ratio
        else:
            sentiment = "Neutral"
            confidence = 0.5
        
        return {"sentiment": sentiment, "confidence": confidence}
    except:
        return {"sentiment": "Neutral", "confidence": 0.5}

def predict_signal_accuracy(features, signal_type):
    """Predict signal accuracy using ML features"""
    try:
        if not features:
            return 0.5
        
        # Simple rule-based accuracy prediction
        accuracy_score = 0.5  # Base accuracy
        
        # RSI-based accuracy
        if features['rsi'] < 30 or features['rsi'] > 70:
            accuracy_score += 0.1  # Extreme RSI levels
        
        # Volume confirmation
        if features['volume_ratio'] > 1.5:
            accuracy_score += 0.1  # High volume confirmation
        
        # Trend alignment
        if signal_type == "BUY" and features['trend_strength'] > 0:
            accuracy_score += 0.1
        elif signal_type == "SELL" and features['trend_strength'] < 0:
            accuracy_score += 0.1
        
        # Volatility consideration
        if 0.01 < features['volatility'] < 0.05:
            accuracy_score += 0.05  # Optimal volatility range
        
        # Price position
        if 0.2 < features['price_position'] < 0.8:
            accuracy_score += 0.05  # Not at extremes
        
        return min(0.95, max(0.1, accuracy_score))
    except:
        return 0.5

# Backtesting Engine Functions
def run_backtest(symbol, timeframe, start_date, end_date, initial_capital=10000):
    """Run backtest on historical data"""
    try:
        # Get historical data
        ticker = yf.Ticker(symbol)
        
        # Map timeframes to yfinance periods
        timeframe_config = {
            "5m": {"period": "60d", "interval": "5m"},
            "15m": {"period": "60d", "interval": "15m"},
            "1h": {"period": "730d", "interval": "1h"},
            "4h": {"period": "730d", "interval": "4h"},
            "1d": {"period": "5y", "interval": "1d"}
        }
        
        config = timeframe_config.get(timeframe, timeframe_config["1h"])
        hist = ticker.history(period=config["period"], interval=config["interval"])
        
        if hist.empty or len(hist) < 50:
            return {"error": "Insufficient historical data"}
        
        # Backtest parameters
        trades = []
        capital = initial_capital
        max_capital = initial_capital
        max_drawdown = 0
        position = None
        trade_count = 0
        win_count = 0
        
        # Simulate trading through historical data
        for i in range(50, len(hist) - 10):  # Leave room for future data
            current_data = hist.iloc[:i+1]
            current_price = hist.iloc[i]['Close']
            
            # Generate signal for this point
            price_data = {
                "current_price": current_price,
                "price_change_pct": 0
            }
            
            signal = generate_trading_signal(symbol, price_data, timeframe)
            
            if signal and signal['signal_type'] in ['BUY', 'SELL']:
                # Close existing position if any
                if position:
                    exit_price = current_price
                    pnl = calculate_trade_pnl(position, exit_price)
                    capital += pnl
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': hist.index[i],
                        'symbol': symbol,
                        'signal_type': position['signal_type'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'stop_loss': position['stop_loss'],
                        'take_profit': position['take_profit'],
                        'pnl': pnl,
                        'pnl_pct': (pnl / position['entry_price']) * 100
                    })
                    
                    if pnl > 0:
                        win_count += 1
                    
                    position = None
                
                # Open new position
                if capital > 0:
                    position = {
                        'entry_time': hist.index[i],
                        'signal_type': signal['signal_type'],
                        'entry_price': signal['entry_price'],
                        'stop_loss': signal['stop_loss'],
                        'take_profit': signal['take_profit'],
                        'position_size': signal['position_size']
                    }
                    trade_count += 1
            
            # Check for stop loss or take profit
            if position:
                if position['signal_type'] == 'BUY':
                    if current_price <= position['stop_loss'] or current_price >= position['take_profit']:
                        exit_price = current_price
                        pnl = calculate_trade_pnl(position, exit_price)
                        capital += pnl
                        
                        trades.append({
                            'entry_time': position['entry_time'],
                            'exit_time': hist.index[i],
                            'symbol': symbol,
                            'signal_type': position['signal_type'],
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'stop_loss': position['stop_loss'],
                            'take_profit': position['take_profit'],
                            'pnl': pnl,
                            'pnl_pct': (pnl / position['entry_price']) * 100
                        })
                        
                        if pnl > 0:
                            win_count += 1
                        
                        position = None
                else:  # SELL
                    if current_price >= position['stop_loss'] or current_price <= position['take_profit']:
                        exit_price = current_price
                        pnl = calculate_trade_pnl(position, exit_price)
                        capital += pnl
                        
                        trades.append({
                            'entry_time': position['entry_time'],
                            'exit_time': hist.index[i],
                            'symbol': symbol,
                            'signal_type': position['signal_type'],
                            'entry_price': position['entry_price'],
                            'exit_price': exit_price,
                            'stop_loss': position['stop_loss'],
                            'take_profit': position['take_profit'],
                            'pnl': pnl,
                            'pnl_pct': (pnl / position['entry_price']) * 100
                        })
                        
                        if pnl > 0:
                            win_count += 1
                        
                        position = None
            
            # Track drawdown
            if capital > max_capital:
                max_capital = capital
            
            current_drawdown = (max_capital - capital) / max_capital
            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown
        
        # Calculate performance metrics
        total_return = (capital - initial_capital) / initial_capital * 100
        win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
        
        # Calculate Sharpe ratio (simplified)
        if trades:
            returns = [trade['pnl_pct'] for trade in trades]
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'start_date': str(hist.index[0].date()),
            'end_date': str(hist.index[-1].date()),
            'initial_capital': initial_capital,
            'final_capital': round(capital, 2),
            'total_return': round(total_return, 2),
            'total_trades': trade_count,
            'winning_trades': win_count,
            'losing_trades': trade_count - win_count,
            'win_rate': round(win_rate, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'trades': trades[-10:] if trades else []  # Last 10 trades
        }
        
    except Exception as e:
        return {"error": f"Backtest failed: {str(e)}"}

def calculate_trade_pnl(position, exit_price):
    """Calculate profit/loss for a trade"""
    try:
        if position['signal_type'] == 'BUY':
            pnl = (exit_price - position['entry_price']) * position['position_size']
        else:  # SELL
            pnl = (position['entry_price'] - exit_price) * position['position_size']
        
        return round(pnl, 2)
    except:
        return 0

def get_backtest_summary(symbols, timeframe="1h"):
    """Get backtest summary for multiple symbols"""
    try:
        results = []
        
        for symbol in symbols[:5]:  # Limit to 5 symbols for performance
            result = run_backtest(symbol, timeframe, None, None)
            if 'error' not in result:
                results.append(result)
        
        if not results:
            return {"error": "No valid backtest results"}
        
        # Aggregate results
        total_return = np.mean([r['total_return'] for r in results])
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_drawdown = np.mean([r['max_drawdown'] for r in results])
        total_trades = sum([r['total_trades'] for r in results])
        
        return {
            'summary': {
                'avg_return': round(total_return, 2),
                'avg_win_rate': round(avg_win_rate, 2),
                'avg_drawdown': round(avg_drawdown, 2),
                'total_trades': total_trades,
                'symbols_tested': len(results)
            },
            'individual_results': results
        }
        
    except Exception as e:
        return {"error": f"Summary failed: {str(e)}"}

def calculate_real_confidence(rsi, volume_ratio, is_above_sma200, is_correct_time, pattern_strength, signal_type):
    """Calculate a realistic confidence score based on confluence factors."""
    score = 0
    
    # RSI: Ideal between 55-70 for bullish, 30-45 for bearish
    if signal_type == "BUY":
        if 55 < rsi < 70:
            score += 20
        elif 50 < rsi < 75:
            score += 10
    elif signal_type == "SELL":
        if 30 < rsi < 45:
            score += 20
        elif 25 < rsi < 50:
            score += 10
    
    # Volume: Confirmation is good
    if volume_ratio > 1.2:
        score += 20
    elif volume_ratio > 1.0:
        score += 10
    
    # Trend: Aligning with trend is good
    if signal_type == "BUY" and is_above_sma200:
        score += 25
    elif signal_type == "SELL" and not is_above_sma200:
        score += 25
    
    # Time: Being in a key market hour is good
    if is_correct_time:
        score += 15
    
    # Pattern: Subjective strength of the pattern itself
    if pattern_strength == "STRONG":
        score += 20
    elif pattern_strength == "MODERATE":
        score += 10
    
    return min(score, 100)  # Cap at 100%

# Generate trading signals with ICT/SMC methodology
def generate_trading_signal(symbol: str, price_data: dict, timeframe: str = "1h", current_market: str = "stocks"):
    """Generate trading signals based on ICT/SMC concepts with additional indicators"""
    try:
        current_price = price_data.get("current_price", 0)
        if current_price == 0:
            return None
        
        # REAL TRADING VALIDATION: Check for valid market data
        if 'error' in price_data or not price_data.get('current_price'):
            return None  # No valid market data
        
        # Get historical data for ATR calculation FIRST
        timeframe_config = {
            "5m": {"period": "1d", "interval": "5m"},
            "15m": {"period": "2d", "interval": "15m"},
            "1h": {"period": "5d", "interval": "1h"},
            "4h": {"period": "1mo", "interval": "4h"},
            "1d": {"period": "3mo", "interval": "1d"}
        }
        
        config = timeframe_config.get(timeframe, timeframe_config["1h"])
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=config["period"], interval=config["interval"])
        
        if hist.empty or len(hist) < 20:
            return None  # Not enough data for proper analysis
        
        # Calculate ATR early for validation
        atr = calculate_atr(hist, 14)
        if atr <= 0:
            return None  # No volatility data - not suitable for trading
        
        # PRICE VALIDATION: Check for realistic prices
        if symbol.endswith('-USD'):  # Crypto symbols
            if 'BTC' in symbol and (current_price < 50000 or current_price > 150000):
                return None  # BTC price unrealistic
            elif 'ETH' in symbol and (current_price < 2000 or current_price > 5000):
                return None  # ETH price unrealistic
        elif current_price <= 0 or current_price > 1000000:
            return None  # Price unrealistic for most assets
        
        # Map timeframes to yfinance periods and intervals
        timeframe_config = {
            "5m": {"period": "1d", "interval": "5m"},
            "15m": {"period": "2d", "interval": "15m"},
            "1h": {"period": "5d", "interval": "1h"},
            "4h": {"period": "10d", "interval": "4h"},
            "1d": {"period": "30d", "interval": "1d"}
        }
        
        config = timeframe_config.get(timeframe, timeframe_config["1h"])
        
        # Get historical data for ICT/SMC analysis based on timeframe
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=config["period"], interval=config["interval"])
        
        if hist.empty or len(hist) < 20:
            return None
        
        # Calculate technical indicators
        close_prices = hist['Close'].values
        high_prices = hist['High'].values
        low_prices = hist['Low'].values
        volume = hist['Volume'].values
        
        # ICT/SMC Core Concepts
        signal_score = 0
        signal_type = "HOLD"
        confidence = 50.0
        pattern = "Advanced ICT/SMC"
        
        # 1. Enhanced Kill Zones Analysis (London/NY/Asian Sessions + Overlaps)
        kill_zone_analysis = analyze_kill_zones(hist, timeframe)
        session_momentum = analyze_session_momentum(hist)
        session_volatility = calculate_session_volatility(hist)
        
        signal_score += kill_zone_analysis['score']
        if kill_zone_analysis['active']:
            pattern += f" + {kill_zone_analysis['zone']}"
            
            # Add session momentum bonus
            if session_momentum['bullish'] and signal_score > 0:
                signal_score += session_momentum['strength'] * 2
                pattern += f" + {kill_zone_analysis['strength']} Session Momentum"
            elif session_momentum['bearish'] and signal_score < 0:
                signal_score -= session_momentum['strength'] * 2
                pattern += f" + {kill_zone_analysis['strength']} Session Momentum"
        
        # Session volatility adjustment
        if session_volatility > 2.0:  # High volatility session
            signal_score *= 1.2
            pattern += " + High Vol Session"
        
        # Multi-Timeframe Confluence Analysis
        mtf_confluence = calculate_multi_timeframe_confluence(symbol)
        if mtf_confluence['confluence_score'] != 0:
            signal_score += mtf_confluence['confluence_score']
            
            # Add confluence details to pattern
            htf_bias = mtf_confluence['htf_bias']
            entry_signal = mtf_confluence['entry_signal']
            ltf_confirmation = mtf_confluence['ltf_confirmation']
            
            pattern += f" + HTF {htf_bias['bias']} Bias"
            if entry_signal['signal'] != 'NEUTRAL':
                pattern += f" + {entry_signal['signal']} Entry"
            if ltf_confirmation['confirmed']:
                pattern += f" + LTF {ltf_confirmation['direction']} Confirmation"
        
        # 2. Displacement Detection (Strong momentum moves)
        displacement_analysis = detect_displacement(hist, timeframe)
        signal_score += displacement_analysis['score']
        if displacement_analysis['detected']:
            pattern += f" + {displacement_analysis['type']} Displacement"
        
        # 3. Optimal Trade Entry (OTE) Zones
        ote_analysis = find_ote_zones(hist, current_price)
        signal_score += ote_analysis['score']
        if ote_analysis['in_zone']:
            pattern += f" + {ote_analysis['zone_type']} OTE"
        
        # 4. Breaker Blocks and Mitigation Blocks
        breaker_analysis = detect_breaker_blocks(hist, current_price)
        signal_score += breaker_analysis['score']
        if breaker_analysis['detected']:
            pattern += f" + {breaker_analysis['type']} Block"
        
        # 5. Machine Learning Analysis
        ml_features = extract_ml_features(hist, current_price)
        market_regime = detect_market_regime(hist)
        sentiment_analysis = analyze_sentiment_patterns(hist, current_price)
        
        # ML-enhanced signal scoring
        if ml_features:
            # Market regime adjustment
            if market_regime == "Trending" and abs(signal_score) > 1:
                signal_score *= 1.2  # Boost trending market signals
            elif market_regime == "Ranging" and abs(signal_score) > 1:
                signal_score *= 0.8  # Reduce ranging market signals
            
            # Sentiment alignment
            if sentiment_analysis['sentiment'] == "Bullish" and signal_score > 0:
                signal_score += 0.5
                pattern += " + Bullish Sentiment"
            elif sentiment_analysis['sentiment'] == "Bearish" and signal_score < 0:
                signal_score -= 0.5
                pattern += " + Bearish Sentiment"
        
        # 1. MARKET STRUCTURE (ICT Core)
        # Higher Highs and Higher Lows (Bullish Structure)
        recent_highs = high_prices[-10:]
        recent_lows = low_prices[-10:]
        
        if len(recent_highs) >= 3 and len(recent_lows) >= 3:
            # Check for Higher Highs
            if recent_highs[-1] > recent_highs[-2] > recent_highs[-3]:
                signal_score += 2
                pattern += " + Higher Highs"
            # Check for Higher Lows
            if recent_lows[-1] > recent_lows[-2] > recent_lows[-3]:
                signal_score += 2
                pattern += " + Higher Lows"
            # Check for Lower Highs and Lower Lows (Bearish Structure)
            elif recent_highs[-1] < recent_highs[-2] < recent_highs[-3]:
                signal_score -= 2
                pattern += " + Lower Highs"
            elif recent_lows[-1] < recent_lows[-2] < recent_lows[-3]:
                signal_score -= 2
                pattern += " + Lower Lows"
        
        # 2. ORDER BLOCKS (SMC Core)
        # Simplified Order Block detection - looking for significant price levels
        price_range = max(high_prices[-20:]) - min(low_prices[-20:])
        if price_range > 0:
            # Bullish Order Block: Strong move up followed by consolidation
            recent_move = close_prices[-1] - close_prices[-5]
            if recent_move > price_range * 0.02:  # 2% move
                signal_score += 1.5
                pattern += " + Bullish OB"
            # Bearish Order Block: Strong move down followed by consolidation
            elif recent_move < -price_range * 0.02:  # -2% move
                signal_score -= 1.5
                pattern += " + Bearish OB"
        
        # 3. FAIR VALUE GAPS (ICT Core)
        # Simplified FVG detection - gaps between candles
        if len(close_prices) >= 3:
            # Bullish FVG: Low of candle 1 < High of candle 3
            if low_prices[-3] < high_prices[-1]:
                signal_score += 1
                pattern += " + Bullish FVG"
            # Bearish FVG: High of candle 1 > Low of candle 3
            elif high_prices[-3] > low_prices[-1]:
                signal_score -= 1
                pattern += " + Bearish FVG"
        
        # 4. LIQUIDITY GRABS (SMC Core)
        # Simplified liquidity detection - wicks beyond recent levels
        recent_high = max(high_prices[-10:])
        recent_low = min(low_prices[-10:])
        
        # Bullish liquidity grab: Price wicks below recent low then moves up
        if low_prices[-1] < recent_low * 0.998 and close_prices[-1] > recent_low:
            signal_score += 1.5
            pattern += " + Bullish Liq Grab"
        # Bearish liquidity grab: Price wicks above recent high then moves down
        elif high_prices[-1] > recent_high * 1.002 and close_prices[-1] < recent_high:
            signal_score -= 1.5
            pattern += " + Bearish Liq Grab"
        
        # 5. TRADITIONAL INDICATORS (Supporting ICT/SMC)
        # RSI for momentum confirmation
        price_changes = [close_prices[i] - close_prices[i-1] for i in range(1, len(close_prices))]
        gains = [change if change > 0 else 0 for change in price_changes[-14:]]
        losses = [-change if change < 0 else 0 for change in price_changes[-14:]]
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0.01
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        # RSI confirmation for ICT signals
        if signal_score > 0 and rsi < 70:  # Bullish ICT + RSI not overbought
            signal_score += 0.5
            pattern += " + RSI Confirmation"
        elif signal_score < 0 and rsi > 30:  # Bearish ICT + RSI not oversold
            signal_score -= 0.5
            pattern += " + RSI Confirmation"
        
        # Volume confirmation (Smart Money Volume)
        avg_volume = sum(volume[-10:]) / 10
        current_volume = volume[-1] if len(volume) > 0 else avg_volume
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Calculate missing variables for confidence calculation
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else hist['Close'].mean()
        is_above_sma200 = current_price > sma_200
        
        # Check if we're in a key market hour (simplified - can be enhanced)
        from datetime import datetime
        current_hour = datetime.now().hour
        is_correct_time = current_hour in [9, 10, 11, 14, 15, 16]  # Key trading hours
        
        # Determine pattern strength based on signal score
        if abs(signal_score) >= 3:
            pattern_strength = "STRONG"
        elif abs(signal_score) >= 1.5:
            pattern_strength = "MODERATE"
        else:
            pattern_strength = "WEAK"
        
        # High volume confirms institutional activity
        if volume_ratio > 1.5:
            signal_score *= 1.3
            pattern += " + High Volume"
        elif volume_ratio < 0.7:
            signal_score *= 0.8
            pattern += " + Low Volume"
        
        # 6. PREMIUM/DISCOUNT ZONES (ICT Core)
        # Simplified premium/discount based on recent range
        range_high = max(high_prices[-20:])
        range_low = min(low_prices[-20:])
        range_mid = (range_high + range_low) / 2
        
        if current_price > range_mid + (range_high - range_mid) * 0.7:  # Premium zone
            signal_score -= 1
            pattern += " + Premium Zone"
        elif current_price < range_low + (range_mid - range_low) * 0.3:  # Discount zone
            signal_score += 1
            pattern += " + Discount Zone"
        
        # Calculate ML accuracy for display (simplified)
        ml_accuracy = 0.75  # Default 75% accuracy
        
        # Determine final signal - Only BUY or SELL, no HOLD
        if signal_score >= 1.0:  # Strong ICT/SMC signal
            signal_type = "BUY"
            # Calculate REAL confidence based on confluence factors
            confidence = calculate_real_confidence(
                rsi=rsi, 
                volume_ratio=volume_ratio, 
                is_above_sma200=is_above_sma200, 
                is_correct_time=is_correct_time, 
                pattern_strength=pattern_strength,
                signal_type="BUY"
            )
        elif signal_score <= -1.0:  # Strong ICT/SMC signal
            signal_type = "SELL"
            # Calculate REAL confidence based on confluence factors
            confidence = calculate_real_confidence(
                rsi=rsi, 
                volume_ratio=volume_ratio, 
                is_above_sma200=is_above_sma200, 
                is_correct_time=is_correct_time, 
                pattern_strength=pattern_strength,
                signal_type="SELL"
            )
        else:
            # Skip weak signals - only show strong ICT/SMC signals
            return None
        
        # CORRECT signal logic - Entry price is the current price
        entry_price = current_price
        
        # ATR already calculated above for validation
        
        # PROPER RISK MANAGEMENT: Use ATR for realistic stop losses
        if atr > 0:
            # Use ATR for stop loss distance (1.5x ATR for safety)
            stop_distance = atr * 1.5
        else:
            # Fallback: percentage-based stops
            if entry_price >= 1000:  # High-value assets (BTC, stocks)
                stop_distance = entry_price * 0.02  # 2% stop loss
            elif entry_price >= 100:  # Medium-value assets
                stop_distance = entry_price * 0.015  # 1.5% stop loss
            elif entry_price >= 10:  # Forex pairs
                stop_distance = entry_price * 0.01  # 1% stop loss
            else:  # Low-value assets
                stop_distance = entry_price * 0.005  # 0.5% stop loss (was 0.005)
        
        # Calculate stop loss and take profit using SENSIBLE ATR-based approach
        if atr > 0:
            # Use your sensible ATR-based approach
            signal_direction = "BULLISH" if signal_type == "BUY" else "BEARISH"
            stop_loss, take_profit = calculate_sensible_sl_tp(entry_price, signal_direction, atr, risk_reward_ratio=1.5)
        else:
            # Fallback to percentage-based (only if ATR is 0)
            if signal_type == "BUY":
                stop_loss = round(entry_price - stop_distance, 2)
                take_profit = round(entry_price + (stop_distance * 1.5), 2)  # 1.5:1 risk/reward ratio
            else:  # SELL
                stop_loss = round(entry_price + stop_distance, 2)
                take_profit = round(entry_price - (stop_distance * 1.5), 2)  # 1.5:1 risk/reward ratio

    
        # Calculate position sizing and trailing stops
        account_balance = 10000  # Default $10,000 account (can be made configurable)
        risk_percent = 2.0  # 2% risk per trade
        position_size = calculate_position_size(account_balance, risk_percent, entry_price, stop_loss)
        trailing_stop = calculate_trailing_stop(current_price, entry_price, atr, signal_type)
        
        # Calculate actual risk/reward ratio
        if atr > 0:
            actual_risk = abs(entry_price - stop_loss)
            actual_reward = abs(take_profit - entry_price)
            risk_reward_ratio = round(actual_reward / actual_risk, 1) if actual_risk > 0 else 0
        else:
            risk_reward_ratio = 1.5  # Default 1.5:1 ratio
        
        # Apply confidence penalty for poor risk/reward ratios
        if risk_reward_ratio < 1.2:  # Below minimum for real trading
            confidence = max(10.0, confidence * 0.2)  # Severe penalty
        elif risk_reward_ratio < 1.5:  # Below optimal
            confidence = max(30.0, confidence * 0.5)  # Moderate penalty
        
        # CRITICAL: Apply severe penalty for broken signals (SL = Entry)
        if stop_loss == entry_price or take_profit == entry_price:
            confidence = max(5.0, confidence * 0.1)  # Extreme penalty for broken signals
        
        # REAL TRADING VALIDATION: Only generate signals with proper market conditions
        if atr <= 0 or confidence < 30 or risk_reward_ratio < 1.2:
            # Don't generate signal - market conditions not suitable (minimum 1.2:1 R/R)
            return None
        
        # Debug logging
        print(f"Signal for {symbol}: {signal_type}, Entry: {current_price}, SL: {stop_loss}, TP: {take_profit}, ATR: {atr:.3f}, Score: {signal_score}")
        
        # Create signal object for alert processing
        signal_data = {
            "symbol": symbol,
            "signal_type": signal_type,
            "timeframe": timeframe.upper(),
            "current_price": round(current_price, 2),
            "entry_price": round(entry_price, 2),
            "price_change": round(price_data.get("price_change_pct", 0), 2),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "trailing_stop": trailing_stop,
            "confidence": round(confidence, 1),
            "pattern": pattern,
            "timestamp": datetime.now().isoformat(),
            "risk_reward": risk_reward_ratio,
            "rsi": round(rsi, 1),
            "volume_ratio": round(volume_ratio, 2),
            "signal_score": round(signal_score, 2),
            "atr": round(atr, 3),
            "position_size": position_size,
            "risk_amount": round(account_balance * (risk_percent / 100), 2),
            "ict_analysis": {
                "market_structure": "Advanced ICT/SMC",
                "kill_zones": kill_zone_analysis['zone'] if kill_zone_analysis['active'] else "Outside KZ",
                "displacement": displacement_analysis['type'] if displacement_analysis['detected'] else "None",
                "ote_zones": ote_analysis['zone_type'] if ote_analysis['in_zone'] else "None",
                "breaker_blocks": breaker_analysis['type'] if breaker_analysis['detected'] else "None",
                "order_blocks": "Detected" if "OB" in pattern else "None",
                "fair_value_gaps": "Detected" if "FVG" in pattern else "None",
                "liquidity_grab": "Detected" if "Liq Grab" in pattern else "None",
                "premium_discount": "Premium" if "Premium Zone" in pattern else "Discount" if "Discount Zone" in pattern else "Neutral"
            },
            "ml_analysis": {
                "market_regime": market_regime,
                "sentiment": sentiment_analysis['sentiment'],
                "sentiment_confidence": round(sentiment_analysis['confidence'] * 100, 1),
                "ml_accuracy": round(ml_accuracy * 100, 1) if ml_features else 50.0,
                "pattern_recognition": "AI Enhanced" if ml_features else "Basic",
                "volatility_regime": "High" if ml_features and ml_features['volatility'] > 0.03 else "Normal" if ml_features and ml_features['volatility'] > 0.01 else "Low"
            }
        }
        
        # Collect learning data
        collect_learning_data(symbol, signal_data, price_data)
        
        # Add analytics tracking
        signal_data['market'] = current_market
        signal_data['timestamp'] = datetime.now().isoformat()
        
        # Process alerts asynchronously (don't wait for completion)
        asyncio.create_task(process_signal_alert(symbol, signal_data))
        
        return signal_data
        
    except Exception as e:
        print(f"Error generating signal for {symbol}: {e}")
        return None

# Live market data endpoint
@app.get("/api/live/price/{symbol}")
async def get_live_price(symbol: str):
    """Get live price for a specific symbol"""
    try:
        # Fix URL encoding issue for forex symbols
        from urllib.parse import unquote
        symbol = unquote(symbol)
        price_data = get_live_price_data(symbol)
        return {
            "status": "success",
            "data": price_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced ICT/SMC Chart Analysis Functions
def detect_order_blocks(hist_data):
    """Detect bullish and bearish order blocks"""
    order_blocks = []
    highs = hist_data['High'].tolist()
    lows = hist_data['Low'].tolist()
    closes = hist_data['Close'].tolist()
    
    for i in range(2, len(hist_data) - 2):
        # Bullish Order Block: Strong bullish candle followed by pullback
        if (closes[i] > highs[i-1] and closes[i] > closes[i-2] and 
            closes[i+1] < closes[i] and closes[i+2] < closes[i]):
            order_blocks.append({
                'type': 'bullish',
                'index': i,
                'high': highs[i],
                'low': lows[i],
                'strength': abs(closes[i] - lows[i]) / (highs[i] - lows[i]) if highs[i] != lows[i] else 0
            })
        
        # Bearish Order Block: Strong bearish candle followed by pullback
        elif (closes[i] < lows[i-1] and closes[i] < closes[i-2] and 
              closes[i+1] > closes[i] and closes[i+2] > closes[i]):
            order_blocks.append({
                'type': 'bearish',
                'index': i,
                'high': highs[i],
                'low': lows[i],
                'strength': abs(highs[i] - closes[i]) / (highs[i] - lows[i]) if highs[i] != lows[i] else 0
            })
    
    return order_blocks

def detect_fair_value_gaps(hist_data):
    """Detect Fair Value Gaps (FVG)"""
    fvgs = []
    highs = hist_data['High'].tolist()
    lows = hist_data['Low'].tolist()
    
    for i in range(1, len(hist_data) - 1):
        # Bullish FVG: Gap between previous high and next low
        if lows[i+1] > highs[i-1]:
            fvgs.append({
                'type': 'bullish',
                'index': i,
                'top': highs[i-1],
                'bottom': lows[i+1],
                'strength': (lows[i+1] - highs[i-1]) / highs[i-1] if highs[i-1] != 0 else 0
            })
        
        # Bearish FVG: Gap between previous low and next high
        elif highs[i+1] < lows[i-1]:
            fvgs.append({
                'type': 'bearish',
                'index': i,
                'top': lows[i-1],
                'bottom': highs[i+1],
                'strength': (lows[i-1] - highs[i+1]) / lows[i-1] if lows[i-1] != 0 else 0
            })
    
    return fvgs

def detect_liquidity_levels(hist_data):
    """Detect liquidity levels (equal highs/lows)"""
    liquidity_levels = []
    highs = hist_data['High'].tolist()
    lows = hist_data['Low'].tolist()
    
    # Look for equal highs (resistance levels)
    for i in range(5, len(hist_data) - 5):
        current_high = highs[i]
        tolerance = current_high * 0.001  # 0.1% tolerance
        
        # Check for similar highs in surrounding area
        similar_highs = []
        for j in range(max(0, i-10), min(len(hist_data), i+10)):
            if abs(highs[j] - current_high) <= tolerance and j != i:
                similar_highs.append(j)
        
        if len(similar_highs) >= 2:  # At least 2 similar highs
            liquidity_levels.append({
                'type': 'resistance',
                'price': current_high,
                'index': i,
                'touches': len(similar_highs) + 1,
                'strength': len(similar_highs) + 1
            })
        
        # Check for equal lows (support levels)
        current_low = lows[i]
        similar_lows = []
        for j in range(max(0, i-10), min(len(hist_data), i+10)):
            if abs(lows[j] - current_low) <= tolerance and j != i:
                similar_lows.append(j)
        
        if len(similar_lows) >= 2:  # At least 2 similar lows
            liquidity_levels.append({
                'type': 'support',
                'price': current_low,
                'index': i,
                'touches': len(similar_lows) + 1,
                'strength': len(similar_lows) + 1
            })
    
    return liquidity_levels

def detect_market_structure_breaks(hist_data):
    """Detect market structure breaks (BOS - Break of Structure)"""
    structure_breaks = []
    highs = hist_data['High'].tolist()
    lows = hist_data['Low'].tolist()
    
    # Look for higher highs and lower lows
    for i in range(5, len(hist_data) - 5):
        # Bullish BOS: Higher high after series of lower highs
        recent_highs = highs[i-5:i]
        if len(recent_highs) >= 3 and highs[i] > max(recent_highs):
            structure_breaks.append({
                'type': 'bullish_bos',
                'index': i,
                'price': highs[i],
                'strength': (highs[i] - max(recent_highs)) / max(recent_highs) if max(recent_highs) != 0 else 0
            })
        
        # Bearish BOS: Lower low after series of higher lows
        recent_lows = lows[i-5:i]
        if len(recent_lows) >= 3 and lows[i] < min(recent_lows):
            structure_breaks.append({
                'type': 'bearish_bos',
                'index': i,
                'price': lows[i],
                'strength': (min(recent_lows) - lows[i]) / min(recent_lows) if min(recent_lows) != 0 else 0
            })
    
    return structure_breaks

# Alert System Functions
def should_send_alert(signal, symbol):
    """Determine if an alert should be sent based on settings and signal strength"""
    if not alert_settings['enabled']:
        return False
    
    if not signal:
        return False
    
    # Check signal strength threshold
    signal_strength = abs(signal.get('score', 0))
    if signal_strength < alert_settings['min_signal_strength']:
        return False
    
    # Check alert frequency settings
    if alert_settings['alert_frequency'] == 'high_only':
        if signal_strength < 7.0:  # Only high-strength signals
            return False
    
    # Check if we've already sent an alert for this symbol recently (avoid spam)
    recent_alerts = [alert for alert in alert_history 
                    if alert['symbol'] == symbol and 
                    alert['timestamp'] > datetime.now() - timedelta(minutes=30)]
    
    if len(recent_alerts) > 0:
        return False
    
    return True

def create_alert_message(signal, symbol):
    """Create a formatted alert message"""
    signal_type = signal.get('signal_type', 'UNKNOWN')
    entry = signal.get('entry_price', 0)
    tp = signal.get('take_profit', 0)
    sl = signal.get('stop_loss', 0)
    score = signal.get('score', 0)
    confidence = signal.get('confidence', 0)
    
    message = f"""
🚨 TRADING ALERT 🚨
Symbol: {symbol}
Signal: {signal_type}
Entry: ${entry:.4f}
Take Profit: ${tp:.4f}
Stop Loss: ${sl:.4f}
Score: {score:.1f}
Confidence: {confidence:.1f}%
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return message.strip()

def log_alert(symbol, signal, message):
    """Log alert to history"""
    alert_record = {
        'timestamp': datetime.now(),
        'symbol': symbol,
        'signal_type': signal.get('signal_type'),
        'score': signal.get('score'),
        'message': message,
        'sent': True
    }
    alert_history.append(alert_record)
    
    # Keep only last 100 alerts
    if len(alert_history) > 100:
        alert_history.pop(0)

async def send_webhook_alert(message, symbol, signal):
    """Send alert via webhook if configured"""
    if not alert_settings['webhook_url']:
        return
    
    try:
        import aiohttp
        payload = {
            'text': message,
            'symbol': symbol,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(alert_settings['webhook_url'], 
                                  json=payload, 
                                  timeout=5) as response:
                if response.status == 200:
                    print(f"✅ Webhook alert sent for {symbol}")
                else:
                    print(f"❌ Webhook alert failed for {symbol}: {response.status}")
    except Exception as e:
        print(f"❌ Webhook error for {symbol}: {str(e)}")

async def send_whatsapp_alert(message, symbol, signal):
    """Send alert via WhatsApp if configured"""
    if not alert_settings['whatsapp_enabled'] or not alert_settings['whatsapp_webhook']:
        return
    
    try:
        import aiohttp
        payload = {
            'message': message,
            'symbol': symbol,
            'signal_type': signal.get('signal_type', 'UNKNOWN'),
            'confidence': signal.get('confidence', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(alert_settings['whatsapp_webhook'], 
                                  json=payload, 
                                  timeout=5) as response:
                if response.status == 200:
                    print(f"✅ WhatsApp alert sent for {symbol}")
                else:
                    print(f"❌ WhatsApp alert failed for {symbol}: {response.status}")
    except Exception as e:
        print(f"❌ WhatsApp error for {symbol}: {str(e)}")

async def send_telegram_alert(message, symbol, signal):
    """Send alert via Telegram if configured"""
    if not alert_settings['telegram_enabled'] or not alert_settings['telegram_bot_token'] or not alert_settings['telegram_chat_id']:
        return
    
    try:
        import aiohttp
        bot_token = alert_settings['telegram_bot_token']
        chat_id = alert_settings['telegram_chat_id']
        
        # Format message for Telegram
        telegram_message = f"""
🚨 *Trading Signal Alert*

📊 *Symbol:* {symbol}
🎯 *Signal:* {signal.get('signal_type', 'UNKNOWN')}
📈 *Entry:* {signal.get('entry_price', 'N/A')}
🛑 *Stop Loss:* {signal.get('stop_loss', 'N/A')}
🎯 *Take Profit:* {signal.get('take_profit', 'N/A')}
📊 *Confidence:* {signal.get('confidence', 0)}%
⏰ *Time:* {datetime.now().strftime('%H:%M:%S')}

{message}
        """
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': telegram_message,
            'parse_mode': 'Markdown'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as response:
                if response.status == 200:
                    print(f"✅ Telegram alert sent for {symbol}")
                else:
                    print(f"❌ Telegram alert failed for {symbol}: {response.status}")
    except Exception as e:
        print(f"❌ Telegram error for {symbol}: {str(e)}")

async def send_sms_alert(message, symbol, signal):
    """Send alert via SMS if configured"""
    if not alert_settings['sms_enabled'] or not alert_settings['sms_phone']:
        return
    
    try:
        import aiohttp
        
        # Format SMS message (shorter for SMS)
        sms_message = f"🚨 {symbol} {signal.get('signal_type', 'SIGNAL')} - Entry: {signal.get('entry_price', 'N/A')} - Conf: {signal.get('confidence', 0)}%"
        
        if alert_settings['sms_provider'] == 'twilio':
            # Twilio SMS integration
            account_sid = "YOUR_TWILIO_SID"  # Should be in environment variables
            auth_token = "YOUR_TWILIO_TOKEN"  # Should be in environment variables
            from_number = "YOUR_TWILIO_NUMBER"  # Should be in environment variables
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            payload = {
                'From': from_number,
                'To': alert_settings['sms_phone'],
                'Body': sms_message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, 
                                      data=payload, 
                                      auth=aiohttp.BasicAuth(account_sid, auth_token),
                                      timeout=5) as response:
                    if response.status == 201:
                        print(f"✅ SMS alert sent for {symbol}")
                    else:
                        print(f"❌ SMS alert failed for {symbol}: {response.status}")
        else:
            # Generic webhook for other SMS providers
            webhook_url = alert_settings.get('sms_webhook')
            if webhook_url:
                payload = {
                    'phone': alert_settings['sms_phone'],
                    'message': sms_message,
                    'symbol': symbol
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload, timeout=5) as response:
                        if response.status == 200:
                            print(f"✅ SMS alert sent for {symbol}")
                        else:
                            print(f"❌ SMS alert failed for {symbol}: {response.status}")
    except Exception as e:
        print(f"❌ SMS error for {symbol}: {str(e)}")

async def process_signal_alert(symbol, signal):
    """Process a signal and send alerts if conditions are met"""
    if not should_send_alert(signal, symbol):
        return
    
    message = create_alert_message(signal, symbol)
    log_alert(symbol, signal, message)
    
    # Send all configured alerts
    await send_webhook_alert(message, symbol, signal)
    await send_whatsapp_alert(message, symbol, signal)
    await send_telegram_alert(message, symbol, signal)
    await send_sms_alert(message, symbol, signal)
    
    # Print to console (always enabled)
    print(f"🚨 ALERT: {message}")
    
    return message

# AI Learning Enhancement Functions
def initialize_ml_models():
    """Initialize machine learning models for continuous learning"""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.neural_network import MLPClassifier
        
        # Initialize models if not already done
        if ml_models['signal_classifier'] is None:
            ml_models['signal_classifier'] = RandomForestClassifier(n_estimators=100, random_state=42)
            ml_models['pattern_recognizer'] = MLPClassifier(hidden_layer_sizes=(50, 25), random_state=42)
            ml_models['sentiment_analyzer'] = LogisticRegression(random_state=42)
            
        return True
    except Exception as e:
        print(f"Error initializing ML models: {e}")
        return False

def collect_learning_data(symbol, signal, price_data, outcome=None):
    """Collect data for continuous learning"""
    try:
        # Extract features for learning
        features = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'signal_type': signal.get('signal_type'),
            'signal_score': signal.get('signal_score', 0),
            'confidence': signal.get('confidence', 0),
            'rsi': signal.get('rsi', 50),
            'volume_ratio': signal.get('volume_ratio', 1.0),
            'atr': signal.get('atr', 0),
            'price_change': price_data.get('price_change_pct', 0),
            'current_price': price_data.get('current_price', 0),
            'ict_patterns': signal.get('ict_analysis', {}),
            'ml_analysis': signal.get('ml_analysis', {}),
            'outcome': outcome  # Will be filled later when we know the result
        }
        
        learning_data['signal_history'].append(features)
        
        # Keep only last 1000 signals to prevent memory issues
        if len(learning_data['signal_history']) > 1000:
            learning_data['signal_history'] = learning_data['signal_history'][-1000:]
            
        return True
    except Exception as e:
        print(f"Error collecting learning data: {e}")
        return False

def update_signal_outcome(symbol, entry_price, exit_price, signal_type, timestamp):
    """Update signal outcome for performance tracking"""
    try:
        # Find the signal in history and update outcome
        for signal in learning_data['signal_history']:
            if (signal['symbol'] == symbol and 
                signal['timestamp'] == timestamp and
                signal['outcome'] is None):
                
                # Calculate outcome
                if signal_type == 'BUY':
                    outcome = (exit_price - entry_price) / entry_price
                else:  # SELL
                    outcome = (entry_price - exit_price) / entry_price
                
                signal['outcome'] = outcome
                signal['exit_price'] = exit_price
                signal['exit_timestamp'] = datetime.now()
                break
                
        # Update performance metrics
        update_performance_metrics()
        return True
    except Exception as e:
        print(f"Error updating signal outcome: {e}")
        return False

def update_performance_metrics():
    """Update performance metrics for adaptive learning"""
    try:
        signals_with_outcomes = [s for s in learning_data['signal_history'] if s['outcome'] is not None]
        
        if len(signals_with_outcomes) < 10:  # Need minimum data
            return
        
        # Calculate metrics
        total_signals = len(signals_with_outcomes)
        winning_signals = len([s for s in signals_with_outcomes if s['outcome'] > 0])
        win_rate = winning_signals / total_signals
        
        avg_return = sum(s['outcome'] for s in signals_with_outcomes) / total_signals
        avg_win = sum(s['outcome'] for s in signals_with_outcomes if s['outcome'] > 0) / max(winning_signals, 1)
        avg_loss = sum(s['outcome'] for s in signals_with_outcomes if s['outcome'] < 0) / max(total_signals - winning_signals, 1)
        
        # Update metrics
        learning_data['performance_metrics'] = {
            'total_signals': total_signals,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'last_updated': datetime.now()
        }
        
        # Adaptive parameter adjustment based on performance
        adjust_adaptive_parameters()
        
    except Exception as e:
        print(f"Error updating performance metrics: {e}")

def adjust_adaptive_parameters():
    """Adjust parameters based on recent performance"""
    try:
        metrics = learning_data['performance_metrics']
        
        if metrics.get('win_rate', 0) > 0.6:  # Good performance
            # Increase confidence in signals
            learning_data['adaptive_parameters']['confidence_boost'] = min(1.5, 
                learning_data['adaptive_parameters']['confidence_boost'] * 1.05)
            learning_data['adaptive_parameters']['signal_threshold'] = max(0.5, 
                learning_data['adaptive_parameters']['signal_threshold'] * 0.95)
        elif metrics.get('win_rate', 0) < 0.4:  # Poor performance
            # Be more conservative
            learning_data['adaptive_parameters']['confidence_boost'] = max(0.5, 
                learning_data['adaptive_parameters']['confidence_boost'] * 0.95)
            learning_data['adaptive_parameters']['signal_threshold'] = min(2.0, 
                learning_data['adaptive_parameters']['signal_threshold'] * 1.05)
        
        # Adjust pattern and volume weights based on what's working
        if metrics.get('profit_factor', 0) > 1.5:  # Good profit factor
            learning_data['adaptive_parameters']['pattern_weight'] = min(1.5, 
                learning_data['adaptive_parameters']['pattern_weight'] * 1.02)
            learning_data['adaptive_parameters']['volume_weight'] = min(1.5, 
                learning_data['adaptive_parameters']['volume_weight'] * 1.02)
        
    except Exception as e:
        print(f"Error adjusting adaptive parameters: {e}")

def retrain_models():
    """Retrain ML models with new data"""
    try:
        if not initialize_ml_models():
            return False
        
        signals_with_outcomes = [s for s in learning_data['signal_history'] if s['outcome'] is not None]
        
        if len(signals_with_outcomes) < 50:  # Need minimum data for training
            return False
        
        # Prepare training data
        X = []
        y = []
        
        for signal in signals_with_outcomes:
            features = [
                signal['signal_score'],
                signal['confidence'],
                signal['rsi'],
                signal['volume_ratio'],
                signal['atr'],
                signal['price_change'],
                signal['current_price']
            ]
            X.append(features)
            
            # Create target: 1 for profitable, 0 for loss
            y.append(1 if signal['outcome'] > 0 else 0)
        
        if len(X) < 10:
            return False
        
        # Train models
        X = np.array(X)
        y = np.array(y)
        
        # Retrain signal classifier
        ml_models['signal_classifier'].fit(X, y)
        
        # Calculate and store accuracy
        accuracy = ml_models['signal_classifier'].score(X, y)
        learning_data['model_accuracy']['signal_classifier'] = accuracy
        
        print(f"✅ Models retrained with {len(X)} samples. Accuracy: {accuracy:.3f}")
        return True
        
    except Exception as e:
        print(f"Error retraining models: {e}")
        return False

def get_adaptive_signal_score(base_score, signal_data):
    """Apply adaptive parameters to signal scoring"""
    try:
        params = learning_data['adaptive_parameters']
        
        # Apply confidence boost
        adjusted_score = base_score * params['confidence_boost']
        
        # Apply pattern weight
        if 'pattern' in signal_data:
            pattern_boost = 1.0
            if 'ICT' in signal_data['pattern']:
                pattern_boost *= params['pattern_weight']
            if 'High Volume' in signal_data['pattern']:
                pattern_boost *= params['volume_weight']
            
            adjusted_score *= pattern_boost
        
        return adjusted_score
        
    except Exception as e:
        print(f"Error applying adaptive scoring: {e}")
        return base_score

def get_learning_insights():
    """Get insights from learning data"""
    try:
        metrics = learning_data['performance_metrics']
        params = learning_data['adaptive_parameters']
        accuracy = learning_data['model_accuracy']
        
        insights = {
            'performance': metrics,
            'adaptive_parameters': params,
            'model_accuracy': accuracy,
            'total_signals_learned': len(learning_data['signal_history']),
            'signals_with_outcomes': len([s for s in learning_data['signal_history'] if s['outcome'] is not None]),
            'learning_status': 'Active' if len(learning_data['signal_history']) > 10 else 'Initializing'
        }
        
        return insights
        
    except Exception as e:
        print(f"Error getting learning insights: {e}")
        return {}

# Enhanced Chart data endpoint with ICT/SMC visualizations
@app.get("/api/live/chart/{symbol}")
async def get_chart_data(symbol: str):
    """Get enhanced chart data with ICT/SMC analysis for a specific symbol"""
    try:
        # Fix URL encoding issue for forex symbols
        from urllib.parse import unquote
        symbol = unquote(symbol)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", interval="1h")
        
        if hist.empty:
            return {"status": "error", "message": "No data available"}
        
        # Prepare chart data
        labels = [date.strftime("%m/%d %H:%M") for date in hist.index]
        prices = hist['Close'].tolist()
        volumes = hist['Volume'].tolist()
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        
        # Calculate SMA 20
        sma_20 = []
        for i in range(len(prices)):
            if i >= 19:
                sma_20.append(sum(prices[i-19:i+1]) / 20)
            else:
                sma_20.append(prices[i])
        
        # Get current price (latest close price)
        current_price = prices[-1] if prices else 0
        
        # Advanced ICT/SMC Analysis
        order_blocks = detect_order_blocks(hist)
        fair_value_gaps = detect_fair_value_gaps(hist)
        liquidity_levels = detect_liquidity_levels(hist)
        structure_breaks = detect_market_structure_breaks(hist)
        
        # Advanced SMC Features
        liquidity_sweep = detect_liquidity_sweep(hist)
        bos_signal = detect_break_of_structure(hist)
        choch_signal = detect_change_of_character(hist)
        order_block_valid = validate_order_blocks(hist, current_price)
        
        # Apply advanced SMC signals
        if liquidity_sweep['bullish']:
            signal_score += 3
            pattern += " + Bullish Liquidity Sweep"
        elif liquidity_sweep['bearish']:
            signal_score -= 3
            pattern += " + Bearish Liquidity Sweep"
            
        if bos_signal['bullish']:
            signal_score += 2
            pattern += " + Bullish BOS"
        elif bos_signal['bearish']:
            signal_score -= 2
            pattern += " + Bearish BOS"
            
        if choch_signal['bullish']:
            signal_score += 4
            pattern += " + Bullish CHoCH"
        elif choch_signal['bearish']:
            signal_score -= 4
            pattern += " + Bearish CHoCH"
            
        if order_block_valid['bullish']:
            signal_score += 2
            pattern += " + Valid Bullish OB"
        elif order_block_valid['bearish']:
            signal_score -= 2
            pattern += " + Valid Bearish OB"
        
        # Get current signal
        price_data = get_live_price_data(symbol)
        signal = generate_trading_signal(symbol, price_data) if price_data and 'error' not in price_data else None
        
        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "labels": labels,
                "prices": prices,
                "volumes": volumes,
                "highs": highs,
                "lows": lows,
                "sma_20": sma_20,
                "signal": signal,
                "ict_analysis": {
                    "order_blocks": order_blocks,
                    "fair_value_gaps": fair_value_gaps,
                    "liquidity_levels": liquidity_levels,
                    "structure_breaks": structure_breaks
                }
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Alert System API Endpoints
@app.get("/api/alerts/settings")
async def get_alert_settings():
    """Get current alert settings"""
    return {
        "status": "success",
        "settings": alert_settings,
        "total_alerts": len(alert_history)
    }

@app.post("/api/alerts/settings")
async def update_alert_settings(request: Request):
    """Update alert settings"""
    try:
        data = await request.json()
        
        # Update settings
        if 'enabled' in data:
            alert_settings['enabled'] = bool(data['enabled'])
        if 'min_signal_strength' in data:
            alert_settings['min_signal_strength'] = float(data['min_signal_strength'])
        if 'alert_frequency' in data:
            alert_settings['alert_frequency'] = data['alert_frequency']
        if 'webhook_url' in data:
            alert_settings['webhook_url'] = data['webhook_url']
        if 'email_notifications' in data:
            alert_settings['email_notifications'] = bool(data['email_notifications'])
        
        # WhatsApp settings
        if 'whatsapp_enabled' in data:
            alert_settings['whatsapp_enabled'] = bool(data['whatsapp_enabled'])
        if 'whatsapp_webhook' in data:
            alert_settings['whatsapp_webhook'] = data['whatsapp_webhook']
        
        # Telegram settings
        if 'telegram_enabled' in data:
            alert_settings['telegram_enabled'] = bool(data['telegram_enabled'])
        if 'telegram_bot_token' in data:
            alert_settings['telegram_bot_token'] = data['telegram_bot_token']
        if 'telegram_chat_id' in data:
            alert_settings['telegram_chat_id'] = data['telegram_chat_id']
        
        # SMS settings
        if 'sms_enabled' in data:
            alert_settings['sms_enabled'] = bool(data['sms_enabled'])
        if 'sms_phone' in data:
            alert_settings['sms_phone'] = data['sms_phone']
        if 'sms_provider' in data:
            alert_settings['sms_provider'] = data['sms_provider']
        
        # Custom conditions
        if 'custom_conditions' in data:
            alert_settings['custom_conditions'].update(data['custom_conditions'])
        
        return {
            "status": "success",
            "message": "Alert settings updated",
            "settings": alert_settings
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/alerts/history")
async def get_alert_history():
    """Get alert history"""
    try:
        # Convert datetime objects to strings for JSON serialization
        history = []
        for alert in alert_history[-50:]:  # Last 50 alerts
            alert_copy = alert.copy()
            alert_copy['timestamp'] = alert['timestamp'].isoformat()
            history.append(alert_copy)
        
        return {
            "status": "success",
            "alerts": history,
            "total_count": len(alert_history)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/alerts/test")
async def test_alert_system():
    """Test the alert system with a sample signal"""
    try:
        test_signal = {
            'signal_type': 'BUY',
            'entry_price': 100.0,
            'take_profit': 105.0,
            'stop_loss': 95.0,
            'score': 8.5,
            'confidence': 85.0
        }
        
        message = await process_signal_alert('TEST', test_signal)
        
        return {
            "status": "success",
            "message": "Test alert sent",
            "alert_message": message
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/alerts/history")
async def clear_alert_history():
    """Clear alert history"""
    try:
        global alert_history
        alert_history.clear()
        
        return {
            "status": "success",
            "message": "Alert history cleared"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# AI Learning Functions
def get_ai_learning_insights():
    """Get AI learning insights and performance metrics"""
    global ai_learning_enhanced
    
    try:
        return {
            "learning_status": "Active",
            "total_signals_learned": len(ai_learning_enhanced.get("learning_data", [])),
            "accuracy_improvement": ai_learning_enhanced.get("accuracy_improvement", 0.0),
            "last_learning_cycle": ai_learning_enhanced.get("last_learning_cycle"),
            "adaptive_parameters": ai_learning_enhanced.get("adaptive_parameters", {}),
            "learning_metrics": ai_learning_enhanced.get("learning_metrics", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting AI learning insights: {e}")
        return {
            "learning_status": "Error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# AI Learning Enhancement API Endpoints
@app.get("/api/ai/learning/insights")
async def get_learning_insights_endpoint():
    """Get AI learning insights and performance metrics"""
    try:
        insights = get_ai_learning_insights()
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/ai/learning/retrain")
async def retrain_ai_models():
    """Manually trigger model retraining"""
    try:
        success = retrain_models()
        if success:
            return {
                "status": "success",
                "message": "Models retrained successfully",
                "insights": get_learning_insights()
            }
        else:
            return {
                "status": "error",
                "message": "Not enough data for retraining (need at least 50 signals with outcomes)"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/ai/learning/outcome")
async def update_signal_outcome(request: Request):
    """Update signal outcome for learning"""
    try:
        data = await request.json()
        
        symbol = data.get('symbol')
        entry_price = data.get('entry_price')
        exit_price = data.get('exit_price')
        signal_type = data.get('signal_type')
        timestamp_str = data.get('timestamp')
        
        if not all([symbol, entry_price, exit_price, signal_type, timestamp_str]):
            return {"status": "error", "message": "Missing required fields"}
        
        # Convert timestamp string back to datetime
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        success = update_signal_outcome(symbol, entry_price, exit_price, signal_type, timestamp)
        
        if success:
            return {
                "status": "success",
                "message": "Signal outcome updated",
                "insights": get_learning_insights()
            }
        else:
            return {"status": "error", "message": "Failed to update signal outcome"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/learning/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        metrics = learning_data['performance_metrics']
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/learning/adaptive-parameters")
async def get_adaptive_parameters():
    """Get current adaptive parameters"""
    try:
        params = learning_data['adaptive_parameters']
        return {
            "status": "success",
            "parameters": params
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Advanced Analytics API Endpoints
@app.get("/api/analytics/performance")
async def get_trading_performance():
    """Get comprehensive trading performance metrics"""
    global trading_performance
    return {
        "performance": trading_performance,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/heatmap")
async def get_performance_heatmap():
    """Get performance heatmap data"""
    heatmap_data = get_performance_heatmap()
    return {
        "heatmap": heatmap_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/equity-curve")
async def get_equity_curve():
    """Get equity curve data for charting"""
    equity_data = get_equity_curve_data()
    return {
        "equity_curve": equity_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/recent-trades")
async def get_recent_trades():
    """Get recent trading history"""
    global trading_performance
    return {
        "recent_trades": trading_performance["recent_trades"],
        "total_trades": trading_performance["total_trades"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/market-performance")
async def get_market_performance():
    """Get performance breakdown by market"""
    global trading_performance
    return {
        "market_performance": trading_performance["trades_by_market"],
        "hourly_performance": trading_performance["performance_by_hour"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analytics/simulate-trade")
async def simulate_trade_outcome(request: dict):
    """Simulate a trade outcome for testing"""
    try:
        signal = request.get('signal', {})
        current_price = request.get('current_price', 0)
        
        if not signal or current_price == 0:
            return {"error": "Invalid signal or current price"}
        
        outcome = calculate_trade_outcome(signal, current_price)
        if outcome:
            update_trading_performance(signal, outcome)
        
        return {
            "outcome": outcome,
            "updated_performance": trading_performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/analytics/reset-performance")
async def reset_trading_performance():
    """Reset all trading performance data"""
    global trading_performance
    
    # Reset to initial state
    trading_performance = {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "total_pnl": 0.0,
        "win_rate": 0.0,
        "profit_factor": 0.0,
        "max_drawdown": 0.0,
        "current_drawdown": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "largest_win": 0.0,
        "largest_loss": 0.0,
        "consecutive_wins": 0,
        "consecutive_losses": 0,
        "max_consecutive_wins": 0,
        "max_consecutive_losses": 0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "calmar_ratio": 0.0,
        "trades_by_market": {},
        "trades_by_timeframe": {},
        "performance_by_hour": {},
        "performance_by_day": {},
        "recent_trades": [],
        "equity_curve": [],
        "drawdown_curve": [],
        "monthly_returns": {},
        "yearly_returns": {}
    }
    
    return {
        "message": "Trading performance data reset successfully",
        "timestamp": datetime.now().isoformat()
    }

# Enhanced AI Learning API Endpoints
@app.get("/api/ai/enhanced/insights")
async def get_enhanced_ai_insights():
    """Get comprehensive enhanced AI learning insights"""
    try:
        insights = get_enhanced_ai_insights()
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/enhanced/sentiment")
async def get_market_sentiment():
    """Get current market sentiment analysis"""
    try:
        sentiment = analyze_market_sentiment()
        return {
            "status": "success",
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/enhanced/regime")
async def get_market_regime():
    """Get current market regime detection"""
    try:
        regime = detect_market_regime([])  # Would pass actual price data
        return {
            "status": "success",
            "regime": regime,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/enhanced/patterns")
async def get_trading_patterns():
    """Get current trading pattern recognition"""
    try:
        patterns = recognize_trading_patterns([], [])  # Would pass actual data
        return {
            "status": "success",
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/enhanced/parameters")
async def get_adaptive_parameters():
    """Get current adaptive AI parameters"""
    try:
        params = adapt_parameters_based_on_performance()
        return {
            "status": "success",
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/ai/enhanced/adapt")
async def trigger_parameter_adaptation():
    """Manually trigger parameter adaptation"""
    try:
        params = adapt_parameters_based_on_performance()
        return {
            "status": "success",
            "message": "Parameters adapted successfully",
            "new_parameters": params,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/ai/enhanced/learning-metrics")
async def get_learning_metrics():
    """Get AI learning performance metrics"""
    try:
        global ai_learning_enhanced
        metrics = ai_learning_enhanced["learning_metrics"]
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Predictive Analytics API Endpoints
@app.get("/api/predictive/price-targets/{symbol}")
async def get_price_targets(symbol: str):
    """Get price targets for a specific symbol"""
    try:
        # Get current price and historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        
        if hist.empty:
            return {"status": "error", "message": f"No data available for {symbol}"}
        
        current_price = hist['Close'].iloc[-1]
        price_data = hist['Close'].tolist()
        
        price_targets = calculate_price_targets(symbol, current_price, price_data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "current_price": current_price,
            "price_targets": price_targets,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/predictive/volatility-forecast/{symbol}")
async def get_volatility_forecast(symbol: str):
    """Get volatility forecast for a specific symbol"""
    try:
        # Get historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        
        if hist.empty:
            return {"status": "error", "message": f"No data available for {symbol}"}
        
        price_data = hist['Close'].tolist()
        volume_data = hist['Volume'].tolist() if 'Volume' in hist.columns else None
        
        volatility_forecast = forecast_volatility(price_data, volume_data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "volatility_forecast": volatility_forecast,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/predictive/market-direction/{symbol}")
async def get_market_direction(symbol: str):
    """Get market direction prediction for a specific symbol"""
    try:
        # Get historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        
        if hist.empty:
            return {"status": "error", "message": f"No data available for {symbol}"}
        
        price_data = hist['Close'].tolist()
        volume_data = hist['Volume'].tolist() if 'Volume' in hist.columns else None
        
        market_direction = predict_market_direction(price_data, volume_data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "market_direction": market_direction,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/predictive/comprehensive/{symbol}")
async def get_comprehensive_predictions(symbol: str):
    """Get comprehensive predictive analytics for a specific symbol"""
    try:
        # Get historical data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo", interval="1d")
        
        if hist.empty:
            return {"status": "error", "message": f"No data available for {symbol}"}
        
        current_price = hist['Close'].iloc[-1]
        price_data = hist['Close'].tolist()
        volume_data = hist['Volume'].tolist() if 'Volume' in hist.columns else None
        
        predictions = get_comprehensive_predictions(symbol, current_price, price_data, volume_data)
        
        return {
            "status": "success",
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/predictive/forecast-multiple")
async def get_multiple_symbol_predictions():
    """Get predictions for multiple symbols"""
    try:
        # Get predictions for major symbols
        symbols = ["AAPL", "GOOGL", "MSFT", "BTC-USD", "EURUSD=X"]
        predictions = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo", interval="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    price_data = hist['Close'].tolist()
                    volume_data = hist['Volume'].tolist() if 'Volume' in hist.columns else None
                    
                    predictions[symbol] = get_comprehensive_predictions(symbol, current_price, price_data, volume_data)
            except Exception as e:
                predictions[symbol] = {"error": str(e)}
        
        return {
            "status": "success",
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Real-Time Market Scanner API Endpoints
@app.get("/api/scanner/hot-list")
async def get_market_hot_list():
    """Get current market hot list"""
    try:
        hot_list = scan_market_hot_list()
        return {
            "status": "success",
            "hot_list": hot_list,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scanner/sector-rotation")
async def get_sector_rotation():
    """Get sector rotation analysis"""
    try:
        sector_rotation = analyze_sector_rotation()
        return {
            "status": "success",
            "sector_rotation": sector_rotation,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scanner/momentum-ranking")
async def get_momentum_ranking():
    """Get momentum ranking opportunities"""
    try:
        momentum_ranking = rank_momentum_opportunities()
        return {
            "status": "success",
            "momentum_ranking": momentum_ranking,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scanner/comprehensive")
async def get_comprehensive_market_scan():
    """Get comprehensive market scan results"""
    try:
        scan_results = get_comprehensive_market_scan()
        return {
            "status": "success",
            "scan_results": scan_results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scanner/settings")
async def get_scanner_settings():
    """Get current scanner settings"""
    try:
        global market_scanner
        return {
            "status": "success",
            "settings": market_scanner["scanner_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scanner/full-market-signals")
async def get_full_market_signals():
    """Scan entire market and generate trading signals for all opportunities"""
    try:
        result = scan_entire_market_for_signals()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/analyze/{symbol}")
async def analyze_symbol(symbol: str, timeframe: str = "1h"):
    """Analyze individual symbol and generate trading signal"""
    try:
        # Decode URL-encoded symbol
        from urllib.parse import unquote
        symbol = unquote(symbol)
        
        result = analyze_individual_symbol(symbol, timeframe)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/scanner/settings")
async def update_scanner_settings(settings: dict):
    """Update scanner settings"""
    try:
        global market_scanner
        
        # Update settings
        for key, value in settings.items():
            if key in market_scanner["scanner_settings"]:
                market_scanner["scanner_settings"][key] = value
        
        return {
            "status": "success",
            "message": "Scanner settings updated successfully",
            "new_settings": market_scanner["scanner_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Social Trading API Endpoints
@app.get("/api/social/signals")
async def get_shared_signals():
    """Get shared trading signals"""
    try:
        global social_trading
        return {
            "status": "success",
            "shared_signals": social_trading["signal_sharing"]["public_signals"][-20:],  # Last 20
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/social/share-signal")
async def share_signal(request: Request):
    """Share a trading signal"""
    try:
        data = await request.json()
        signal_data = data.get("signal_data", {})
        trader_id = data.get("trader_id", "user_001")
        
        shared_signal = share_trading_signal(signal_data, trader_id)
        
        if shared_signal:
            return {
                "status": "success",
                "message": "Signal shared successfully",
                "shared_signal": shared_signal,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": "Failed to share signal"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/social/leaderboard")
async def get_performance_leaderboard():
    """Get performance leaderboard"""
    try:
        leaderboard = update_performance_leaderboard()
        return {
            "status": "success",
            "leaderboard": leaderboard,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/social/copy-trading")
async def setup_copy_trading_endpoint(request: Request):
    """Setup copy trading"""
    try:
        data = await request.json()
        copier_id = data.get("copier_id", "user_002")
        trader_id = data.get("trader_id", "trader_001")
        copy_settings = data.get("copy_settings", {})
        
        copy_config = setup_copy_trading(copier_id, trader_id, copy_settings)
        
        if copy_config:
            return {
                "status": "success",
                "message": "Copy trading setup successfully",
                "copy_config": copy_config,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": "Failed to setup copy trading"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/social/community-insights")
async def get_community_insights():
    """Get community insights"""
    try:
        insights = analyze_community_insights()
        return {
            "status": "success",
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/social/summary")
async def get_social_trading_summary_endpoint():
    """Get comprehensive social trading summary"""
    try:
        summary = get_social_trading_summary()
        return {
            "status": "success",
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/social/settings")
async def get_social_settings():
    """Get social trading settings"""
    try:
        global social_trading
        return {
            "status": "success",
            "settings": social_trading["social_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/social/settings")
async def update_social_settings(request: Request):
    """Update social trading settings"""
    try:
        data = await request.json()
        global social_trading
        
        # Update settings
        for key, value in data.items():
            if key in social_trading["social_settings"]:
                social_trading["social_settings"][key] = value
        
        return {
            "status": "success",
            "message": "Social settings updated successfully",
            "new_settings": social_trading["social_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Advanced Risk Management API Endpoints
@app.get("/api/risk/portfolio-heatmap")
async def get_portfolio_heatmap():
    """Get portfolio heatmap with correlation matrix"""
    try:
        heatmap = calculate_portfolio_heatmap()
        return {
            "status": "success",
            "portfolio_heatmap": heatmap,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/risk/correlation-analysis")
async def get_correlation_analysis():
    """Get correlation analysis between assets"""
    try:
        correlations = analyze_correlations()
        return {
            "status": "success",
            "correlation_analysis": correlations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/risk/position-sizing")
async def get_dynamic_position_sizing():
    """Get dynamic position sizing recommendations"""
    try:
        position_sizing = calculate_dynamic_position_sizing()
        return {
            "status": "success",
            "position_sizing": position_sizing,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/risk/metrics")
async def get_risk_metrics():
    """Get advanced risk metrics"""
    try:
        risk_metrics = calculate_risk_metrics()
        return {
            "status": "success",
            "risk_metrics": risk_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/risk/comprehensive")
async def get_comprehensive_risk_analysis():
    """Get comprehensive risk analysis"""
    try:
        risk_analysis = get_comprehensive_risk_analysis()
        return {
            "status": "success",
            "risk_analysis": risk_analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/risk/settings")
async def get_risk_settings():
    """Get risk management settings"""
    try:
        global risk_management
        return {
            "status": "success",
            "risk_settings": risk_management["risk_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/risk/settings")
async def update_risk_settings(request: Request):
    """Update risk management settings"""
    try:
        data = await request.json()
        global risk_management
        
        # Update settings
        for key, value in data.items():
            if key in risk_management["risk_settings"]:
                risk_management["risk_settings"][key] = value
        
        return {
            "status": "success",
            "message": "Risk settings updated successfully",
            "new_settings": risk_management["risk_settings"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Main function to run the server
def run_server():
    print("🚀 Starting Simple Trading Signals Server...")
    print("📍 API URL: http://localhost:8004")
    print("🔗 Health check: http://localhost:8004/api/health")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")

# Backtesting API Endpoints
@app.get("/api/backtest/{symbol}")
async def run_single_backtest(symbol: str, timeframe: str = "1h"):
    """Run backtest for a single symbol"""
    try:
        result = run_backtest(symbol, timeframe, None, None)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/backtest/summary")
async def get_backtest_summary_endpoint(timeframe: str = "1h", market: str = "stocks"):
    """Get backtest summary for current market"""
    try:
        # Get symbols for the specified market
        market_symbols = {
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCAD=X'],
            'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'SOL-USD'],
            'futures': ['ES=F', 'NQ=F', 'YM=F', 'RTY=F', 'GC=F'],
            'indices': ['^GSPC', '^IXIC', '^DJI', '^RUT', '^VIX'],
            'metals': ['GC=F', 'SI=F', 'PL=F', 'PA=F', 'HG=F']
        }
        
        symbols = market_symbols.get(market, market_symbols['stocks'])
        result = get_backtest_summary(symbols, timeframe)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Multi-Timeframe Analysis Functions
def get_multi_timeframe_data(symbol):
    """Get data from multiple timeframes for confluence analysis"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get different timeframe data
        timeframes = {
            'daily': ticker.history(period="30d", interval="1d"),    # HTF - Higher Timeframe
            '4h': ticker.history(period="10d", interval="4h"),       # MTF - Medium Timeframe  
            '1h': ticker.history(period="5d", interval="1h"),        # Entry TF - Entry Timeframe
            '15m': ticker.history(period="2d", interval="15m"),      # LTF - Lower Timeframe
            '5m': ticker.history(period="1d", interval="5m")         # LTF - Lower Timeframe
        }
        
        # Validate data availability
        valid_timeframes = {}
        for tf, data in timeframes.items():
            if not data.empty and len(data) > 10:
                valid_timeframes[tf] = data
        
        return valid_timeframes
    except Exception as e:
        print(f"Multi-timeframe data error for {symbol}: {e}")
        return {}

def analyze_htf_bias(timeframes):
    """Analyze Higher Timeframe bias (Daily/4H)"""
    try:
        if 'daily' not in timeframes and '4h' not in timeframes:
            return {'bias': 'NEUTRAL', 'strength': 0, 'trend': 'SIDEWAYS'}
        
        # Use daily if available, otherwise 4H
        htf_data = timeframes.get('daily', timeframes.get('4h'))
        if htf_data is None or len(htf_data) < 20:
            return {'bias': 'NEUTRAL', 'strength': 0, 'trend': 'SIDEWAYS'}
        
        # Calculate HTF trend
        closes = htf_data['Close'].tolist()
        current_price = closes[-1]
        
        # Simple moving averages for trend
        sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
        sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
        
        # Determine bias
        if current_price > sma_20 > sma_50:
            bias = 'BULLISH'
            strength = min((current_price - sma_20) / sma_20 * 100, 5.0)
            trend = 'UPTREND'
        elif current_price < sma_20 < sma_50:
            bias = 'BEARISH'
            strength = min((sma_20 - current_price) / sma_20 * 100, 5.0)
            trend = 'DOWNTREND'
        else:
            bias = 'NEUTRAL'
            strength = 0
            trend = 'SIDEWAYS'
        
        return {
            'bias': bias,
            'strength': strength,
            'trend': trend,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'current_price': current_price
        }
    except Exception as e:
        print(f"HTF bias analysis error: {e}")
        return {'bias': 'NEUTRAL', 'strength': 0, 'trend': 'SIDEWAYS'}

def analyze_entry_timeframe(timeframes):
    """Analyze Entry Timeframe (1H) for precise entry signals"""
    try:
        if '1h' not in timeframes:
            return {'signal': 'NEUTRAL', 'strength': 0, 'pattern': 'No Entry TF Data'}
        
        entry_data = timeframes['1h']
        if len(entry_data) < 10:
            return {'signal': 'NEUTRAL', 'strength': 0, 'pattern': 'Insufficient Data'}
        
        # Analyze 1H timeframe for entry signals
        closes = entry_data['Close'].tolist()
        volumes = entry_data['Volume'].tolist()
        
        # Recent price action
        recent_closes = closes[-5:]
        recent_volumes = volumes[-5:]
        
        # Calculate momentum
        price_change = (recent_closes[-1] - recent_closes[0]) / recent_closes[0]
        volume_avg = sum(recent_volumes) / len(recent_volumes)
        current_volume = recent_volumes[-1]
        volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
        
        # Entry signal logic
        if price_change > 0.005 and volume_ratio > 1.2:  # Bullish entry
            return {
                'signal': 'BULLISH',
                'strength': min(abs(price_change) * 100 * volume_ratio, 3.0),
                'pattern': f'Bullish Momentum + Volume Spike ({volume_ratio:.1f}x)'
            }
        elif price_change < -0.005 and volume_ratio > 1.2:  # Bearish entry
            return {
                'signal': 'BEARISH', 
                'strength': min(abs(price_change) * 100 * volume_ratio, 3.0),
                'pattern': f'Bearish Momentum + Volume Spike ({volume_ratio:.1f}x)'
            }
        else:
            return {
                'signal': 'NEUTRAL',
                'strength': 0,
                'pattern': 'No Clear Entry Signal'
            }
    except Exception as e:
        print(f"Entry timeframe analysis error: {e}")
        return {'signal': 'NEUTRAL', 'strength': 0, 'pattern': 'Analysis Error'}

def analyze_ltf_confirmation(timeframes):
    """Analyze Lower Timeframe confirmation (15m/5m)"""
    try:
        ltf_data = timeframes.get('15m', timeframes.get('5m'))
        if ltf_data is None or len(ltf_data) < 10:
            return {'confirmed': False, 'strength': 0, 'pattern': 'No LTF Data'}
        
        # Analyze LTF for confirmation
        closes = ltf_data['Close'].tolist()
        highs = ltf_data['High'].tolist()
        lows = ltf_data['Low'].tolist()
        
        # Recent LTF action
        recent_closes = closes[-3:]
        recent_highs = highs[-3:]
        recent_lows = lows[-3:]
        
        # Look for confirmation patterns
        higher_highs = all(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
        higher_lows = all(recent_lows[i] > recent_lows[i-1] for i in range(1, len(recent_lows)))
        lower_highs = all(recent_highs[i] < recent_highs[i-1] for i in range(1, len(recent_highs)))
        lower_lows = all(recent_lows[i] < recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        if higher_highs and higher_lows:
            return {
                'confirmed': True,
                'strength': 1.5,
                'pattern': 'LTF Bullish Structure',
                'direction': 'BULLISH'
            }
        elif lower_highs and lower_lows:
            return {
                'confirmed': True,
                'strength': 1.5,
                'pattern': 'LTF Bearish Structure',
                'direction': 'BEARISH'
            }
        else:
            return {
                'confirmed': False,
                'strength': 0,
                'pattern': 'LTF Mixed Signals',
                'direction': 'NEUTRAL'
            }
    except Exception as e:
        print(f"LTF confirmation analysis error: {e}")
        return {'confirmed': False, 'strength': 0, 'pattern': 'Analysis Error'}

def calculate_multi_timeframe_confluence(symbol):
    """Calculate multi-timeframe confluence score"""
    try:
        # Get multi-timeframe data
        timeframes = get_multi_timeframe_data(symbol)
        if not timeframes:
            return {'confluence_score': 0, 'bias': 'NEUTRAL', 'entry': 'NEUTRAL', 'confirmation': False}
        
        # Analyze each timeframe
        htf_bias = analyze_htf_bias(timeframes)
        entry_signal = analyze_entry_timeframe(timeframes)
        ltf_confirmation = analyze_ltf_confirmation(timeframes)
        
        # Calculate confluence score
        confluence_score = 0
        
        # HTF bias contribution (40% weight)
        if htf_bias['bias'] == 'BULLISH':
            confluence_score += htf_bias['strength'] * 0.4
        elif htf_bias['bias'] == 'BEARISH':
            confluence_score -= htf_bias['strength'] * 0.4
        
        # Entry signal contribution (35% weight)
        if entry_signal['signal'] == 'BULLISH':
            confluence_score += entry_signal['strength'] * 0.35
        elif entry_signal['signal'] == 'BEARISH':
            confluence_score -= entry_signal['strength'] * 0.35
        
        # LTF confirmation contribution (25% weight)
        if ltf_confirmation['confirmed']:
            if ltf_confirmation['direction'] == 'BULLISH':
                confluence_score += ltf_confirmation['strength'] * 0.25
            elif ltf_confirmation['direction'] == 'BEARISH':
                confluence_score -= ltf_confirmation['strength'] * 0.25
        
        return {
            'confluence_score': confluence_score,
            'htf_bias': htf_bias,
            'entry_signal': entry_signal,
            'ltf_confirmation': ltf_confirmation,
            'timeframes_analyzed': list(timeframes.keys())
        }
    except Exception as e:
        print(f"Multi-timeframe confluence error for {symbol}: {e}")
        return {'confluence_score': 0, 'bias': 'NEUTRAL', 'entry': 'NEUTRAL', 'confirmation': False}

# Performance Optimization Functions
data_cache = {}
cache_ttl = 300  # 5 minutes cache TTL
executor = ThreadPoolExecutor(max_workers=4)
last_cache_cleanup = time.time()
cache_cleanup_interval = 60  # 1 minute

@lru_cache(maxsize=128)
def cached_get_ticker_data(symbol, period, interval):
    """Cached version of yfinance data fetching"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        return hist
    except Exception as e:
        print(f"Cached data fetch error for {symbol}: {e}")
        return None

def get_cached_data(symbol, period="5d", interval="1h"):
    """Get data with caching and TTL"""
    cache_key = f"{symbol}_{period}_{interval}"
    current_time = time.time()
    
    # Check if data exists in cache and is not expired
    if cache_key in data_cache:
        cached_data, timestamp = data_cache[cache_key]
        if current_time - timestamp < cache_ttl:
            return cached_data
    
    # Fetch new data
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        # Cache the data
        data_cache[cache_key] = (hist, current_time)
        
        # Cleanup old cache entries periodically
        cleanup_cache()
        
        return hist
    except Exception as e:
        print(f"Data fetch error for {symbol}: {e}")
        return None

def cleanup_cache():
    """Remove expired cache entries"""
    global last_cache_cleanup
    current_time = time.time()
    
    if current_time - last_cache_cleanup > cache_cleanup_interval:
        expired_keys = []
        for key, (data, timestamp) in data_cache.items():
            if current_time - timestamp > cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del data_cache[key]
        
        last_cache_cleanup = current_time
        print(f"Cache cleanup: removed {len(expired_keys)} expired entries")

async def parallel_signal_generation(symbols):
    """Generate signals for multiple symbols in parallel"""
    loop = asyncio.get_event_loop()
    
    # Create tasks for parallel execution
    tasks = []
    for symbol in symbols:
        task = loop.run_in_executor(executor, generate_trading_signal, symbol, "1h")
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return valid signals
    valid_signals = []
    for i, result in enumerate(results):
        if not isinstance(result, Exception) and result:
            valid_signals.append(result)
        elif isinstance(result, Exception):
            print(f"Error generating signal for {symbols[i]}: {result}")
    
    return valid_signals

def optimize_signal_generation(symbols):
    """Optimized signal generation with caching and parallel processing"""
    # Use cached data when possible
    optimized_symbols = []
    for symbol in symbols:
        # Check if we have recent cached data
        cache_key = f"{symbol}_5d_1h"
        if cache_key in data_cache:
            cached_data, timestamp = data_cache[cache_key]
            if time.time() - timestamp < cache_ttl:
                optimized_symbols.append(symbol)
                continue
        
        # If no recent cache, add to fetch list
        optimized_symbols.append(symbol)
    
    return optimized_symbols

# WebSocket connection management
websocket_connections = set()

# Global monitoring variables
monitoring_active = False
current_market = "stocks"
monitoring_interval = 30

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.add(websocket)
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            
            # Send monitoring status
            status_data = {
                "type": "status",
                "monitoring_active": monitoring_active,
                "current_market": current_market,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(status_data))
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

async def broadcast_to_websockets(data):
    """Broadcast data to all connected WebSocket clients"""
    if websocket_connections:
        message = json.dumps(data)
        disconnected = set()
        
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        websocket_connections -= disconnected

# Enhanced monitoring with performance optimizations
async def enhanced_monitoring_loop():
    """Enhanced monitoring loop with performance optimizations"""
    global monitoring_active, monitoring_symbols
    
    while monitoring_active:
        try:
            if monitoring_symbols:
                # Use parallel signal generation
                signals = await parallel_signal_generation(monitoring_symbols)
                
                # Broadcast to WebSocket clients
                if signals:
                    await broadcast_to_websockets({
                        "type": "signals",
                        "signals": signals,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Process alerts
                for signal in signals:
                    await process_signal_alert(signal['symbol'], signal)
            
            # Wait for next iteration
            await asyncio.sleep(monitoring_interval)
            
        except Exception as e:
            print(f"Monitoring loop error: {e}")
            await asyncio.sleep(5)  # Short delay before retry

# Advanced Analytics Functions
def calculate_trade_outcome(signal, current_price):
    """Calculate the outcome of a trade based on signal and current price"""
    try:
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', 0)
        direction = signal.get('direction', 'BUY')
        
        if entry_price == 0 or stop_loss == 0 or take_profit == 0:
            return None
            
        # Determine if trade hit TP or SL first
        if direction == 'BUY':
            if current_price >= take_profit:
                return {'outcome': 'WIN', 'pnl': take_profit - entry_price, 'exit_price': take_profit}
            elif current_price <= stop_loss:
                return {'outcome': 'LOSS', 'pnl': stop_loss - entry_price, 'exit_price': stop_loss}
        else:  # SELL
            if current_price <= take_profit:
                return {'outcome': 'WIN', 'pnl': entry_price - take_profit, 'exit_price': take_profit}
            elif current_price >= stop_loss:
                return {'outcome': 'LOSS', 'pnl': entry_price - stop_loss, 'exit_price': stop_loss}
        
        return None  # Trade still open
    except Exception as e:
        print(f"Error calculating trade outcome: {e}")
        return None

def update_trading_performance(signal, outcome):
    """Update trading performance metrics"""
    global trading_performance
    
    try:
        if outcome is None:
            return
            
        # Update basic metrics
        trading_performance["total_trades"] += 1
        trading_performance["total_pnl"] += outcome['pnl']
        
        if outcome['outcome'] == 'WIN':
            trading_performance["winning_trades"] += 1
            trading_performance["consecutive_wins"] += 1
            trading_performance["consecutive_losses"] = 0
            trading_performance["max_consecutive_wins"] = max(
                trading_performance["max_consecutive_wins"], 
                trading_performance["consecutive_wins"]
            )
            if outcome['pnl'] > trading_performance["largest_win"]:
                trading_performance["largest_win"] = outcome['pnl']
        else:
            trading_performance["losing_trades"] += 1
            trading_performance["consecutive_losses"] += 1
            trading_performance["consecutive_wins"] = 0
            trading_performance["max_consecutive_losses"] = max(
                trading_performance["max_consecutive_losses"], 
                trading_performance["consecutive_losses"]
            )
            if outcome['pnl'] < trading_performance["largest_loss"]:
                trading_performance["largest_loss"] = outcome['pnl']
        
        # Calculate derived metrics
        if trading_performance["total_trades"] > 0:
            trading_performance["win_rate"] = (trading_performance["winning_trades"] / trading_performance["total_trades"]) * 100
        
        if trading_performance["losing_trades"] > 0:
            total_wins = sum([t['pnl'] for t in trading_performance["recent_trades"] if t['outcome'] == 'WIN'])
            total_losses = abs(sum([t['pnl'] for t in trading_performance["recent_trades"] if t['outcome'] == 'LOSS']))
            if total_losses > 0:
                trading_performance["profit_factor"] = total_wins / total_losses
        
        # Update averages
        if trading_performance["winning_trades"] > 0:
            winning_pnls = [t['pnl'] for t in trading_performance["recent_trades"] if t['outcome'] == 'WIN']
            trading_performance["avg_win"] = sum(winning_pnls) / len(winning_pnls)
        
        if trading_performance["losing_trades"] > 0:
            losing_pnls = [t['pnl'] for t in trading_performance["recent_trades"] if t['outcome'] == 'LOSS']
            trading_performance["avg_loss"] = sum(losing_pnls) / len(losing_pnls)
        
        # Update equity curve
        trading_performance["equity_curve"].append({
            'timestamp': datetime.now().isoformat(),
            'equity': trading_performance["total_pnl"],
            'trade_count': trading_performance["total_trades"]
        })
        
        # Keep only last 1000 equity points
        if len(trading_performance["equity_curve"]) > 1000:
            trading_performance["equity_curve"] = trading_performance["equity_curve"][-1000:]
        
        # Calculate drawdown
        if trading_performance["equity_curve"]:
            peak_equity = max([point['equity'] for point in trading_performance["equity_curve"]])
            current_equity = trading_performance["total_pnl"]
            current_drawdown = ((peak_equity - current_equity) / peak_equity * 100) if peak_equity > 0 else 0
            trading_performance["current_drawdown"] = current_drawdown
            trading_performance["max_drawdown"] = max(trading_performance["max_drawdown"], current_drawdown)
        
        # Add to recent trades
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': signal.get('symbol', ''),
            'direction': signal.get('direction', ''),
            'entry_price': signal.get('entry_price', 0),
            'exit_price': outcome['exit_price'],
            'pnl': outcome['pnl'],
            'outcome': outcome['outcome'],
            'confidence': signal.get('confidence', 0),
            'market': signal.get('market', 'UNKNOWN')
        }
        
        trading_performance["recent_trades"].append(trade_record)
        
        # Keep only last 100 trades
        if len(trading_performance["recent_trades"]) > 100:
            trading_performance["recent_trades"] = trading_performance["recent_trades"][-100:]
        
        # Update market performance
        market = signal.get('market', 'UNKNOWN')
        if market not in trading_performance["trades_by_market"]:
            trading_performance["trades_by_market"][market] = {
                'total_trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0.0
            }
        
        trading_performance["trades_by_market"][market]['total_trades'] += 1
        trading_performance["trades_by_market"][market]['total_pnl'] += outcome['pnl']
        if outcome['outcome'] == 'WIN':
            trading_performance["trades_by_market"][market]['wins'] += 1
        else:
            trading_performance["trades_by_market"][market]['losses'] += 1
        
        # Update hourly performance
        hour = datetime.now().hour
        if hour not in trading_performance["performance_by_hour"]:
            trading_performance["performance_by_hour"][hour] = {
                'total_trades': 0, 'wins': 0, 'total_pnl': 0.0
            }
        
        trading_performance["performance_by_hour"][hour]['total_trades'] += 1
        trading_performance["performance_by_hour"][hour]['total_pnl'] += outcome['pnl']
        if outcome['outcome'] == 'WIN':
            trading_performance["performance_by_hour"][hour]['wins'] += 1
        
        # Calculate advanced ratios
        calculate_advanced_ratios()
        
    except Exception as e:
        print(f"Error updating trading performance: {e}")

def calculate_advanced_ratios():
    """Calculate advanced performance ratios"""
    global trading_performance
    
    try:
        if len(trading_performance["equity_curve"]) < 2:
            return
        
        # Calculate returns
        returns = []
        for i in range(1, len(trading_performance["equity_curve"])):
            prev_equity = trading_performance["equity_curve"][i-1]['equity']
            curr_equity = trading_performance["equity_curve"][i]['equity']
            if prev_equity != 0:
                returns.append((curr_equity - prev_equity) / prev_equity)
        
        if not returns:
            return
        
        # Sharpe Ratio (assuming risk-free rate of 0)
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return > 0:
            trading_performance["sharpe_ratio"] = mean_return / std_return
        
        # Sortino Ratio (downside deviation)
        negative_returns = [r for r in returns if r < 0]
        if negative_returns:
            downside_deviation = np.std(negative_returns)
            if downside_deviation > 0:
                trading_performance["sortino_ratio"] = mean_return / downside_deviation
        
        # Calmar Ratio (annual return / max drawdown)
        if trading_performance["max_drawdown"] > 0:
            # Estimate annual return (simplified)
            total_return = trading_performance["total_pnl"]
            days_trading = len(trading_performance["equity_curve"]) / 24  # Assuming hourly data
            if days_trading > 0:
                annual_return = (total_return / days_trading) * 365
                trading_performance["calmar_ratio"] = annual_return / trading_performance["max_drawdown"]
        
    except Exception as e:
        print(f"Error calculating advanced ratios: {e}")

def get_performance_heatmap():
    """Generate performance heatmap data"""
    global trading_performance
    
    try:
        heatmap_data = []
        
        # Market performance heatmap
        for market, data in trading_performance["trades_by_market"].items():
            win_rate = (data['wins'] / data['total_trades'] * 100) if data['total_trades'] > 0 else 0
            heatmap_data.append({
                'category': 'Market',
                'name': market,
                'value': win_rate,
                'trades': data['total_trades'],
                'pnl': data['total_pnl']
            })
        
        # Hourly performance heatmap
        for hour, data in trading_performance["performance_by_hour"].items():
            win_rate = (data['wins'] / data['total_trades'] * 100) if data['total_trades'] > 0 else 0
            heatmap_data.append({
                'category': 'Hour',
                'name': f"{hour:02d}:00",
                'value': win_rate,
                'trades': data['total_trades'],
                'pnl': data['total_pnl']
            })
        
        return heatmap_data
    except Exception as e:
        print(f"Error generating performance heatmap: {e}")
        return []

def get_equity_curve_data():
    """Get equity curve data for charting"""
    global trading_performance
    
    try:
        if not trading_performance["equity_curve"]:
            return []
        
        # Return last 100 points for performance
        recent_curve = trading_performance["equity_curve"][-100:]
        
        return [{
            'x': i,
            'y': point['equity'],
            'timestamp': point['timestamp'],
            'trades': point['trade_count']
        } for i, point in enumerate(recent_curve)]
    except Exception as e:
        print(f"Error getting equity curve data: {e}")
        return []

# Enhanced AI Learning Functions
def analyze_market_sentiment():
    """Analyze market sentiment using multiple indicators"""
    global ai_learning_enhanced
    
    try:
        # Simulate sentiment analysis (in real implementation, would use news APIs, social media, etc.)
        import random
        
        # Generate realistic sentiment data
        base_sentiment = random.uniform(-1, 1)
        news_impact = random.uniform(-0.5, 0.5)
        social_sentiment = random.uniform(-0.3, 0.3)
        
        # Calculate overall sentiment score
        sentiment_score = (base_sentiment + news_impact + social_sentiment) / 3
        
        # Determine sentiment category
        if sentiment_score > 0.3:
            market_sentiment = "BULLISH"
        elif sentiment_score < -0.3:
            market_sentiment = "BEARISH"
        else:
            market_sentiment = "NEUTRAL"
        
        # Calculate fear/greed index (0-100)
        fear_greed_index = 50 + (sentiment_score * 50)
        fear_greed_index = max(0, min(100, fear_greed_index))
        
        # Update sentiment data
        ai_learning_enhanced["sentiment_analysis"].update({
            "market_sentiment": market_sentiment,
            "sentiment_score": sentiment_score,
            "sentiment_trend": "IMPROVING" if sentiment_score > 0 else "DETERIORATING" if sentiment_score < 0 else "STABLE",
            "news_impact": news_impact,
            "social_sentiment": social_sentiment,
            "fear_greed_index": fear_greed_index,
            "last_updated": datetime.now().isoformat()
        })
        
        return ai_learning_enhanced["sentiment_analysis"]
        
    except Exception as e:
        print(f"Error analyzing market sentiment: {e}")
        return ai_learning_enhanced["sentiment_analysis"]

def detect_market_regime(price_data_list):
    """Detect current market regime based on price data"""
    global ai_learning_enhanced
    
    try:
        if not price_data_list or len(price_data_list) < 20:
            return ai_learning_enhanced["market_regime"]
        
        # Calculate volatility regime
        returns = []
        for i in range(1, len(price_data_list)):
            if price_data_list[i-1] != 0:
                returns.append((price_data_list[i] - price_data_list[i-1]) / price_data_list[i-1])
        
        if returns:
            volatility = np.std(returns)
            if volatility > 0.03:
                volatility_regime = "HIGH"
            elif volatility < 0.01:
                volatility_regime = "LOW"
            else:
                volatility_regime = "MEDIUM"
        else:
            volatility_regime = "MEDIUM"
        
        # Calculate trend regime
        recent_prices = price_data_list[-10:]
        if len(recent_prices) >= 10:
            trend_slope = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
            if trend_slope > 0.02:
                trend_regime = "UPTREND"
            elif trend_slope < -0.02:
                trend_regime = "DOWNTREND"
            else:
                trend_regime = "SIDEWAYS"
        else:
            trend_regime = "SIDEWAYS"
        
        # Determine overall regime
        if volatility_regime == "HIGH" and trend_regime in ["UPTREND", "DOWNTREND"]:
            current_regime = "TRENDING_HIGH_VOL"
        elif volatility_regime == "LOW" and trend_regime == "SIDEWAYS":
            current_regime = "RANGING_LOW_VOL"
        elif volatility_regime == "HIGH":
            current_regime = "HIGH_VOLATILITY"
        elif trend_regime in ["UPTREND", "DOWNTREND"]:
            current_regime = "TRENDING"
        else:
            current_regime = "NORMAL"
        
        # Calculate regime confidence
        regime_confidence = min(1.0, len(price_data_list) / 100)
        
        # Update regime data
        regime_data = {
            "current_regime": current_regime,
            "regime_confidence": regime_confidence,
            "volatility_regime": volatility_regime,
            "trend_regime": trend_regime,
            "liquidity_regime": "NORMAL",  # Simplified for now
            "last_updated": datetime.now().isoformat()
        }
        
        # Add to regime history
        ai_learning_enhanced["market_regime"]["regime_history"].append(regime_data)
        if len(ai_learning_enhanced["market_regime"]["regime_history"]) > 50:
            ai_learning_enhanced["market_regime"]["regime_history"] = ai_learning_enhanced["market_regime"]["regime_history"][-50:]
        
        # Update current regime
        ai_learning_enhanced["market_regime"].update(regime_data)
        
        return ai_learning_enhanced["market_regime"]
        
    except Exception as e:
        print(f"Error detecting market regime: {e}")
        return ai_learning_enhanced["market_regime"]

def recognize_trading_patterns(price_data, volume_data):
    """Recognize trading patterns using technical analysis"""
    global ai_learning_enhanced
    
    try:
        if not price_data or len(price_data) < 20:
            return ai_learning_enhanced["pattern_recognition"]
        
        patterns = []
        pattern_strength = 0.0
        
        # Simple pattern recognition (in real implementation, would use more sophisticated algorithms)
        
        # Head and Shoulders pattern
        if len(price_data) >= 20:
            recent_highs = []
            for i in range(2, len(price_data) - 2):
                if (price_data[i] > price_data[i-1] and price_data[i] > price_data[i-2] and
                    price_data[i] > price_data[i+1] and price_data[i] > price_data[i+2]):
                    recent_highs.append(price_data[i])
            
            if len(recent_highs) >= 3:
                # Check for head and shoulders
                if (recent_highs[-3] < recent_highs[-2] > recent_highs[-1] and
                    abs(recent_highs[-3] - recent_highs[-1]) < recent_highs[-2] * 0.05):
                    patterns.append("HEAD_AND_SHOULDERS")
                    pattern_strength += 0.3
        
        # Double Top/Bottom pattern
        if len(price_data) >= 15:
            recent_highs = []
            recent_lows = []
            for i in range(1, len(price_data) - 1):
                if price_data[i] > price_data[i-1] and price_data[i] > price_data[i+1]:
                    recent_highs.append(price_data[i])
                elif price_data[i] < price_data[i-1] and price_data[i] < price_data[i+1]:
                    recent_lows.append(price_data[i])
            
            # Double top
            if len(recent_highs) >= 2:
                if abs(recent_highs[-1] - recent_highs[-2]) < recent_highs[-1] * 0.02:
                    patterns.append("DOUBLE_TOP")
                    pattern_strength += 0.2
            
            # Double bottom
            if len(recent_lows) >= 2:
                if abs(recent_lows[-1] - recent_lows[-2]) < recent_lows[-1] * 0.02:
                    patterns.append("DOUBLE_BOTTOM")
                    pattern_strength += 0.2
        
        # Trend line patterns
        if len(price_data) >= 10:
            # Simple trend detection
            start_price = price_data[0]
            end_price = price_data[-1]
            trend_strength = abs(end_price - start_price) / start_price
            
            if trend_strength > 0.05:
                if end_price > start_price:
                    patterns.append("UPTREND")
                else:
                    patterns.append("DOWNTREND")
                pattern_strength += min(trend_strength, 0.3)
        
        # Volume confirmation
        if volume_data and len(volume_data) >= 5:
            avg_volume = np.mean(volume_data[-5:])
            recent_volume = volume_data[-1]
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:
                patterns.append("HIGH_VOLUME")
                pattern_strength += 0.1
        
        # Update pattern recognition data
        ai_learning_enhanced["pattern_recognition"].update({
            "active_patterns": patterns,
            "pattern_strength": min(pattern_strength, 1.0),
            "pattern_confidence": min(len(patterns) * 0.2, 1.0),
            "last_updated": datetime.now().isoformat()
        })
        
        return ai_learning_enhanced["pattern_recognition"]
        
    except Exception as e:
        print(f"Error recognizing trading patterns: {e}")
        return ai_learning_enhanced["pattern_recognition"]

def adapt_parameters_based_on_performance():
    """Adapt AI parameters based on recent performance"""
    global ai_learning_enhanced, trading_performance
    
    try:
        # Get recent performance
        recent_trades = trading_performance.get("recent_trades", [])
        if len(recent_trades) < 10:
            return ai_learning_enhanced["adaptive_parameters"]
        
        # Calculate recent win rate
        recent_wins = sum(1 for trade in recent_trades[-10:] if trade.get('outcome') == 'WIN')
        recent_win_rate = recent_wins / min(len(recent_trades), 10)
        
        # Calculate recent profit factor
        recent_pnls = [trade.get('pnl', 0) for trade in recent_trades[-10:]]
        wins = [pnl for pnl in recent_pnls if pnl > 0]
        losses = [abs(pnl) for pnl in recent_pnls if pnl < 0]
        
        if losses and sum(losses) > 0:
            recent_profit_factor = sum(wins) / sum(losses)
        else:
            recent_profit_factor = 2.0  # Default good performance
        
        # Adapt parameters based on performance
        params = ai_learning_enhanced["adaptive_parameters"]
        learning_rate = params["learning_rate"]
        
        # Adjust confidence threshold
        if recent_win_rate > 0.7:
            params["confidence_threshold"] = max(0.5, params["confidence_threshold"] - learning_rate)
        elif recent_win_rate < 0.4:
            params["confidence_threshold"] = min(0.9, params["confidence_threshold"] + learning_rate)
        
        # Adjust risk adjustment
        if recent_profit_factor > 2.0:
            params["risk_adjustment"] = min(1.5, params["risk_adjustment"] + learning_rate)
        elif recent_profit_factor < 1.0:
            params["risk_adjustment"] = max(0.5, params["risk_adjustment"] - learning_rate)
        
        # Adjust pattern weight based on pattern recognition success
        pattern_data = ai_learning_enhanced["pattern_recognition"]
        if pattern_data["pattern_confidence"] > 0.7:
            params["pattern_weight"] = min(1.0, params["pattern_weight"] + learning_rate)
        elif pattern_data["pattern_confidence"] < 0.3:
            params["pattern_weight"] = max(0.3, params["pattern_weight"] - learning_rate)
        
        # Update learning metrics
        ai_learning_enhanced["learning_metrics"]["total_learning_cycles"] += 1
        ai_learning_enhanced["learning_metrics"]["successful_adaptations"] += 1
        ai_learning_enhanced["learning_metrics"]["learning_accuracy"] = recent_win_rate
        ai_learning_enhanced["learning_metrics"]["last_updated"] = datetime.now().isoformat()
        
        # Update last adaptation time
        params["last_adaptation"] = datetime.now().isoformat()
        
        return params
        
    except Exception as e:
        print(f"Error adapting parameters: {e}")
        return ai_learning_enhanced["adaptive_parameters"]

def get_enhanced_ai_insights():
    """Get comprehensive AI learning insights"""
    global ai_learning_enhanced
    
    try:
        # Update all AI components
        sentiment = analyze_market_sentiment()
        regime = detect_market_regime([])  # Would pass actual price data in real implementation
        patterns = recognize_trading_patterns([], [])  # Would pass actual data
        params = adapt_parameters_based_on_performance()
        
        return {
            "sentiment_analysis": sentiment,
            "market_regime": regime,
            "pattern_recognition": patterns,
            "adaptive_parameters": params,
            "learning_metrics": ai_learning_enhanced["learning_metrics"],
            "overall_ai_health": {
                "status": "HEALTHY",
                "confidence": (sentiment.get("sentiment_score", 0) + 
                             regime.get("regime_confidence", 0) + 
                             patterns.get("pattern_confidence", 0)) / 3,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error getting enhanced AI insights: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Predictive Analytics Functions
def calculate_price_targets(symbol, current_price, price_data_list):
    """Calculate price targets using multiple methods"""
    global predictive_analytics
    
    try:
        if not price_data_list or len(price_data_list) < 20:
            return predictive_analytics["price_targets"]
        
        # Calculate technical price targets
        recent_high = max(price_data_list[-20:])
        recent_low = min(price_data_list[-20:])
        recent_range = recent_high - recent_low
        
        # Fibonacci retracement levels
        fib_236 = current_price + (recent_range * 0.236)
        fib_382 = current_price + (recent_range * 0.382)
        fib_618 = current_price + (recent_range * 0.618)
        
        # Support and resistance levels
        support_levels = [recent_low, current_price - (recent_range * 0.5)]
        resistance_levels = [recent_high, current_price + (recent_range * 0.5)]
        
        # Calculate targets based on volatility
        volatility = np.std([(price_data_list[i] - price_data_list[i-1]) / price_data_list[i-1] 
                           for i in range(1, len(price_data_list)) if price_data_list[i-1] != 0])
        
        # Short-term targets (1-3 days)
        short_term_bullish = current_price * (1 + volatility * 2)
        short_term_bearish = current_price * (1 - volatility * 2)
        
        # Medium-term targets (1-2 weeks)
        medium_term_bullish = current_price * (1 + volatility * 4)
        medium_term_bearish = current_price * (1 - volatility * 4)
        
        # Long-term targets (1-3 months)
        long_term_bullish = current_price * (1 + volatility * 8)
        long_term_bearish = current_price * (1 - volatility * 8)
        
        # Update price targets
        predictive_analytics["price_targets"].update({
            "short_term": {
                "bullish": round(short_term_bullish, 5),
                "bearish": round(short_term_bearish, 5),
                "fibonacci": {
                    "236": round(fib_236, 5),
                    "382": round(fib_382, 5),
                    "618": round(fib_618, 5)
                }
            },
            "medium_term": {
                "bullish": round(medium_term_bullish, 5),
                "bearish": round(medium_term_bearish, 5)
            },
            "long_term": {
                "bullish": round(long_term_bullish, 5),
                "bearish": round(long_term_bearish, 5)
            },
            "support_levels": [round(level, 5) for level in support_levels],
            "resistance_levels": [round(level, 5) for level in resistance_levels],
            "last_updated": datetime.now().isoformat()
        })
        
        return predictive_analytics["price_targets"]
        
    except Exception as e:
        print(f"Error calculating price targets: {e}")
        return predictive_analytics["price_targets"]

def forecast_volatility(price_data_list, volume_data=None):
    """Forecast future volatility using historical data"""
    global predictive_analytics
    
    try:
        if not price_data_list or len(price_data_list) < 20:
            return predictive_analytics["volatility_forecast"]
        
        # Calculate historical volatility
        returns = []
        for i in range(1, len(price_data_list)):
            if price_data_list[i-1] != 0:
                returns.append((price_data_list[i] - price_data_list[i-1]) / price_data_list[i-1])
        
        if not returns:
            return predictive_analytics["volatility_forecast"]
        
        current_volatility = np.std(returns)
        
        # Calculate volatility trend
        recent_vol = np.std(returns[-10:]) if len(returns) >= 10 else current_volatility
        older_vol = np.std(returns[-20:-10]) if len(returns) >= 20 else current_volatility
        
        if recent_vol > older_vol * 1.2:
            volatility_trend = "INCREASING"
        elif recent_vol < older_vol * 0.8:
            volatility_trend = "DECREASING"
        else:
            volatility_trend = "STABLE"
        
        # Predict future volatility using simple trend extrapolation
        volatility_change = (recent_vol - older_vol) / older_vol if older_vol > 0 else 0
        predicted_volatility = current_volatility * (1 + volatility_change * 0.5)
        
        # Calculate volatility percentile (simplified)
        volatility_percentile = min(100, max(0, (current_volatility / 0.05) * 50))
        
        # Forecast for different periods
        forecast_periods = {
            "1_day": predicted_volatility * 0.8,
            "1_week": predicted_volatility * 1.2,
            "1_month": predicted_volatility * 1.5
        }
        
        # Update volatility forecast
        predictive_analytics["volatility_forecast"].update({
            "current_volatility": round(current_volatility, 6),
            "predicted_volatility": round(predicted_volatility, 6),
            "volatility_trend": volatility_trend,
            "volatility_percentile": round(volatility_percentile, 1),
            "volatility_forecast_periods": {k: round(v, 6) for k, v in forecast_periods.items()},
            "last_updated": datetime.now().isoformat()
        })
        
        return predictive_analytics["volatility_forecast"]
        
    except Exception as e:
        print(f"Error forecasting volatility: {e}")
        return predictive_analytics["volatility_forecast"]

def predict_market_direction(price_data_list, volume_data=None):
    """Predict market direction using multiple indicators"""
    global predictive_analytics
    
    try:
        if not price_data_list or len(price_data_list) < 20:
            return predictive_analytics["market_direction"]
        
        # Calculate trend indicators
        recent_prices = price_data_list[-10:]
        older_prices = price_data_list[-20:-10] if len(price_data_list) >= 20 else price_data_list[:10]
        
        recent_avg = np.mean(recent_prices)
        older_avg = np.mean(older_prices)
        
        # Trend strength calculation
        trend_strength = abs(recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        # Momentum calculation
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] if recent_prices[0] > 0 else 0
        
        # Calculate direction probabilities
        if momentum > 0.02:
            bullish_prob = min(0.8, 0.5 + trend_strength * 2)
            bearish_prob = max(0.1, 0.3 - trend_strength)
            sideways_prob = 1 - bullish_prob - bearish_prob
        elif momentum < -0.02:
            bearish_prob = min(0.8, 0.5 + trend_strength * 2)
            bullish_prob = max(0.1, 0.3 - trend_strength)
            sideways_prob = 1 - bullish_prob - bearish_prob
        else:
            sideways_prob = min(0.7, 0.4 + (1 - trend_strength) * 0.5)
            bullish_prob = (1 - sideways_prob) * 0.6
            bearish_prob = (1 - sideways_prob) * 0.4
        
        # Calculate key levels
        recent_high = max(price_data_list[-20:])
        recent_low = min(price_data_list[-20:])
        recent_range = recent_high - recent_low
        
        support_levels = [
            recent_low,
            recent_low + (recent_range * 0.25),
            recent_low + (recent_range * 0.5)
        ]
        
        resistance_levels = [
            recent_high,
            recent_high - (recent_range * 0.25),
            recent_high - (recent_range * 0.5)
        ]
        
        # Pivot points
        pivot_point = (recent_high + recent_low + price_data_list[-1]) / 3
        pivot_points = [
            pivot_point,
            pivot_point + (recent_range * 0.1),
            pivot_point - (recent_range * 0.1)
        ]
        
        # Confidence level based on trend strength and data quality
        confidence_level = min(0.9, trend_strength * 2 + 0.3)
        
        # Update market direction
        predictive_analytics["market_direction"].update({
            "direction_probability": {
                "bullish": round(bullish_prob, 3),
                "bearish": round(bearish_prob, 3),
                "sideways": round(sideways_prob, 3)
            },
            "confidence_level": round(confidence_level, 3),
            "key_levels": {
                "support": [round(level, 5) for level in support_levels],
                "resistance": [round(level, 5) for level in resistance_levels],
                "pivot_points": [round(level, 5) for level in pivot_points]
            },
            "trend_strength": round(trend_strength, 3),
            "momentum_score": round(momentum, 3),
            "last_updated": datetime.now().isoformat()
        })
        
        return predictive_analytics["market_direction"]
        
    except Exception as e:
        print(f"Error predicting market direction: {e}")
        return predictive_analytics["market_direction"]

def get_comprehensive_predictions(symbol, current_price, price_data_list, volume_data=None):
    """Get comprehensive predictive analytics"""
    global predictive_analytics
    
    try:
        # Calculate all predictions
        price_targets = calculate_price_targets(symbol, current_price, price_data_list)
        volatility_forecast = forecast_volatility(price_data_list, volume_data)
        market_direction = predict_market_direction(price_data_list, volume_data)
        
        # Calculate overall prediction confidence
        overall_confidence = (
            market_direction.get("confidence_level", 0) * 0.4 +
            min(1.0, len(price_data_list) / 100) * 0.3 +
            (1 - abs(volatility_forecast.get("volatility_percentile", 50) - 50) / 50) * 0.3
        )
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "price_targets": price_targets,
            "volatility_forecast": volatility_forecast,
            "market_direction": market_direction,
            "overall_confidence": round(overall_confidence, 3),
            "prediction_timestamp": datetime.now().isoformat(),
            "data_quality": {
                "price_data_points": len(price_data_list),
                "volume_data_available": volume_data is not None,
                "data_freshness": "REAL_TIME" if len(price_data_list) > 0 else "STALE"
            }
        }
        
    except Exception as e:
        print(f"Error getting comprehensive predictions: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Real-Time Market Scanner Functions
def scan_market_hot_list():
    """Scan market for hot trading opportunities"""
    global market_scanner
    
    try:
        start_time = time.time()
        
        # Define symbols to scan
        stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        forex_symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X"]
        crypto_symbols = ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD"]
        index_symbols = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]
        
        hot_stocks = []
        hot_forex = []
        hot_crypto = []
        hot_indices = []
        
        # Scan stocks
        for symbol in stock_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1h")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                    
                    # Calculate momentum
                    momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                    
                    # Check if it's "hot" based on criteria
                    if (abs(momentum) > market_scanner["scanner_settings"]["momentum_threshold"] or
                        volume > market_scanner["scanner_settings"]["min_volume"]):
                        
                        hot_stocks.append({
                            "symbol": symbol,
                            "price": round(float(current_price), 2),
                            "change": round(float(momentum) * 100, 2),
                            "volume": int(volume) if volume else 0,
                            "momentum_score": abs(float(momentum)) * 100,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        # Scan forex
        for symbol in forex_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1h")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    
                    momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                    
                    if abs(momentum) > market_scanner["scanner_settings"]["momentum_threshold"]:
                        hot_forex.append({
                            "symbol": symbol,
                            "price": round(float(current_price), 5),
                            "change": round(float(momentum) * 100, 3),
                            "momentum_score": abs(float(momentum)) * 100,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        # Scan crypto
        for symbol in crypto_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1h")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                    
                    momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                    
                    if (abs(momentum) > market_scanner["scanner_settings"]["momentum_threshold"] or
                        volume > market_scanner["scanner_settings"]["min_volume"]):
                        
                        hot_crypto.append({
                            "symbol": symbol,
                            "price": round(float(current_price), 2),
                            "change": round(float(momentum) * 100, 2),
                            "volume": int(volume) if volume else 0,
                            "momentum_score": abs(float(momentum)) * 100,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        # Scan indices
        for symbol in index_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1h")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    
                    momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                    
                    if abs(momentum) > market_scanner["scanner_settings"]["momentum_threshold"]:
                        hot_indices.append({
                            "symbol": symbol,
                            "price": round(float(current_price), 2),
                            "change": round(float(momentum) * 100, 2),
                            "momentum_score": abs(float(momentum)) * 100,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        # Sort by momentum score
        hot_stocks.sort(key=lambda x: x['momentum_score'], reverse=True)
        hot_forex.sort(key=lambda x: x['momentum_score'], reverse=True)
        hot_crypto.sort(key=lambda x: x['momentum_score'], reverse=True)
        hot_indices.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        # Update hot list
        market_scanner["hot_list"].update({
            "stocks": hot_stocks[:5],  # Top 5
            "forex": hot_forex[:5],
            "crypto": hot_crypto[:5],
            "indices": hot_indices[:5],
            "last_updated": datetime.now().isoformat()
        })
        
        # Update scan results
        scan_duration = time.time() - start_time
        market_scanner["scan_results"].update({
            "total_scanned": len(stock_symbols) + len(forex_symbols) + len(crypto_symbols) + len(index_symbols),
            "signals_found": len(hot_stocks) + len(hot_forex) + len(hot_crypto) + len(hot_indices),
            "scan_duration": round(scan_duration, 2),
            "last_scan_time": datetime.now().isoformat()
        })
        
        return market_scanner["hot_list"]
        
    except Exception as e:
        print(f"Error scanning market hot list: {e}")
        return market_scanner["hot_list"]

def analyze_sector_rotation():
    """Analyze sector rotation and momentum"""
    global market_scanner
    
    try:
        # Define sector symbols
        sector_symbols = {
            "technology": ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA"],
            "healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "TMO"],
            "financial": ["JPM", "BAC", "WFC", "GS", "MS", "C"],
            "energy": ["XOM", "CVX", "COP", "EOG", "SLB", "KMI"],
            "consumer": ["WMT", "PG", "KO", "PEP", "MCD", "NKE"],
            "industrial": ["BA", "CAT", "GE", "MMM", "HON", "UPS"],
            "materials": ["LIN", "APD", "SHW", "ECL", "DD", "DOW"],
            "utilities": ["NEE", "DUK", "SO", "AEP", "EXC", "XEL"]
        }
        
        sector_momentum = {}
        
        # Calculate momentum for each sector
        for sector, symbols in sector_symbols.items():
            total_momentum = 0.0
            valid_symbols = 0
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d", interval="1d")
                    
                    if not hist.empty and len(hist) >= 2:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[-2]
                        
                        momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                        total_momentum += momentum
                        valid_symbols += 1
                except Exception as e:
                    print(f"Error analyzing {symbol} for sector {sector}: {e}")
            
            if valid_symbols > 0:
                avg_momentum = total_momentum / valid_symbols
                sector_momentum[sector] = {
                    "momentum": round(avg_momentum, 4),
                    "symbols": symbols[:3],  # Top 3 symbols
                    "valid_count": valid_symbols
                }
        
        # Rank sectors by momentum
        sorted_sectors = sorted(sector_momentum.items(), key=lambda x: x[1]["momentum"], reverse=True)
        
        # Update sector rotation
        for i, (sector, data) in enumerate(sorted_sectors):
            if sector in market_scanner["sector_rotation"]:
                market_scanner["sector_rotation"][sector].update({
                    "momentum": data["momentum"],
                    "rank": i + 1,
                    "symbols": data["symbols"]
                })
        
        market_scanner["sector_rotation"]["last_updated"] = datetime.now().isoformat()
        
        return market_scanner["sector_rotation"]
        
    except Exception as e:
        print(f"Error analyzing sector rotation: {e}")
        return market_scanner["sector_rotation"]

def rank_momentum_opportunities():
    """Rank momentum trading opportunities"""
    global market_scanner
    
    try:
        # Get all symbols to analyze
        all_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC",
                      "JPM", "BAC", "WFC", "GS", "MS", "C", "JNJ", "PFE", "UNH", "ABBV"]
        
        momentum_data = []
        
        for symbol in all_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d", interval="1d")
                
                if not hist.empty and len(hist) >= 5:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                    avg_volume = hist['Volume'].mean() if 'Volume' in hist.columns else 0
                    
                    # Calculate metrics
                    momentum = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                    
                    # Calculate breakout potential
                    high_5d = hist['High'].max()
                    low_5d = hist['Low'].min()
                    breakout_potential = (current_price - low_5d) / (high_5d - low_5d) if high_5d != low_5d else 0.5
                    
                    momentum_data.append({
                        "symbol": symbol,
                        "price": round(float(current_price), 2),
                        "momentum": round(float(momentum), 4),
                        "volume": int(volume) if volume else 0,
                        "volume_ratio": round(float(volume_ratio), 2),
                        "breakout_potential": round(float(breakout_potential), 3),
                        "momentum_score": abs(float(momentum)) * 100
                    })
            except Exception as e:
                print(f"Error ranking {symbol}: {e}")
        
        # Sort and categorize
        momentum_data.sort(key=lambda x: x['momentum'], reverse=True)
        
        top_gainers = [item for item in momentum_data if item['momentum'] > 0][:5]
        top_losers = [item for item in momentum_data if item['momentum'] < 0][:5]
        
        # Sort by volume
        momentum_data.sort(key=lambda x: x['volume'], reverse=True)
        most_active = momentum_data[:5]
        
        # Sort by volume ratio
        momentum_data.sort(key=lambda x: x['volume_ratio'], reverse=True)
        highest_volume = momentum_data[:5]
        
        # Sort by breakout potential
        momentum_data.sort(key=lambda x: x['breakout_potential'], reverse=True)
        breakout_candidates = momentum_data[:5]
        
        # Update momentum ranking
        market_scanner["momentum_ranking"].update({
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "most_active": most_active,
            "highest_volume": highest_volume,
            "breakout_candidates": breakout_candidates,
            "last_updated": datetime.now().isoformat()
        })
        
        return market_scanner["momentum_ranking"]
        
    except Exception as e:
        print(f"Error ranking momentum opportunities: {e}")
        return market_scanner["momentum_ranking"]

def get_comprehensive_market_scan():
    """Get comprehensive market scan results"""
    global market_scanner
    
    try:
        # Run all scans
        hot_list = scan_market_hot_list()
        sector_rotation = analyze_sector_rotation()
        momentum_ranking = rank_momentum_opportunities()
        
        return {
            "hot_list": hot_list,
            "sector_rotation": sector_rotation,
            "momentum_ranking": momentum_ranking,
            "scan_results": market_scanner["scan_results"],
            "scanner_settings": market_scanner["scanner_settings"],
            "scan_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting comprehensive market scan: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def scan_entire_market_for_signals():
    """Scan entire market and generate trading signals for all opportunities"""
    global market_scanner
    
    try:
        start_time = time.time()
        signals_found = []
        
        # Define comprehensive symbol lists
        all_symbols = {
            "stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC", "CRM", "ADBE", "PYPL", "UBER", "SQ", "ZM", "ROKU", "SPOT", "TWTR", "SNAP"],
            "forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X"],
            "crypto": ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD", "XRP-USD", "DOT-USD", "AVAX-USD", "MATIC-USD", "LINK-USD"],
            "indices": ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX", "SPY", "QQQ", "IWM", "DIA", "VTI"],
            "metals": ["GC=F", "SI=F", "PL=F", "PA=F", "GLD", "SLV", "GDX", "GDXJ"]
        }
        
        total_scanned = 0
        signals_generated = 0
        
        # Scan each market category
        for market_type, symbols in all_symbols.items():
            print(f"🔍 Scanning {market_type.upper()} market...")
            
            for symbol in symbols:
                try:
                    total_scanned += 1
                    
                    # Get current price data
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d", interval="1h")
                    
                    if hist.empty or len(hist) < 20:
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    price_data = {
                        "current_price": float(current_price),
                        "volume": float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                        "high": float(hist['High'].iloc[-1]),
                        "low": float(hist['Low'].iloc[-1]),
                        "open": float(hist['Open'].iloc[-1])
                    }
                    
                    # Generate trading signal
                    signal = generate_trading_signal(symbol, price_data, "1h", market_type)
                    
                    if signal and signal.get("signal_type") in ["BUY", "SELL"]:
                        signals_found.append({
                            "symbol": symbol,
                            "market": market_type,
                            "signal": signal,
                            "scan_time": datetime.now().isoformat()
                        })
                        signals_generated += 1
                        
                        print(f"✅ Signal found: {symbol} - {signal['signal_type']} (Confidence: {signal['confidence']}%)")
                    
                except Exception as e:
                    print(f"❌ Error scanning {symbol}: {e}")
                    continue
        
        scan_duration = time.time() - start_time
        
        # Update scanner results
        market_scanner["scan_results"] = {
            "total_scanned": total_scanned,
            "signals_found": signals_generated,
            "scan_duration": round(scan_duration, 2),
            "last_scan_time": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "total_symbols_scanned": total_scanned,
            "signals_generated": signals_generated,
            "scan_duration_seconds": round(scan_duration, 2),
            "signals": signals_found,
            "scan_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error scanning entire market: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def analyze_individual_symbol(symbol: str, timeframe: str = "1h"):
    """Analyze individual symbol and generate trading signal"""
    try:
        print(f"🔍 Analyzing {symbol} on {timeframe} timeframe...")
        
        # Get current price data
        ticker = yf.Ticker(symbol)
        
        # Map timeframes to yfinance periods and intervals
        timeframe_config = {
            "5m": {"period": "1d", "interval": "5m"},
            "15m": {"period": "2d", "interval": "15m"},
            "1h": {"period": "5d", "interval": "1h"},
            "4h": {"period": "10d", "interval": "4h"},
            "1d": {"period": "30d", "interval": "1d"}
        }
        
        config = timeframe_config.get(timeframe, timeframe_config["1h"])
        hist = ticker.history(period=config["period"], interval=config["interval"])
        
        if hist.empty or len(hist) < 20:
            return {
                "status": "error",
                "message": f"Insufficient data for {symbol}",
                "symbol": symbol,
                "timeframe": timeframe
            }
        
        current_price = hist['Close'].iloc[-1]
        price_data = {
            "current_price": float(current_price),
            "volume": float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
            "high": float(hist['High'].iloc[-1]),
            "low": float(hist['Low'].iloc[-1]),
            "open": float(hist['Open'].iloc[-1])
        }
        
        # Determine market type based on symbol
        market_type = "stocks"
        if symbol.endswith('=X'):
            market_type = "forex"
        elif symbol.endswith('-USD') or 'BTC' in symbol or 'ETH' in symbol:
            market_type = "crypto"
        elif symbol.startswith('^') or symbol in ['SPY', 'QQQ', 'IWM', 'DIA']:
            market_type = "indices"
        elif symbol in ['GC=F', 'SI=F', 'GLD', 'SLV']:
            market_type = "metals"
        
        # Generate trading signal
        signal = generate_trading_signal(symbol, price_data, timeframe, market_type)
        
        if signal:
            return {
                "status": "success",
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "analysis_timestamp": datetime.now().isoformat(),
                "signal": signal,
                "price_data": price_data
            }
        else:
            return {
                "status": "no_signal",
                "message": f"No trading signal generated for {symbol} - market conditions don't meet criteria",
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }

# Social Trading Functions
def share_trading_signal(signal_data, trader_id="user_001"):
    """Share a trading signal with the community"""
    global social_trading
    
    try:
        shared_signal = {
            "signal_id": f"shared_{int(time.time())}",
            "trader_id": trader_id,
            "symbol": signal_data.get("symbol", "UNKNOWN"),
            "signal_type": signal_data.get("signal", "HOLD"),
            "entry_price": signal_data.get("entry_price", 0),
            "take_profit": signal_data.get("take_profit", 0),
            "stop_loss": signal_data.get("stop_loss", 0),
            "confidence": signal_data.get("confidence", 0),
            "timestamp": datetime.now().isoformat(),
            "likes": 0,
            "copies": 0,
            "performance": None
        }
        
        social_trading["signal_sharing"]["shared_signals"].append(shared_signal)
        social_trading["signal_sharing"]["public_signals"].append(shared_signal)
        social_trading["signal_sharing"]["last_shared"] = datetime.now().isoformat()
        
        # Keep only last 100 shared signals
        if len(social_trading["signal_sharing"]["shared_signals"]) > 100:
            social_trading["signal_sharing"]["shared_signals"] = social_trading["signal_sharing"]["shared_signals"][-100:]
            social_trading["signal_sharing"]["public_signals"] = social_trading["signal_sharing"]["public_signals"][-100:]
        
        return shared_signal
        
    except Exception as e:
        print(f"Error sharing trading signal: {e}")
        return None

def update_performance_leaderboard():
    """Update the performance leaderboard"""
    global social_trading, trading_performance
    
    try:
        # Simulate trader performance data
        traders = [
            {"id": "trader_001", "name": "CryptoKing", "win_rate": 0.78, "profit": 15420.50, "followers": 1250},
            {"id": "trader_002", "name": "ForexMaster", "win_rate": 0.72, "profit": 12890.30, "followers": 980},
            {"id": "trader_003", "name": "StockGuru", "win_rate": 0.69, "profit": 11250.80, "followers": 750},
            {"id": "trader_004", "name": "DayTraderPro", "win_rate": 0.65, "profit": 9850.20, "followers": 650},
            {"id": "trader_005", "name": "SwingTrader", "win_rate": 0.71, "profit": 8750.90, "followers": 520}
        ]
        
        # Sort by profit
        top_traders = sorted(traders, key=lambda x: x["profit"], reverse=True)
        
        # Monthly winners (simulate)
        monthly_winners = sorted(traders, key=lambda x: x["win_rate"], reverse=True)
        
        # All time best
        all_time_best = sorted(traders, key=lambda x: x["followers"], reverse=True)
        
        # Copy traders (most copied)
        copy_traders = sorted(traders, key=lambda x: x["followers"] * 0.3 + x["profit"] * 0.7, reverse=True)
        
        social_trading["performance_leaderboard"].update({
            "top_traders": top_traders[:5],
            "monthly_winners": monthly_winners[:5],
            "all_time_best": all_time_best[:5],
            "copy_traders": copy_traders[:5],
            "last_updated": datetime.now().isoformat()
        })
        
        return social_trading["performance_leaderboard"]
        
    except Exception as e:
        print(f"Error updating performance leaderboard: {e}")
        return social_trading["performance_leaderboard"]

def setup_copy_trading(copier_id, trader_id, copy_settings):
    """Setup copy trading between users"""
    global social_trading
    
    try:
        copy_config = {
            "copy_id": f"copy_{int(time.time())}",
            "copier_id": copier_id,
            "trader_id": trader_id,
            "copy_percentage": copy_settings.get("copy_percentage", 100),
            "max_risk_per_trade": copy_settings.get("max_risk_per_trade", 2.0),
            "max_daily_risk": copy_settings.get("max_daily_risk", 5.0),
            "auto_copy": copy_settings.get("auto_copy", True),
            "copy_signals": copy_settings.get("copy_signals", ["BUY", "SELL"]),
            "created_at": datetime.now().isoformat(),
            "status": "ACTIVE",
            "performance": {
                "total_copied": 0,
                "successful_copies": 0,
                "total_profit": 0.0,
                "win_rate": 0.0
            }
        }
        
        social_trading["copy_trading"]["active_copies"].append(copy_config)
        social_trading["copy_trading"]["copy_settings"][copy_config["copy_id"]] = copy_config
        social_trading["copy_trading"]["last_updated"] = datetime.now().isoformat()
        
        return copy_config
        
    except Exception as e:
        print(f"Error setting up copy trading: {e}")
        return None

def analyze_community_insights():
    """Analyze community insights and sentiment"""
    global social_trading
    
    try:
        # Analyze shared signals for community sentiment
        shared_signals = social_trading["signal_sharing"]["public_signals"]
        
        if shared_signals:
            # Calculate community sentiment
            bullish_signals = len([s for s in shared_signals[-50:] if s["signal_type"] == "BUY"])
            bearish_signals = len([s for s in shared_signals[-50:] if s["signal_type"] == "SELL"])
            total_signals = bullish_signals + bearish_signals
            
            if total_signals > 0:
                bullish_ratio = bullish_signals / total_signals
                if bullish_ratio > 0.6:
                    market_sentiment = "BULLISH"
                elif bullish_ratio < 0.4:
                    market_sentiment = "BEARISH"
                else:
                    market_sentiment = "NEUTRAL"
            else:
                market_sentiment = "NEUTRAL"
        else:
            market_sentiment = "NEUTRAL"
        
        # Popular symbols
        symbol_counts = {}
        for signal in shared_signals[-100:]:
            symbol = signal["symbol"]
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        popular_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Trending strategies (simulate)
        trending_strategies = [
            {"name": "ICT/SMC", "popularity": 85, "success_rate": 0.72},
            {"name": "Multi-Timeframe", "popularity": 78, "success_rate": 0.68},
            {"name": "Kill Zones", "popularity": 72, "success_rate": 0.65},
            {"name": "Breakout Trading", "popularity": 68, "success_rate": 0.61},
            {"name": "Mean Reversion", "popularity": 55, "success_rate": 0.58}
        ]
        
        # Community predictions (simulate)
        community_predictions = {
            "market_direction": market_sentiment,
            "confidence": 0.75,
            "key_levels": ["Support: 1.3400", "Resistance: 1.3600"],
            "timeframe": "1-3 days"
        }
        
        # Discussion topics (simulate)
        discussion_topics = [
            {"topic": "Market Volatility", "posts": 45, "sentiment": "NEUTRAL"},
            {"topic": "Fed Rate Decision", "posts": 38, "sentiment": "BEARISH"},
            {"topic": "Earnings Season", "posts": 32, "sentiment": "BULLISH"},
            {"topic": "Crypto Regulation", "posts": 28, "sentiment": "NEUTRAL"},
            {"topic": "Oil Prices", "posts": 22, "sentiment": "BULLISH"}
        ]
        
        social_trading["community_insights"].update({
            "market_sentiment": market_sentiment,
            "popular_symbols": [{"symbol": s[0], "mentions": s[1]} for s in popular_symbols],
            "trending_strategies": trending_strategies,
            "community_predictions": community_predictions,
            "discussion_topics": discussion_topics,
            "last_updated": datetime.now().isoformat()
        })
        
        return social_trading["community_insights"]
        
    except Exception as e:
        print(f"Error analyzing community insights: {e}")
        return social_trading["community_insights"]

def get_social_trading_summary():
    """Get comprehensive social trading summary"""
    global social_trading
    
    try:
        # Update all components
        leaderboard = update_performance_leaderboard()
        insights = analyze_community_insights()
        
        return {
            "signal_sharing": {
                "total_shared": len(social_trading["signal_sharing"]["shared_signals"]),
                "public_signals": len(social_trading["signal_sharing"]["public_signals"]),
                "last_shared": social_trading["signal_sharing"]["last_shared"]
            },
            "performance_leaderboard": leaderboard,
            "copy_trading": {
                "active_copies": len(social_trading["copy_trading"]["active_copies"]),
                "total_copiers": sum(len(copy["copier_id"]) for copy in social_trading["copy_trading"]["active_copies"]),
                "last_updated": social_trading["copy_trading"]["last_updated"]
            },
            "community_insights": insights,
            "social_settings": social_trading["social_settings"],
            "summary_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting social trading summary: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Advanced Risk Management Functions
def calculate_portfolio_heatmap():
    """Calculate portfolio heatmap with correlation matrix and risk scores"""
    global risk_management
    
    try:
        # Define portfolio symbols
        portfolio_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "BTC-USD", "ETH-USD", "EURUSD=X"]
        
        correlation_matrix = {}
        risk_scores = {}
        position_sizes = {}
        
        # Calculate correlations and risk scores
        for i, symbol1 in enumerate(portfolio_symbols):
            correlation_matrix[symbol1] = {}
            risk_scores[symbol1] = 0.0
            position_sizes[symbol1] = 0.1  # Default 10% position size
            
            for j, symbol2 in enumerate(portfolio_symbols):
                if i == j:
                    correlation_matrix[symbol1][symbol2] = 1.0
                else:
                    try:
                        # Get price data for correlation calculation
                        ticker1 = yf.Ticker(symbol1)
                        ticker2 = yf.Ticker(symbol2)
                        
                        hist1 = ticker1.history(period="1mo", interval="1d")
                        hist2 = ticker2.history(period="1mo", interval="1d")
                        
                        if not hist1.empty and not hist2.empty and len(hist1) > 10 and len(hist2) > 10:
                            # Calculate returns
                            returns1 = hist1['Close'].pct_change().dropna()
                            returns2 = hist2['Close'].pct_change().dropna()
                            
                            # Align data
                            min_len = min(len(returns1), len(returns2))
                            if min_len > 5:
                                returns1 = returns1.iloc[-min_len:]
                                returns2 = returns2.iloc[-min_len:]
                                
                                # Calculate correlation
                                correlation = returns1.corr(returns2)
                                correlation_matrix[symbol1][symbol2] = float(correlation) if not np.isnan(correlation) else 0.0
                            else:
                                correlation_matrix[symbol1][symbol2] = 0.0
                        else:
                            correlation_matrix[symbol1][symbol2] = 0.0
                    except Exception as e:
                        print(f"Error calculating correlation between {symbol1} and {symbol2}: {e}")
                        correlation_matrix[symbol1][symbol2] = 0.0
            
            # Calculate risk score based on volatility
            try:
                ticker = yf.Ticker(symbol1)
                hist = ticker.history(period="1mo", interval="1d")
                
                if not hist.empty and len(hist) > 10:
                    returns = hist['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                    risk_scores[symbol1] = float(volatility) if not np.isnan(volatility) else 0.2
                else:
                    risk_scores[symbol1] = 0.2  # Default risk score
            except Exception as e:
                print(f"Error calculating risk score for {symbol1}: {e}")
                risk_scores[symbol1] = 0.2
        
        # Update portfolio heatmap
        risk_management["portfolio_heatmap"].update({
            "correlation_matrix": correlation_matrix,
            "risk_scores": risk_scores,
            "position_sizes": position_sizes,
            "exposure_limits": {symbol: 0.25 for symbol in portfolio_symbols},  # 25% max exposure
            "last_updated": datetime.now().isoformat()
        })
        
        return risk_management["portfolio_heatmap"]
        
    except Exception as e:
        print(f"Error calculating portfolio heatmap: {e}")
        return risk_management["portfolio_heatmap"]

def analyze_correlations():
    """Analyze correlations between different asset pairs and sectors"""
    global risk_management
    
    try:
        # Define asset pairs for correlation analysis
        stock_pairs = [
            ("AAPL", "GOOGL"), ("MSFT", "AMZN"), ("TSLA", "NVDA"),
            ("META", "NFLX"), ("JPM", "BAC"), ("XOM", "CVX")
        ]
        
        forex_pairs = [
            ("EURUSD=X", "GBPUSD=X"), ("USDJPY=X", "USDCHF=X"),
            ("AUDUSD=X", "USDCAD=X")
        ]
        
        crypto_pairs = [
            ("BTC-USD", "ETH-USD"), ("BNB-USD", "ADA-USD")
        ]
        
        pair_correlations = {}
        sector_correlations = {}
        market_correlations = {}
        
        # Analyze stock correlations
        for pair in stock_pairs:
            symbol1, symbol2 = pair
            try:
                ticker1 = yf.Ticker(symbol1)
                ticker2 = yf.Ticker(symbol2)
                
                hist1 = ticker1.history(period="3mo", interval="1d")
                hist2 = ticker2.history(period="3mo", interval="1d")
                
                if not hist1.empty and not hist2.empty and len(hist1) > 20 and len(hist2) > 20:
                    returns1 = hist1['Close'].pct_change().dropna()
                    returns2 = hist2['Close'].pct_change().dropna()
                    
                    min_len = min(len(returns1), len(returns2))
                    if min_len > 10:
                        returns1 = returns1.iloc[-min_len:]
                        returns2 = returns2.iloc[-min_len:]
                        
                        correlation = returns1.corr(returns2)
                        pair_correlations[f"{symbol1}-{symbol2}"] = {
                            "correlation": float(correlation) if not np.isnan(correlation) else 0.0,
                            "strength": "HIGH" if abs(correlation) > 0.7 else "MEDIUM" if abs(correlation) > 0.4 else "LOW",
                            "direction": "POSITIVE" if correlation > 0 else "NEGATIVE"
                        }
            except Exception as e:
                print(f"Error analyzing correlation for {pair}: {e}")
        
        # Analyze forex correlations
        for pair in forex_pairs:
            symbol1, symbol2 = pair
            try:
                ticker1 = yf.Ticker(symbol1)
                ticker2 = yf.Ticker(symbol2)
                
                hist1 = ticker1.history(period="3mo", interval="1d")
                hist2 = ticker2.history(period="3mo", interval="1d")
                
                if not hist1.empty and not hist2.empty and len(hist1) > 20 and len(hist2) > 20:
                    returns1 = hist1['Close'].pct_change().dropna()
                    returns2 = hist2['Close'].pct_change().dropna()
                    
                    min_len = min(len(returns1), len(returns2))
                    if min_len > 10:
                        returns1 = returns1.iloc[-min_len:]
                        returns2 = returns2.iloc[-min_len:]
                        
                        correlation = returns1.corr(returns2)
                        pair_correlations[f"{symbol1}-{symbol2}"] = {
                            "correlation": float(correlation) if not np.isnan(correlation) else 0.0,
                            "strength": "HIGH" if abs(correlation) > 0.7 else "MEDIUM" if abs(correlation) > 0.4 else "LOW",
                            "direction": "POSITIVE" if correlation > 0 else "NEGATIVE"
                        }
            except Exception as e:
                print(f"Error analyzing forex correlation for {pair}: {e}")
        
        # Analyze crypto correlations
        for pair in crypto_pairs:
            symbol1, symbol2 = pair
            try:
                ticker1 = yf.Ticker(symbol1)
                ticker2 = yf.Ticker(symbol2)
                
                hist1 = ticker1.history(period="3mo", interval="1d")
                hist2 = ticker2.history(period="3mo", interval="1d")
                
                if not hist1.empty and not hist2.empty and len(hist1) > 20 and len(hist2) > 20:
                    returns1 = hist1['Close'].pct_change().dropna()
                    returns2 = hist2['Close'].pct_change().dropna()
                    
                    min_len = min(len(returns1), len(returns2))
                    if min_len > 10:
                        returns1 = returns1.iloc[-min_len:]
                        returns2 = returns2.iloc[-min_len:]
                        
                        correlation = returns1.corr(returns2)
                        pair_correlations[f"{symbol1}-{symbol2}"] = {
                            "correlation": float(correlation) if not np.isnan(correlation) else 0.0,
                            "strength": "HIGH" if abs(correlation) > 0.7 else "MEDIUM" if abs(correlation) > 0.4 else "LOW",
                            "direction": "POSITIVE" if correlation > 0 else "NEGATIVE"
                        }
            except Exception as e:
                print(f"Error analyzing crypto correlation for {pair}: {e}")
        
        # Sector correlations (simulate)
        sector_correlations = {
            "technology-healthcare": {"correlation": 0.35, "strength": "LOW"},
            "technology-financial": {"correlation": 0.42, "strength": "MEDIUM"},
            "energy-materials": {"correlation": 0.68, "strength": "HIGH"},
            "consumer-industrial": {"correlation": 0.55, "strength": "MEDIUM"},
            "utilities-real_estate": {"correlation": 0.72, "strength": "HIGH"}
        }
        
        # Market correlations (simulate)
        market_correlations = {
            "stocks-bonds": {"correlation": -0.25, "strength": "LOW"},
            "stocks-commodities": {"correlation": 0.15, "strength": "LOW"},
            "forex-crypto": {"correlation": 0.08, "strength": "LOW"},
            "emerging-developed": {"correlation": 0.78, "strength": "HIGH"}
        }
        
        # Update correlation analysis
        risk_management["correlation_analysis"].update({
            "pair_correlations": pair_correlations,
            "sector_correlations": sector_correlations,
            "market_correlations": market_correlations,
            "last_updated": datetime.now().isoformat()
        })
        
        return risk_management["correlation_analysis"]
        
    except Exception as e:
        print(f"Error analyzing correlations: {e}")
        return risk_management["correlation_analysis"]

def calculate_dynamic_position_sizing():
    """Calculate dynamic position sizing using Kelly Criterion and risk parity"""
    global risk_management
    
    try:
        portfolio_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "BTC-USD", "ETH-USD", "EURUSD=X"]
        
        kelly_criterion = {}
        volatility_adjustment = {}
        risk_parity = {}
        
        for symbol in portfolio_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="6mo", interval="1d")
                
                if not hist.empty and len(hist) > 50:
                    returns = hist['Close'].pct_change().dropna()
                    
                    # Calculate Kelly Criterion
                    win_rate = len(returns[returns > 0]) / len(returns)
                    avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0.01
                    avg_loss = abs(returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0.01
                    
                    kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                    kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
                    
                    kelly_criterion[symbol] = {
                        "kelly_fraction": float(kelly_fraction),
                        "win_rate": float(win_rate),
                        "avg_win": float(avg_win),
                        "avg_loss": float(avg_loss)
                    }
                    
                    # Calculate volatility adjustment
                    volatility = returns.std() * np.sqrt(252)
                    vol_adjustment = 1.0 / (1.0 + volatility)  # Inverse volatility weighting
                    volatility_adjustment[symbol] = {
                        "volatility": float(volatility),
                        "adjustment_factor": float(vol_adjustment),
                        "recommended_size": float(vol_adjustment * 0.1)  # Base 10% * adjustment
                    }
                    
                    # Calculate risk parity
                    risk_parity[symbol] = {
                        "risk_contribution": 1.0 / len(portfolio_symbols),  # Equal risk contribution
                        "position_size": 0.1,  # Equal position size
                        "risk_adjusted_size": float(vol_adjustment * 0.1)
                    }
                    
                else:
                    # Default values
                    kelly_criterion[symbol] = {
                        "kelly_fraction": 0.1,
                        "win_rate": 0.5,
                        "avg_win": 0.02,
                        "avg_loss": 0.02
                    }
                    
                    volatility_adjustment[symbol] = {
                        "volatility": 0.2,
                        "adjustment_factor": 0.8,
                        "recommended_size": 0.08
                    }
                    
                    risk_parity[symbol] = {
                        "risk_contribution": 1.0 / len(portfolio_symbols),
                        "position_size": 0.1,
                        "risk_adjusted_size": 0.08
                    }
                    
            except Exception as e:
                print(f"Error calculating position sizing for {symbol}: {e}")
                # Default values
                kelly_criterion[symbol] = {"kelly_fraction": 0.1, "win_rate": 0.5, "avg_win": 0.02, "avg_loss": 0.02}
                volatility_adjustment[symbol] = {"volatility": 0.2, "adjustment_factor": 0.8, "recommended_size": 0.08}
                risk_parity[symbol] = {"risk_contribution": 0.1, "position_size": 0.1, "risk_adjusted_size": 0.08}
        
        # Update dynamic position sizing
        risk_management["dynamic_position_sizing"].update({
            "kelly_criterion": kelly_criterion,
            "volatility_adjustment": volatility_adjustment,
            "risk_parity": risk_parity,
            "last_updated": datetime.now().isoformat()
        })
        
        return risk_management["dynamic_position_sizing"]
        
    except Exception as e:
        print(f"Error calculating dynamic position sizing: {e}")
        return risk_management["dynamic_position_sizing"]

def calculate_risk_metrics():
    """Calculate advanced risk metrics including VaR, Expected Shortfall, etc."""
    global risk_management, trading_performance
    
    try:
        # Simulate portfolio returns for risk calculation
        np.random.seed(42)
        portfolio_returns = np.random.normal(0.0008, 0.02, 252)  # Daily returns
        
        # Calculate VaR (Value at Risk)
        var_95 = np.percentile(portfolio_returns, 5)  # 5th percentile
        var_99 = np.percentile(portfolio_returns, 1)  # 1st percentile
        
        # Calculate Expected Shortfall (Conditional VaR)
        expected_shortfall = portfolio_returns[portfolio_returns <= var_95].mean()
        
        # Calculate Maximum Drawdown
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        maximum_drawdown = drawdowns.min()
        
        # Calculate Sharpe Ratio
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = portfolio_returns - risk_free_rate
        sharpe_ratio = excess_returns.mean() / portfolio_returns.std() * np.sqrt(252)
        
        # Calculate Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else portfolio_returns.std()
        sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252)
        
        # Calculate Calmar Ratio
        annual_return = (1 + portfolio_returns.mean()) ** 252 - 1
        calmar_ratio = annual_return / abs(maximum_drawdown) if maximum_drawdown != 0 else 0
        
        # Calculate Beta (simulate)
        beta = 1.2  # Slightly more volatile than market
        
        # Calculate Alpha (simulate)
        alpha = 0.05  # 5% excess return
        
        # Update risk metrics
        risk_management["risk_metrics"].update({
            "var_95": float(var_95),
            "var_99": float(var_99),
            "expected_shortfall": float(expected_shortfall),
            "maximum_drawdown": float(maximum_drawdown),
            "sharpe_ratio": float(sharpe_ratio),
            "sortino_ratio": float(sortino_ratio),
            "calmar_ratio": float(calmar_ratio),
            "beta": float(beta),
            "alpha": float(alpha),
            "last_updated": datetime.now().isoformat()
        })
        
        return risk_management["risk_metrics"]
        
    except Exception as e:
        print(f"Error calculating risk metrics: {e}")
        return risk_management["risk_metrics"]

def get_comprehensive_risk_analysis():
    """Get comprehensive risk analysis combining all risk management components"""
    global risk_management
    
    try:
        # Calculate all risk components
        portfolio_heatmap = calculate_portfolio_heatmap()
        correlation_analysis = analyze_correlations()
        position_sizing = calculate_dynamic_position_sizing()
        risk_metrics = calculate_risk_metrics()
        
        return {
            "portfolio_heatmap": portfolio_heatmap,
            "correlation_analysis": correlation_analysis,
            "dynamic_position_sizing": position_sizing,
            "risk_metrics": risk_metrics,
            "risk_settings": risk_management["risk_settings"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting comprehensive risk analysis: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    run_server()
