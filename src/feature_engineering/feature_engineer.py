import pandas as pd
import numpy as np
from typing import Optional, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class FeatureEngineer:
    """
    Feature engineering for market and alternative data.
    Outputs feature DataFrames to data/processed/features/.
    Upgrades: symbol-aware sentiment, source separation, MACD, volatility, z-score normalization, logging.
    """
    def __init__(self, output_dir: str = "data/processed/features/"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # --- Technical Indicators ---
    def add_sma(self, df: pd.DataFrame, window: int = 20, price_col: str = 'close') -> pd.DataFrame:
        df[f'sma_{window}'] = df[price_col].rolling(window=window, min_periods=1).mean()
        return df

    def add_ema(self, df: pd.DataFrame, window: int = 12, price_col: str = 'close') -> pd.DataFrame:
        df[f'ema_{window}'] = df[price_col].ewm(span=window, adjust=False).mean()
        return df

    def add_rsi(self, df: pd.DataFrame, window: int = 14, price_col: str = 'close') -> pd.DataFrame:
        delta = df[price_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        df[f'rsi_{window}'] = 100 - (100 / (1 + rs))
        return df

    def add_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, price_col: str = 'close') -> pd.DataFrame:
        ema_fast = df[price_col].ewm(span=fast, adjust=False).mean()
        ema_slow = df[price_col].ewm(span=slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        return df

    def add_bollinger_bands(self, df: pd.DataFrame, window: int = 20, price_col: str = 'close') -> pd.DataFrame:
        sma = df[price_col].rolling(window=window, min_periods=1).mean()
        std = df[price_col].rolling(window=window, min_periods=1).std()
        df['bb_upper'] = sma + 2 * std
        df['bb_lower'] = sma - 2 * std
        df['bb_position'] = (df[price_col] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-9)
        return df

    def add_volatility(self, df: pd.DataFrame, window: int = 20, price_col: str = 'close') -> pd.DataFrame:
        df['volatility'] = df[price_col].rolling(window=window, min_periods=1).std()
        return df

    def add_zscore(self, df: pd.DataFrame, col: str, window: int = 20) -> pd.DataFrame:
        mean = df[col].rolling(window=window, min_periods=1).mean()
        std = df[col].rolling(window=window, min_periods=1).std()
        df[f'{col}_zscore'] = (df[col] - mean) / (std + 1e-9)
        return df

    # --- Sentiment Features ---
    def aggregate_sentiment(self, alt_df: pd.DataFrame, symbol: str, timestamp_col: str = 'timestamp', entity_col: str = 'entities', source_col: str = 'source', sentiment_col: str = 'sentiment_score', freq: str = 'D') -> pd.DataFrame:
        # Filter for posts mentioning the symbol
        alt_df = alt_df[alt_df[entity_col].apply(lambda ents: symbol in ents if isinstance(ents, list) else False)]
        # Group by time and source
        alt_df[timestamp_col] = pd.to_datetime(alt_df[timestamp_col])
        alt_df['date_bin'] = alt_df[timestamp_col].dt.floor(freq)
        grouped = alt_df.groupby(['date_bin', source_col])[sentiment_col].mean().unstack(fill_value=0)
        grouped.columns = [f'sentiment_{src}' for src in grouped.columns]
        grouped['sentiment_mean'] = grouped.mean(axis=1)
        return grouped.reset_index().rename(columns={'date_bin': 'timestamp'})

    def add_sentiment_features(self, df: pd.DataFrame, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        # Merge on timestamp
        df = pd.merge(df, sentiment_df, on='timestamp', how='left')
        # Fill missing sentiment with 0
        for col in df.columns:
            if col.startswith('sentiment_'):
                df[col] = df[col].fillna(0)
        # Rolling means/volatility for mean sentiment
        df['sentiment_ma_1d'] = df['sentiment_mean'].rolling(window=1, min_periods=1).mean()
        df['sentiment_volatility'] = df['sentiment_mean'].rolling(window=5, min_periods=1).std()
        return df

    # --- Time Features ---
    def add_time_features(self, df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
        df['hour'] = pd.to_datetime(df[timestamp_col]).dt.hour
        df['day_of_week'] = pd.to_datetime(df[timestamp_col]).dt.dayofweek
        df['is_weekend'] = df['day_of_week'] >= 5
        df['is_market_open'] = df['hour'].between(9, 16) & (~df['is_weekend'])
        return df

    # --- Data Validation ---
    def validate(self, df: pd.DataFrame) -> bool:
        if df.isnull().any().any():
            logging.warning("DataFrame contains missing values.")
        if not np.isfinite(df.select_dtypes(include=[np.number])).all().all():
            logging.warning("DataFrame contains non-finite values.")
        return True

    # --- Main Pipeline ---
    def generate_features(self, market_df: pd.DataFrame, alt_df: pd.DataFrame, symbol: str, date: Optional[str] = None) -> pd.DataFrame:
        logging.info(f"Generating features for {symbol}...")
        df = market_df.copy()
        df = self.add_sma(df, window=20)
        df = self.add_ema(df, window=12)
        df = self.add_rsi(df, window=14)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df, window=20)
        df = self.add_volatility(df, window=20)
        df = self.add_zscore(df, 'close', window=20)
        # Aggregate and add sentiment features
        sentiment_df = self.aggregate_sentiment(alt_df, symbol)
        df = self.add_sentiment_features(df, sentiment_df)
        df = self.add_time_features(df)
        self.validate(df)
        # Save to file
        if date is None and 'timestamp' in df.columns:
            date = pd.to_datetime(df['timestamp']).dt.date.min().isoformat()
        filename = f"features_{symbol}_{date}.parquet"
        out_path = self.output_dir / filename
        df.to_parquet(out_path, index=False)
        logging.info(f"[FeatureEngineer] Saved features to {out_path}")
        return df

# Example usage (for testing)
if __name__ == "__main__":
    # Example: Load sample market data and sentiment, generate features
    import sys
    if len(sys.argv) < 2:
        print("Usage: python feature_engineer.py <input_csv> [symbol] [date]")
        sys.exit(1)
    input_csv = sys.argv[1]
    symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
    date = sys.argv[3] if len(sys.argv) > 3 else None
    df = pd.read_csv(input_csv)
    fe = FeatureEngineer()
    fe.generate_features(df, symbol, date) 