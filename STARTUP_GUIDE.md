# 🚀 Trading Signals Pro - Startup Guide

Welcome to Trading Signals Pro! This comprehensive guide will help you get the application up and running.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Backend Requirements
- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Usually comes with Python

### Frontend Requirements
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **npm** - Usually comes with Node.js

## 🏗️ Project Structure

```
trading-signals-app/
├── src/                    # Backend source code
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   └── database.py        # Database models
├── public/                # Frontend public files
├── src/                   # Frontend source code
│   └── components/        # React components
├── main.py               # Backend entry point
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

#### Windows
1. **Start Backend**: Double-click `start_backend.py`
2. **Start Frontend**: Double-click `start_frontend.bat`

#### Unix/Linux/Mac
1. **Start Backend**: `python start_backend.py`
2. **Start Frontend**: `./start_frontend.sh`

### Option 2: Manual Startup

#### Step 1: Start Backend Server

1. **Open terminal/command prompt** in the project directory
2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Unix/Linux/Mac: `source venv/bin/activate`
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Start server**:
   ```bash
   python main.py
   ```

The backend will start on **http://localhost:8000**

#### Step 2: Start Frontend

1. **Open a new terminal/command prompt** in the project directory
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Start development server**:
   ```bash
   npm start
   ```

The frontend will start on **http://localhost:3000**

## 🌐 Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Optional: API Keys for enhanced features
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Database configuration
DATABASE_URL=sqlite:///trading_signals.db
```

### Customizing Market Symbols

Edit `src/services/market_scanner.py` to add/remove symbols:

```python
self.monitored_symbols = [
    "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA",
    # Add your preferred symbols here
]
```

## 📊 Features Overview

### 🎯 Core Features
- **Real-time Market Scanner**: Continuously monitors markets
- **Technical Analysis**: 20+ technical indicators
- **Sentiment Analysis**: News and social media sentiment
- **Signal Generation**: AI-powered trading signals
- **Portfolio Tracking**: Position management and P&L

### 📈 Technical Indicators
- RSI, MACD, Bollinger Bands
- Moving Averages (SMA, EMA)
- Stochastic Oscillator
- ATR, Volume Analysis
- Support/Resistance Levels

### 🧠 Sentiment Analysis
- News sentiment scoring
- Social media sentiment
- Market fear/greed indicators
- Economic calendar integration

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
- **Port 8000 in use**: Change port in `main.py`
- **Python version**: Ensure Python 3.9+
- **Dependencies**: Run `pip install -r requirements.txt`

#### Frontend Won't Start
- **Port 3000 in use**: Frontend will automatically use next available port
- **Node.js version**: Ensure Node.js 16+
- **Dependencies**: Run `npm install`

#### Database Issues
- **SQLite locked**: Close any other applications using the database
- **Permission denied**: Check file permissions

#### API Connection Issues
- **CORS errors**: Backend CORS is configured for localhost:3000
- **Network errors**: Ensure both servers are running

### Performance Tips

- **Market scanning**: Adjust scan interval in `MarketScanner` class
- **Data storage**: Consider using PostgreSQL for production
- **Caching**: Implement Redis for frequently accessed data

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Database**: Use strong passwords for production databases
- **CORS**: Configure CORS properly for production deployment

## 📚 API Endpoints

### Markets
- `GET /api/markets` - List available markets
- `GET /api/markets/scan` - Scan markets for opportunities
- `GET /api/markets/{symbol}` - Get market data

### Technical Analysis
- `GET /api/analysis/{symbol}` - Get technical analysis
- `GET /api/analysis/{symbol}/indicators` - Get specific indicators

### Trading Signals
- `GET /api/signals` - List trading signals
- `GET /api/signals/generate` - Generate new signals
- `GET /api/signals/{symbol}/latest` - Get latest signal

### Sentiment
- `GET /api/sentiment/{symbol}` - Get sentiment analysis
- `GET /api/sentiment/market/fear-greed` - Get fear/greed index

### Portfolio
- `GET /api/portfolio` - Get portfolio positions
- `POST /api/portfolio/add` - Add position
- `POST /api/portfolio/close` - Close position

## 🚀 Next Steps

1. **Explore the Dashboard**: Start with the main dashboard
2. **Run Market Scanner**: Scan for trading opportunities
3. **Generate Signals**: Create AI-powered trading signals
4. **Analyze Markets**: Use technical and sentiment analysis
5. **Track Portfolio**: Monitor positions and performance

## 📞 Support

- **Documentation**: Check the README.md file
- **Issues**: Report bugs in the project repository
- **Questions**: Review the code comments and API documentation

## ⚠️ Disclaimer

This application is for **educational and research purposes only**. Trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor.

---

**Happy Trading! 📈🚀**

