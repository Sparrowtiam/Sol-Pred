"""
Historical backtesting module to evaluate signal accuracy.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class BacktestEngine:
    """Backtest trading signals on historical data."""
    
    def __init__(self, 
                 initial_capital: float = 10000,
                 position_size_pct: float = 0.95,
                 stop_loss_pct: float = 0.05,
                 take_profit_pct: float = 0.15):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital in USD
            position_size_pct: Percentage of capital to use per trade
            stop_loss_pct: Stop-loss percentage (e.g., 0.05 for 5%)
            take_profit_pct: Take-profit percentage
        """
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trades = []
        self.equity_curve = []
    
    
    def run_backtest(self, 
                    historical_df: pd.DataFrame,
                    features_df: pd.DataFrame,
                    lookback_months: int = 12) -> dict:
        """
        Run backtest on historical data.
        
        Args:
            historical_df: Historical price data
            features_df: DataFrame with technical indicators
            lookback_months: Number of months to backtest
            
        Returns:
            Dictionary with backtest results
        """
        print(f"\n🔄 Running {lookback_months}-month backtest...")
        
        # Calculate lookback date
        start_date = historical_df.index[-1] - timedelta(days=lookback_months*30)
        backtest_data = historical_df[historical_df.index >= start_date].copy()
        backtest_features = features_df[features_df.index >= start_date].copy()
        
        if len(backtest_data) == 0:
            print("⚠️ Insufficient data for backtest")
            return {}
        
        capital = self.initial_capital
        position = None  # None, 'long', or 'short'
        entry_price = None
        entry_date = None
        
        self.equity_curve = [capital]
        
        # Simple signal generation based on moving averages and RSI
        for i in range(1, len(backtest_data)):
            date = backtest_data.index[i]
            close_price = float(backtest_data['Close'].iloc[i])
            
            # Get indicators as scalars
            ma7 = float(backtest_features['MA7'].iloc[i]) if pd.notna(backtest_features['MA7'].iloc[i]) else close_price
            ma14 = float(backtest_features['MA14'].iloc[i]) if pd.notna(backtest_features['MA14'].iloc[i]) else close_price
            ma30 = float(backtest_features['MA30'].iloc[i]) if pd.notna(backtest_features['MA30'].iloc[i]) else close_price
            rsi = float(backtest_features['RSI'].iloc[i]) if pd.notna(backtest_features['RSI'].iloc[i]) else 50
            momentum = float(backtest_features['Momentum'].iloc[i]) if pd.notna(backtest_features['Momentum'].iloc[i]) else 0
            
            # Generate signal
            buy_signal = (close_price > ma7 > ma14 > ma30) and (rsi < 70) and (momentum > 0)
            sell_signal = (close_price < ma7) or (rsi > 75) or (momentum < -0.5)
            
            # Exit logic
            if position == 'long':
                # Check stop-loss or take-profit
                loss_pct = (entry_price - close_price) / entry_price
                gain_pct = (close_price - entry_price) / entry_price
                
                if loss_pct > self.stop_loss_pct or gain_pct > self.take_profit_pct or sell_signal:
                    # Close position
                    trade_pnl = (close_price - entry_price) * (capital * self.position_size_pct / entry_price)
                    capital += trade_pnl
                    
                    self.trades.append({
                        'Entry_Date': entry_date,
                        'Exit_Date': date,
                        'Entry_Price': entry_price,
                        'Exit_Price': close_price,
                        'Return_Pct': gain_pct * 100,
                        'PnL': trade_pnl
                    })
                    
                    position = None
                    entry_price = None
            
            # Entry logic
            if position is None and buy_signal:
                position = 'long'
                entry_price = close_price
                entry_date = date
            
            self.equity_curve.append(capital)
        
        # Calculate statistics
        return self._calculate_statistics(backtest_data)
    
    
    def _calculate_statistics(self, backtest_data: pd.DataFrame) -> dict:
        """Calculate backtest performance metrics."""
        
        if len(self.trades) == 0:
            return {
                'Total_Trades': 0,
                'Winning_Trades': 0,
                'Losing_Trades': 0,
                'Win_Rate': 0,
                'Total_Return_Pct': ((self.equity_curve[-1] - self.initial_capital) / self.initial_capital) * 100,
                'Max_Drawdown_Pct': 0,
                'Profit_Factor': 0
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Count trades
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['PnL'] > 0])
        losing_trades = len(trades_df[trades_df['PnL'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = trades_df['PnL'].sum()
        total_return_pct = (total_pnl / self.initial_capital) * 100
        
        # Profit factor
        gross_profit = trades_df[trades_df['PnL'] > 0]['PnL'].sum()
        gross_loss = abs(trades_df[trades_df['PnL'] < 0]['PnL'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown_pct = np.min(drawdown) * 100
        
        # Buy and hold benchmark
        buy_hold_return = ((backtest_data['Close'].iloc[-1] - backtest_data['Close'].iloc[0]) / 
                          backtest_data['Close'].iloc[0]) * 100
        
        stats = {
            'Total_Trades': total_trades,
            'Winning_Trades': winning_trades,
            'Losing_Trades': losing_trades,
            'Win_Rate_Pct': win_rate,
            'Total_Return_Pct': total_return_pct,
            'Avg_Trade_Return_Pct': trades_df['Return_Pct'].mean() if len(trades_df) > 0 else 0,
            'Max_Drawdown_Pct': max_drawdown_pct,
            'Profit_Factor': profit_factor,
            'Buy_Hold_Return_Pct': buy_hold_return,
            'Avg_Win': trades_df[trades_df['PnL'] > 0]['PnL'].mean() if winning_trades > 0 else 0,
            'Avg_Loss': trades_df[trades_df['PnL'] < 0]['PnL'].mean() if losing_trades > 0 else 0,
        }
        
        return stats
    
    
    def print_backtest_report(self, stats: dict):
        """Print formatted backtest report."""
        
        print("\n" + "="*70)
        print("BACKTEST REPORT (12-Month Historical Test)".center(70))
        print("="*70)
        
        print(f"\n[TRADE STATISTICS]")
        print(f"   Total Trades:            {int(stats.get('Total_Trades', 0)):>10}")
        print(f"   Winning Trades:          {int(stats.get('Winning_Trades', 0)):>10}")
        print(f"   Losing Trades:           {int(stats.get('Losing_Trades', 0)):>10}")
        print(f"   Win Rate:                {float(stats.get('Win_Rate_Pct', 0)):>9.1f}%")
        
        print(f"\n[PERFORMANCE METRICS]")
        print(f"   Strategy Return:         {float(stats.get('Total_Return_Pct', 0)):>9.2f}%")
        print(f"   Buy & Hold Return:       {float(stats.get('Buy_Hold_Return_Pct', 0)):>9.2f}%")
        print(f"   Avg Trade Return:        {float(stats.get('Avg_Trade_Return_Pct', 0)):>9.2f}%")
        print(f"   Max Drawdown:            {float(stats.get('Max_Drawdown_Pct', 0)):>9.2f}%")
        print(f"   Profit Factor:           {float(stats.get('Profit_Factor', 0)):>15.2f}")
        
        if stats.get('Winning_Trades', 0) > 0:
            print(f"\n[TRADE QUALITY]")
            print(f"   Avg Win:                 ${float(stats.get('Avg_Win', 0)):>10.2f}")
            print(f"   Avg Loss:                ${float(stats.get('Avg_Loss', 0)):>10.2f}")
            print(f"   Risk/Reward Ratio:       {abs(float(stats.get('Avg_Win', 1)) / float(stats.get('Avg_Loss', 1))):>10.2f}")
        
        print("\n" + "="*70)
        
        # Interpretation
        total_trades = int(stats.get('Total_Trades', 0))
        win_rate = float(stats.get('Win_Rate_Pct', 0))
        strat_return = float(stats.get('Total_Return_Pct', 0))
        bh_return = float(stats.get('Buy_Hold_Return_Pct', 0))
        
        if total_trades == 0:
            print("[WARNING] No trades generated in backtest period")
        elif win_rate > 50:
            print("[OK] Positive win rate - Strategy shows promise")
        else:
            print("[WARNING] Low win rate - Strategy may need refinement")
        
        if strat_return > bh_return:
            print("[OK] Outperformed buy & hold strategy")
        else:
            print("[INFO] Underperformed buy & hold - Consider position sizing")
        
        print("="*70)
    
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        return pd.DataFrame(self.trades)
