import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)

class SignalGenerator:
    """
    Loads features, combines them into trading signals, and saves to data/processed/signals/.
    Upgrades: z-score normalization, configurable weights, source-specific sentiment, logging, more features.
    """
    def __init__(self, features_dir: str = "data/processed/features/", output_dir: str = "data/processed/signals/", config: Optional[Dict] = None):
        self.features_dir = Path(features_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {
            'weights': {
                'technical': 0.4,
                'sentiment_mean': 0.3,
                'sentiment_reddit': 0.15,
                'sentiment_news': 0.15
            },
            'thresholds': {
                'buy': 0.5,
                'sell': -0.5
            }
        }

    def load_features(self, symbol: str, date: str) -> pd.DataFrame:
        filename = f"features_{symbol}_{date}.parquet"
        path = self.features_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Feature file not found: {path}")
        return pd.read_parquet(path)

    def combine_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        w = self.config['weights']
        # Use z-score of close, MACD, RSI, and sentiment features if present
        tech = df['rsi_14_zscore'] if 'rsi_14_zscore' in df else (df['rsi_14'] - 50) / 50
        sent_mean = df['sentiment_mean'].clip(-1, 1) if 'sentiment_mean' in df else 0
        sent_reddit = df['sentiment_reddit'].clip(-1, 1) if 'sentiment_reddit' in df else 0
        sent_news = df['sentiment_news'].clip(-1, 1) if 'sentiment_news' in df else 0
        # Weighted sum
        df['technical_signal'] = tech
        df['sentiment_mean_signal'] = sent_mean
        df['sentiment_reddit_signal'] = sent_reddit
        df['sentiment_news_signal'] = sent_news
        df['combined_signal'] = (
            w['technical'] * tech +
            w['sentiment_mean'] * sent_mean +
            w['sentiment_reddit'] * sent_reddit +
            w['sentiment_news'] * sent_news
        )
        # Signal action
        buy_th = self.config['thresholds']['buy']
        sell_th = self.config['thresholds']['sell']
        df['signal_action'] = np.where(df['combined_signal'] > buy_th, 'BUY',
                                np.where(df['combined_signal'] < sell_th, 'SELL', 'HOLD'))
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        if df.isnull().any().any():
            logging.warning("Signal DataFrame contains missing values.")
        if not np.isfinite(df.select_dtypes(include=[np.number])).all().all():
            logging.warning("Signal DataFrame contains non-finite values.")
        return True

    def save_signals(self, df: pd.DataFrame, symbol: str, date: str):
        filename = f"signals_{symbol}_{date}.parquet"
        out_path = self.output_dir / filename
        df.to_parquet(out_path, index=False)
        logging.info(f"[SignalGenerator] Saved signals to {out_path}")

    def generate_signals(self, symbol: str, date: str) -> pd.DataFrame:
        logging.info(f"Generating signals for {symbol} {date}...")
        df = self.load_features(symbol, date)
        df = self.combine_signals(df)
        self.validate(df)
        self.save_signals(df, symbol, date)
        return df

# Example usage (for testing)
if __name__ == "__main__":
    import sys
    symbol = "AAPL"
    date = "2024-06-01"
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    if len(sys.argv) > 2:
        date = sys.argv[2]
    sg = SignalGenerator()
    signals = sg.generate_signals(symbol, date)
    print(signals[[c for c in signals.columns if 'signal' in c or c == 'timestamp' or c == 'combined_signal' or c == 'signal_action']].head(10).to_string(index=False)) 