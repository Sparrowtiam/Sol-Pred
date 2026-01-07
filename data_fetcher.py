"""
Data fetching and preprocessing module for Solana price prediction.
Handles data retrieval from Yahoo Finance and feature engineering.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

try:
    import yfinance as yf
except ImportError:
    raise ImportError("yfinance library not found. Please install: pip install yfinance")

warnings.filterwarnings('ignore')


def fetch_solana_data(period: str = "5y") -> pd.DataFrame:
    """
    Fetch historical SOL-USD price data from Yahoo Finance.
    
    Args:
        period: Historical period to fetch ('5y', '10y', etc.)
        
    Returns:
        DataFrame with OHLCV data
    """
    print(f"📊 Fetching SOL-USD historical data for {period}...")
    
    try:
        sol_data = yf.download("SOL-USD", period=period, interval="1d", progress=False)
        print(f"✅ Retrieved {len(sol_data)} trading days of data")
        return sol_data
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        raise


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values and outliers in price data.
    
    Args:
        df: DataFrame with price data
        
    Returns:
        Cleaned DataFrame
    """
    initial_missing = df.isnull().sum().sum()
    
    # Forward fill missing values
    df = df.fillna(method='ffill')
    
    # Remove outliers using IQR method on daily returns
    df['Returns'] = df['Close'].pct_change()
    Q1 = df['Returns'].quantile(0.25)
    Q3 = df['Returns'].quantile(0.75)
    IQR = Q3 - Q1
    
    outlier_bounds = (Q1 - 3 * IQR, Q3 + 3 * IQR)
    outlier_mask = (df['Returns'] < outlier_bounds[0]) | (df['Returns'] > outlier_bounds[1])
    
    if outlier_mask.sum() > 0:
        print(f"🔧 Detected and handled {outlier_mask.sum()} potential outliers")
        # Interpolate outliers
        df.loc[outlier_mask, 'Close'] = np.nan
        df['Close'] = df['Close'].interpolate(method='linear')
    
    df = df.drop('Returns', axis=1)
    
    if initial_missing > 0:
        print(f"🔧 Handled {initial_missing} missing values")
    
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer technical features for better predictions.
    
    Args:
        df: DataFrame with price data
        
    Returns:
        DataFrame with engineered features
    """
    # Moving averages
    df['MA7'] = df['Close'].rolling(window=7).mean()
    df['MA14'] = df['Close'].rolling(window=14).mean()
    df['MA30'] = df['Close'].rolling(window=30).mean()
    
    # Volatility (rolling standard deviation of returns)
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=14).std()
    
    # Average True Range (ATR) for stop-loss/take-profit
    df['HL'] = df['High'] - df['Low']
    df['HC'] = abs(df['High'] - df['Close'].shift())
    df['LC'] = abs(df['Low'] - df['Close'].shift())
    df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # Momentum
    df['Momentum'] = df['Close'] - df['Close'].shift(10)
    
    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    print("✅ Feature engineering completed")
    print(f"   - Moving Averages (7, 14, 30 days)")
    print(f"   - Volatility (14-day rolling)")
    print(f"   - ATR for stop-loss/take-profit")
    print(f"   - Momentum indicator")
    print(f"   - RSI indicator")
    
    return df


def prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data in Prophet format (ds, y).
    
    Args:
        df: DataFrame with price data
        
    Returns:
        DataFrame with Prophet format (ds, y columns)
    """
    prophet_df = pd.DataFrame()
    prophet_df['ds'] = df.index.values
    prophet_df['y'] = df['Close'].values
    
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    
    return prophet_df


def get_latest_price() -> tuple:
    """
    Get the latest SOL-USD price.
    
    Returns:
        Tuple of (price, timestamp)
    """
    latest_data = yf.download("SOL-USD", period="1d", progress=False)
    latest_price = latest_data['Close'].iloc[-1]
    latest_time = latest_data.index[-1]
    
    return latest_price, latest_time


def prepare_full_data(period: str = "5y") -> tuple:
    """
    Complete data preparation pipeline.
    
    Args:
        period: Historical period to fetch
        
    Returns:
        Tuple of (raw_df, prophet_df, features_df)
    """
    # Fetch data
    raw_df = fetch_solana_data(period=period)
    
    # Clean data
    raw_df = handle_missing_values(raw_df)
    
    # Engineer features
    features_df = engineer_features(raw_df.copy())
    
    # Prepare for Prophet
    prophet_df = prepare_prophet_data(raw_df)
    
    print(f"\n📈 Data preparation complete:")
    print(f"   Total records: {len(raw_df)}")
    print(f"   Date range: {raw_df.index[0].date()} to {raw_df.index[-1].date()}")
    latest_price = float(raw_df['Close'].iloc[-1])
    print(f"   Latest close price: ${latest_price:.2f}")
    
    return raw_df, prophet_df, features_df
