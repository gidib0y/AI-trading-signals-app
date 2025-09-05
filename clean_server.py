#!/usr/bin/env python3
"""
Clean Trading Signals Server
A simplified, working trading interface focused on signal quality
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Clean Trading Signals Server", version="1.0.0")

# Global variables
current_signals = []
market_data = {}

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Main trading interface page"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clean Trading Signals</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #4CAF50, #2196F3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .market-selection {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .market-card {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .market-card:hover {
            transform: translateY(-5px);
            border-color: #4CAF50;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        
        .market-card.active {
            border-color: #4CAF50;
            background: rgba(76, 175, 80, 0.2);
        }
        
        .market-card h3 {
            font-size: 1.2em;
            margin-bottom: 5px;
        }
        
        .market-card .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .panel h2 {
            color: #4CAF50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .symbols-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .symbol-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .symbol-card:hover {
            background: rgba(76, 175, 80, 0.3);
            transform: scale(1.05);
        }
        
        .trading-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .action-button {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            border: none;
            border-radius: 8px;
            padding: 15px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .action-button.blue {
            background: linear-gradient(135deg, #2196F3, #1976D2);
        }
        
        .action-button.purple {
            background: linear-gradient(135deg, #9C27B0, #7B1FA2);
        }
        
        .results {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            min-height: 100px;
        }
        
        .loading {
            color: #4CAF50;
            text-align: center;
            padding: 20px;
        }
        
        .error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
        
        .success {
            color: #4CAF50;
            text-align: center;
            padding: 20px;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        
        .input-group input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .category-header {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(76, 175, 80, 0.1));
            border-left: 4px solid #4CAF50;
            border-radius: 6px;
            padding: 10px 15px;
            margin: 15px 0 10px 0;
            font-weight: bold;
            color: #4CAF50;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .market-selection {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .trading-actions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Clean Trading Signals</h1>
            <p>Professional Trading Interface - Focused on Signal Quality</p>
        </div>
        
        <!-- Market Selection -->
        <div class="market-selection">
            <div class="market-card" onclick="selectMarket('stocks', this)">
                <div class="icon">📊</div>
                <h3>STOCKS</h3>
                <p>US Equities & ETFs</p>
            </div>
            <div class="market-card" onclick="selectMarket('forex', this)">
                <div class="icon">💱</div>
                <h3>FOREX</h3>
                <p>Currency Pairs</p>
            </div>
            <div class="market-card" onclick="selectMarket('crypto', this)">
                <div class="icon">₿</div>
                <h3>CRYPTO</h3>
                <p>Digital Assets</p>
            </div>
            <div class="market-card" onclick="selectMarket('futures', this)">
                <div class="icon">⛽</div>
                <h3>FUTURES</h3>
                <p>Commodities & Indices</p>
            </div>
            <div class="market-card" onclick="selectMarket('indices', this)">
                <div class="icon">📈</div>
                <h3>INDICES</h3>
                <p>Market Indexes</p>
            </div>
            <div class="market-card" onclick="selectMarket('metals', this)">
                <div class="icon">🥇</div>
                <h3>METALS</h3>
                <p>Precious Metals</p>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Market Scanner Panel -->
            <div class="panel">
                <h2>🔍 Market Scanner</h2>
                <div class="symbols-grid" id="symbols-container">
                    <div class="loading">Select a market to view symbols</div>
                </div>
                <div class="results" id="scanner-results">
                    <div class="loading">Ready to scan market</div>
                </div>
            </div>
            
            <!-- Symbol Analyzer Panel -->
            <div class="panel">
                <h2>📊 Symbol Analyzer</h2>
                <div class="input-group">
                    <input type="text" id="symbol-input" placeholder="Enter symbol (e.g., AAPL, BTC-USD, EURUSD)" />
                </div>
                <div class="results" id="analyzer-results">
                    <div class="loading">Enter a symbol to analyze</div>
                </div>
            </div>
        </div>
        
        <!-- Trading Actions -->
        <div class="trading-actions">
            <button class="action-button" onclick="scanFullMarket()">
                🔍 Scan Full Market
            </button>
            <button class="action-button blue" onclick="analyzeSymbol()">
                📊 Analyze Symbol
            </button>
            <button class="action-button purple" onclick="getLiveSignals()">
                📈 Get Live Signals
            </button>
            <button class="action-button purple" onclick="createCharts()">
                📊 Load Charts
            </button>
            <button class="action-button purple" onclick="getMarketSummary()">
                📊 Market Summary
            </button>
        </div>
        
        <!-- Live Signals Display -->
        <div class="panel">
            <h2>📈 Live Trading Signals</h2>
            <div class="results" id="signals-display">
                <div class="loading">Ready to display live trading signals</div>
            </div>
        </div>
    </div>

    <script>
        // Clean, working JavaScript
        let currentMarket = 'stocks';
        
        // Market data with organized categories
        const marketData = {
            stocks: {
                name: 'STOCKS',
                icon: '📊',
                color: '#4CAF50',
                categories: {
                    'NASDAQ': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC'],
                    'NYSE': ['JPM', 'JNJ', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'V', 'NKE', 'DIS'],
                    'ETFs': ['SPY', 'QQQ', 'IWM', 'DIA', 'GLD', 'SLV', 'USO', 'TLT', 'VXX']
                }
            },
            forex: {
                name: 'FOREX',
                icon: '💱',
                color: '#2196F3',
                categories: {
                    'MAJORS': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X'],
                    'MINORS': ['EURGBP=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 'EURAUD=X', 'GBPAUD=X'],
                    'EXOTICS': ['USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'EURCHF=X', 'GBPCHF=X', 'USDZAR=X']
                }
            },
            crypto: {
                name: 'CRYPTO',
                icon: '₿',
                color: '#FFC107',
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
                categories: {
                    'PRECIOUS': ['GC', 'SI', 'PL', 'PA', 'GLD', 'SLV', 'PPLT', 'PALL'],
                    'MINING': ['GDX', 'GDXJ', 'SIL', 'COPX', 'PICK', 'REMX', 'URA', 'LIT'],
                    'AGRICULTURE': ['BAL', 'NIB', 'JO', 'CAFE', 'WEAT', 'CORN', 'SOYB', 'CANE']
                }
            }
        };
        
        // Core Functions
        function selectMarket(market, element) {
            console.log('Selecting market:', market);
            currentMarket = market;
            
            // Update active market styling
            document.querySelectorAll('.market-card').forEach(card => {
                card.classList.remove('active');
            });
            element.classList.add('active');
            
            // Show market symbols
            showMarketSymbols(market);
        }
        
        function showMarketSymbols(market) {
            console.log('Showing symbols for market:', market);
            
            const symbolsContainer = document.getElementById('symbols-container');
            const marketInfo = marketData[market];
            const categories = marketInfo.categories;
            
            // Clear container
            symbolsContainer.innerHTML = '';
            
            // Create category sections
            Object.entries(categories).forEach(([categoryName, symbols]) => {
                // Create category header
                const categoryHeader = document.createElement('div');
                categoryHeader.className = 'category-header';
                categoryHeader.innerHTML = `📂 ${categoryName}`;
                symbolsContainer.appendChild(categoryHeader);
                
                // Create symbols grid for this category
                const categoryGrid = document.createElement('div');
                categoryGrid.className = 'symbols-grid';
                
                // Add symbols for this category
                symbols.slice(0, 6).forEach(symbol => {
                    const symbolCard = document.createElement('div');
                    symbolCard.className = 'symbol-card';
                    symbolCard.innerHTML = `
                        <div style="font-weight: bold; margin-bottom: 2px;">${symbol}</div>
                        <div style="font-size: 0.8em; opacity: 0.7;">${categoryName}</div>
                    `;
                    symbolCard.onclick = () => {
                        document.getElementById('symbol-input').value = symbol;
                    };
                    categoryGrid.appendChild(symbolCard);
                });
                
                symbolsContainer.appendChild(categoryGrid);
            });
        }
        
        // Button Functions
        async function scanFullMarket() {
            console.log('Scanning full market...');
            const resultsDiv = document.getElementById('scanner-results');
            resultsDiv.innerHTML = '<div class="loading">🔍 Scanning entire market for trading signals...</div>';
            
            try {
                const response = await fetch('/api/scan/full-market');
                const data = await response.json();
                
                resultsDiv.innerHTML = `
                    <div class="success">
                        ✅ Market scan completed!<br>
                        Found ${data.signals?.length || 0} trading signals<br>
                        <small>${data.message || 'Market analysis complete'}</small>
                    </div>
                `;
            } catch (error) {
                console.error('Scan error:', error);
                resultsDiv.innerHTML = '<div class="error">❌ Error scanning market</div>';
            }
        }
        
        async function analyzeSymbol() {
            const symbolInput = document.getElementById('symbol-input');
            const symbol = symbolInput?.value?.trim();
            
            if (!symbol) {
                alert('Please enter a symbol to analyze');
                return;
            }
            
            console.log('Analyzing symbol:', symbol);
            const resultsDiv = document.getElementById('analyzer-results');
            resultsDiv.innerHTML = `<div class="loading">📊 Analyzing ${symbol}...</div>`;
            
            try {
                const response = await fetch(`/api/analyze/${symbol}`);
                const data = await response.json();
                
                resultsDiv.innerHTML = `
                    <div class="success">
                        📊 Analysis for ${symbol}<br>
                        <small>${data.message || 'Analysis complete'}</small>
                    </div>
                `;
            } catch (error) {
                console.error('Analysis error:', error);
                resultsDiv.innerHTML = '<div class="error">❌ Error analyzing symbol</div>';
            }
        }
        
        async function getLiveSignals() {
            console.log('Getting live signals...');
            const signalsDiv = document.getElementById('signals-display');
            signalsDiv.innerHTML = '<div class="loading">📈 Getting live trading signals...</div>';
            
            try {
                const response = await fetch('/api/live/signals');
                const data = await response.json();
                
                signalsDiv.innerHTML = `
                    <div class="success">
                        📈 Live Signals Loaded<br>
                        <small>${data.message || 'Live signals ready'}</small>
                    </div>
                `;
            } catch (error) {
                console.error('Signals error:', error);
                signalsDiv.innerHTML = '<div class="error">❌ Error loading signals</div>';
            }
        }
        
        async function createCharts() {
            console.log('Creating charts...');
            alert('Charts functionality coming soon!');
        }
        
        async function getMarketSummary() {
            console.log('Getting market summary...');
            alert('Market summary functionality coming soon!');
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Clean trading interface loaded successfully!');
            
            // Set default market selection
            const firstMarketCard = document.querySelector('.market-card');
            if (firstMarketCard) {
                selectMarket('stocks', firstMarketCard);
            }
        });
    </script>
</body>
</html>
    """)

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/scan/full-market")
async def scan_full_market():
    """Scan full market for trading signals"""
    try:
        # Simulate market scanning
        signals = [
            {"symbol": "AAPL", "signal": "BUY", "strength": 0.85, "price": 175.50},
            {"symbol": "TSLA", "signal": "SELL", "strength": 0.72, "price": 245.30},
            {"symbol": "MSFT", "signal": "BUY", "strength": 0.91, "price": 378.20},
            {"symbol": "GOOGL", "signal": "HOLD", "strength": 0.45, "price": 142.80}
        ]
        
        return {
            "status": "success",
            "signals": signals,
            "message": f"Market scan completed. Found {len(signals)} trading opportunities.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error scanning market: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyze/{symbol}")
async def analyze_symbol(symbol: str):
    """Analyze individual symbol"""
    try:
        # Simulate symbol analysis
        analysis = {
            "symbol": symbol.upper(),
            "current_price": 150.25,
            "signal": "BUY",
            "confidence": 0.78,
            "target_price": 165.00,
            "stop_loss": 140.00,
            "analysis": f"Strong bullish momentum detected for {symbol.upper()}"
        }
        
        return {
            "status": "success",
            "analysis": analysis,
            "message": f"Analysis complete for {symbol.upper()}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live/signals")
async def get_live_signals():
    """Get live trading signals"""
    try:
        # Simulate live signals
        live_signals = [
            {"symbol": "BTC-USD", "signal": "BUY", "price": 43250.00, "timestamp": datetime.now().isoformat()},
            {"symbol": "ETH-USD", "signal": "SELL", "price": 2650.00, "timestamp": datetime.now().isoformat()},
            {"symbol": "EURUSD=X", "signal": "BUY", "price": 1.0850, "timestamp": datetime.now().isoformat()}
        ]
        
        return {
            "status": "success",
            "signals": live_signals,
            "message": f"Live signals updated. {len(live_signals)} active signals.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting live signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Clean Trading Signals Server...")
    print("📍 API URL: http://localhost:8005")
    print("🔗 Health check: http://localhost:8005/api/health")
    print("⏹️  Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "clean_server:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
