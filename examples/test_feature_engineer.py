import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import sys
import os

# Add project root to sys.path for src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.feature_engineering.feature_engineer import FeatureEngineer

# Generate sample market data with sentiment
np.random.seed(42)
dates = pd.date_range(start=datetime(2024, 6, 1, tzinfo=timezone.utc), periods=30, freq='D')
base_price = 100.0
rows = []
for i, date in enumerate(dates):
    open_price = base_price if i == 0 else rows[-1]['close']
    change = np.random.normal(0, 0.02)
    close_price = open_price * (1 + change)
    high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
    low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
    volume = int(np.random.lognormal(10, 0.5))
    sentiment_score = np.random.uniform(-1, 1)
    rows.append({
        'timestamp': date,
        'symbol': 'AAPL',
        'open': round(open_price, 2),
        'high': round(high_price, 2),
        'low': round(low_price, 2),
        'close': round(close_price, 2),
        'volume': volume,
        'sentiment_score': round(sentiment_score, 3)
    })
df = pd.DataFrame(rows)

# Run feature engineering
fe = FeatureEngineer()
features = fe.generate_features(df, symbol='AAPL', date='2024-06-01')

# Print a sample of the resulting features
to_show = ['timestamp', 'close', 'sma_20', 'ema_12', 'rsi_14', 'bb_upper', 'bb_lower', 'bb_position', 'sentiment_score', 'sentiment_ma_1h', 'sentiment_ma_1d', 'sentiment_volatility', 'hour', 'day_of_week', 'is_market_open']
print(features[to_show].head(10).to_string(index=False)) 