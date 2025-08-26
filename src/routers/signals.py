from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.database import get_db, TradingSignal, MarketData, TechnicalIndicators, SentimentData
from src.services.signal_generator import SignalGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

signal_generator = SignalGenerator()

@router.get("/")
async def get_trading_signals(
    signal_type: Optional[str] = Query(None, description="Filter by signal type (BUY, SELL, HOLD)"),
    min_confidence: Optional[float] = Query(70.0, description="Minimum confidence score"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(50, description="Maximum number of signals to return"),
    db: Session = Depends(get_db)
):
    """Get trading signals with optional filtering"""
    try:
        query = db.query(TradingSignal)
        
        if signal_type:
            query = query.filter(TradingSignal.signal_type == signal_type.upper())
        
        if min_confidence:
            query = query.filter(TradingSignal.confidence_score >= min_confidence)
        
        if symbol:
            query = query.filter(TradingSignal.symbol == symbol.upper())
        
        # Get latest signals first
        signals = query.order_by(TradingSignal.timestamp.desc()).limit(limit).all()
        
        return {
            "signals": [
                {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "timestamp": signal.timestamp.isoformat(),
                    "signal_type": signal.signal_type,
                    "confidence_score": signal.confidence_score,
                    "price_target": signal.price_target,
                    "stop_loss": signal.stop_loss,
                    "technical_score": signal.technical_score,
                    "sentiment_score": signal.sentiment_score,
                    "volume_score": signal.volume_score,
                    "overall_score": signal.overall_score,
                    "reasoning": signal.reasoning
                }
                for signal in signals
            ],
            "count": len(signals),
            "filters": {
                "signal_type": signal_type,
                "min_confidence": min_confidence,
                "symbol": symbol,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching trading signals: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching signals: {str(e)}")

@router.get("/generate")
async def generate_signals(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols to analyze"),
    db: Session = Depends(get_db)
):
    """Generate new trading signals for specified symbols or all monitored symbols"""
    try:
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            # Get all symbols from recent market data
            recent_data = db.query(MarketData.symbol).distinct().all()
            symbol_list = [data[0] for data in recent_data]
        
        generated_signals = []
        
        for symbol in symbol_list:
            try:
                # Generate signal for this symbol
                signal = await signal_generator.generate_signal_for_symbol(symbol, db)
                if signal:
                    generated_signals.append(signal)
                    
                    # Store in database
                    db_signal = TradingSignal(
                        symbol=symbol,
                        signal_type=signal['signal_type'],
                        confidence_score=signal['confidence_score'],
                        price_target=signal['price_target'],
                        stop_loss=signal['stop_loss'],
                        technical_score=signal['technical_score'],
                        sentiment_score=signal['sentiment_score'],
                        volume_score=signal['volume_score'],
                        overall_score=signal['overall_score'],
                        reasoning=signal['reasoning']
                    )
                    db.add(db_signal)
                
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {e}")
                continue
        
        db.commit()
        
        return {
            "generated_signals": generated_signals,
            "count": len(generated_signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating signals: {str(e)}")

@router.get("/{signal_id}")
async def get_signal_details(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific trading signal"""
    try:
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        return {
            "id": signal.id,
            "symbol": signal.symbol,
            "timestamp": signal.timestamp.isoformat(),
            "signal_type": signal.signal_type,
            "confidence_score": signal.confidence_score,
            "price_target": signal.price_target,
            "stop_loss": signal.stop_loss,
            "technical_score": signal.technical_score,
            "sentiment_score": signal.sentiment_score,
            "volume_score": signal.volume_score,
            "overall_score": signal.overall_score,
            "reasoning": signal.reasoning
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal {signal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching signal: {str(e)}")

@router.get("/{symbol}/latest")
async def get_latest_signal(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get the latest trading signal for a specific symbol"""
    try:
        signal = db.query(TradingSignal).filter(
            TradingSignal.symbol == symbol.upper()
        ).order_by(TradingSignal.timestamp.desc()).first()
        
        if not signal:
            raise HTTPException(status_code=404, detail=f"No signals found for {symbol}")
        
        return {
            "id": signal.id,
            "symbol": signal.symbol,
            "timestamp": signal.timestamp.isoformat(),
            "signal_type": signal.signal_type,
            "confidence_score": signal.confidence_score,
            "price_target": signal.price_target,
            "stop_loss": signal.stop_loss,
            "technical_score": signal.technical_score,
            "sentiment_score": signal.sentiment_score,
            "volume_score": signal.volume_score,
            "overall_score": signal.overall_score,
            "reasoning": signal.reasoning
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching signal: {str(e)}")

@router.get("/{symbol}/history")
async def get_signal_history(
    symbol: str,
    days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(100, description="Maximum number of signals to return"),
    db: Session = Depends(get_db)
):
    """Get signal history for a specific symbol"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        signals = db.query(TradingSignal).filter(
            TradingSignal.symbol == symbol.upper(),
            TradingSignal.timestamp >= cutoff_date
        ).order_by(TradingSignal.timestamp.desc()).limit(limit).all()
        
        if not signals:
            raise HTTPException(status_code=404, detail=f"No signals found for {symbol} in the last {days} days")
        
        return {
            "symbol": symbol,
            "period_days": days,
            "signals": [
                {
                    "id": signal.id,
                    "timestamp": signal.timestamp.isoformat(),
                    "signal_type": signal.signal_type,
                    "confidence_score": signal.confidence_score,
                    "price_target": signal.price_target,
                    "stop_loss": signal.stop_loss,
                    "overall_score": signal.overall_score
                }
                for signal in signals
            ],
            "count": len(signals),
            "signal_distribution": {
                "BUY": len([s for s in signals if s.signal_type == "BUY"]),
                "SELL": len([s for s in signals if s.signal_type == "SELL"]),
                "HOLD": len([s for s in signals if s.signal_type == "HOLD"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching signal history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching signal history: {str(e)}")

@router.get("/dashboard/summary")
async def get_signals_dashboard(db: Session = Depends(get_db)):
    """Get dashboard summary of trading signals"""
    try:
        # Get recent signals (last 24 hours)
        cutoff_date = datetime.now() - timedelta(hours=24)
        recent_signals = db.query(TradingSignal).filter(
            TradingSignal.timestamp >= cutoff_date
        ).all()
        
        # Get high confidence signals
        high_confidence_signals = db.query(TradingSignal).filter(
            TradingSignal.confidence_score >= 80
        ).order_by(TradingSignal.timestamp.desc()).limit(10).all()
        
        # Calculate statistics
        total_signals = len(recent_signals)
        buy_signals = len([s for s in recent_signals if s.signal_type == "BUY"])
        sell_signals = len([s for s in recent_signals if s.signal_type == "SELL"])
        hold_signals = len([s for s in recent_signals if s.signal_type == "HOLD"])
        
        avg_confidence = sum(s.confidence_score for s in recent_signals) / total_signals if total_signals > 0 else 0
        
        return {
            "last_24_hours": {
                "total_signals": total_signals,
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "hold_signals": hold_signals,
                "average_confidence": round(avg_confidence, 1)
            },
            "high_confidence_signals": [
                {
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type,
                    "confidence_score": signal.confidence_score,
                    "timestamp": signal.timestamp.isoformat()
                }
                for signal in high_confidence_signals
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching signals dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")

@router.delete("/{signal_id}")
async def delete_signal(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """Delete a trading signal"""
    try:
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        db.delete(signal)
        db.commit()
        
        return {"message": f"Signal {signal_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting signal {signal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting signal: {str(e)}")

@router.post("/{signal_id}/validate")
async def validate_signal(
    signal_id: int,
    actual_outcome: str = Query(..., description="Actual outcome (PROFIT, LOSS, BREAKEVEN)"),
    actual_return: Optional[float] = Query(None, description="Actual return percentage"),
    notes: Optional[str] = Query(None, description="Additional notes"),
    db: Session = Depends(get_db)
):
    """Validate a trading signal with actual outcome"""
    try:
        signal = db.query(TradingSignal).filter(TradingSignal.id == signal_id).first()
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        # In a real implementation, you would add validation fields to the TradingSignal model
        # For now, we'll just return a success message
        
        return {
            "message": f"Signal {signal_id} validated with outcome: {actual_outcome}",
            "signal_id": signal_id,
            "outcome": actual_outcome,
            "return": actual_return,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating signal {signal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating signal: {str(e)}")

