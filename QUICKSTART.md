# 🚀 Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python tests/test_basic.py
   ```

## Running the Application

### Option 1: Demo Mode (Recommended for first run)
```bash
python demo.py
```
This will test the core functionality without starting the web server.

### Option 2: Web Interface
```bash
python run.py
```
Then open your browser to: http://localhost:8000

### Option 3: Direct FastAPI Server
```bash
uvicorn app.main:app --reload
```

## Features

✅ **Real-time Market Data** - Fetches live data from Yahoo Finance  
✅ **Technical Indicators** - RSI, MACD, Bollinger Bands, Moving Averages  
✅ **Machine Learning** - Random Forest model for signal prediction  
✅ **Trading Signals** - BUY/SELL/HOLD recommendations with confidence scores  
✅ **Beautiful Web Interface** - Interactive charts and real-time analysis  
✅ **API Endpoints** - RESTful API for integration  

## Usage

1. **Enter a stock symbol** (e.g., AAPL, GOOGL, TSLA)
2. **Select time period** (1 month to 5 years)
3. **Click Analyze** to generate signals
4. **View results** in the interactive dashboard

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/symbols` - Available symbols
- `POST /api/analyze` - Analyze a symbol
- `GET /api/signals/{symbol}` - Get signals for a symbol
- `GET /api/history/{symbol}` - Historical data
- `GET /docs` - API documentation (Swagger UI)

## Project Structure

```
├── app/                    # Main application
│   ├── main.py            # FastAPI app
│   ├── models/            # Data schemas
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── data/                  # Data storage
├── models/                # ML models
├── tests/                 # Unit tests
├── run.py                 # Run script
├── demo.py                # Demo script
└── requirements.txt       # Dependencies
```

## Troubleshooting

### Common Issues:

1. **Import errors**: Make sure you're in the project root directory
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Data fetch errors**: Check internet connection and symbol validity
4. **Port conflicts**: Change port in `run.py` or use `--port` with uvicorn

### Getting Help:

- Check the console output for error messages
- Verify all dependencies are installed
- Ensure you're using Python 3.8+

## Next Steps

- Customize trading parameters in `config.py`
- Add more technical indicators
- Implement backtesting strategies
- Connect to real trading APIs
- Add more ML models

---

**Happy Trading! 📈📉**



