import pandas as pd
import numpy as np
import ta
from typing import Dict, Any

class TechnicalIndicators:
    """Utility class for calculating technical analysis indicators"""
    
    def __init__(self):
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        self.sma_periods = [20, 50, 200]
        self.ema_periods = [12, 26]
    
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for the given data"""
        if data.empty:
            return data
        
        # Create a copy to avoid modifying original data
        df = data.copy()
        
        # Calculate RSI
        df = self._calculate_rsi(df)
        
        # Calculate MACD
        df = self._calculate_macd(df)
        
        # Calculate Bollinger Bands
        df = self._calculate_bollinger_bands(df)
        
        # Calculate Moving Averages
        df = self._calculate_moving_averages(df)
        
        # Calculate Volume Indicators
        df = self._calculate_volume_indicators(df)
        
        # Calculate Additional Indicators
        df = self._calculate_additional_indicators(df)
        
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        try:
            df['RSI'] = ta.momentum.RSIIndicator(
                close=df['Close'], 
                window=self.rsi_period
            ).rsi()
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            df['RSI'] = 50  # Default neutral value
        
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            macd_indicator = ta.trend.MACD(
                close=df['Close'],
                window_fast=self.macd_fast,
                window_slow=self.macd_slow,
                window_sign=self.macd_signal
            )
            
            df['MACD'] = macd_indicator.macd()
            df['MACD_Signal'] = macd_indicator.macd_signal()
            df['MACD_Histogram'] = macd_indicator.macd_diff()
            
        except Exception as e:
            print(f"Error calculating MACD: {e}")
            df['MACD'] = 0
            df['MACD_Signal'] = 0
            df['MACD_Histogram'] = 0
        
        return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        try:
            bb_indicator = ta.volatility.BollingerBands(
                close=df['Close'],
                window=self.bb_period,
                window_dev=self.bb_std
            )
            
            df['BB_Upper'] = bb_indicator.bollinger_hband()
            df['BB_Middle'] = bb_indicator.bollinger_mavg()
            df['BB_Lower'] = bb_indicator.bollinger_lband()
            # Safe division for BB_Width to avoid NaN
            bb_upper = df['BB_Upper']
            bb_lower = df['BB_Lower']
            bb_middle = df['BB_Middle']
            
            # Avoid division by zero or very small numbers
            safe_bb_middle = np.where(np.abs(bb_middle) < 0.0001, 1.0, bb_middle)
            df['BB_Width'] = np.where(
                (bb_upper - bb_lower) > 0,
                (bb_upper - bb_lower) / safe_bb_middle,
                0
            )
            # Safe division for BB_Position to avoid NaN
            bb_upper = df['BB_Upper']
            bb_lower = df['BB_Lower']
            bb_range = bb_upper - bb_lower
            
            # Avoid division by zero
            df['BB_Position'] = np.where(
                bb_range > 0.0001,
                (df['Close'] - bb_lower) / bb_range,
                0.5  # Default to middle when range is too small
            )
            
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {e}")
            df['BB_Upper'] = df['Close']
            df['BB_Middle'] = df['Close']
            df['BB_Lower'] = df['Close']
            df['BB_Width'] = 0
            df['BB_Position'] = 0.5
        
        return df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Simple and Exponential Moving Averages"""
        try:
            # Simple Moving Averages
            for period in self.sma_periods:
                df[f'SMA_{period}'] = ta.trend.SMAIndicator(
                    close=df['Close'], 
                    window=period
                ).sma_indicator()
            
            # Exponential Moving Averages
            for period in self.ema_periods:
                df[f'EMA_{period}'] = ta.trend.EMAIndicator(
                    close=df['Close'], 
                    window=period
                ).ema_indicator()
            
            # Moving Average Crossovers
            if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
                df['SMA_20_50_Cross'] = np.where(
                    df['SMA_20'] > df['SMA_50'], 1, -1
                )
            
            if 'EMA_12' in df.columns and 'EMA_26' in df.columns:
                df['EMA_12_26_Cross'] = np.where(
                    df['EMA_12'] > df['EMA_26'], 1, -1
                )
                
        except Exception as e:
            print(f"Error calculating Moving Averages: {e}")
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        try:
            # Volume Moving Average
            df['Volume_MA'] = ta.volume.VolumeWeightedAveragePrice(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                volume=df['Volume']
            ).volume_weighted_average_price()
            
            # On-Balance Volume (OBV)
            df['OBV'] = ta.volume.OnBalanceVolumeIndicator(
                close=df['Close'],
                volume=df['Volume']
            ).on_balance_volume()
            
            # Volume Rate of Change (using simple calculation instead)
            df['Volume_ROC'] = df['Volume'].pct_change(periods=20) * 100
            
            # Money Flow Index
            df['MFI'] = ta.volume.MFIIndicator(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                volume=df['Volume'],
                window=14
            ).money_flow_index()
            
        except Exception as e:
            print(f"Error calculating Volume Indicators: {e}")
            df['Volume_MA'] = df['Volume']
            df['OBV'] = 0
            df['Volume_ROC'] = 0
            df['MFI'] = 50
        
        return df
    
    def _calculate_additional_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional technical indicators"""
        try:
            # Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                window=14,
                smooth_window=3
            )
            df['Stoch_K'] = stoch.stoch()
            df['Stoch_D'] = stoch.stoch_signal()
            
            # Williams %R
            df['Williams_R'] = ta.momentum.WilliamsRIndicator(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                lbp=14
            ).williams_r()
            
            # Average True Range (ATR)
            df['ATR'] = ta.volatility.AverageTrueRange(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                window=14
            ).average_true_range()
            
            # Commodity Channel Index (CCI)
            df['CCI'] = ta.trend.CCIIndicator(
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                window=20
            ).cci()
            
            # Price Rate of Change
            df['Price_ROC'] = ta.momentum.ROCIndicator(
                close=df['Close'],
                window=12
            ).roc()
            
        except Exception as e:
            print(f"Error calculating Additional Indicators: {e}")
            df['Stoch_K'] = 50
            df['Stoch_D'] = 50
            df['Williams_R'] = -50
            df['ATR'] = 0
            df['CCI'] = 0
            df['Price_ROC'] = 0
        
        return df
    
    def get_indicator_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get a summary of current indicator values"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        
        summary = {
            'rsi': float(latest.get('RSI', 50)),
            'macd': {
                'macd': float(latest.get('MACD', 0)),
                'signal': float(latest.get('MACD_Signal', 0)),
                'histogram': float(latest.get('MACD_Histogram', 0))
            },
            'bollinger_bands': {
                'upper': float(latest.get('BB_Upper', latest['Close'])),
                'middle': float(latest.get('BB_Middle', latest['Close'])),
                'lower': float(latest.get('BB_Lower', latest['Close'])),
                'width': float(latest.get('BB_Width', 0)),
                'position': float(latest.get('BB_Position', 0.5))
            },
            'moving_averages': {
                'sma_20': float(latest.get('SMA_20', latest['Close'])),
                'sma_50': float(latest.get('SMA_50', latest['Close'])),
                'ema_12': float(latest.get('EMA_12', latest['Close'])),
                'ema_26': float(latest.get('EMA_26', latest['Close']))
            },
            'volume_indicators': {
                'volume_ma': float(latest.get('Volume_MA', latest['Volume'])),
                'obv': float(latest.get('OBV', 0)),
                'mfi': float(latest.get('MFI', 50))
            }
        }
        
        return summary
    
    def get_signal_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate signal strength for various indicators"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        
        signals = {}
        
        # RSI Signal Strength
        rsi = latest.get('RSI', 50)
        if rsi < 30:
            signals['rsi'] = 0.9  # Strong buy
        elif rsi > 70:
            signals['rsi'] = -0.9  # Strong sell
        else:
            # Safe division to avoid NaN
            rsi_diff = 50 - rsi
            signals['rsi'] = (rsi_diff / 50) * 0.5 if rsi != 50 else 0  # Neutral to moderate
        
        # MACD Signal Strength
        macd = latest.get('MACD', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        if macd > macd_signal:
            # Safe division to avoid NaN
            macd_diff = macd - macd_signal
            signals['macd'] = min(macd_diff / 0.01, 1.0) if abs(macd_diff) > 0.0001 else 0  # Buy strength
        else:
            # Safe division to avoid NaN
            macd_diff = macd_signal - macd
            signals['macd'] = max(-macd_diff / 0.01, -1.0) if abs(macd_diff) > 0.0001 else 0  # Sell strength
        
        # Bollinger Bands Signal Strength
        bb_position = latest.get('BB_Position', 0.5)
        if bb_position < 0.2:
            signals['bollinger'] = 0.8  # Strong buy
        elif bb_position > 0.8:
            signals['bollinger'] = -0.8  # Strong sell
        else:
            # Safe calculation to avoid NaN
            bb_diff = 0.5 - bb_position
            signals['bollinger'] = bb_diff * 1.6  # Neutral to moderate
        
        return signals




