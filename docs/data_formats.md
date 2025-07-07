# Data Formats Specification

## Overview
This document defines the data formats, file naming conventions, and storage structure for the EchoAlpha quant trading platform.

## Directory Structure
```
data/
├── raw/                    # Raw ingested data
│   ├── market/            # OHLCV, order book data
│   ├── alternative/       # Reddit, Twitter, news data
│   └── metadata/          # Symbol lists, calendar data
├── processed/             # Cleaned and feature-engineered data
│   ├── features/          # Technical indicators, sentiment features
│   ├── signals/           # Combined trading signals
│   └── targets/           # Price targets, labels for ML
├── signals/               # Final trading signals and decisions
├── logs/                  # System logs, trade logs, performance logs
└── models/                # Trained models, parameters, checkpoints
```

## 1. Raw Data Formats

### 1.1 Market Data (OHLCV)
**File Format:** Parquet (preferred) or CSV
**Naming Convention:** `{symbol}_{date}.parquet` or `{symbol}_{start_date}_{end_date}.parquet`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol (e.g., 'AAPL')
    'open': float64,              # Opening price
    'high': float64,              # High price
    'low': float64,               # Low price
    'close': float64,             # Closing price
    'volume': int64,              # Trading volume
    'vwap': float64,              # Volume-weighted average price (optional)
    'source': str                 # Data source (e.g., 'yahoo', 'alpaca')
}
```

**Example:** `AAPL_2024-06-01.parquet`

### 1.2 Alternative Data

#### Reddit Data
**File Format:** CSV or Parquet
**Naming Convention:** `reddit_{subreddit}_{date}.csv`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'subreddit': str,             # Subreddit name
    'title': str,                 # Post title
    'text': str,                  # Post text content
    'score': int64,               # Reddit score
    'num_comments': int64,        # Number of comments
    'author': str,                # Username
    'url': str,                   # Post URL
    'sentiment_score': float64,   # VADER sentiment score
    'entities': list,             # Extracted entities (tickers, companies)
    'source': str                 # Always 'reddit'
}
```

#### Twitter Data
**File Format:** CSV or Parquet
**Naming Convention:** `twitter_{date}.csv`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'tweet_id': str,              # Twitter tweet ID
    'text': str,                  # Tweet text
    'user_id': str,               # Twitter user ID
    'followers_count': int64,     # User follower count
    'retweet_count': int64,       # Retweet count
    'like_count': int64,          # Like count
    'sentiment_score': float64,   # VADER sentiment score
    'entities': list,             # Extracted entities
    'source': str                 # Always 'twitter'
}
```

#### News Data
**File Format:** CSV or Parquet
**Naming Convention:** `news_{source}_{date}.csv`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'headline': str,              # News headline
    'text': str,                  # Article text
    'source': str,                # News source (e.g., 'reuters', 'bloomberg')
    'url': str,                   # Article URL
    'sentiment_score': float64,   # VADER sentiment score
    'entities': list,             # Extracted entities
    'category': str               # News category (e.g., 'earnings', 'merger')
}
```

### 1.3 Order Book Data (if available)
**File Format:** Parquet
**Naming Convention:** `orderbook_{symbol}_{date}.parquet`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol
    'bid_price_1': float64,       # Best bid price
    'bid_size_1': int64,          # Best bid size
    'ask_price_1': float64,       # Best ask price
    'ask_size_1': int64,          # Best ask size
    'spread': float64,            # Bid-ask spread
    'mid_price': float64,         # Mid price
    'source': str                 # Data source
}
```

## 2. Processed Data Formats

### 2.1 Feature Data
**File Format:** Parquet
**Naming Convention:** `features_{symbol}_{date}.parquet`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol
    
    # Technical Indicators
    'sma_20': float64,            # 20-day simple moving average
    'ema_12': float64,            # 12-day exponential moving average
    'rsi_14': float64,            # 14-day RSI
    'bb_upper': float64,          # Bollinger Band upper
    'bb_lower': float64,          # Bollinger Band lower
    'bb_position': float64,       # Position within BB (0-1)
    'macd': float64,              # MACD line
    'macd_signal': float64,       # MACD signal line
    'volume_sma': float64,        # Volume SMA
    
    # Sentiment Features
    'sentiment_score': float64,   # VADER sentiment
    'sentiment_ma_1h': float64,   # 1-hour sentiment moving average
    'sentiment_ma_1d': float64,   # 1-day sentiment moving average
    'sentiment_volatility': float64, # Sentiment volatility
    
    # Microstructure Features (if available)
    'bid_ask_spread': float64,    # Bid-ask spread
    'order_imbalance': float64,   # Order book imbalance
    'volume_profile': float64,    # Volume profile indicator
    
    # Time Features
    'hour': int64,                # Hour of day (0-23)
    'day_of_week': int64,         # Day of week (0-6)
    'is_weekend': bool,           # Weekend flag
    'is_market_open': bool        # Market open flag
}
```

### 2.2 Signal Data
**File Format:** Parquet
**Naming Convention:** `signals_{symbol}_{date}.parquet`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol
    
    # Combined Signals
    'technical_signal': float64,  # Technical indicator signal (-1 to 1)
    'sentiment_signal': float64,  # Sentiment signal (-1 to 1)
    'microstructure_signal': float64, # Microstructure signal (-1 to 1)
    'combined_signal': float64,   # Weighted combination of all signals
    
    # Signal Components
    'momentum_score': float64,    # Momentum component
    'mean_reversion_score': float64, # Mean reversion component
    'trend_score': float64,       # Trend component
    
    # Signal Metadata
    'signal_strength': float64,   # Signal strength (0-1)
    'confidence': float64,        # Model confidence
    'regime': str                 # Market regime classification
}
```

## 3. Model Outputs

### 3.1 Trading Decisions
**File Format:** CSV or Parquet
**Naming Convention:** `decisions_{date}.csv`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol
    'action': str,                # 'BUY', 'SELL', 'HOLD'
    'position_size': float64,     # Position size (shares or % of portfolio)
    'entry_price': float64,       # Entry price
    'stop_loss': float64,         # Stop loss price
    'take_profit': float64,       # Take profit price
    'confidence': float64,        # Decision confidence
    'reason': str,                # Reason for decision
    'signal_strength': float64    # Signal strength
}
```

### 3.2 Performance Logs
**File Format:** CSV
**Naming Convention:** `performance_{date}.csv`

**Schema:**
```python
{
    'timestamp': datetime64[ns],  # UTC timestamp
    'symbol': str,                # Stock symbol
    'action': str,                # 'BUY', 'SELL', 'HOLD'
    'quantity': int64,            # Number of shares
    'price': float64,             # Execution price
    'commission': float64,        # Commission paid
    'slippage': float64,          # Slippage cost
    'pnl': float64,               # Realized P&L
    'cumulative_pnl': float64,    # Cumulative P&L
    'portfolio_value': float64,   # Total portfolio value
    'drawdown': float64           # Current drawdown
}
```

## 4. Configuration and Metadata

### 4.1 Symbol Universe
**File Format:** CSV
**File:** `data/raw/metadata/symbols.csv`

**Schema:**
```python
{
    'symbol': str,                # Stock symbol
    'name': str,                  # Company name
    'sector': str,                # Sector
    'market_cap': float64,        # Market capitalization
    'avg_volume': int64,          # Average daily volume
    'is_active': bool,            # Active trading flag
    'added_date': datetime64[ns], # Date added to universe
    'removed_date': datetime64[ns] # Date removed (if applicable)
}
```

### 4.2 Model Parameters
**File Format:** YAML or JSON
**File:** `data/models/model_config_{version}.yaml`

**Schema:**
```yaml
model_version: "v1.0.0"
training_date: "2024-06-01"
parameters:
  technical_weights:
    momentum: 0.3
    mean_reversion: 0.4
    trend: 0.3
  sentiment_weights:
    vader: 0.6
    news: 0.4
  risk_parameters:
    max_position_size: 0.05
    stop_loss: 0.02
    max_drawdown: 0.15
performance_metrics:
  sharpe_ratio: 1.85
  max_drawdown: 0.08
  total_return: 0.25
```

## 5. Data Quality Standards

### 5.1 Required Fields
- All data must have a valid `timestamp` field
- All numeric fields must be finite (no NaN or inf values)
- All string fields must be non-empty for required data

### 5.2 Data Validation
- Timestamps must be in UTC
- Price data must be positive
- Volume data must be non-negative
- Sentiment scores must be between -1 and 1
- Signal scores must be between -1 and 1

### 5.3 Data Retention
- Raw data: Keep for 2 years
- Processed data: Keep for 1 year
- Model outputs: Keep indefinitely
- Logs: Keep for 1 year

## 6. File Naming Conventions Summary

| Data Type | Format | Naming Pattern | Example |
|-----------|--------|----------------|---------|
| Market Data | Parquet | `{symbol}_{date}.parquet` | `AAPL_2024-06-01.parquet` |
| Reddit Data | CSV | `reddit_{subreddit}_{date}.csv` | `reddit_wallstreetbets_2024-06-01.csv` |
| Twitter Data | CSV | `twitter_{date}.csv` | `twitter_2024-06-01.csv` |
| News Data | CSV | `news_{source}_{date}.csv` | `news_reuters_2024-06-01.csv` |
| Features | Parquet | `features_{symbol}_{date}.parquet` | `features_AAPL_2024-06-01.parquet` |
| Signals | Parquet | `signals_{symbol}_{date}.parquet` | `signals_AAPL_2024-06-01.parquet` |
| Decisions | CSV | `decisions_{date}.csv` | `decisions_2024-06-01.csv` |
| Performance | CSV | `performance_{date}.csv` | `performance_2024-06-01.csv` |
| Model Config | YAML | `model_config_{version}.yaml` | `model_config_v1.0.0.yaml` | 