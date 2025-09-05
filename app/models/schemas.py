from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class PeriodType(str, Enum):
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    MAX = "max"

class AnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to analyze")
    period: PeriodType = Field(default=PeriodType.ONE_YEAR, description="Time period for analysis")

class Signal(BaseModel):
    timestamp: str
    signal_type: SignalType
    price: float
    confidence: float
    reason: str
    indicators: Dict[str, Any]

class IndicatorSummary(BaseModel):
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    moving_averages: Dict[str, float]
    volume_indicators: Dict[str, float]

class MLPrediction(BaseModel):
    signal_probability: float
    confidence_score: float
    model_version: str
    features_used: List[str]

class AnalysisResponse(BaseModel):
    symbol: str
    signals: List[Signal]
    data: List[Dict[str, Any]]
    indicators: IndicatorSummary
    predictions: MLPrediction
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

class SignalResponse(BaseModel):
    symbol: str
    signals: List[Signal]
    last_updated: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)












