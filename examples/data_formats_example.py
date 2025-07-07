"""
Example script demonstrating data formats and utilities for EchoAlpha.

This script shows how to:
1. Create sample data in the correct formats
2. Use the data loading/saving utilities
3. Validate data against schemas
4. Work with different data types
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add src to path to import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.data_formats import DataLoader, DataFormatValidator, FileNamingConventions

def create_sample_market_data(symbol: str, start_date: datetime, days: int = 30) -> pd.DataFrame:
    """Create sample market data for testing."""
    
    # Generate date range
    dates = pd.date_range(start=start_date, periods=days, freq='D')
    
    # Create sample OHLCV data
    np.random.seed(42)  # For reproducible results
    base_price = 100.0
    
    data = []
    for i, date in enumerate(dates):
        # Generate realistic price movements
        if i == 0:
            open_price = base_price
        else:
            open_price = data[-1]['close']
        
        # Random price movement
        change = np.random.normal(0, 0.02)  # 2% daily volatility
        close_price = open_price * (1 + change)
        
        # Generate high/low from open/close
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
        
        # Generate volume
        volume = int(np.random.lognormal(10, 0.5))  # Realistic volume distribution
        
        data.append({
            'timestamp': date.replace(tzinfo=timezone.utc),
            'symbol': symbol,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': volume,
            'vwap': round((high_price + low_price + close_price) / 3, 2),
            'source': 'yahoo'
        })
    
    return pd.DataFrame(data)

def create_sample_reddit_data(subreddit: str, date: datetime, num_posts: int = 50) -> pd.DataFrame:
    """Create sample Reddit data for testing."""
    
    np.random.seed(42)
    
    # Sample titles and content
    sample_titles = [
        f"Thoughts on {subreddit.upper()}?",
        "Market analysis for today",
        "Technical indicators showing bullish signals",
        "Earnings report discussion",
        "Trading strategy question"
    ]
    
    sample_content = [
        "What do you think about the current market conditions?",
        "I've been following the technical analysis and it looks promising.",
        "The fundamentals seem strong for this sector.",
        "Any thoughts on the recent price action?",
        "Looking for advice on position sizing."
    ]
    
    data = []
    for i in range(num_posts):
        # Random timestamp within the day
        hour = np.random.randint(0, 24)
        minute = np.random.randint(0, 60)
        timestamp = date.replace(hour=hour, minute=minute, tzinfo=timezone.utc)
        
        data.append({
            'timestamp': timestamp,
            'subreddit': subreddit,
            'title': np.random.choice(sample_titles),
            'text': np.random.choice(sample_content),
            'score': np.random.randint(-10, 100),
            'num_comments': np.random.randint(0, 50),
            'author': f"user_{np.random.randint(1000, 9999)}",
            'url': f"https://reddit.com/r/{subreddit}/comments/{np.random.randint(100000, 999999)}",
            'sentiment_score': np.random.uniform(-1, 1),
            'entities': ['AAPL', 'TSLA', 'SPY'],  # Sample entities
            'source': 'reddit'
        })
    
    return pd.DataFrame(data)

def create_sample_feature_data(symbol: str, date: datetime, days: int = 30) -> pd.DataFrame:
    """Create sample feature data for testing."""
    
    # Generate date range
    dates = pd.date_range(start=date, periods=days, freq='D')
    
    np.random.seed(42)
    
    data = []
    for i, timestamp in enumerate(dates):
        # Technical indicators
        sma_20 = 100 + np.random.normal(0, 5)
        ema_12 = 100 + np.random.normal(0, 5)
        rsi_14 = np.random.uniform(20, 80)
        bb_upper = 105 + np.random.normal(0, 2)
        bb_lower = 95 + np.random.normal(0, 2)
        bb_position = np.random.uniform(0, 1)
        macd = np.random.normal(0, 1)
        macd_signal = macd + np.random.normal(0, 0.5)
        volume_sma = np.random.lognormal(10, 0.5)
        
        # Sentiment features
        sentiment_score = np.random.uniform(-1, 1)
        sentiment_ma_1h = sentiment_score + np.random.normal(0, 0.1)
        sentiment_ma_1d = sentiment_score + np.random.normal(0, 0.2)
        sentiment_volatility = np.random.uniform(0, 0.5)
        
        # Microstructure features
        bid_ask_spread = np.random.uniform(0.01, 0.1)
        order_imbalance = np.random.uniform(-1, 1)
        volume_profile = np.random.uniform(0, 1)
        
        # Time features
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        is_market_open = not is_weekend and 9 <= hour <= 16
        
        data.append({
            'timestamp': timestamp.replace(tzinfo=timezone.utc),
            'symbol': symbol,
            'sma_20': round(sma_20, 2),
            'ema_12': round(ema_12, 2),
            'rsi_14': round(rsi_14, 2),
            'bb_upper': round(bb_upper, 2),
            'bb_lower': round(bb_lower, 2),
            'bb_position': round(bb_position, 3),
            'macd': round(macd, 3),
            'macd_signal': round(macd_signal, 3),
            'volume_sma': round(volume_sma, 0),
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_ma_1h': round(sentiment_ma_1h, 3),
            'sentiment_ma_1d': round(sentiment_ma_1d, 3),
            'sentiment_volatility': round(sentiment_volatility, 3),
            'bid_ask_spread': round(bid_ask_spread, 3),
            'order_imbalance': round(order_imbalance, 3),
            'volume_profile': round(volume_profile, 3),
            'hour': hour,
            'day_of_week': day_of_week,
            'is_weekend': is_weekend,
            'is_market_open': is_market_open
        })
    
    return pd.DataFrame(data)

def demonstrate_data_formats():
    """Demonstrate the data formats and utilities."""
    
    print("=== EchoAlpha Data Formats Demonstration ===\n")
    
    # Initialize data loader
    data_loader = DataLoader()
    validator = DataFormatValidator()
    naming = FileNamingConventions()
    
    # Create sample data
    start_date = datetime(2024, 6, 1, tzinfo=timezone.utc)
    symbol = "AAPL"
    subreddit = "wallstreetbets"
    
    print("1. Creating sample market data...")
    market_data = create_sample_market_data(symbol, start_date, days=10)
    print(f"   Created {len(market_data)} market data records")
    print(f"   Columns: {list(market_data.columns)}")
    print(f"   Date range: {market_data['timestamp'].min()} to {market_data['timestamp'].max()}")
    
    print("\n2. Creating sample Reddit data...")
    reddit_data = create_sample_reddit_data(subreddit, start_date, num_posts=20)
    print(f"   Created {len(reddit_data)} Reddit posts")
    print(f"   Columns: {list(reddit_data.columns)}")
    
    print("\n3. Creating sample feature data...")
    feature_data = create_sample_feature_data(symbol, start_date, days=10)
    print(f"   Created {len(feature_data)} feature records")
    print(f"   Technical indicators: {[col for col in feature_data.columns if 'sma' in col or 'rsi' in col or 'macd' in col]}")
    print(f"   Sentiment features: {[col for col in feature_data.columns if 'sentiment' in col]}")
    
    # Validate data
    print("\n4. Validating data...")
    market_valid = validator.validate_market_data(market_data)
    feature_valid = validator.validate_feature_data(feature_data)
    
    print(f"   Market data validation: {'✓ PASS' if market_valid else '✗ FAIL'}")
    print(f"   Feature data validation: {'✓ PASS' if feature_valid else '✗ FAIL'}")
    
    # Demonstrate file naming
    print("\n5. File naming conventions...")
    market_filename = naming.get_market_data_filename(symbol, start_date)
    reddit_filename = naming.get_reddit_data_filename(subreddit, start_date)
    feature_filename = naming.get_feature_data_filename(symbol, start_date)
    
    print(f"   Market data: {market_filename}")
    print(f"   Reddit data: {reddit_filename}")
    print(f"   Feature data: {feature_filename}")
    
    # Save data (commented out to avoid creating files in example)
    print("\n6. Data saving (demonstration only)...")
    print("   To save data, uncomment the following lines:")
    print("   data_loader.save_market_data(market_data, symbol, start_date)")
    print("   data_loader.save_reddit_data(reddit_data, subreddit, start_date)")
    print("   data_loader.save_feature_data(feature_data, symbol, start_date)")
    
    # Show data samples
    print("\n7. Data samples...")
    print("\nMarket Data Sample:")
    print(market_data.head(3).to_string(index=False))
    
    print("\nReddit Data Sample:")
    print(reddit_data[['timestamp', 'title', 'sentiment_score', 'score']].head(3).to_string(index=False))
    
    print("\nFeature Data Sample:")
    feature_sample_cols = ['timestamp', 'sma_20', 'rsi_14', 'sentiment_score', 'is_market_open']
    print(feature_data[feature_sample_cols].head(3).to_string(index=False))
    
    print("\n=== Demonstration Complete ===")

if __name__ == "__main__":
    demonstrate_data_formats() 