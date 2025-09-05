"""
Configuration settings for the AI Trading Signal Generator
"""

import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # API Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Data Source Configuration
    CACHE_DURATION_MINUTES: int = int(os.getenv("CACHE_DURATION_MINUTES", "5"))
    MAX_CACHE_SIZE: int = int(os.getenv("MAX_CACHE_SIZE", "100"))
    
    # ML Model Configuration
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "v1.0")
    FEATURE_LOOKBACK_DAYS: int = int(os.getenv("FEATURE_LOOKBACK_DAYS", "5"))
    
    # Trading Signal Configuration
    RSI_OVERSOLD_THRESHOLD: float = float(os.getenv("RSI_OVERSOLD_THRESHOLD", "30"))
    RSI_OVERBOUGHT_THRESHOLD: float = float(os.getenv("RSI_OVERBOUGHT_THRESHOLD", "70"))
    MACD_SIGNAL_THRESHOLD: float = float(os.getenv("MACD_SIGNAL_THRESHOLD", "0.001"))
    VOLUME_THRESHOLD: float = float(os.getenv("VOLUME_THRESHOLD", "1.5"))
    PRICE_CHANGE_THRESHOLD: float = float(os.getenv("PRICE_CHANGE_THRESHOLD", "0.02"))
    
    # Web Interface Configuration
    CHART_HEIGHT: int = int(os.getenv("CHART_HEIGHT", "400"))
    AUTO_REFRESH_INTERVAL: int = int(os.getenv("AUTO_REFRESH_INTERVAL", "300"))
    
    # Model Storage
    MODEL_DIR: str = os.getenv("MODEL_DIR", "models")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    @classmethod
    def get_model_path(cls, filename: str) -> str:
        """Get full path for model files"""
        return os.path.join(cls.MODEL_DIR, filename)
    
    @classmethod
    def get_data_path(cls, filename: str) -> str:
        """Get full path for data files"""
        return os.path.join(cls.DATA_DIR, filename)
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        os.makedirs(cls.MODEL_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)














