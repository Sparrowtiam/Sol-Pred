# SOL-USD Price Prediction System

A comprehensive quantitative analysis and forecasting system for Solana (SOL-USD) using Facebook Prophet, technical indicators, and machine learning-based trading signals.

## 🎯 Overview

This project predicts Solana cryptocurrency prices using:
- **Facebook Prophet**: Time-series forecasting with seasonality detection
- **Technical Indicators**: RSI, Moving Averages, ATR, Momentum, Volatility
- **Trading Signals**: Intelligent BUY/SELL/HOLD signals based on multiple factors
- **Risk Management**: Stop-loss and take-profit levels
- **Backtesting**: Historical performance evaluation
- **Alerts**: Console, Email, and Telegram notifications

## ✨ Features

### 1. **Data Collection**
- Automatic data fetching from Yahoo Finance
- 5 years of historical daily data
- Missing value handling with interpolation
- Outlier detection using IQR method

### 2. **Feature Engineering**
- Moving Averages: 7, 14, 30-day periods
- Volatility: 14-day rolling standard deviation
- Average True Range (ATR) for risk measurement
- Momentum indicator (10-day)
- Relative Strength Index (RSI)
- Daily returns calculation

### 3. **Prophet Model**
- Weekly seasonality enabled
- Yearly seasonality enabled
- Changepoint detection for trend shifts
- 95% confidence intervals
- 30-day forward forecast

### 4. **Trading Signals**
Signals are generated based on:
- **Price Momentum**: Positive/negative momentum direction
- **Trend Analysis**: Moving average relationships
- **Momentum Confirmation**: Price crossing forecast
- **Overbought/Oversold**: RSI levels (>70 sell, <30 buy)
- **Distance to Extrema**: Price proximity to forecast min/max

Signal Strength:
- **BUY**: 3+ conditions met with positive forecast trend
- **SELL**: Bearish indicators or overbought conditions
- **HOLD**: Mixed signals, unclear setup

### 5. **Risk Management**
Calculates:
- Stop-loss levels (ATR-based and forecast-based)
- Take-profit targets (local maxima + buffer)
- Risk/Reward ratio evaluation
- Position sizing recommendations

### 6. **Backtesting Engine**
- 12-month historical backtest
- Trade tracking with entry/exit prices
- Win rate calculation
- Profit factor analysis
- Maximum drawdown measurement
- Comparison with buy & hold strategy

### 7. **Multi-Channel Alerts**
- Console alerts with emoji indicators
- Email notifications (optional)
- Telegram bot support (optional)
- Detailed alert messages with price levels

### 8. **Visualization**
- Historical vs. forecast price chart
- 95% confidence intervals
- Moving averages overlays
- Buy/Sell signal markers
- Volatility indicator plot
- RSI indicator plot
- Signal history tracking

## 📋 Project Structure

```
Prediction/
├── main.py                 # Main execution script
├── data_fetcher.py        # Data collection & feature engineering
├── model.py               # Prophet model training & forecasting
├── signals.py             # Trading signal generation
├── alerts.py              # Alert system (console, email, telegram)
├── visualization.py       # Charts and reports
├── backtester.py          # Historical backtesting engine
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running the System

```bash
python main.py
```

The script will:
1. Fetch 5 years of SOL-USD data
2. Engineer technical features
3. Train Prophet model
4. Generate 30-day forecast
5. Calculate trading signals
6. Run 12-month backtest
7. Create visualizations
8. Display comprehensive report

## 📊 Output Examples

### Console Output
```
SOL-USD PRICE PREDICTION SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRICE OVERVIEW
Current Price: $100.50
7-Day Forecast: $105.25 (+4.74%)
30-Day Forecast: $108.00 (+7.46%)

TECHNICAL LEVELS
Support Level: $95.00 (-5.46%)
Resistance Level: $115.00 (+14.43%)

TRADING SIGNAL
Signal Type: BUY
Confidence: 85%
Expected Upside: +4.74%
```

### Generated Charts
- `sol_forecast_YYYYMMDD_HHMMSS.png` - Main forecast chart
- `signal_history_YYYYMMDD_HHMMSS.png` - Signal history (if multiple signals)

## 🔧 Configuration

### Signal Generator Parameters
Edit in `signals.py`:
```python
signal_gen = SignalGenerator(
    buy_momentum_threshold=0.0,
    rsi_oversold=30.0,
    rsi_overbought=70.0
)
```

### Backtest Parameters
Edit in `backtester.py`:
```python
backtest_engine = BacktestEngine(
    initial_capital=10000,
    position_size_pct=0.95,
    stop_loss_pct=0.05,      # 5% stop-loss
    take_profit_pct=0.15     # 15% take-profit
)
```

### Prophet Model Parameters
Edit in `model.py`:
```python
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10.0
)
```

## 🔔 Setting Up Alerts (Optional)

### Email Alerts
Set environment variables:
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your_email@gmail.com
export SENDER_PASSWORD=your_app_password
export RECIPIENT_EMAIL=recipient@example.com
```

### Telegram Alerts
Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id
```

## 📈 Trading Strategy Explanation

### BUY Signal Conditions
1. Forecasted price crosses above current price
2. Positive momentum detected
3. RSI indicates oversold condition (< 30) OR price near support
4. Price above 7-day moving average
5. Confidence level > 75%

### SELL Signal Conditions
1. Forecasted bearish trend (price falling)
2. RSI overbought (> 70) OR resistance breach
3. Negative momentum confirmed
4. Price near local maximum in forecast
5. High volatility risk detected

### Risk Management
- **Stop-Loss**: Based on ATR × 1.5 or forecast local minimum
- **Take-Profit**: Based on ATR × 3.0 or forecast local maximum
- **Position Sizing**: 95% of capital per trade (adjustable)
- **Risk/Reward**: Target minimum 1:2 ratio

## ⚠️ Important Disclaimers

1. **NOT Financial Advice**: This system is for educational purposes only
2. **No Guarantees**: Past performance ≠ future results
3. **Volatility**: Cryptocurrency markets are highly unpredictable
4. **Backtest Bias**: Historical results may not reflect live trading
5. **Risk Capital**: Only invest what you can afford to lose
6. **Research**: Always conduct your own due diligence
7. **Professional Advice**: Consider consulting a financial advisor

## 📚 Key Libraries

| Library | Purpose |
|---------|---------|
| `prophet` | Time-series forecasting |
| `yfinance` | Historical price data |
| `pandas` | Data manipulation |
| `numpy` | Numerical computing |
| `matplotlib` | Visualization |
| `plotly` | Interactive charts |

## 🧪 Backtesting Results Interpretation

### Key Metrics
- **Win Rate**: % of trades that made profit
- **Profit Factor**: Gross profit / Gross loss (>1.5 is good)
- **Max Drawdown**: Largest peak-to-trough decline
- **Strategy Return vs Buy & Hold**: Relative performance

### Signal Accuracy
The backtest uses simplified signal logic. Live results may differ due to:
- Slippage and fees
- Order execution delays
- Market microstructure
- Gap risk in volatile markets

## 🔄 Continuous Monitoring

Run the script daily/weekly:

```bash
# Windows Task Scheduler
# Or use a cron job on Linux
@daily python C:\Users\HP\Prediction\main.py
```

Monitor alert messages and update stop-loss/take-profit as needed.

## 🐛 Troubleshooting

### "No module named 'prophet'"
```bash
pip install prophet
```

### yfinance connection issues
```bash
pip install --upgrade yfinance
```

### Matplotlib display issues
```bash
pip install matplotlib plotly
```

### Virtual environment not activating
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## 📝 Example Output Files

1. **Price Forecast Chart** - Shows historical prices, forecast, and confidence intervals
2. **Signal Markers** - Buy/Sell points marked on chart
3. **Technical Indicators** - Volatility and RSI plots
4. **Backtest Report** - Win rate, profit factor, max drawdown
5. **Summary Report** - Complete analysis with levels and recommendations

## 🚀 Advanced Usage

### Custom Signal Logic
Modify `SignalGenerator.generate_signals()` in `signals.py` to add:
- Bollinger Band analysis
- MACD indicators
- Ichimoku cloud
- Custom ML models

### Integration with Trading Bots
Export signals to APIs:
- Binance API
- Kraken API
- Coinbase API
- Tradingview Webhooks

### Machine Learning Enhancements
Add ensemble models:
- LSTM neural networks
- Random Forest
- XGBoost
- Hybrid Prophet + ML

## 📞 Support

For issues or improvements:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Review error messages carefully
4. Check for data availability from Yahoo Finance

## 📜 License

Educational use only. Use at your own risk.

## 🎓 Learning Resources

- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Technical Analysis](https://investopedia.com/technical-analysis)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)
- [Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Author**: Quantitative Python Developer

⚠️ **REMINDER**: This is educational software. Cryptocurrency trading involves substantial risk. Past results do not guarantee future performance.
