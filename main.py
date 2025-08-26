from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from datetime import datetime, timedelta
import logging

from src.database import init_db
from src.routers import signals, analysis, sentiment, portfolio
from src.services.market_scanner import MarketScanner
from src.services.signal_generator import SignalGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Signals API",
    description="Advanced trading signals with technical analysis and sentiment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])

# Global services
market_scanner = MarketScanner()
signal_generator = SignalGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    logger.info("Starting Trading Signals API...")
    await init_db()
    
    # Start background market scanning
    asyncio.create_task(background_market_scanning())

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trading Signals API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "signals": "/api/signals",
            "analysis": "/api/analysis",
            "sentiment": "/api/sentiment",
            "portfolio": "/api/portfolio"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def background_market_scanning():
    """Background task for continuous market scanning"""
    while True:
        try:
            logger.info("Running market scan...")
            await market_scanner.scan_markets()
            await signal_generator.generate_signals()
            await asyncio.sleep(300)  # Scan every 5 minutes
        except Exception as e:
            logger.error(f"Error in background scanning: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

