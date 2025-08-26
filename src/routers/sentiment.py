from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import requests
import json
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.database import get_db, SentimentData

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()

@router.get("/{symbol}")
async def get_sentiment_analysis(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive sentiment analysis for a symbol"""
    try:
        # Get news sentiment
        news_sentiment = await analyze_news_sentiment(symbol)
        
        # Get social media sentiment (simulated)
        social_sentiment = await analyze_social_sentiment(symbol)
        
        # Get fear/greed index
        fear_greed = await get_fear_greed_index()
        
        # Calculate overall sentiment
        overall_sentiment = calculate_overall_sentiment(
            news_sentiment, social_sentiment, fear_greed
        )
        
        # Store in database
        sentiment_data = SentimentData(
            symbol=symbol,
            news_sentiment=news_sentiment['score'],
            social_sentiment=social_sentiment['score'],
            fear_greed_index=fear_greed['value'],
            overall_sentiment=overall_sentiment['score'],
            news_count=news_sentiment['count']
        )
        db.add(sentiment_data)
        db.commit()
        
        return {
            "symbol": symbol,
            "news_sentiment": news_sentiment,
            "social_sentiment": social_sentiment,
            "fear_greed_index": fear_greed,
            "overall_sentiment": overall_sentiment,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.get("/{symbol}/news")
async def get_news_sentiment(symbol: str):
    """Get news sentiment analysis for a symbol"""
    try:
        return await analyze_news_sentiment(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news sentiment: {str(e)}")

@router.get("/{symbol}/social")
async def get_social_sentiment(symbol: str):
    """Get social media sentiment analysis for a symbol"""
    try:
        return await analyze_social_sentiment(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching social sentiment: {str(e)}")

@router.get("/market/fear-greed")
async def get_market_fear_greed():
    """Get market fear and greed index"""
    try:
        return await get_fear_greed_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fear/greed index: {str(e)}")

async def analyze_news_sentiment(symbol: str) -> dict:
    """Analyze news sentiment for a symbol"""
    try:
        # Simulate news sentiment analysis
        # In a real implementation, you would use news APIs like NewsAPI, Alpha Vantage, etc.
        
        # Simulated news headlines and sentiment scores
        simulated_news = [
            f"{symbol} reports strong quarterly earnings",
            f"Analysts upgrade {symbol} stock rating",
            f"{symbol} announces new product launch",
            f"Market volatility affects {symbol} performance",
            f"{symbol} expands into new markets"
        ]
        
        # Calculate sentiment scores using VADER
        sentiments = []
        for headline in simulated_news:
            sentiment = vader_analyzer.polarity_scores(headline)
            sentiments.append(sentiment['compound'])
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Categorize sentiment
        if avg_sentiment >= 0.05:
            sentiment_category = "POSITIVE"
        elif avg_sentiment <= -0.05:
            sentiment_category = "NEGATIVE"
        else:
            sentiment_category = "NEUTRAL"
        
        return {
            "score": round(avg_sentiment, 3),
            "category": sentiment_category,
            "count": len(simulated_news),
            "headlines": simulated_news,
            "sentiments": [round(s, 3) for s in sentiments]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing news sentiment: {e}")
        return {
            "score": 0,
            "category": "NEUTRAL",
            "count": 0,
            "headlines": [],
            "sentiments": []
        }

async def analyze_social_sentiment(symbol: str) -> dict:
    """Analyze social media sentiment for a symbol"""
    try:
        # Simulate social media sentiment analysis
        # In a real implementation, you would use Twitter API, Reddit API, etc.
        
        # Simulated social media posts
        simulated_posts = [
            f"Just bought more {symbol} stock! 🚀",
            f"{symbol} looking bullish today",
            f"Not sure about {symbol} right now",
            f"{symbol} earnings call was impressive",
            f"Market sentiment for {symbol} seems mixed"
        ]
        
        # Calculate sentiment scores using TextBlob
        sentiments = []
        for post in simulated_posts:
            blob = TextBlob(post)
            sentiment = blob.sentiment.polarity
            sentiments.append(sentiment)
        
        # Calculate average sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Categorize sentiment
        if avg_sentiment >= 0.1:
            sentiment_category = "POSITIVE"
        elif avg_sentiment <= -0.1:
            sentiment_category = "NEGATIVE"
        else:
            sentiment_category = "NEUTRAL"
        
        return {
            "score": round(avg_sentiment, 3),
            "category": sentiment_category,
            "count": len(simulated_posts),
            "posts": simulated_posts,
            "sentiments": [round(s, 3) for s in sentiments]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing social sentiment: {e}")
        return {
            "score": 0,
            "category": "NEUTRAL",
            "count": 0,
            "posts": [],
            "sentiments": []
        }

async def get_fear_greed_index() -> dict:
    """Get market fear and greed index"""
    try:
        # Simulate fear/greed index
        # In a real implementation, you would use CNN Fear & Greed API or similar
        
        # Simulate market conditions
        import random
        random.seed(datetime.now().day)  # Consistent for the day
        
        # Simulate different market conditions
        market_conditions = [
            "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"
        ]
        
        # Simulate values based on market conditions
        condition = random.choice(market_conditions)
        
        if condition == "Extreme Fear":
            value = random.randint(0, 25)
        elif condition == "Fear":
            value = random.randint(26, 45)
        elif condition == "Neutral":
            value = random.randint(46, 55)
        elif condition == "Greed":
            value = random.randint(56, 75)
        else:  # Extreme Greed
            value = random.randint(76, 100)
        
        # Get market indicators
        indicators = {
            "volatility": random.randint(20, 80),
            "market_momentum": random.randint(20, 80),
            "stock_price_strength": random.randint(20, 80),
            "stock_price_breadth": random.randint(20, 80),
            "put_call_ratio": random.randint(20, 80),
            "market_volatility": random.randint(20, 80),
            "safe_haven_demand": random.randint(20, 80)
        }
        
        return {
            "value": value,
            "category": condition,
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "description": f"Market sentiment shows {condition.lower()} with a value of {value}"
        }
        
    except Exception as e:
        logger.error(f"Error fetching fear/greed index: {e}")
        return {
            "value": 50,
            "category": "Neutral",
            "timestamp": datetime.now().isoformat(),
            "indicators": {},
            "description": "Unable to fetch fear/greed index"
        }

def calculate_overall_sentiment(news_sentiment: dict, social_sentiment: dict, fear_greed: dict) -> dict:
    """Calculate overall sentiment score"""
    try:
        # Normalize scores to 0-100 scale
        news_score = (news_sentiment['score'] + 1) * 50  # Convert from -1,1 to 0,100
        social_score = (social_sentiment['score'] + 1) * 50  # Convert from -1,1 to 0,100
        fear_greed_score = fear_greed['value']  # Already 0-100
        
        # Weighted average (news: 40%, social: 30%, fear/greed: 30%)
        overall_score = (news_score * 0.4) + (social_score * 0.3) + (fear_greed_score * 0.3)
        
        # Categorize overall sentiment
        if overall_score >= 70:
            category = "VERY_BULLISH"
        elif overall_score >= 60:
            category = "BULLISH"
        elif overall_score >= 40:
            category = "NEUTRAL"
        elif overall_score >= 30:
            category = "BEARISH"
        else:
            category = "VERY_BEARISH"
        
        return {
            "score": round(overall_score, 1),
            "category": category,
            "components": {
                "news": round(news_score, 1),
                "social": round(social_score, 1),
                "fear_greed": round(fear_greed_score, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating overall sentiment: {e}")
        return {
            "score": 50,
            "category": "NEUTRAL",
            "components": {
                "news": 50,
                "social": 50,
                "fear_greed": 50
            }
        }

@router.get("/{symbol}/trend")
async def get_sentiment_trend(
    symbol: str,
    days: int = Query(7, description="Number of days to analyze")
):
    """Get sentiment trend over time"""
    try:
        # Simulate sentiment trend data
        trend_data = []
        base_date = datetime.now()
        
        for i in range(days):
            date = base_date - timedelta(days=i)
            
            # Simulate daily sentiment variation
            import random
            random.seed(date.day)
            
            news_sentiment = random.uniform(-0.5, 0.5)
            social_sentiment = random.uniform(-0.5, 0.5)
            fear_greed = random.randint(20, 80)
            
            overall = calculate_overall_sentiment(
                {"score": news_sentiment, "count": 5},
                {"score": social_sentiment, "count": 5},
                {"value": fear_greed, "category": "Neutral"}
            )
            
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "news_sentiment": round(news_sentiment, 3),
                "social_sentiment": round(social_sentiment, 3),
                "fear_greed": fear_greed,
                "overall_sentiment": overall['score']
            })
        
        # Reverse to show oldest first
        trend_data.reverse()
        
        return {
            "symbol": symbol,
            "period_days": days,
            "trend_data": trend_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sentiment trend: {str(e)}")

