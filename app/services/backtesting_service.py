import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import math
import logging
from dataclasses import dataclass

@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    position_size: float
    side: str  # 'LONG' or 'SHORT'
    stop_loss: float
    take_profit: float
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    status: str = 'OPEN'  # 'OPEN', 'CLOSED', 'STOPPED_OUT', 'TAKE_PROFIT'

@dataclass
class BacktestResult:
    """Results of a backtest"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    profit_factor: float
    average_trade: float
    best_trade: float
    worst_trade: float
    trades: List[Trade]
    equity_curve: List[float]
    drawdown_curve: List[float]

class BacktestingService:
    """Comprehensive backtesting service for trading strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_data_points = 100
        
    def run_backtest(self, strategy_config: Dict, historical_data: Dict) -> BacktestResult:
        """Run a complete backtest of a trading strategy"""
        
        try:
            # Validate data
            if not self._validate_data(historical_data):
                raise ValueError("Insufficient historical data for backtesting")
            
            # Initialize backtest
            initial_capital = strategy_config.get('initial_capital', 10000)
            position_size_pct = strategy_config.get('position_size_pct', 0.1)
            stop_loss_pct = strategy_config.get('stop_loss_pct', 0.02)
            take_profit_pct = strategy_config.get('take_profit_pct', 0.04)
            
            # Extract price data
            prices = historical_data['close_prices']
            volumes = historical_data.get('volumes', [1000] * len(prices))
            timestamps = historical_data.get('timestamps', [datetime.now() + timedelta(minutes=i) for i in range(len(prices))])
            
            # Run strategy simulation
            trades, equity_curve = self._simulate_strategy(
                prices, volumes, timestamps, strategy_config,
                initial_capital, position_size_pct, stop_loss_pct, take_profit_pct
            )
            
            # Calculate performance metrics
            result = self._calculate_performance_metrics(
                trades, equity_curve, initial_capital
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise
    
    def _validate_data(self, data: Dict) -> bool:
        """Validate that we have sufficient data for backtesting"""
        required_fields = ['close_prices']
        
        for field in required_fields:
            if field not in data or len(data[field]) < self.min_data_points:
                return False
        
        return True
    
    def _simulate_strategy(self, prices: List[float], volumes: List[float], 
                          timestamps: List[datetime], strategy_config: Dict,
                          initial_capital: float, position_size_pct: float,
                          stop_loss_pct: float, take_profit_pct: float) -> Tuple[List[Trade], List[float]]:
        """Simulate trading strategy execution"""
        
        trades = []
        equity_curve = [initial_capital]
        current_capital = initial_capital
        open_position = None
        
        # Strategy parameters
        rsi_oversold = strategy_config.get('rsi_oversold', 30)
        rsi_overbought = strategy_config.get('rsi_overbought', 70)
        macd_signal_threshold = strategy_config.get('macd_signal_threshold', 0.1)
        
        for i in range(20, len(prices)):  # Start from 20 to have enough data for indicators
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(prices[:i+1])
            macd, macd_signal = self._calculate_macd(prices[:i+1])
            
            # Check for exit conditions on open position
            if open_position:
                exit_signal = self._check_exit_conditions(
                    open_position, prices[i], i, timestamps[i],
                    stop_loss_pct, take_profit_pct
                )
                
                if exit_signal:
                    # Close position
                    open_position.exit_time = timestamps[i]
                    open_position.exit_price = prices[i]
                    open_position.status = 'CLOSED'
                    
                    # Calculate P&L
                    if open_position.side == 'LONG':
                        open_position.pnl = (prices[i] - open_position.entry_price) * open_position.position_size
                    else:
                        open_position.pnl = (open_position.entry_price - prices[i]) * open_position.position_size
                    
                    open_position.pnl_percent = (open_position.pnl / (open_position.entry_price * open_position.position_size)) * 100
                    
                    # Update capital
                    current_capital += open_position.pnl
                    equity_curve.append(current_capital)
                    
                    trades.append(open_position)
                    open_position = None
            
            # Check for entry conditions (only if no open position)
            if not open_position:
                entry_signal = self._check_entry_conditions(
                    rsi, macd, macd_signal, prices[i], volumes[i],
                    rsi_oversold, rsi_overbought, macd_signal_threshold
                )
                
                if entry_signal:
                    # Open new position
                    position_size = current_capital * position_size_pct / prices[i]
                    
                    if entry_signal == 'BUY':
                        side = 'LONG'
                        stop_loss = prices[i] * (1 - stop_loss_pct)
                        take_profit = prices[i] * (1 + take_profit_pct)
                    else:
                        side = 'SHORT'
                        stop_loss = prices[i] * (1 + stop_loss_pct)
                        take_profit = prices[i] * (1 - take_profit_pct)
                    
                    open_position = Trade(
                        entry_time=timestamps[i],
                        exit_time=None,
                        entry_price=prices[i],
                        exit_price=None,
                        position_size=position_size,
                        side=side,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
            
            # Update equity curve
            if not open_position:
                equity_curve.append(current_capital)
        
        # Close any remaining open position
        if open_position:
            open_position.exit_time = timestamps[-1]
            open_position.exit_price = prices[-1]
            open_position.status = 'CLOSED'
            
            if open_position.side == 'LONG':
                open_position.pnl = (prices[-1] - open_position.entry_price) * open_position.position_size
            else:
                open_position.pnl = (open_position.entry_price - prices[-1]) * open_position.position_size
            
            open_position.pnl_percent = (open_position.pnl / (open_position.entry_price * open_position.position_size)) * 100
            trades.append(open_position)
        
        return trades, equity_curve
    
    def _check_entry_conditions(self, rsi: float, macd: float, macd_signal: float,
                               price: float, volume: float, rsi_oversold: float,
                               rsi_overbought: float, macd_threshold: float) -> Optional[str]:
        """Check if entry conditions are met"""
        
        # RSI conditions
        rsi_buy = rsi < rsi_oversold
        rsi_sell = rsi > rsi_overbought
        
        # MACD conditions
        macd_buy = macd > macd_signal + macd_threshold
        macd_sell = macd < macd_signal - macd_threshold
        
        # Volume confirmation
        volume_confirm = volume > 1000  # Simple volume filter
        
        if rsi_buy and macd_buy and volume_confirm:
            return 'BUY'
        elif rsi_sell and macd_sell and volume_confirm:
            return 'SELL'
        
        return None
    
    def _check_exit_conditions(self, trade: Trade, current_price: float,
                              current_index: int, current_time: datetime,
                              stop_loss_pct: float, take_profit_pct: float) -> bool:
        """Check if position should be closed"""
        
        # Stop loss hit
        if trade.side == 'LONG' and current_price <= trade.stop_loss:
            trade.status = 'STOPPED_OUT'
            return True
        elif trade.side == 'SHORT' and current_price >= trade.stop_loss:
            trade.status = 'STOPPED_OUT'
            return True
        
        # Take profit hit
        if trade.side == 'LONG' and current_price >= trade.take_profit:
            trade.status = 'TAKE_PROFIT'
            return True
        elif trade.side == 'SHORT' and current_price <= trade.take_profit:
            trade.status = 'TAKE_PROFIT'
            return True
        
        # Time-based exit (optional)
        max_hold_time = timedelta(hours=24)  # 24 hours max hold
        if current_time - trade.entry_time > max_hold_time:
            trade.status = 'TIME_EXIT'
            return True
        
        return False
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI for the given prices"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calculate MACD and signal line"""
        if len(prices) < slow + signal:
            return 0.0, 0.0
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        macd_values = []
        for i in range(slow, len(prices)):
            macd_values.append(self._calculate_ema(prices[:i+1], fast) - self._calculate_ema(prices[:i+1], slow))
        
        if len(macd_values) >= signal:
            signal_line = self._calculate_ema(macd_values, signal)
        else:
            signal_line = macd_line
        
        return macd_line, signal_line
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_performance_metrics(self, trades: List[Trade], 
                                     equity_curve: List[float], 
                                     initial_capital: float) -> BacktestResult:
        """Calculate comprehensive performance metrics"""
        
        if not trades:
            return BacktestResult(
                total_trades=0, winning_trades=0, losing_trades=0,
                win_rate=0.0, total_pnl=0.0, total_pnl_percent=0.0,
                max_drawdown=0.0, max_drawdown_percent=0.0,
                sharpe_ratio=0.0, profit_factor=0.0, average_trade=0.0,
                best_trade=0.0, worst_trade=0.0, trades=[], equity_curve=equity_curve,
                drawdown_curve=[]
            )
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl and t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl and t.pnl < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # P&L metrics
        total_pnl = sum([t.pnl for t in trades if t.pnl])
        total_pnl_percent = (total_pnl / initial_capital) * 100
        
        # Trade analysis
        pnls = [t.pnl for t in trades if t.pnl]
        if pnls:
            best_trade = max(pnls)
            worst_trade = min(pnls)
            average_trade = np.mean(pnls)
        else:
            best_trade = worst_trade = average_trade = 0.0
        
        # Drawdown analysis
        drawdown_curve = self._calculate_drawdown_curve(equity_curve)
        max_drawdown = min(drawdown_curve) if drawdown_curve else 0.0
        max_drawdown_percent = (max_drawdown / max(equity_curve)) * 100 if equity_curve else 0.0
        
        # Risk metrics
        sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
        profit_factor = self._calculate_profit_factor(trades)
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            average_trade=average_trade,
            best_trade=best_trade,
            worst_trade=worst_trade,
            trades=trades,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve
        )
    
    def _calculate_drawdown_curve(self, equity_curve: List[float]) -> List[float]:
        """Calculate drawdown curve"""
        if not equity_curve:
            return []
        
        peak = equity_curve[0]
        drawdown_curve = []
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak
            drawdown_curve.append(drawdown)
        
        return drawdown_curve
    
    def _calculate_sharpe_ratio(self, equity_curve: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = np.diff(equity_curve) / equity_curve[:-1]
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if len(excess_returns) == 0 or np.std(excess_returns) == 0:
            return 0.0
        
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return sharpe
    
    def _calculate_profit_factor(self, trades: List[Trade]) -> float:
        """Calculate profit factor"""
        gross_profit = sum([t.pnl for t in trades if t.pnl and t.pnl > 0])
        gross_loss = abs(sum([t.pnl for t in trades if t.pnl and t.pnl < 0]))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    def optimize_strategy_parameters(self, historical_data: Dict, 
                                   param_ranges: Dict) -> Dict:
        """Optimize strategy parameters using grid search"""
        
        best_params = {}
        best_sharpe = -999
        
        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_ranges)
        
        for params in param_combinations:
            try:
                # Run backtest with these parameters
                strategy_config = {
                    'initial_capital': 10000,
                    'position_size_pct': 0.1,
                    **params
                }
                
                result = self.run_backtest(strategy_config, historical_data)
                
                # Use Sharpe ratio as optimization metric
                if result.sharpe_ratio > best_sharpe:
                    best_sharpe = result.sharpe_ratio
                    best_params = params.copy()
                    best_params['sharpe_ratio'] = best_sharpe
                    best_params['win_rate'] = result.win_rate
                    best_params['profit_factor'] = result.profit_factor
                
            except Exception as e:
                self.logger.warning(f"Parameter combination failed: {e}")
                continue
        
        return best_params
    
    def _generate_param_combinations(self, param_ranges: Dict) -> List[Dict]:
        """Generate all possible parameter combinations"""
        import itertools
        
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        combinations = []
        for combo in itertools.product(*param_values):
            combinations.append(dict(zip(param_names, combo)))
        
        return combinations
    
    def generate_backtest_report(self, result: BacktestResult) -> Dict:
        """Generate a comprehensive backtest report"""
        
        return {
            'summary': {
                'total_trades': result.total_trades,
                'win_rate': f"{result.win_rate:.2%}",
                'total_return': f"{result.total_pnl_percent:.2f}%",
                'sharpe_ratio': f"{result.sharpe_ratio:.2f}",
                'max_drawdown': f"{result.max_drawdown_percent:.2f}%"
            },
            'performance': {
                'total_pnl': f"${result.total_pnl:.2f}",
                'average_trade': f"${result.average_trade:.2f}",
                'best_trade': f"${result.best_trade:.2f}",
                'worst_trade': f"${result.worst_trade:.2f}",
                'profit_factor': f"{result.profit_factor:.2f}"
            },
            'risk_metrics': {
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'max_drawdown_percent': result.max_drawdown_percent,
                'winning_trades': result.winning_trades,
                'losing_trades': result.losing_trades
            },
            'trade_analysis': {
                'trades': [
                    {
                        'entry_time': trade.entry_time.isoformat(),
                        'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                        'side': trade.side,
                        'entry_price': f"${trade.entry_price:.2f}",
                        'exit_price': f"${trade.exit_price:.2f}" if trade.exit_price else None,
                        'pnl': f"${trade.pnl:.2f}" if trade.pnl else None,
                        'status': trade.status
                    }
                    for trade in result.trades
                ]
            }
        }
