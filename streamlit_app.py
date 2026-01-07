"""
Streamlit App for SOL-USD Price Prediction System
Interactive web interface for Solana cryptocurrency price forecasting
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import prepare_full_data, get_latest_price
from model import train_prophet_model, forecast_future, get_forecast_statistics, get_support_resistance_levels
from signals import SignalGenerator
from backtester import BacktestEngine

# Page configuration
st.set_page_config(
    page_title="SOL-USD Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Page title
st.title("🚀 SOL-USD Price Prediction System")
st.subheader("Real-time Cryptocurrency Analysis & Forecasting with Prophet")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    data_period = st.selectbox(
        "Historical Data Period",
        ["1y", "2y", "3y", "5y"],
        index=3
    )
    
    forecast_days = st.slider(
        "Forecast Days Ahead",
        min_value=7,
        max_value=90,
        value=30,
        step=7
    )
    
    st.markdown("---")
    st.markdown("**About This App**")
    st.info("""
    This system uses Facebook Prophet for time-series forecasting
    combined with technical indicators to predict SOL-USD price movements.
    
    ⚠️ **Disclaimer**: Not financial advice. For educational purposes only.
    """)

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
        
        # Display current price
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${current_price:.2f}")
        with col2:
            forecast_7d = forecast_df[forecast_df['Date'] > pd.Timestamp.now()].iloc[min(6, len(forecast_df)-1)]['Forecast']
            change_7d = ((forecast_7d - current_price) / current_price) * 100
            st.metric("7-Day Forecast", f"${float(forecast_7d):.2f}", f"{change_7d:+.2f}%")
        with col3:
            forecast_30d = forecast_df[forecast_df['Date'] > pd.Timestamp.now()].iloc[min(29, len(forecast_df)-1)]['Forecast']
            change_30d = ((forecast_30d - current_price) / current_price) * 100
            st.metric("30-Day Forecast", f"${float(forecast_30d):.2f}", f"{change_30d:+.2f}%")
        
        # Create forecast chart
        st.subheader("Price Forecast with Confidence Intervals")
        
        fig = go.Figure()
        
        # Historical prices
        fig.add_trace(go.Scatter(
            x=raw_df.index,
            y=raw_df['Close'],
            mode='lines',
            name='Historical Price',
            line=dict(color='blue', width=2),
            opacity=0.7
        ))
        
        # Forecast
        future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
        fig.add_trace(go.Scatter(
            x=future_forecast['Date'],
            y=future_forecast['Forecast'],
            mode='lines',
            name='Forecast',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=future_forecast['Date'],
            y=future_forecast['Upper_Bound'],
            fill=None,
            mode='lines',
            line_color='rgba(0,100,0,0)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=future_forecast['Date'],
            y=future_forecast['Lower_Bound'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,0,0)',
            name='95% Confidence Interval',
            fillcolor='rgba(0,255,0,0.2)'
        ))
        
        fig.update_layout(
            title="SOL-USD Price Forecast",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=features_df.index,
            y=features_df['Close'],
            name='Price',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=features_df.index,
            y=features_df['MA7'],
            name='MA7',
            line=dict(color='orange', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=features_df.index,
            y=features_df['MA14'],
            name='MA14',
            line=dict(color='red', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=features_df.index,
            y=features_df['MA30'],
            name='MA30',
            line=dict(color='purple', width=1, dash='dash')
        ))
        
        fig.update_layout(
            title="Price with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in analysis: {e}")

# Tab 3: Signals
with tab3:
    st.header("Trading Signals")
    
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
            col_color = "green"
            emoji = "🟢"
        elif signal_type == "SELL":
            col_color = "red"
            emoji = "🔴"
        else:
            col_color = "gray"
            emoji = "⚪"
        
        st.markdown(f"### {emoji} Current Signal: **{signal_type}**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Confidence", f"{confidence:.0f}%")
        
        with col2:
            upside = float(signal.get('Expected_Upside_Pct', 0))
            st.metric("Expected Upside", f"{upside:+.2f}%")
        
        with col3:
            st.metric("Signal Reason", signal['Reason'])
        
        # Signal details
        st.subheader("Signal Details")
        st.info(f"""
        **Signal Type**: {signal_type}
        
        **Confidence Level**: {confidence:.0f}%
        
        **Reason**: {signal['Reason']}
        
        **Current Price**: ${current_price:.2f}
        
        **Expected Price (7d)**: ${signal.get('Forecast_Price', current_price):.2f}
        """)
        
        # Signal conditions
        if signal.get('Details'):
            st.subheader("Signal Conditions")
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
⚠️ **DISCLAIMER**: This application provides statistical forecasts for educational purposes only. 
It is NOT financial advice. Cryptocurrency trading involves substantial risk. Past performance does 
not guarantee future results. Always conduct your own research before making investment decisions.

**Created by**: Sparrowtiam | **Email**: tiamsparrow@gmail.com
""")
