"""
Streamlit App for SOL-USD Price Prediction System
Interactive web interface for Solana cryptocurrency price forecasting
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import local modules
try:
    from data_fetcher import prepare_full_data, get_latest_price
    from model import train_prophet_model, forecast_future, get_forecast_statistics, get_support_resistance_levels
    from signals import SignalGenerator
    from backtester import BacktestEngine
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="SOL Price AI Predictor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling with enhanced UI
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: white;
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    h2 {
        color: white;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        text-align: center;
        margin: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        margin: 5px;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
    }
    
    /* Success signal */
    .success-signal {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
    }
    
    /* Warning signal */
    .warning-signal {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
    }
    
    /* Neutral signal */
    .neutral-signal {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Page title with emoji
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1>🚀 SOL Price AI Predictor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 1.1em;'>Real-time Solana Price Forecasting & Trading Signals</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    st.markdown("---")
    st.markdown("**📊 Data Settings**")
    
    data_period = st.selectbox(
        "Historical Data Period",
        ["1y", "2y", "3y", "5y"],
        index=3,
        help="How much historical data to analyze"
    )
    
    forecast_days = st.slider(
        "Forecast Days Ahead",
        min_value=7,
        max_value=90,
        value=30,
        step=7,
        help="How many days ahead to predict"
    )
    
    st.markdown("---")
    st.markdown("**ℹ️ About This App**")
    
    st.markdown("""
    <div class='info-box'>
    <h4>🤖 AI-Powered Prediction</h4>
    <p>Uses Facebook Prophet for time-series forecasting combined with 15+ technical indicators to predict SOL-USD price movements in real-time.</p>
    <hr>
    <h4>📈 Features</h4>
    <ul>
    <li>30-day price forecasts</li>
    <li>Technical analysis</li>
    <li>Trading signals</li>
    <li>12-month backtesting</li>
    </ul>
    <hr>
    <p><strong>⚠️ Disclaimer:</strong> Not financial advice. For educational purposes only.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**📱 About Developer**")
    st.markdown("Created by: **Sparrowtiam**")
    st.markdown("Email: tiamsparrow@gmail.com")

# Main layout
tab1, tab2, tab3, tab4 = st.tabs(["📈 Forecast", "📊 Analysis", "🎯 Signals", "📉 Backtest"])

# Loading message
@st.cache_resource
def load_data(period):
    """Load and prepare data"""
    with st.spinner("Loading data and training model..."):
        raw_df, prophet_df, features_df = prepare_full_data(period=period)
        model = train_prophet_model(prophet_df)
        forecast_df = forecast_future(model, periods=forecast_days)
        return raw_df, prophet_df, features_df, model, forecast_df

# Tab 1: Forecast
with tab1:
    st.header("Price Forecast & Analysis")
    
    try:
        raw_df, prophet_df, features_df, model, forecast_df = load_data(data_period)
        
        # Get current price
        current_price_val, current_time = get_latest_price()
        current_price = float(current_price_val)
        
        # Display key metrics in attractive cards
        st.markdown("### 💰 Key Price Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💵 Current Price</h3>
                <h2>${current_price:.2f}</h2>
                <p>Live SOL/USD</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            forecast_7d = forecast_df[forecast_df['Date'] > pd.Timestamp.now()].iloc[min(6, len(forecast_df)-1)]['Forecast']
            change_7d = ((forecast_7d - current_price) / current_price) * 100
            arrow = "📈" if change_7d > 0 else "📉" if change_7d < 0 else "➡️"
            st.markdown(f"""
            <div class='metric-card'>
                <h3>{arrow} 7-Day Forecast</h3>
                <h2>${float(forecast_7d):.2f}</h2>
                <p style='color: {'#11ff00' if change_7d > 0 else '#ff1111'};'>{change_7d:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            forecast_30d = forecast_df[forecast_df['Date'] > pd.Timestamp.now()].iloc[min(29, len(forecast_df)-1)]['Forecast']
            change_30d = ((forecast_30d - current_price) / current_price) * 100
            arrow = "📈" if change_30d > 0 else "📉" if change_30d < 0 else "➡️"
            st.markdown(f"""
            <div class='metric-card'>
                <h3>{arrow} 30-Day Forecast</h3>
                <h2>${float(forecast_30d):.2f}</h2>
                <p style='color: {'#11ff00' if change_30d > 0 else '#ff1111'};'>{change_30d:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_forecast = forecast_df['Forecast'].mean()
            volatility = forecast_df['Forecast'].std()
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📊 Volatility</h3>
                <h2>${volatility:.2f}</h2>
                <p>Std Dev</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Create forecast chart using matplotlib
        st.markdown("### 📈 30-Day Price Forecast")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Historical prices
        ax.plot(raw_df.index, raw_df['Close'], label='Historical Price', color='blue', linewidth=2, alpha=0.7)
        
        # Forecast
        future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
        ax.plot(future_forecast['Date'], future_forecast['Forecast'], label='Forecast', 
                color='green', linewidth=2, linestyle='--')
        
        # Confidence interval
        if 'Upper_Bound' in future_forecast.columns and 'Lower_Bound' in future_forecast.columns:
            ax.fill_between(future_forecast['Date'], 
                            future_forecast['Lower_Bound'],
                            future_forecast['Upper_Bound'],
                            alpha=0.2, color='green', label='95% Confidence Interval')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.set_title('SOL-USD Price Forecast')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Tab 2: Analysis
with tab2:
    st.header("Technical Analysis")
    
    try:
        raw_df, prophet_df, features_df, model, forecast_df = load_data(data_period)
        current_price_val, _ = get_latest_price()
        current_price = float(current_price_val)
        
        forecast_stats = get_forecast_statistics(forecast_df, current_price, raw_df)
        levels = get_support_resistance_levels(forecast_df, current_price)
        
        # Technical indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = float(features_df['RSI'].iloc[-1])
            st.metric(
                "RSI (14)",
                f"{rsi:.2f}",
                "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
            )
        
        with col2:
            volatility = float(features_df['Volatility'].iloc[-1])
            st.metric("Volatility", f"{volatility:.4f}")
        
        with col3:
            momentum = float(features_df['Momentum'].iloc[-1])
            st.metric("Momentum", f"{momentum:+.2f}")
        
        with col4:
            atr = float(features_df['ATR'].iloc[-1])
            st.metric("ATR (14)", f"${atr:.2f}")
        
        # Support & Resistance
        st.subheader("Support & Resistance Levels")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            support = float(levels.get('Support', 0))
            support_pct = float(levels.get('Support_Distance_Pct', 0))
            st.metric("Support", f"${support:.2f}", f"{support_pct:+.2f}%")
        
        with col2:
            pivot = float(levels.get('Pivot', 0))
            st.metric("Pivot Point", f"${pivot:.2f}")
        
        with col3:
            resistance = float(levels.get('Resistance', 0))
            resistance_pct = float(levels.get('Resistance_Distance_Pct', 0))
            st.metric("Resistance", f"${resistance:.2f}", f"{resistance_pct:+.2f}%")
        
        # Moving Averages Chart
        st.subheader("Moving Averages Trend")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(features_df.index, features_df['Close'], label='Price', color='blue', linewidth=2)
        ax.plot(features_df.index, features_df['MA7'], label='MA7', color='orange', linewidth=1, linestyle='--')
        ax.plot(features_df.index, features_df['MA14'], label='MA14', color='red', linewidth=1, linestyle='--')
        ax.plot(features_df.index, features_df['MA30'], label='MA30', color='purple', linewidth=1, linestyle='--')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (USD)')
        ax.set_title('Price with Moving Averages')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error in analysis: {e}")

# Tab 3: Signals
with tab3:
    st.markdown("### 🎯 Trading Signal Analysis")
    
    try:
        raw_df, prophet_df, features_df, model, forecast_df = load_data(data_period)
        current_price_val, _ = get_latest_price()
        current_price = float(current_price_val)
        
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_signals(current_price, forecast_df, features_df)
        
        # Display signal
        signal_type = signal['Type']
        confidence = float(signal['Confidence'])
        
        if signal_type == "BUY":
            css_class = "success-signal"
            emoji = "🟢"
            color = "#11ff00"
        elif signal_type == "SELL":
            css_class = "warning-signal"
            emoji = "🔴"
            color = "#ff1111"
        else:
            css_class = "neutral-signal"
            emoji = "⚪"
            color = "#00f2fe"
        
        # Large signal display
        st.markdown(f"""
        <div class='{css_class}'>
            <h1>{emoji} {signal_type} SIGNAL</h1>
            <h2>Confidence: {confidence:.0f}%</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Signal metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🎯 Confidence</h3>
                <h2>{confidence:.0f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            upside = float(signal.get('Expected_Upside_Pct', 0))
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📈 Expected Upside</h3>
                <h2>{upside:+.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💰 Current Price</h3>
                <h2>${current_price:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            forecast_price = float(signal.get('Forecast_Price', current_price))
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🔮 Target Price</h3>
                <h2>${forecast_price:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Signal details
        st.markdown("---")
        st.markdown("### 📋 Signal Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>Signal Information</h4>
                <p><strong>Type:</strong> {signal_type}</p>
                <p><strong>Confidence:</strong> {confidence:.0f}%</p>
                <p><strong>Reason:</strong> {signal['Reason']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>Price Targets</h4>
                <p><strong>Current:</strong> ${current_price:.2f}</p>
                <p><strong>Target:</strong> ${forecast_price:.2f}</p>
                <p><strong>Expected Move:</strong> {upside:+.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Signal conditions
        if signal.get('Details'):
            st.markdown("### 📋 Signal Conditions")
            for detail in signal['Details']:
                st.write(f"• {detail}")
        
    except Exception as e:
        st.error(f"Error generating signals: {e}")

# Tab 4: Backtest
with tab4:
    st.header("Historical Backtesting (12 Months)")
    
    try:
        raw_df, prophet_df, features_df, model, forecast_df = load_data(data_period)
        
        backtest_engine = BacktestEngine()
        backtest_stats = backtest_engine.run_backtest(raw_df, features_df, lookback_months=12)
        
        if backtest_stats:
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", int(backtest_stats.get('Total_Trades', 0)))
            
            with col2:
                win_rate = float(backtest_stats.get('Win_Rate_Pct', 0))
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            with col3:
                profit_factor = float(backtest_stats.get('Profit_Factor', 0))
                st.metric("Profit Factor", f"{profit_factor:.2f}")
            
            with col4:
                strategy_return = float(backtest_stats.get('Total_Return_Pct', 0))
                st.metric("Strategy Return", f"{strategy_return:+.2f}%")
            
            # Detailed results
            st.subheader("Backtest Results")
            
            results_data = {
                "Metric": [
                    "Total Trades",
                    "Winning Trades",
                    "Losing Trades",
                    "Win Rate",
                    "Avg Trade Return",
                    "Max Drawdown",
                    "Strategy Return",
                    "Buy & Hold Return",
                    "Avg Win",
                    "Avg Loss"
                ],
                "Value": [
                    int(backtest_stats.get('Total_Trades', 0)),
                    int(backtest_stats.get('Winning_Trades', 0)),
                    int(backtest_stats.get('Losing_Trades', 0)),
                    f"{float(backtest_stats.get('Win_Rate_Pct', 0)):.1f}%",
                    f"{float(backtest_stats.get('Avg_Trade_Return_Pct', 0)):.2f}%",
                    f"{float(backtest_stats.get('Max_Drawdown_Pct', 0)):.2f}%",
                    f"{float(backtest_stats.get('Total_Return_Pct', 0)):+.2f}%",
                    f"{float(backtest_stats.get('Buy_Hold_Return_Pct', 0)):+.2f}%",
                    f"${float(backtest_stats.get('Avg_Win', 0)):.2f}",
                    f"${float(backtest_stats.get('Avg_Loss', 0)):.2f}"
                ]
            }
            
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in backtesting: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; text-align: center;'>
    <h3>⚠️ Important Disclaimer</h3>
    <p>This application provides statistical forecasts for educational purposes only. It is <strong>NOT financial advice</strong>.</p>
    <p>Cryptocurrency trading involves substantial risk. Past performance does not guarantee future results.</p>
    <p style='font-weight: bold;'>Always conduct your own research before making investment decisions.</p>
    <hr>
    <p><strong>Created by:</strong> Sparrowtiam | <strong>Email:</strong> tiamsparrow@gmail.com</p>
    <p><strong>Last Updated:</strong> January 2026 | <strong>Version:</strong> 1.0</p>
</div>
""", unsafe_allow_html=True)

