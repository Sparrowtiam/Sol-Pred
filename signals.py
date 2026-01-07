"""
Buy/Sell signal generation module based on Prophet forecast and technical indicators.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class SignalGenerator:
    """Generate trading signals based on forecast and technical indicators."""
    
    def __init__(self, 
                 buy_momentum_threshold: float = 0.0,
                 rsi_oversold: float = 30.0,
                 rsi_overbought: float = 70.0):
        """
        Initialize signal generator.
        
        Args:
            buy_momentum_threshold: Minimum momentum for buy signal
            rsi_oversold: RSI threshold for oversold condition
            rsi_overbought: RSI threshold for overbought condition
        """
        self.buy_momentum_threshold = buy_momentum_threshold
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.signals_history = []
    
    
    def generate_signals(self, 
                        current_price: float,
                        forecast_df: pd.DataFrame,
                        features_df: pd.DataFrame) -> dict:
        """
        Generate BUY, SELL, or HOLD signals based on multiple factors.
        
        Args:
            current_price: Current SOL-USD price
            forecast_df: Prophet forecast DataFrame
            features_df: DataFrame with technical indicators
            
        Returns:
            Dictionary with signal information
        """
        # Get future forecast
        future_forecast = forecast_df[forecast_df['Date'] > pd.Timestamp.now()]
        
        if len(future_forecast) < 7:
            return self._create_signal('HOLD', 'Insufficient forecast data', 20, current_price)
        
        # Get recent indicators
        latest_rsi = features_df['RSI'].iloc[-1]
        latest_momentum = features_df['Momentum'].iloc[-1]
        latest_volatility = features_df['Volatility'].iloc[-1]
        ma7 = features_df['MA7'].iloc[-1]
        ma14 = features_df['MA14'].iloc[-1]
        ma30 = features_df['MA30'].iloc[-1]
        
        # Get forecast metrics
        forecast_7d = future_forecast.iloc[min(6, len(future_forecast)-1)]['Forecast']
        local_min = future_forecast['Forecast'].min()
        local_max = future_forecast['Forecast'].max()
        forecast_trend = forecast_7d - current_price
        
        # Calculate distances to extrema
        distance_to_min = abs(current_price - local_min) / local_min
        distance_to_max = abs(current_price - local_max) / local_max
        
        signal_strength = 0
        signal_reasons = []
        
        # ===== BUY Signal Logic =====
        buy_conditions = []
        
        # Condition 1: Price crosses above forecast (uptrend)
        if forecast_trend > 0:
            buy_conditions.append(True)
            signal_strength += 20  # Increased weight
            signal_reasons.append("✓ Forecasted uptrend detected")
        else:
            signal_reasons.append("✗ Forecasted downtrend")
        
        # Condition 2: Positive momentum
        if latest_momentum > self.buy_momentum_threshold:
            buy_conditions.append(True)
            signal_strength += 18  # Increased weight
            signal_reasons.append(f"✓ Positive momentum: {latest_momentum:.2f}")
        else:
            signal_reasons.append(f"✗ Weak momentum: {latest_momentum:.2f}")
        
        # Condition 3: Price near local minimum (good entry)
        if distance_to_min < 0.05:  # Within 5% of local min
            buy_conditions.append(True)
            signal_strength += 20  # Increased from 10
            signal_reasons.append(f"✓ Near local minimum (5% threshold)")
        elif distance_to_min < 0.10:
            signal_strength += 12  # Increased from 5
            signal_reasons.append(f"✓ Near local minimum (10% threshold)")
        elif distance_to_min < 0.15:
            signal_strength += 8
            signal_reasons.append(f"✓ Near local minimum (15% threshold)")
        
        # Condition 4: RSI oversold (good entry)
        if latest_rsi < self.rsi_oversold:
            buy_conditions.append(True)
            signal_strength += 22  # Increased from 15
            signal_reasons.append(f"✓ RSI oversold: {latest_rsi:.2f}")
        elif latest_rsi < 40:
            signal_strength += 12
            signal_reasons.append(f"✓ RSI neutral-low: {latest_rsi:.2f}")
        
        # Condition 5: Price above key moving averages
        if current_price > ma7 > ma14 > ma30:
            buy_conditions.append(True)
            signal_strength += 18  # Increased from 5
            signal_reasons.append(f"✓ Price above all moving averages")
        elif current_price > ma7 > ma14:
            signal_strength += 12  # Added new tier
            signal_reasons.append(f"✓ Price above MA7 and MA14")
        elif current_price > ma7:
            signal_strength += 8  # Increased from 2
            signal_reasons.append(f"✓ Price above MA7")
        
        # ===== SELL Signal Logic =====
        sell_conditions = []
        
        # Condition 1: Bearish forecast
        if forecast_trend < 0:
            sell_conditions.append(True)
            signal_strength += 18  # Increased from implicit
            signal_reasons.append("✓ Forecasted downtrend")
        
        # Condition 2: Negative momentum (deteriorating)
        if latest_momentum < -self.buy_momentum_threshold:
            sell_conditions.append(True)
            signal_strength += 16  # Increased
            signal_reasons.append(f"✓ Negative momentum: {latest_momentum:.2f}")
        elif latest_momentum < 0:
            signal_strength += 8
            signal_reasons.append(f"✓ Weakening momentum: {latest_momentum:.2f}")
        
        # Condition 3: Price near local maximum (good exit)
        if distance_to_max < 0.05:
            sell_conditions.append(True)
            signal_strength += 20  # Increased from 15
            signal_reasons.append(f"✓ Near local maximum (5% threshold)")
        elif distance_to_max < 0.10:
            signal_strength += 14  # Increased from 8
            signal_reasons.append(f"✓ Near local maximum (10% threshold)")
        elif distance_to_max < 0.15:
            signal_strength += 10
            signal_reasons.append(f"✓ Near local maximum (15% threshold)")
        
        # Condition 4: RSI overbought (good exit)
        if latest_rsi > self.rsi_overbought:
            sell_conditions.append(True)
            signal_strength += 22  # Increased from 15
            signal_reasons.append(f"✓ RSI overbought: {latest_rsi:.2f}")
        elif latest_rsi > 60:
            signal_strength += 12  # Added new tier
            signal_reasons.append(f"✓ RSI elevated: {latest_rsi:.2f}")
        
        # Condition 5: High volatility risk
        if latest_volatility > features_df['Volatility'].quantile(0.90):  # Changed to 90th percentile
            sell_conditions.append(True)
            signal_strength += 15  # Increased from 5
            signal_reasons.append(f"✓ Extreme volatility risk: {latest_volatility:.2f}")
        elif latest_volatility > features_df['Volatility'].quantile(0.75):
            signal_strength += 10  # Added tier
            signal_reasons.append(f"✓ High volatility risk: {latest_volatility:.2f}")
        
        # Condition 6: Death cross (MA7 < MA14 < MA30)
        if ma7 < ma14 and ma14 < ma30:
            sell_conditions.append(True)
            signal_strength += 18  # Increased from 10
            signal_reasons.append(f"✓ Death cross detected (MA7 < MA14 < MA30)")
        elif ma7 < ma14:
            signal_strength += 10
            signal_reasons.append(f"✓ Bearish MA crossover (MA7 < MA14)")
        
        # ===== Determine Final Signal =====
        # Strong buy: All conditions align
        if len(buy_conditions) >= 3 and forecast_trend > 0 and latest_momentum > 0:
            return self._create_signal(
                'BUY',
                f"Strong buy signal with {len(buy_conditions)} conditions met",
                min(95, signal_strength + 45),  # Increased boost
                current_price,
                forecast_7d,
                signal_reasons
            )
        
        # Moderate buy: Most conditions align
        elif len(buy_conditions) >= 2 and forecast_trend > 0:
            return self._create_signal(
                'BUY',
                f"Buy signal with {len(buy_conditions)} conditions met",
                min(85, signal_strength + 35),  # Increased boost
                current_price,
                forecast_7d,
                signal_reasons
            )
        
        # Weak buy: Some positive signals
        elif len(buy_conditions) >= 1 and forecast_trend > 0:
            return self._create_signal(
                'BUY',
                f"Weak buy signal - {len(buy_conditions)} condition(s) met",
                min(70, signal_strength + 25),
                current_price,
                forecast_7d,
                signal_reasons
            )
        
        # Strong sell: Multiple negative conditions
        elif len(sell_conditions) >= 3 or (latest_rsi > self.rsi_overbought and forecast_trend < 0):
            return self._create_signal(
                'SELL',
                f"Strong sell signal with {len(sell_conditions)} conditions met",
                min(90, signal_strength + 40),  # Increased boost
                current_price,
                forecast_7d,
                signal_reasons
            )
        
        # Moderate sell: Some negative conditions
        elif len(sell_conditions) >= 2:
            return self._create_signal(
                'SELL',
                f"Sell signal with {len(sell_conditions)} conditions met",
                min(75, signal_strength + 25),  # Increased boost
                current_price,
                forecast_7d,
                signal_reasons
            )
        
        # Hold: Unclear signals but not completely neutral
        else:
            return self._create_signal(
                'HOLD',
                "Mixed signals - Hold current position",
                max(50, min(65, signal_strength + 10)),  # Better baseline for hold
                current_price,
                forecast_7d,
                signal_reasons
            )
    
    
    def _create_signal(self, 
                      signal_type: str,
                      reason: str,
                      confidence: float,
                      current_price: float,
                      forecast_price: float = None,
                      details: list = None) -> dict:
        """
        Create a signal dictionary.
        
        Args:
            signal_type: 'BUY', 'SELL', or 'HOLD'
            reason: String explanation
            confidence: Confidence score (0-100)
            current_price: Current price
            forecast_price: Forecasted price
            details: List of detailed reasons
            
        Returns:
            Signal dictionary
        """
        signal = {
            'Type': signal_type,
            'Reason': reason,
            'Confidence': min(100, max(0, confidence)),  # Clamp 0-100
            'Timestamp': datetime.now(),
            'Current_Price': current_price,
            'Forecast_Price': forecast_price,
            'Details': details or [],
            'Expected_Upside_Pct': ((forecast_price - current_price) / current_price * 100) if forecast_price else 0
        }
        
        self.signals_history.append(signal)
        return signal
    
    
    def get_signal_history(self) -> pd.DataFrame:
        """Get historical signals as DataFrame."""
        return pd.DataFrame(self.signals_history)
