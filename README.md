# Trading Signals WebApp

A comprehensive trading signals application that combines market scanning, historical data analysis, market sentiment, and technical analysis to generate profitable trading signals.

## Features

### 🚀 Core Functionality
- **Real-time Market Scanner**: Continuously monitors multiple markets and instruments
- **Technical Analysis**: Implements 20+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Sentiment Analysis**: Analyzes news, social media, and market sentiment
- **Signal Generation**: AI-powered trading signal generation with confidence scores
- **Historical Data**: Comprehensive historical data analysis and backtesting
- **Portfolio Tracking**: Monitor your positions and track performance

### 📊 Technical Indicators
- Moving Averages (SMA, EMA, WMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Stochastic Oscillator
- Williams %R
- ATR (Average True Range)
- Volume Analysis
- Support/Resistance Levels

### 🧠 Sentiment Analysis
- News sentiment scoring
- Social media sentiment analysis
- Market fear/greed indicators
- Economic calendar integration

### 📈 Data Sources
- Yahoo Finance API
- Alpha Vantage (optional)
- Real-time market data
- Historical price data
- Volume and market cap data

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI**: High-performance web framework
- **Pandas & NumPy**: Data manipulation and analysis
- **TA-Lib**: Technical analysis library
- **SQLAlchemy**: Database ORM
- **SQLite**: Lightweight database

### Frontend
- **React 18** with TypeScript
- **Material-UI**: Modern, responsive UI components
- **Recharts**: Interactive charts and visualizations
- **Lightweight Charts**: Professional trading charts
- **Axios**: HTTP client for API communication

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python main.py
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start
```

## Usage

1. **Start the backend server** (runs on http://localhost:8000)
2. **Start the frontend** (runs on http://localhost:3000)
3. **Configure your API keys** in the `.env` file
4. **Select markets** to scan and analyze
5. **Review generated signals** with confidence scores
6. **Track your portfolio** and performance

## API Endpoints

- `GET /api/markets` - Available markets
- `GET /api/scan` - Market scanner results
- `GET /api/signals` - Trading signals
- `GET /api/analysis/{symbol}` - Technical analysis for symbol
- `GET /api/sentiment/{symbol}` - Sentiment analysis
- `POST /api/portfolio` - Portfolio management

## Configuration

Create a `.env` file in the backend directory:
```env
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
DATABASE_URL=sqlite:///trading_signals.db
```

## Disclaimer

This application is for educational and research purposes only. Trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor.

## License

MIT License - see LICENSE file for details.

