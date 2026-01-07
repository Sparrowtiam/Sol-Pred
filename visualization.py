"""
Visualization module for price forecasts, signals, and technical indicators.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import warnings

warnings.filterwarnings('ignore')


def plot_forecast_with_signals(raw_df: pd.DataFrame,
                               forecast_df: pd.DataFrame,
                               signal: dict,
                               features_df: pd.DataFrame,
                               figsize: tuple = (16, 10)):
    """
    Create comprehensive forecast visualization with signals.
    
    Args:
        raw_df: Historical price data
        forecast_df: Prophet forecast DataFrame
        signal: Current signal from SignalGenerator
        features_df: DataFrame with technical indicators
        figsize: Figure size tuple
    """
    fig = plt.figure(figsize=figsize)
    
    # Create grid for subplots
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    
    # ===== Main Price Plot =====
    # Historical prices
    ax1.plot(raw_df.index, raw_df['Close'], 'b-', label='Historical Price', linewidth=2, alpha=0.7)
    
    # Prophet forecast
    future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
    ax1.plot(future_forecast['Date'], future_forecast['Forecast'], 'g--', 
             label='Prophet Forecast', linewidth=2, alpha=0.8)
    
    # Confidence interval
    ax1.fill_between(future_forecast['Date'],
                      future_forecast['Lower_Bound'],
                      future_forecast['Upper_Bound'],
                      alpha=0.2, color='green', label='95% Confidence Interval')
    
    # Moving averages
    ax1.plot(features_df.index, features_df['MA7'], 'orange', label='MA7', linewidth=1, alpha=0.6)
    ax1.plot(features_df.index, features_df['MA14'], 'red', label='MA14', linewidth=1, alpha=0.6)
    ax1.plot(features_df.index, features_df['MA30'], 'purple', label='MA30', linewidth=1, alpha=0.6)
    
    # Signal marker
    current_price = signal['Current_Price']
    signal_type = signal['Type']
    
    if signal_type == 'BUY':
        color = 'green'
        marker = '^'
    elif signal_type == 'SELL':
        color = 'red'
        marker = 'v'
    else:
        color = 'gray'
        marker = 'o'
    
    ax1.scatter(pd.Timestamp.now(), current_price, color=color, s=200, marker=marker, 
               zorder=5, label=f'{signal_type} Signal', edgecolors='black', linewidths=2)
    
    # Formatting
    ax1.set_title(f'SOL-USD Price Forecast with {signal_type} Signal\nConfidence: {signal["Confidence"]:.0f}%',
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price (USD)', fontsize=11)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # ===== Volatility Plot =====
    ax2.fill_between(features_df.index, features_df['Volatility'], alpha=0.3, color='blue')
    ax2.plot(features_df.index, features_df['Volatility'], 'b-', linewidth=2, label='14-day Volatility')
    
    # Volatility threshold
    vol_mean = features_df['Volatility'].mean()
    vol_std = features_df['Volatility'].std()
    ax2.axhline(y=vol_mean, color='orange', linestyle='--', label=f'Mean Volatility: {vol_mean:.4f}')
    ax2.axhline(y=vol_mean + vol_std, color='red', linestyle='--', alpha=0.5, label=f'High Volatility')
    
    ax2.set_ylabel('Volatility', fontsize=11)
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # ===== RSI Plot =====
    ax3.plot(features_df.index, features_df['RSI'], 'purple', linewidth=2, label='RSI (14)')
    ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
    ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
    ax3.fill_between(features_df.index, 30, 70, alpha=0.1, color='gray')
    
    # Highlight current RSI
    current_rsi = features_df['RSI'].iloc[-1]
    ax3.scatter(features_df.index[-1], current_rsi, color='purple', s=100, zorder=5)
    
    ax3.set_ylabel('RSI', fontsize=11)
    ax3.set_xlabel('Date', fontsize=11)
    ax3.set_ylim(0, 100)
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save figure
    filename = f"sol_forecast_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Chart saved as: {filename}")
    
    plt.show()


def plot_signal_history(signal_history: pd.DataFrame):
    """
    Plot history of generated signals.
    
    Args:
        signal_history: DataFrame with signal history
    """
    if len(signal_history) == 0:
        print("⚠️ No signals in history to plot")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Extract signal types and prices
    buy_signals = signal_history[signal_history['Type'] == 'BUY']
    sell_signals = signal_history[signal_history['Type'] == 'SELL']
    hold_signals = signal_history[signal_history['Type'] == 'HOLD']
    
    # Plot signals
    if len(buy_signals) > 0:
        ax.scatter(range(len(buy_signals)), buy_signals['Current_Price'], 
                  color='green', s=200, marker='^', label='BUY', zorder=5)
    
    if len(sell_signals) > 0:
        ax.scatter(range(len(sell_signals)), sell_signals['Current_Price'],
                  color='red', s=200, marker='v', label='SELL', zorder=5)
    
    if len(hold_signals) > 0:
        ax.scatter(range(len(hold_signals)), hold_signals['Current_Price'],
                  color='gray', s=100, marker='o', label='HOLD', zorder=5)
    
    ax.set_xlabel('Signal Index', fontsize=12)
    ax.set_ylabel('Price at Signal (USD)', fontsize=12)
    ax.set_title('Trading Signal History', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    filename = f"signal_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Signal history chart saved as: {filename}")
    
    plt.show()


def create_summary_report(current_price: float,
                         forecast_stats: dict,
                         levels: dict,
                         signal: dict,
                         features_df: pd.DataFrame):
    """
    Print comprehensive analysis summary.
    
    Args:
        current_price: Current SOL-USD price
        forecast_stats: Dictionary with forecast statistics
        levels: Dictionary with support/resistance levels
        signal: Current signal
        features_df: DataFrame with technical indicators
    """
    
    print("\n" + "="*70)
    print("SOL-USD PRICE PREDICTION ANALYSIS SUMMARY".center(70))
    print("="*70)
    
    # Forecast
    print(f"\n[PRICE OVERVIEW]")
    print(f"   Current Price:           ${float(current_price):>10.2f}")
    print(f"   7-Day Forecast:          ${float(forecast_stats.get('Forecast_7d', 0)):>10.2f} ({float(forecast_stats.get('Change_7d_Pct', 0)):+.2f}%)")
    print(f"   30-Day Forecast:         ${float(forecast_stats.get('Forecast_30d', 0)):>10.2f} ({float(forecast_stats.get('Change_30d_Pct', 0)):+.2f}%)")
    
    # Support/Resistance
    print(f"\n[TECHNICAL LEVELS]")
    print(f"   Support Level:           ${float(levels.get('Support', 0)):>10.2f} ({float(levels.get('Support_Distance_Pct', 0)):+.2f}%)")
    print(f"   Resistance Level:        ${float(levels.get('Resistance', 0)):>10.2f} ({float(levels.get('Resistance_Distance_Pct', 0)):+.2f}%)")
    print(f"   Pivot Point:             ${float(levels.get('Pivot', 0)):>10.2f}")
    
    # Technical indicators
    latest_rsi = float(features_df['RSI'].iloc[-1])
    latest_volatility = float(features_df['Volatility'].iloc[-1])
    latest_momentum = float(features_df['Momentum'].iloc[-1])
    
    print(f"\n[TECHNICAL INDICATORS]")
    print(f"   RSI (14):                {latest_rsi:>15.2f} {'(Overbought)' if latest_rsi > 70 else '(Oversold)' if latest_rsi < 30 else '(Neutral)'}")
    print(f"   Volatility (14-day):     {latest_volatility:>15.4f}")
    print(f"   Momentum (10-day):       {latest_momentum:>15.2f}")
    
    # Moving averages
    print(f"\n[MOVING AVERAGES]")
    print(f"   MA7:                     ${float(features_df['MA7'].iloc[-1]):>10.2f}")
    print(f"   MA14:                    ${float(features_df['MA14'].iloc[-1]):>10.2f}")
    print(f"   MA30:                    ${float(features_df['MA30'].iloc[-1]):>10.2f}")
    
    # Signal
    print(f"\n[TRADING SIGNAL]")
    print(f"   Signal Type:             {signal['Type']:>15}")
    print(f"   Confidence:              {float(signal['Confidence']):>14.0f}%")
    print(f"   Expected Upside:         {float(signal['Expected_Upside_Pct']):>14.2f}%")
    print(f"   Reason:                  {signal['Reason']}")
    
    # Best Buy/Sell Times
    print(f"\n[OPTIMAL TRADING TIMES]")
    if forecast_stats.get('Best_Buy_Time'):
        print(f"   Best Buy Date:           {forecast_stats['Best_Buy_Time'].strftime('%Y-%m-%d'):>15} (${float(forecast_stats.get('Local_Min', 0)):.2f})")
    if forecast_stats.get('Best_Sell_Time'):
        print(f"   Best Sell Date:          {forecast_stats['Best_Sell_Time'].strftime('%Y-%m-%d'):>15} (${float(forecast_stats.get('Local_Max', 0)):.2f})")
    
    # Confidence
    print(f"\n[FORECAST QUALITY]")
    print(f"   Confidence Level:        {float(forecast_stats.get('Confidence_Level', 0)):>14.0f}%")
    print(f"   Mean Uncertainty:        ${float(forecast_stats.get('Mean_Uncertainty', 0)):>10.2f}")
    print(f"   Historical Volatility:   {float(forecast_stats.get('Historical_Volatility', 0)):>14.4f}")
    
    # Disclaimer
    print("\n" + "="*70)
    print("⚠️  IMPORTANT DISCLAIMER")
    print("="*70)
    print("""
This analysis is based on statistical forecasting (Prophet) and technical
indicators. It is NOT financial advice and should not be used as the sole
basis for investment decisions.

Key Points:
• Past performance does not guarantee future results
• Cryptocurrency markets are highly volatile and unpredictable
• Always conduct your own research (DYOR)
• Only invest what you can afford to lose
• Consider consulting a financial advisor
• Backtesting results may not reflect live trading conditions

The generated signals are for educational and analytical purposes only.
""")
    print("="*70)
