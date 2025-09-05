import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math
import logging
# from scipy import stats
# from scipy.optimize import minimize

class VolatilityForecastingService:
    """Enhanced volatility forecasting service for advanced risk management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.volatility_models = {
            'garch': 'GARCH(1,1) volatility model',
            'ewma': 'Exponentially Weighted Moving Average',
            'realized': 'Realized volatility estimator',
            'implied': 'Implied volatility from options',
            'regime': 'Regime-switching volatility model'
        }
        
        self.forecast_horizons = [1, 5, 10, 20, 30]  # Days ahead
        
    def forecast_volatility(self, prices: List[float], volumes: List[float] = None,
                          method: str = 'garch', horizon: int = 10) -> Dict:
        """Forecast volatility using multiple methods"""
        
        if len(prices) < 50:
            return {'error': 'Insufficient data for volatility forecasting'}
        
        try:
            # Calculate returns
            returns = np.diff(np.log(prices))
            
            # Get historical volatility
            historical_vol = self._calculate_historical_volatility(returns)
            
            # Generate forecasts based on method
            if method == 'garch':
                forecast = self._garch_forecast(returns, horizon)
            elif method == 'ewma':
                forecast = self._ewma_forecast(returns, horizon)
            elif method == 'realized':
                forecast = self._realized_volatility_forecast(returns, horizon)
            elif method == 'regime':
                forecast = self._regime_switching_forecast(returns, horizon)
            else:
                forecast = self._combined_forecast(returns, horizon)
            
            # Calculate volatility regime
            regime = self._classify_volatility_regime(historical_vol, forecast['forecast'])
            
            # Generate position sizing recommendations
            position_recommendations = self._generate_position_recommendations(
                historical_vol, forecast['forecast'], regime
            )
            
            # Risk metrics
            risk_metrics = self._calculate_risk_metrics(returns, forecast['forecast'])
            
            return {
                'method': method,
                'horizon_days': horizon,
                'historical_volatility': {
                    'daily': round(historical_vol * np.sqrt(252), 4),
                    'annualized': round(historical_vol * np.sqrt(252), 4),
                    'rolling_20d': round(np.std(returns[-20:]) * np.sqrt(252), 4)
                },
                'forecast': {
                    'volatility': round(forecast['forecast'], 4),
                    'confidence_interval': forecast['confidence_interval'],
                    'trend': forecast['trend']
                },
                'regime': regime,
                'position_recommendations': position_recommendations,
                'risk_metrics': risk_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Volatility forecasting failed: {e}")
            return {'error': str(e)}
    
    def _calculate_historical_volatility(self, returns: np.ndarray) -> float:
        """Calculate historical volatility"""
        return np.std(returns)
    
    def _garch_forecast(self, returns: np.ndarray, horizon: int) -> Dict:
        """GARCH(1,1) volatility forecast"""
        
        # Simple GARCH(1,1) implementation
        omega = 0.000001  # Constant
        alpha = 0.1       # ARCH parameter
        beta = 0.8        # GARCH parameter
        
        # Initialize variance
        variance = np.var(returns)
        variances = [variance]
        
        # GARCH recursion
        for i in range(1, len(returns)):
            new_variance = omega + alpha * returns[i-1]**2 + beta * variances[i-1]
            variances.append(new_variance)
        
        # Forecast
        last_variance = variances[-1]
        forecast_variance = omega / (1 - alpha - beta)  # Long-run variance
        
        # Confidence interval
        confidence_interval = [
            max(0, forecast_variance * 0.8),
            forecast_variance * 1.2
        ]
        
        # Trend
        recent_trend = np.mean(np.diff(variances[-10:])) if len(variances) > 10 else 0
        trend = 'INCREASING' if recent_trend > 0 else 'DECREASING' if recent_trend < 0 else 'STABLE'
        
        return {
            'forecast': np.sqrt(forecast_variance),
            'confidence_interval': [np.sqrt(ci) for ci in confidence_interval],
            'trend': trend,
            'model_params': {'omega': omega, 'alpha': alpha, 'beta': beta}
        }
    
    def _ewma_forecast(self, returns: np.ndarray, horizon: int) -> Dict:
        """Exponentially Weighted Moving Average volatility forecast"""
        
        # EWMA parameters
        lambda_param = 0.94  # Decay factor
        
        # Calculate EWMA variance
        variance = np.var(returns[:20])  # Initial variance
        ewma_variances = [variance]
        
        for i in range(1, len(returns)):
            new_variance = lambda_param * ewma_variances[i-1] + (1 - lambda_param) * returns[i-1]**2
            ewma_variances.append(new_variance)
        
        # Forecast (mean reversion to long-run average)
        long_run_variance = np.mean(ewma_variances)
        forecast_variance = ewma_variances[-1] * 0.9 + long_run_variance * 0.1
        
        # Confidence interval
        confidence_interval = [
            max(0, forecast_variance * 0.85),
            forecast_variance * 1.15
        ]
        
        # Trend
        recent_trend = np.mean(np.diff(ewma_variances[-10:])) if len(ewma_variances) > 10 else 0
        trend = 'INCREASING' if recent_trend > 0 else 'DECREASING' if recent_trend < 0 else 'STABLE'
        
        return {
            'forecast': np.sqrt(forecast_variance),
            'confidence_interval': [np.sqrt(ci) for ci in confidence_interval],
            'trend': trend,
            'model_params': {'lambda': lambda_param}
        }
    
    def _realized_volatility_forecast(self, returns: np.ndarray, horizon: int) -> Dict:
        """Realized volatility forecast using high-frequency data approximation"""
        
        # Use squared returns as realized volatility proxy
        realized_variances = returns**2
        
        # Rolling average
        window = min(20, len(realized_variances))
        rolling_variance = np.mean(realized_variances[-window:])
        
        # Forecast with mean reversion
        long_run_variance = np.mean(realized_variances)
        forecast_variance = rolling_variance * 0.8 + long_run_variance * 0.2
        
        # Confidence interval
        confidence_interval = [
            max(0, forecast_variance * 0.8),
            forecast_variance * 1.2
        ]
        
        # Trend
        recent_trend = np.mean(np.diff(realized_variances[-10:])) if len(realized_variances) > 10 else 0
        trend = 'INCREASING' if recent_trend > 0 else 'DECREASING' if recent_trend < 0 else 'STABLE'
        
        return {
            'forecast': np.sqrt(forecast_variance),
            'confidence_interval': [np.sqrt(ci) for ci in confidence_interval],
            'trend': trend,
            'model_params': {'window': window}
        }
    
    def _regime_switching_forecast(self, returns: np.ndarray, horizon: int) -> Dict:
        """Regime-switching volatility forecast"""
        
        # Simple regime detection
        rolling_vol = []
        window = 20
        
        for i in range(window, len(returns)):
            vol = np.std(returns[i-window:i])
            rolling_vol.append(vol)
        
        if len(rolling_vol) < 2:
            return self._ewma_forecast(returns, horizon)
        
        # Detect regime changes
        vol_changes = np.diff(rolling_vol)
        regime_threshold = np.std(vol_changes) * 1.5
        
        # Current regime
        current_regime = 'HIGH' if rolling_vol[-1] > np.mean(rolling_vol) + regime_threshold else \
                        'LOW' if rolling_vol[-1] < np.mean(rolling_vol) - regime_threshold else 'NORMAL'
        
        # Regime-specific forecast
        if current_regime == 'HIGH':
            # High volatility regime - expect mean reversion
            forecast_variance = rolling_vol[-1] * 0.7 + np.mean(rolling_vol) * 0.3
        elif current_regime == 'LOW':
            # Low volatility regime - expect increase
            forecast_variance = rolling_vol[-1] * 1.2 + np.mean(rolling_vol) * 0.1
        else:
            # Normal regime - slight mean reversion
            forecast_variance = rolling_vol[-1] * 0.9 + np.mean(rolling_vol) * 0.1
        
        # Confidence interval
        confidence_interval = [
            max(0, forecast_variance * 0.8),
            forecast_variance * 1.2
        ]
        
        return {
            'forecast': forecast_variance,
            'confidence_interval': confidence_interval,
            'trend': 'MEAN_REVERSION' if current_regime == 'HIGH' else 'INCREASING' if current_regime == 'LOW' else 'STABLE',
            'model_params': {'regime': current_regime, 'threshold': regime_threshold}
        }
    
    def _combined_forecast(self, returns: np.ndarray, horizon: int) -> Dict:
        """Combine multiple forecasting methods"""
        
        forecasts = []
        
        # Get forecasts from different methods
        methods = ['garch', 'ewma', 'realized']
        
        for method in methods:
            try:
                if method == 'garch':
                    forecast = self._garch_forecast(returns, horizon)
                elif method == 'ewma':
                    forecast = self._ewma_forecast(returns, horizon)
                elif method == 'realized':
                    forecast = self._realized_volatility_forecast(returns, horizon)
                
                forecasts.append(forecast['forecast'])
            except:
                continue
        
        if not forecasts:
            return self._ewma_forecast(returns, horizon)
        
        # Weighted average (give more weight to recent methods)
        weights = [0.5, 0.3, 0.2][:len(forecasts)]
        weights = np.array(weights) / sum(weights)
        
        combined_forecast = np.average(forecasts, weights=weights)
        
        # Confidence interval
        confidence_interval = [
            max(0, combined_forecast * 0.8),
            combined_forecast * 1.2
        ]
        
        return {
            'forecast': combined_forecast,
            'confidence_interval': confidence_interval,
            'trend': 'COMBINED',
            'model_params': {'methods': methods, 'weights': weights.tolist()}
        }
    
    def _classify_volatility_regime(self, historical_vol: float, forecast_vol: float) -> Dict:
        """Classify current volatility regime"""
        
        # Define regime thresholds
        low_threshold = 0.15
        high_threshold = 0.35
        
        if forecast_vol < low_threshold:
            regime = 'LOW'
            description = 'Low volatility - favorable for trend following'
            risk_level = 'LOW'
        elif forecast_vol > high_threshold:
            regime = 'HIGH'
            description = 'High volatility - increased risk, reduce position size'
            risk_level = 'HIGH'
        else:
            regime = 'NORMAL'
            description = 'Normal volatility - standard trading conditions'
            risk_level = 'MEDIUM'
        
        # Regime change
        regime_change = 'INCREASING' if forecast_vol > historical_vol * 1.2 else \
                       'DECREASING' if forecast_vol < historical_vol * 0.8 else 'STABLE'
        
        return {
            'regime': regime,
            'description': description,
            'risk_level': risk_level,
            'regime_change': regime_change,
            'volatility_ratio': round(forecast_vol / historical_vol, 2)
        }
    
    def _generate_position_recommendations(self, historical_vol: float, 
                                         forecast_vol: float, regime: Dict) -> Dict:
        """Generate position sizing recommendations based on volatility"""
        
        # Base position size
        base_position = 1.0
        
        # Volatility adjustment
        vol_adjustment = historical_vol / forecast_vol if forecast_vol > 0 else 1.0
        vol_adjustment = np.clip(vol_adjustment, 0.5, 2.0)
        
        # Regime-specific adjustments
        if regime['regime'] == 'HIGH':
            position_multiplier = 0.5  # Reduce position size
            stop_loss_multiplier = 1.5  # Wider stops
            take_profit_multiplier = 1.2  # Closer targets
        elif regime['regime'] == 'LOW':
            position_multiplier = 1.5  # Increase position size
            stop_loss_multiplier = 0.8  # Tighter stops
            take_profit_multiplier = 1.5  # Further targets
        else:
            position_multiplier = 1.0  # Standard position size
            stop_loss_multiplier = 1.0  # Standard stops
            take_profit_multiplier = 1.0  # Standard targets
        
        # Final position size
        recommended_position = base_position * vol_adjustment * position_multiplier
        recommended_position = np.clip(recommended_position, 0.2, 2.0)
        
        return {
            'position_size': round(recommended_position, 2),
            'position_multiplier': round(position_multiplier, 2),
            'volatility_adjustment': round(vol_adjustment, 2),
            'stop_loss_multiplier': round(stop_loss_multiplier, 2),
            'take_profit_multiplier': round(take_profit_multiplier, 2),
            'recommendation': self._get_position_recommendation(recommended_position, regime)
        }
    
    def _get_position_recommendation(self, position_size: float, regime: Dict) -> str:
        """Get human-readable position recommendation"""
        
        if position_size >= 1.5:
            return f"AGGRESSIVE - Use {position_size}x normal position size (Low volatility regime)"
        elif position_size >= 1.0:
            return f"STANDARD - Use normal position size (Normal volatility regime)"
        elif position_size >= 0.7:
            return f"CONSERVATIVE - Use {position_size}x normal position size (Moderate volatility)"
        else:
            return f"DEFENSIVE - Use {position_size}x normal position size (High volatility regime)"
    
    def _calculate_risk_metrics(self, returns: np.ndarray, forecast_vol: float) -> Dict:
        """Calculate comprehensive risk metrics"""
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5)  # 95% VaR
        var_99 = np.percentile(returns, 1)  # 99% VaR
        
        # Expected Shortfall (Conditional VaR)
        es_95 = np.mean(returns[returns <= var_95])
        es_99 = np.mean(returns[returns <= var_99])
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Volatility clustering
        volatility_clustering = self._calculate_volatility_clustering(returns)
        
        # Leverage effect
        leverage_effect = self._calculate_leverage_effect(returns)
        
        return {
            'var_95': round(var_95 * 100, 2),
            'var_99': round(var_99 * 100, 2),
            'expected_shortfall_95': round(es_95 * 100, 2),
            'expected_shortfall_99': round(es_99 * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'volatility_clustering': volatility_clustering,
            'leverage_effect': leverage_effect,
            'forecast_volatility': round(forecast_vol * 100, 2)
        }
    
    def _calculate_volatility_clustering(self, returns: np.ndarray) -> str:
        """Calculate volatility clustering (GARCH effects)"""
        
        if len(returns) < 20:
            return 'INSUFFICIENT_DATA'
        
        # Calculate squared returns
        squared_returns = returns**2
        
        # Autocorrelation of squared returns
        autocorr = np.corrcoef(squared_returns[:-1], squared_returns[1:])[0, 1]
        
        if autocorr > 0.3:
            return 'HIGH_CLUSTERING'
        elif autocorr > 0.1:
            return 'MODERATE_CLUSTERING'
        else:
            return 'LOW_CLUSTERING'
    
    def _calculate_leverage_effect(self, returns: np.ndarray) -> str:
        """Calculate leverage effect (asymmetric volatility)"""
        
        if len(returns) < 20:
            return 'INSUFFICIENT_DATA'
        
        # Separate positive and negative returns
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        if len(positive_returns) == 0 or len(negative_returns) == 0:
            return 'NO_LEVERAGE_EFFECT'
        
        # Compare volatility
        pos_vol = np.std(positive_returns)
        neg_vol = np.std(negative_returns)
        
        leverage_ratio = neg_vol / pos_vol if pos_vol > 0 else 1.0
        
        if leverage_ratio > 1.5:
            return 'STRONG_LEVERAGE_EFFECT'
        elif leverage_ratio > 1.2:
            return 'MODERATE_LEVERAGE_EFFECT'
        else:
            return 'WEAK_LEVERAGE_EFFECT'
    
    def generate_volatility_report(self, symbol: str, forecast_data: Dict) -> Dict:
        """Generate a comprehensive volatility report"""
        
        return {
            'symbol': symbol,
            'summary': {
                'current_regime': forecast_data['regime']['regime'],
                'forecast_volatility': f"{forecast_data['forecast']['volatility']:.2%}",
                'regime_change': forecast_data['regime']['regime_change'],
                'risk_level': forecast_data['regime']['risk_level']
            },
            'forecasting': {
                'method': forecast_data['method'],
                'horizon': f"{forecast_data['horizon_days']} days",
                'confidence_interval': [
                    f"{ci:.2%}" for ci in forecast_data['forecast']['confidence_interval']
                ],
                'trend': forecast_data['forecast']['trend']
            },
            'position_sizing': {
                'recommended_size': forecast_data['position_recommendations']['position_size'],
                'recommendation': forecast_data['position_recommendations']['recommendation'],
                'stop_loss_adjustment': forecast_data['position_recommendations']['stop_loss_multiplier'],
                'take_profit_adjustment': forecast_data['position_recommendations']['take_profit_multiplier']
            },
            'risk_analysis': {
                'var_95': f"{forecast_data['risk_metrics']['var_95']:.2f}%",
                'max_drawdown': f"{forecast_data['risk_metrics']['max_drawdown']:.2f}%",
                'volatility_clustering': forecast_data['risk_metrics']['volatility_clustering'],
                'leverage_effect': forecast_data['risk_metrics']['leverage_effect']
            },
            'timestamp': forecast_data['timestamp']
        }
