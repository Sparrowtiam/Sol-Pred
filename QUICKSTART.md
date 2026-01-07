# Quick Start Guide - SOL-USD Price Prediction System

## ✅ Installation Complete!

Your SOL-USD price prediction system is ready to use. Here's how to get started:

## 🚀 Running the System

```bash
# Navigate to the project directory
cd C:\Users\HP\Prediction

# Activate virtual environment
.\venv\Scripts\activate

# Run the analysis
python main.py
```

## 📁 Project Structure

```
Prediction/
├── main.py                 # Main entry point - run this
├── data_fetcher.py         # Data collection & feature engineering
├── model.py                # Prophet forecasting model
├── signals.py              # Trading signal generation
├── alerts.py               # Alert system (email, telegram)
├── visualization.py        # Charts and reports
├── backtester.py           # Historical backtesting
├── requirements.txt        # Python dependencies
└── README.md              # Full documentation
```

## 📊 What The System Does

1. **Data Collection**: Fetches 5 years of SOL-USD data from Yahoo Finance
2. **Feature Engineering**: Calculates 15+ technical indicators
3. **Prophet Forecasting**: Trains forecasting model, predicts 30 days forward
4. **Signal Generation**: Creates BUY/SELL/HOLD signals
5. **Risk Management**: Calculates stop-loss and take-profit levels
6. **Backtesting**: Tests strategy on 12 months of historical data
7. **Visualization**: Generates price charts with forecasts
8. **Alerts**: Sends notifications for trading signals

## 🎯 Output Files

- `sol_forecast_YYYYMMDD_HHMMSS.png` - Main price forecast chart
- `signal_history_YYYYMMDD_HHMMSS.png` - Signal history (if multiple signals)
- `prediction_output.txt` - Complete analysis output

## 📈 Interpreting Results

### Signal Types
- **BUY**: Price expected to rise, good entry point
- **SELL**: Price expected to fall, consider exiting
- **HOLD**: Mixed signals, wait for clearer setup

### Key Metrics
- **Confidence**: How certain the forecast is (0-100%)
- **Expected Upside**: Projected price movement %
- **Support/Resistance**: Price levels to watch

### Backtest Results
- **Win Rate**: % of trades that made profit (>50% is good)
- **Profit Factor**: Gross profit / Gross loss (>1.5 is excellent)
- **Max Drawdown**: Largest peak-to-trough decline

## ⚙️ Configuration

### Modify Signal Parameters
Edit `signals.py` line ~20:
```python
signal_gen = SignalGenerator(
    buy_momentum_threshold=0.0,
    rsi_oversold=30.0,
    rsi_overbought=70.0
)
```

### Modify Backtest Settings
Edit `backtester.py` line ~30:
```python
backtest_engine = BacktestEngine(
    initial_capital=10000,
    position_size_pct=0.95,
    stop_loss_pct=0.05,
    take_profit_pct=0.15
)
```

### Add Email Alerts
Set environment variables:
```bash
$env:SMTP_SERVER="smtp.gmail.com"
$env:SENDER_EMAIL="your_email@gmail.com"
$env:SENDER_PASSWORD="your_app_password"
$env:RECIPIENT_EMAIL="recipient@example.com"
```

### Add Telegram Alerts
```bash
$env:TELEGRAM_BOT_TOKEN="your_bot_token"
$env:TELEGRAM_CHAT_ID="your_chat_id"
```

## 🔄 Run Daily

Create a Windows Task Scheduler task:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at your preferred time
4. Set action:
   - Program: `C:\Users\HP\Prediction\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\HP\Prediction`

Or use this PowerShell command:
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At 09:00AM
$action = New-ScheduledTaskAction -Execute "C:\Users\HP\Prediction\venv\Scripts\python.exe" -Argument "main.py" -WorkingDirectory "C:\Users\HP\Prediction"
Register-ScheduledTask -TaskName "SOL-USD Prediction" -Trigger $trigger -Action $action -Description "Daily Solana price prediction"
```

## ⚠️ Important Disclaimers

1. **NOT Financial Advice** - This is educational software only
2. **No Guarantees** - Past performance ≠ future results
3. **High Risk** - Cryptocurrency is volatile and unpredictable
4. **Research Required** - Always conduct your own due diligence
5. **Limited Liabilities** - Use at your own risk

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Slow performance
- The Prophet model takes 1-2 minutes to train
- First run may fetch all 5 years of data
- Patience required!

### No chart display
- Charts are saved as PNG files automatically
- Check the `sol_forecast_*.png` files in the project directory

### Connection errors
- Yahoo Finance may be throttling requests
- Wait a few minutes and try again

## 📚 Learn More

- See `README.md` for complete documentation
- Review `main.py` for system flow
- Check individual modules for detailed explanations

## 🎓 Next Steps

1. Run the system and review the output
2. Study the generated charts
3. Examine the backtest results
4. Test different parameter combinations
5. Consider adding custom indicators
6. Integrate with your trading strategy

---

**Happy Analyzing!**

Remember: Knowledge is power. Always stay informed and trade responsibly.
