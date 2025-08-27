import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path

class MLService:
    """Machine Learning service for predicting trading signals"""
    
    def __init__(self):
        self.model_version = "v1.0-mock"
        self.features = [
            'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'BB_Upper', 'BB_Lower', 'BB_Middle', 'BB_Width',
            'SMA_20', 'EMA_12', 'Volume_MA', 'Price_Change',
            'Volume_Change', 'Volatility'
        ]
        print("Using mock ML service - scikit-learn not available")
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        features_df = pd.DataFrame()
        
        # Basic technical indicators
        features_df['RSI'] = data.get('RSI', 50)
        features_df['MACD'] = data.get('MACD', 0)
        features_df['MACD_Signal'] = data.get('MACD_Signal', 0)
        features_df['MACD_Histogram'] = data.get('MACD_Histogram', 0)
        
        # Bollinger Bands
        features_df['BB_Upper'] = data.get('BB_Upper', data['Close'])
        features_df['BB_Lower'] = data.get('BB_Lower', data['Close'])
        features_df['BB_Middle'] = data.get('BB_Middle', data['Close'])
        features_df['BB_Width'] = (features_df['BB_Upper'] - features_df['BB_Lower']) / features_df['BB_Middle']
        
        # Moving Averages
        features_df['SMA_20'] = data.get('SMA_20', data['Close'])
        features_df['EMA_12'] = data.get('EMA_12', data['Close'])
        
        # Volume indicators
        features_df['Volume_MA'] = data.get('Volume_MA', data['Volume'])
        features_df['Volume_Change'] = data['Volume'].pct_change()
        
        # Price indicators
        features_df['Price_Change'] = data['Close'].pct_change()
        features_df['Volatility'] = data['Close'].rolling(20).std()
        
        # Fill NaN values
        features_df = features_df.fillna(0)
        
        return features_df
    
    def predict_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Predict trading signals using mock ML model"""
        try:
            # Prepare features for prediction
            features_df = self.prepare_features(data)
            
            if features_df.empty:
                return self._default_prediction()
            
            # Get latest features
            latest_features = features_df.iloc[-1]
            
            # Simple mock prediction based on RSI and MACD
            rsi = latest_features.get('RSI', 50)
            macd = latest_features.get('MACD', 0)
            macd_signal = latest_features.get('MACD_Signal', 0)
            
            # Mock prediction logic
            if rsi < 30 and macd > macd_signal:
                signal_probability = 0.8  # Strong buy
            elif rsi > 70 and macd < macd_signal:
                signal_probability = 0.2  # Strong sell
            else:
                signal_probability = 0.5  # Neutral
            
            # Calculate mock confidence based on indicator strength
            confidence = min(abs(rsi - 50) / 50 + abs(macd - macd_signal) / 0.01, 0.9)
            
            return {
                'signal_probability': float(signal_probability),
                'confidence_score': float(confidence),
                'model_version': self.model_version,
                'features_used': self.features,
                'prediction': 1 if signal_probability > 0.6 else 0,
                'prediction_proba': [1 - signal_probability, signal_probability]
            }
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return self._default_prediction()
    
    def _default_prediction(self) -> Dict[str, Any]:
        """Return default prediction when model is not available"""
        return {
            'signal_probability': 0.5,
            'confidence_score': 0.5,
            'model_version': self.model_version,
            'features_used': self.features,
            'prediction': 0,
            'prediction_proba': [0.5, 0.5]
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get mock feature importance"""
        return {
            'RSI': 0.3,
            'MACD': 0.25,
            'Bollinger_Bands': 0.2,
            'Moving_Averages': 0.15,
            'Volume': 0.1
        }
    
    def train_model(self, data: pd.DataFrame):
        """Mock training method"""
        print("Mock ML model training completed (no actual training)")
    
    def retrain_model(self, data: pd.DataFrame):
        """Mock retraining method"""
        print("Mock ML model retraining completed (no actual training)")

