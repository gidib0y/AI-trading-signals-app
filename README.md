# AI Trading Signal Generator

An intelligent trading signal generator that uses machine learning to analyze market data and generate buy/sell signals for various financial instruments.

## Features

- **Real-time Market Data**: Fetches live data from Yahoo Finance
- **Technical Indicators**: Calculates various technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **Machine Learning Models**: Uses scikit-learn for signal prediction
- **Web Interface**: FastAPI-based web application with interactive charts
- **Signal Generation**: Generates buy/sell/hold signals based on ML predictions
- **Backtesting**: Historical performance analysis

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # Data models and schemas
│   ├── services/            # Business logic and ML services
│   ├── utils/               # Utility functions and helpers
│   └── templates/           # HTML templates for web interface
├── data/                    # Data storage and caching
├── models/                  # Trained ML models
├── notebooks/               # Jupyter notebooks for analysis
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to `http://localhost:8000`

3. Use the web interface to:
   - Select stocks/symbols
   - Generate trading signals
   - View technical analysis charts
   - Analyze historical performance

## API Endpoints

- `GET /`: Main dashboard
- `GET /api/symbols`: Get available symbols
- `POST /api/analyze`: Analyze a symbol and generate signals
- `GET /api/signals/{symbol}`: Get signals for a specific symbol
- `GET /api/history/{symbol}`: Get historical data and analysis

## Configuration

Create a `.env` file in the root directory:
```
API_KEY=your_api_key_here
DEBUG=True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License









