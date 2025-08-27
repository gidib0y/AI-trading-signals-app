from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

from app.services.trading_service import TradingService
from app.services.ml_service import MLService
from app.models.schemas import AnalysisRequest, AnalysisResponse, SignalResponse
from app.utils.data_fetcher import DataFetcher
from app.utils.indicators import TechnicalIndicators

# Initialize FastAPI app
app = FastAPI(
    title="AI Trading Signal Generator",
    description="An intelligent trading signal generator using machine learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
trading_service = TradingService()
ml_service = MLService()
data_fetcher = DataFetcher()
indicators = TechnicalIndicators()

# Templates setup
templates = Jinja2Templates(directory="app/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/symbols")
async def get_symbols():
    """Get list of available symbols"""
    try:
        # Popular stock symbols
        symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "SPY", "QQQ", "IWM", "GLD", "SLV", "USO", "TLT", "VXX"
        ]
        return {"symbols": symbols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_symbol(request: AnalysisRequest):
    """Analyze a symbol and generate trading signals"""
    try:
        # Fetch historical data
        data = await data_fetcher.fetch_data(request.symbol, request.period)
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")
        
        # Calculate technical indicators
        data_with_indicators = indicators.calculate_all(data)
        
        # Generate ML predictions
        predictions = ml_service.predict_signals(data_with_indicators)
        
        # Generate trading signals
        signals = trading_service.generate_signals(data_with_indicators, predictions)
        
        # Prepare response
        response = AnalysisResponse(
            symbol=request.symbol,
            signals=signals,
            data=data_with_indicators.to_dict('records'),
            indicators=indicators.get_indicator_summary(data_with_indicators),
            predictions=predictions
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals/{symbol}")
async def get_signals(symbol: str, period: str = "1y"):
    """Get trading signals for a specific symbol"""
    try:
        # Fetch data and generate signals
        data = await data_fetcher.fetch_data(symbol, period)
        data_with_indicators = indicators.calculate_all(data)
        predictions = ml_service.predict_signals(data_with_indicators)
        signals = trading_service.generate_signals(data_with_indicators, predictions)
        
        return SignalResponse(
            symbol=symbol,
            signals=signals,
            last_updated=data.index[-1].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{symbol}")
async def get_history(symbol: str, period: str = "1y"):
    """Get historical data and analysis for a symbol"""
    try:
        data = await data_fetcher.fetch_data(symbol, period)
        data_with_indicators = indicators.calculate_all(data)
        
        return {
            "symbol": symbol,
            "period": period,
            "data": data_with_indicators.to_dict('records'),
            "summary": {
                "total_days": len(data),
                "start_date": data.index[0].isoformat(),
                "end_date": data.index[-1].isoformat(),
                "current_price": float(data['Close'].iloc[-1]),
                "price_change": float(data['Close'].iloc[-1] - data['Close'].iloc[0]),
                "price_change_pct": float(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Trading Signal Generator"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



