"""
Data format utilities for EchoAlpha quant trading platform.

This module provides utilities for:
- Data format validation
- File naming conventions
- Data loading and saving
- Schema validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml
import json
import logging

logger = logging.getLogger(__name__)

# Data schemas
MARKET_DATA_SCHEMA = {
    'timestamp': 'datetime64[ns]',
    'symbol': 'object',
    'open': 'float64',
    'high': 'float64',
    'low': 'float64',
    'close': 'float64',
    'volume': 'int64',
    'vwap': 'float64',
    'source': 'object'
}

REDDIT_DATA_SCHEMA = {
    'timestamp': 'datetime64[ns]',
    'subreddit': 'object',
    'title': 'object',
    'text': 'object',
    'score': 'int64',
    'num_comments': 'int64',
    'author': 'object',
    'url': 'object',
    'sentiment_score': 'float64',
    'entities': 'object',
    'source': 'object'
}

FEATURE_DATA_SCHEMA = {
    'timestamp': 'datetime64[ns]',
    'symbol': 'object',
    # Technical indicators
    'sma_20': 'float64',
    'ema_12': 'float64',
    'rsi_14': 'float64',
    'bb_upper': 'float64',
    'bb_lower': 'float64',
    'bb_position': 'float64',
    'macd': 'float64',
    'macd_signal': 'float64',
    'volume_sma': 'float64',
    # Sentiment features
    'sentiment_score': 'float64',
    'sentiment_ma_1h': 'float64',
    'sentiment_ma_1d': 'float64',
    'sentiment_volatility': 'float64',
    # Microstructure features
    'bid_ask_spread': 'float64',
    'order_imbalance': 'float64',
    'volume_profile': 'float64',
    # Time features
    'hour': 'int64',
    'day_of_week': 'int64',
    'is_weekend': 'bool',
    'is_market_open': 'bool'
}


class DataFormatValidator:
    """Validates data formats and schemas."""
    
    @staticmethod
    def validate_market_data(df: pd.DataFrame) -> bool:
        """Validate market data DataFrame."""
        try:
            # Check required columns
            required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check data types
            for col, dtype in MARKET_DATA_SCHEMA.items():
                if col in df.columns and str(df[col].dtype) != dtype:
                    logger.warning(f"Column {col} has dtype {df[col].dtype}, expected {dtype}")
            
            # Check data quality
            if df['timestamp'].isna().any():
                logger.error("Found NaN timestamps")
                return False
            
            price_cols = ['open', 'high', 'low', 'close']
            price_check = (df[price_cols] <= 0).any()
            if price_check.any():
                logger.error("Found non-positive prices")
                return False
            
            volume_check = (df['volume'] < 0)
            if volume_check.any():
                logger.error("Found negative volumes")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating market data: {e}")
            return False
    
    @staticmethod
    def validate_feature_data(df: pd.DataFrame) -> bool:
        """Validate feature data DataFrame."""
        try:
            # Check required columns
            required_cols = ['timestamp', 'symbol']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check for infinite values
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if df[numeric_cols].isin([np.inf, -np.inf]).any().any():
                logger.error("Found infinite values in numeric columns")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating feature data: {e}")
            return False


class FileNamingConventions:
    """Handles file naming conventions for different data types."""
    
    @staticmethod
    def get_market_data_filename(symbol: str, date: Union[str, datetime]) -> str:
        """Generate market data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"{symbol}_{date_str}.parquet"
    
    @staticmethod
    def get_reddit_data_filename(subreddit: str, date: Union[str, datetime]) -> str:
        """Generate Reddit data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"reddit_{subreddit}_{date_str}.csv"
    
    @staticmethod
    def get_twitter_data_filename(date: Union[str, datetime]) -> str:
        """Generate Twitter data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"twitter_{date_str}.csv"
    
    @staticmethod
    def get_feature_data_filename(symbol: str, date: Union[str, datetime]) -> str:
        """Generate feature data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"features_{symbol}_{date_str}.parquet"
    
    @staticmethod
    def get_signal_data_filename(symbol: str, date: Union[str, datetime]) -> str:
        """Generate signal data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"signals_{symbol}_{date_str}.parquet"
    
    @staticmethod
    def get_decision_data_filename(date: Union[str, datetime]) -> str:
        """Generate decision data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"decisions_{date_str}.csv"
    
    @staticmethod
    def get_performance_data_filename(date: Union[str, datetime]) -> str:
        """Generate performance data filename."""
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
        return f"performance_{date_str}.csv"


class DataLoader:
    """Handles data loading and saving operations."""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.validator = DataFormatValidator()
        self.naming = FileNamingConventions()
    
    def load_market_data(self, symbol: str, date: Union[str, datetime]) -> Optional[pd.DataFrame]:
        """Load market data for a symbol and date."""
        try:
            filename = self.naming.get_market_data_filename(symbol, date)
            filepath = self.base_path / "raw" / "market" / filename
            
            if not filepath.exists():
                logger.warning(f"Market data file not found: {filepath}")
                return None
            
            df = pd.read_parquet(filepath)
            
            if not self.validator.validate_market_data(df):
                logger.error(f"Market data validation failed for {filename}")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading market data: {e}")
            return None
    
    def save_market_data(self, df: pd.DataFrame, symbol: str, date: Union[str, datetime]) -> bool:
        """Save market data for a symbol and date."""
        try:
            if not self.validator.validate_market_data(df):
                logger.error("Market data validation failed before saving")
                return False
            
            filename = self.naming.get_market_data_filename(symbol, date)
            filepath = self.base_path / "raw" / "market" / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved market data: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving market data: {e}")
            return False
    
    def load_feature_data(self, symbol: str, date: Union[str, datetime]) -> Optional[pd.DataFrame]:
        """Load feature data for a symbol and date."""
        try:
            filename = self.naming.get_feature_data_filename(symbol, date)
            filepath = self.base_path / "processed" / "features" / filename
            
            if not filepath.exists():
                logger.warning(f"Feature data file not found: {filepath}")
                return None
            
            df = pd.read_parquet(filepath)
            
            if not self.validator.validate_feature_data(df):
                logger.error(f"Feature data validation failed for {filename}")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading feature data: {e}")
            return None
    
    def save_feature_data(self, df: pd.DataFrame, symbol: str, date: Union[str, datetime]) -> bool:
        """Save feature data for a symbol and date."""
        try:
            if not self.validator.validate_feature_data(df):
                logger.error("Feature data validation failed before saving")
                return False
            
            filename = self.naming.get_feature_data_filename(symbol, date)
            filepath = self.base_path / "processed" / "features" / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved feature data: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving feature data: {e}")
            return False
    
    def load_reddit_data(self, subreddit: str, date: Union[str, datetime]) -> Optional[pd.DataFrame]:
        """Load Reddit data for a subreddit and date."""
        try:
            filename = self.naming.get_reddit_data_filename(subreddit, date)
            filepath = self.base_path / "raw" / "alternative" / filename
            
            if not filepath.exists():
                logger.warning(f"Reddit data file not found: {filepath}")
                return None
            
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading Reddit data: {e}")
            return None
    
    def save_reddit_data(self, df: pd.DataFrame, subreddit: str, date: Union[str, datetime]) -> bool:
        """Save Reddit data for a subreddit and date."""
        try:
            filename = self.naming.get_reddit_data_filename(subreddit, date)
            filepath = self.base_path / "raw" / "alternative" / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(filepath, index=False)
            logger.info(f"Saved Reddit data: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving Reddit data: {e}")
            return False


class ModelConfigManager:
    """Manages model configuration files."""
    
    def __init__(self, base_path: str = "data/models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_model_config(self, config: Dict[str, Any], version: str) -> bool:
        """Save model configuration."""
        try:
            filename = f"model_config_{version}.yaml"
            filepath = self.base_path / filename
            
            # Add metadata
            config_with_metadata = {
                'model_version': version,
                'created_date': datetime.now(timezone.utc).isoformat(),
                **config
            }
            
            with open(filepath, 'w') as f:
                yaml.dump(config_with_metadata, f, default_flow_style=False)
            
            logger.info(f"Saved model config: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model config: {e}")
            return False
    
    def load_model_config(self, version: str) -> Optional[Dict[str, Any]]:
        """Load model configuration."""
        try:
            filename = f"model_config_{version}.yaml"
            filepath = self.base_path / filename
            
            if not filepath.exists():
                logger.warning(f"Model config file not found: {filepath}")
                return None
            
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f)
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading model config: {e}")
            return None


# Convenience functions
def get_data_loader(base_path: str = "data") -> DataLoader:
    """Get a DataLoader instance."""
    return DataLoader(base_path)


def get_model_config_manager(base_path: str = "data/models") -> ModelConfigManager:
    """Get a ModelConfigManager instance."""
    return ModelConfigManager(base_path)


def validate_dataframe_schema(df: pd.DataFrame, schema: Dict[str, str]) -> bool:
    """Validate DataFrame against a schema."""
    try:
        for col, expected_dtype in schema.items():
            if col not in df.columns:
                logger.warning(f"Column {col} not found in DataFrame")
                continue
            
            if str(df[col].dtype) != expected_dtype:
                logger.warning(f"Column {col} has dtype {df[col].dtype}, expected {expected_dtype}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating schema: {e}")
        return False 