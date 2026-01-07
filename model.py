"""
Prophet model training and forecasting module for Solana price prediction.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


def train_prophet_model(prophet_df: pd.DataFrame, 
                       yearly_seasonality: bool = True,
                       weekly_seasonality: bool = True,
                       daily_seasonality: bool = False) -> Prophet:
    """
    Train Prophet model with optimal configuration.
    
    Args:
        prophet_df: DataFrame in Prophet format (ds, y)
        yearly_seasonality: Include yearly seasonality
        weekly_seasonality: Include weekly seasonality
        daily_seasonality: Include daily seasonality
        
    Returns:
        Trained Prophet model
    """
    print("🤖 Training Prophet model...")
    
    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        changepoint_prior_scale=0.05,  # Enable changepoint detection
        seasonality_prior_scale=10.0,
        seasonality_mode='additive',
        interval_width=0.95
    )
    
    # Fit the model
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(prophet_df)
    
    print("✅ Model training completed")
    
    return model


def forecast_future(model: Prophet, periods: int = 30) -> pd.DataFrame:
    """
    Generate future price forecast.
    
    Args:
        model: Trained Prophet model
        periods: Number of days to forecast (default: 30)
        
    Returns:
        DataFrame with forecast data
    """
    print(f"\n🔮 Generating {periods}-day forecast...")
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    # Extract relevant columns
    forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_df.columns = ['Date', 'Forecast', 'Lower_Bound', 'Upper_Bound']
    
    print(f"✅ Forecast generated for {len(forecast_df)} dates")
    
    return forecast_df


def get_forecast_statistics(forecast_df: pd.DataFrame, 
                            current_price: float,
                            historical_df: pd.DataFrame) -> dict:
    """
    Calculate forecast statistics and confidence metrics.
    
    Args:
        forecast_df: Prophet forecast DataFrame
        current_price: Current price of SOL-USD
        historical_df: Historical price data
        
    Returns:
        Dictionary with forecast statistics
    """
    future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
    
    if len(future_forecast) == 0:
        return {}
    
    # Calculate key metrics
    forecast_7d = future_forecast.iloc[min(6, len(future_forecast)-1)]['Forecast']
    forecast_30d = future_forecast.iloc[min(29, len(future_forecast)-1)]['Forecast']
    
    # Find local extrema in forecast
    local_min = future_forecast['Forecast'].min()
    local_max = future_forecast['Forecast'].max()
    
    # Calculate confidence (inverse of uncertainty width)
    mean_uncertainty = (future_forecast['Upper_Bound'] - future_forecast['Lower_Bound']).mean()
    historical_volatility = historical_df['Close'].pct_change().std()
    confidence = 100 * (1 - min(mean_uncertainty / current_price / 4, 1))
    
    # Calculate percentage changes
    change_7d_pct = ((forecast_7d - current_price) / current_price) * 100
    change_30d_pct = ((forecast_30d - current_price) / current_price) * 100
    
    # Identify best buy/sell times
    best_buy_time = future_forecast.loc[future_forecast['Forecast'].idxmin(), 'Date']
    best_sell_time = future_forecast.loc[future_forecast['Forecast'].idxmax(), 'Date']
    
    stats = {
        'Current_Price': current_price,
        'Forecast_7d': forecast_7d,
        'Forecast_30d': forecast_30d,
        'Change_7d_Pct': change_7d_pct,
        'Change_30d_Pct': change_30d_pct,
        'Local_Min': local_min,
        'Local_Max': local_max,
        'Min_Date': future_forecast.loc[future_forecast['Forecast'].idxmin(), 'Date'],
        'Max_Date': future_forecast.loc[future_forecast['Forecast'].idxmax(), 'Date'],
        'Best_Buy_Time': best_buy_time,
        'Best_Sell_Time': best_sell_time,
        'Confidence_Level': confidence,
        'Mean_Uncertainty': mean_uncertainty,
        'Historical_Volatility': historical_volatility
    }
    
    return stats


def get_support_resistance_levels(forecast_df: pd.DataFrame, 
                                  current_price: float) -> dict:
    """
    Calculate support and resistance levels based on forecast.
    
    Args:
        forecast_df: Prophet forecast DataFrame
        current_price: Current price
        
    Returns:
        Dictionary with price levels
    """
    future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
    
    # Support = local minimum
    support = future_forecast['Forecast'].min()
    
    # Resistance = local maximum
    resistance = future_forecast['Forecast'].max()
    
    # Pivot point
    pivot = (support + resistance) / 2
    
    return {
        'Support': support,
        'Resistance': resistance,
        'Pivot': pivot,
        'Support_Distance_Pct': ((support - current_price) / current_price) * 100,
        'Resistance_Distance_Pct': ((resistance - current_price) / current_price) * 100
    }
