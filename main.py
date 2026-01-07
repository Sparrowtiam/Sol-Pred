"""
Main execution script for SOL-USD price prediction system.

This is a complete quantitative analysis and forecasting system for Solana (SOL-USD)
using Prophet for time-series forecasting, technical indicators, and trading signals.

Author: Quantitative Python Developer
Date: 2026
Disclaimer: This is for educational purposes. NOT financial advice.
"""

import sys
import warnings
import os
import io

# Handle Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Import all modules
from data_fetcher import prepare_full_data, get_latest_price
from model import train_prophet_model, forecast_future, get_forecast_statistics, get_support_resistance_levels
from signals import SignalGenerator
from alerts import AlertSystem
from visualization import plot_forecast_with_signals, create_summary_report, plot_signal_history
from backtester import BacktestEngine


def calculate_risk_management_levels(current_price: float, atr: float, forecast_stats: dict) -> dict:
    """
    Calculate stop-loss and take-profit levels based on ATR and forecast.
    
    Args:
        current_price: Current price
        atr: Average True Range
        forecast_stats: Forecast statistics
        
    Returns:
        Dictionary with risk management levels
    """
    
    # Method 1: ATR-based
    stop_loss_atr = current_price - (atr * 1.5)
    take_profit_atr = current_price + (atr * 3.0)
    
    # Method 2: Forecast-based
    local_min = forecast_stats.get('Local_Min', current_price)
    local_max = forecast_stats.get('Local_Max', current_price)
    
    stop_loss_forecast = local_min * 0.98  # 2% below local minimum
    take_profit_forecast = local_max * 1.02  # 2% above local maximum
    
    # Use more conservative levels
    stop_loss = max(stop_loss_atr, stop_loss_forecast)
    take_profit = min(take_profit_atr, take_profit_forecast)
    
    return {
        'Stop_Loss': stop_loss,
        'Take_Profit': take_profit,
        'Risk_Amount': current_price - stop_loss,
        'Reward_Amount': take_profit - current_price,
        'Risk_Reward_Ratio': (take_profit - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0
    }


def main():
    """Main execution function."""
    
    print("\n" + "="*70)
    print("SOL-USD PRICE PREDICTION SYSTEM".center(70))
    print("Using Prophet Forecasting & Technical Analysis".center(70))
    print("="*70)
    
    try:
        # ===== STEP 1: Data Collection =====
        print("\n🔄 STEP 1: Data Collection & Preparation")
        print("-" * 70)
        raw_df, prophet_df, features_df = prepare_full_data(period="5y")
        
        # ===== STEP 2: Model Training =====
        print("\n🔄 STEP 2: Model Training")
        print("-" * 70)
        model = train_prophet_model(prophet_df)
        
        # ===== STEP 3: Forecasting =====
        print("\n🔄 STEP 3: Price Forecasting")
        print("-" * 70)
        forecast_df = forecast_future(model, periods=30)
        
        # ===== STEP 4: Get Current Price =====
        current_price_val, current_time = get_latest_price()
        current_price = float(current_price_val)
        print(f"\n✅ Current Price: ${current_price:.2f} (as of {current_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # ===== STEP 5: Calculate Forecast Statistics =====
        print("\n🔄 STEP 5: Computing Forecast Statistics")
        print("-" * 70)
        forecast_stats = get_forecast_statistics(forecast_df, current_price, raw_df)
        levels = get_support_resistance_levels(forecast_df, current_price)
        
        # ===== STEP 6: Generate Trading Signals =====
        print("\n🔄 STEP 6: Signal Generation")
        print("-" * 70)
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_signals(current_price, forecast_df, features_df)
        
        print(f"\n🎯 Signal Type: {signal['Type']}")
        print(f"   Confidence: {signal['Confidence']:.0f}%")
        print(f"   Expected Move: {signal['Expected_Upside_Pct']:.2f}%")
        print(f"   Reason: {signal['Reason']}")
        
        # ===== STEP 7: Risk Management Levels =====
        print("\n🔄 STEP 7: Risk Management Levels")
        print("-" * 70)
        atr = features_df['ATR'].iloc[-1]
        risk_levels = calculate_risk_management_levels(current_price, atr, forecast_stats)
        
        print(f"✅ Stop Loss: ${risk_levels['Stop_Loss']:.2f}")
        print(f"✅ Take Profit: ${risk_levels['Take_Profit']:.2f}")
        print(f"✅ Risk/Reward Ratio: {risk_levels['Risk_Reward_Ratio']:.2f}")
        
        # ===== STEP 8: Send Alerts =====
        print("\n🔄 STEP 8: Alert System")
        print("-" * 70)
        alert_system = AlertSystem()
        alert_system.send_alert(signal, atr, risk_levels['Stop_Loss'], risk_levels['Take_Profit'])
        
        # ===== STEP 9: Historical Backtesting =====
        print("\n🔄 STEP 9: Historical Backtesting")
        print("-" * 70)
        backtest_engine = BacktestEngine(
            initial_capital=10000,
            position_size_pct=0.95,
            stop_loss_pct=0.05,
            take_profit_pct=0.15
        )
        backtest_stats = backtest_engine.run_backtest(raw_df, features_df, lookback_months=12)
        backtest_engine.print_backtest_report(backtest_stats)
        
        # ===== STEP 10: Summary Report =====
        print("\n🔄 STEP 10: Analysis Summary")
        print("-" * 70)
        create_summary_report(current_price, forecast_stats, levels, signal, features_df)
        
        # ===== STEP 11: Visualization =====
        print("\n[STEP 11: Generating Visualizations]")
        print("-" * 70)
        try:
            plot_forecast_with_signals(raw_df, forecast_df, signal, features_df)
            
            # Also plot signal history if multiple signals exist
            signal_history = signal_gen.get_signal_history()
            if len(signal_history) > 1:
                plot_signal_history(signal_history)
        except Exception as e:
            print(f"[WARNING] Could not generate visualizations: {e}")
            print("[INFO] This is normal if running in headless mode")
        
        # ===== Final Message =====
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE".center(70))
        print("="*70)
        print("""
Next Steps:
1. Review the generated charts and analysis
2. Evaluate the backtest results
3. Consider risk management levels
4. Monitor for signal updates

Remember: This is educational analysis, not financial advice.
Always conduct your own research and risk management.
""")
        print("="*70 + "\n")
        
        return True
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        return False
    
    except Exception as e:
        print(f"\n\n❌ Error during execution: {e}")
        print(f"\nFull traceback:")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
