from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import yfinance as yf

from src.database import get_db, Portfolio, MarketData

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_portfolio(db: Session = Depends(get_db)):
    """Get current portfolio positions"""
    try:
        positions = db.query(Portfolio).filter(Portfolio.status == "OPEN").all()
        
        portfolio_data = []
        total_value = 0
        total_pnl = 0
        
        for position in positions:
            # Get current market price
            try:
                ticker = yf.Ticker(position.symbol)
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
            except:
                current_price = position.current_price
            
            # Calculate current position value and P&L
            current_value = position.quantity * current_price
            pnl = current_value - (position.quantity * position.entry_price)
            pnl_percentage = (pnl / (position.quantity * position.entry_price)) * 100 if position.entry_price > 0 else 0
            
            # Update position with current data
            position.current_price = current_price
            position.pnl = pnl
            position.pnl_percentage = pnl_percentage
            
            portfolio_data.append({
                "id": position.id,
                "symbol": position.symbol,
                "quantity": position.quantity,
                "entry_price": position.entry_price,
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "pnl": round(pnl, 2),
                "pnl_percentage": round(pnl_percentage, 2),
                "timestamp": position.timestamp.isoformat()
            })
            
            total_value += current_value
            total_pnl += pnl
        
        # Calculate portfolio performance
        total_invested = sum(pos['quantity'] * pos['entry_price'] for pos in portfolio_data)
        total_return_percentage = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        db.commit()
        
        return {
            "positions": portfolio_data,
            "summary": {
                "total_positions": len(portfolio_data),
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_value, 2),
                "total_pnl": round(total_pnl, 2),
                "total_return_percentage": round(total_return_percentage, 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio: {str(e)}")

@router.post("/add")
async def add_position(
    symbol: str = Query(..., description="Stock symbol"),
    quantity: float = Query(..., description="Number of shares"),
    entry_price: float = Query(..., description="Entry price per share"),
    db: Session = Depends(get_db)
):
    """Add a new position to the portfolio"""
    try:
        # Check if position already exists
        existing_position = db.query(Portfolio).filter(
            Portfolio.symbol == symbol.upper(),
            Portfolio.status == "OPEN"
        ).first()
        
        if existing_position:
            # Update existing position (average down/up)
            total_quantity = existing_position.quantity + quantity
            total_cost = (existing_position.quantity * existing_position.entry_price) + (quantity * entry_price)
            new_avg_price = total_cost / total_quantity
            
            existing_position.quantity = total_quantity
            existing_position.entry_price = round(new_avg_price, 2)
            existing_position.timestamp = datetime.now()
            
            message = f"Updated position for {symbol}: {quantity} shares at ${entry_price:.2f}, new avg: ${new_avg_price:.2f}"
        else:
            # Create new position
            new_position = Portfolio(
                symbol=symbol.upper(),
                quantity=quantity,
                entry_price=entry_price,
                current_price=entry_price,
                pnl=0,
                pnl_percentage=0,
                status="OPEN"
            )
            db.add(new_position)
            message = f"Added new position: {quantity} shares of {symbol} at ${entry_price:.2f}"
        
        db.commit()
        
        return {
            "message": message,
            "symbol": symbol.upper(),
            "quantity": quantity,
            "entry_price": entry_price,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding position: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding position: {str(e)}")

@router.post("/close")
async def close_position(
    position_id: int = Query(..., description="Position ID to close"),
    exit_price: float = Query(..., description="Exit price per share"),
    db: Session = Depends(get_db)
):
    """Close a portfolio position"""
    try:
        position = db.query(Portfolio).filter(Portfolio.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        if position.status == "CLOSED":
            raise HTTPException(status_code=400, detail="Position already closed")
        
        # Calculate final P&L
        final_pnl = (exit_price - position.entry_price) * position.quantity
        final_pnl_percentage = (final_pnl / (position.quantity * position.entry_price)) * 100
        
        # Update position
        position.current_price = exit_price
        position.pnl = final_pnl
        position.pnl_percentage = final_pnl_percentage
        position.status = "CLOSED"
        position.timestamp = datetime.now()
        
        db.commit()
        
        return {
            "message": f"Closed position for {position.symbol}",
            "position_id": position_id,
            "symbol": position.symbol,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "final_pnl": round(final_pnl, 2),
            "final_pnl_percentage": round(final_pnl_percentage, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=f"Error closing position: {str(e)}")

@router.get("/performance")
async def get_portfolio_performance(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get portfolio performance over time"""
    try:
        # Get all positions (open and closed)
        all_positions = db.query(Portfolio).all()
        
        if not all_positions:
            return {
                "message": "No positions found",
                "performance_data": [],
                "summary": {}
            }
        
        # Calculate daily performance
        performance_data = []
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Calculate portfolio value for this date
            daily_value = 0
            daily_pnl = 0
            
            for position in all_positions:
                if position.status == "OPEN":
                    # For open positions, use current price
                    daily_value += position.quantity * position.current_price
                    daily_pnl += position.pnl
                else:
                    # For closed positions, use final values
                    if position.timestamp.date() <= date.date():
                        daily_value += position.quantity * position.current_price
                        daily_pnl += position.pnl
            
            performance_data.append({
                "date": date_str,
                "portfolio_value": round(daily_value, 2),
                "daily_pnl": round(daily_pnl, 2)
            })
        
        # Reverse to show oldest first
        performance_data.reverse()
        
        # Calculate performance metrics
        if len(performance_data) > 1:
            initial_value = performance_data[0]['portfolio_value']
            final_value = performance_data[-1]['portfolio_value']
            total_return = final_value - initial_value
            total_return_percentage = (total_return / initial_value) * 100 if initial_value > 0 else 0
        else:
            total_return = 0
            total_return_percentage = 0
        
        return {
            "period_days": days,
            "performance_data": performance_data,
            "summary": {
                "initial_value": performance_data[0]['portfolio_value'] if performance_data else 0,
                "final_value": performance_data[-1]['portfolio_value'] if performance_data else 0,
                "total_return": round(total_return, 2),
                "total_return_percentage": round(total_return_percentage, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating portfolio performance: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating performance: {str(e)}")

@router.get("/positions/{symbol}")
async def get_position_details(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific symbol's positions"""
    try:
        positions = db.query(Portfolio).filter(
            Portfolio.symbol == symbol.upper()
        ).order_by(Portfolio.timestamp.desc()).all()
        
        if not positions:
            raise HTTPException(status_code=404, detail=f"No positions found for {symbol}")
        
        # Calculate position statistics
        open_positions = [p for p in positions if p.status == "OPEN"]
        closed_positions = [p for p in positions if p.status == "CLOSED"]
        
        total_quantity = sum(p.quantity for p in open_positions)
        total_invested = sum(p.quantity * p.entry_price for p in open_positions)
        total_pnl = sum(p.pnl for p in open_positions)
        
        # Calculate average entry price
        avg_entry_price = total_invested / total_quantity if total_quantity > 0 else 0
        
        # Get current market price
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
        except:
            current_price = open_positions[0].current_price if open_positions else 0
        
        current_value = total_quantity * current_price
        unrealized_pnl = current_value - total_invested
        unrealized_pnl_percentage = (unrealized_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            "symbol": symbol.upper(),
            "current_position": {
                "total_quantity": total_quantity,
                "total_invested": round(total_invested, 2),
                "avg_entry_price": round(avg_entry_price, 2),
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_percentage": round(unrealized_pnl_percentage, 2)
            },
            "open_positions": [
                {
                    "id": p.id,
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "entry_date": p.timestamp.isoformat(),
                    "current_pnl": round(p.pnl, 2),
                    "current_pnl_percentage": round(p.pnl_percentage, 2)
                }
                for p in open_positions
            ],
            "closed_positions": [
                {
                    "id": p.id,
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "exit_price": p.current_price,
                    "entry_date": p.timestamp.isoformat(),
                    "final_pnl": round(p.pnl, 2),
                    "final_pnl_percentage": round(p.pnl_percentage, 2)
                }
                for p in closed_positions
            ],
            "summary": {
                "total_open_positions": len(open_positions),
                "total_closed_positions": len(closed_positions),
                "total_realized_pnl": round(sum(p.pnl for p in closed_positions), 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching position details for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching position details: {str(e)}")

@router.delete("/positions/{position_id}")
async def delete_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Delete a portfolio position"""
    try:
        position = db.query(Portfolio).filter(Portfolio.id == position_id).first()
        
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        
        db.delete(position)
        db.commit()
        
        return {"message": f"Position {position_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting position {position_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting position: {str(e)}")

@router.get("/watchlist")
async def get_watchlist():
    """Get watchlist of stocks to monitor"""
    # This could be expanded to include user-specific watchlists
    return {
        "watchlist": [
            {"symbol": "AAPL", "name": "Apple Inc.", "reason": "Strong technical indicators"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "reason": "Oversold conditions"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "reason": "Breakout potential"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "reason": "AI momentum"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "reason": "Support level test"}
        ],
        "timestamp": datetime.now().isoformat()
    }

