import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import sys
import os

# Add project root to sys.path for src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.feature_engineering.feature_engineer import FeatureEngineer
from src.signal_generation.signal_generator import SignalGenerator

# Generate sample market data
np.random.seed(42)
dates = pd.date_range(start=datetime(2024, 6, 1, tzinfo=timezone.utc), periods=30, freq='D')
base_price = 100.0
market_rows = []
for i, date in enumerate(dates):
    open_price = base_price if i == 0 else market_rows[-1]['close']
    change = np.random.normal(0, 0.02)
    close_price = open_price * (1 + change)
    high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
    low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))
    volume = int(np.random.lognormal(10, 0.5))
    market_rows.append({
        'timestamp': date,
        'symbol': 'AAPL',
        'open': round(open_price, 2),
        'high': round(high_price, 2),
        'low': round(low_price, 2),
        'close': round(close_price, 2),
        'volume': volume
    })
market_df = pd.DataFrame(market_rows)

# Generate sample alternative data (Reddit, News, X)
alt_rows = []
sources = ['reddit', 'news', 'twitter']
for date in dates:
    for src in sources:
        for _ in range(np.random.randint(1, 4)):
            sentiment_score = np.random.uniform(-1, 1)
            # 80% chance to mention AAPL, 20% to mention something else
            if np.random.rand() < 0.8:
                entities = ['AAPL']
            else:
                entities = ['TSLA']
            alt_rows.append({
                'timestamp': date + timedelta(hours=np.random.randint(0, 24)),
                'source': src,
                'sentiment_score': round(sentiment_score, 3),
                'entities': entities,
                'text': f"Sample {src} post about {entities[0]}"
            })
alt_df = pd.DataFrame(alt_rows)

# Run feature engineering
fe = FeatureEngineer()
features = fe.generate_features(market_df, alt_df, symbol='AAPL', date='2024-06-01')

# Run signal generation
sg = SignalGenerator()
signals = sg.generate_signals('AAPL', '2024-06-01')

# Print a sample of the resulting signals
cols = [c for c in signals.columns if 'signal' in c or c == 'timestamp' or c == 'combined_signal' or c == 'signal_action']
print(signals[cols].head(10).to_string(index=False)) 