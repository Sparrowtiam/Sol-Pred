"""
Alert system for trading signals (console, optional email and Telegram support).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


class AlertSystem:
    """Handle trading alerts through multiple channels."""
    
    def __init__(self, 
                 telegram_token: str = None,
                 telegram_chat_id: str = None,
                 email_config: dict = None):
        """
        Initialize alert system.
        
        Args:
            telegram_token: Telegram bot token (optional)
            telegram_chat_id: Telegram chat ID (optional)
            email_config: Dict with email configuration (optional)
        """
        self.telegram_token = telegram_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = telegram_chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.email_config = email_config or {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL')
        }
        self.alerts_log = []
    
    
    def send_alert(self, signal: dict, atr: float = None, stop_loss: float = None, take_profit: float = None):
        """
        Send alert for trading signal through all available channels.
        
        Args:
            signal: Signal dictionary from SignalGenerator
            atr: Average True Range for risk management
            stop_loss: Stop-loss price level
            take_profit: Take-profit price level
        """
        alert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_type = signal['Type']
        confidence = signal['Confidence']
        current_price = signal['Current_Price']
        expected_upside = signal['Expected_Upside_Pct']
        
        # Create alert message
        if signal_type == 'BUY':
            emoji = "🔥"
            alert_message = self._format_buy_alert(
                current_price, 
                expected_upside, 
                confidence,
                stop_loss,
                take_profit,
                alert_time
            )
        elif signal_type == 'SELL':
            emoji = "⚠️"
            alert_message = self._format_sell_alert(
                current_price,
                expected_upside,
                confidence,
                alert_time
            )
        else:
            emoji = "📊"
            alert_message = self._format_hold_alert(current_price, alert_time)
        
        # Console alert
        self._print_console_alert(emoji, signal_type, alert_message)
        
        # Send to other channels
        if self.telegram_token and self.telegram_chat_id:
            self._send_telegram_alert(emoji, signal_type, alert_message)
        
        if all(self.email_config.values()):
            self._send_email_alert(emoji, signal_type, alert_message)
        
        # Log alert
        self.alerts_log.append({
            'Timestamp': alert_time,
            'Type': signal_type,
            'Price': current_price,
            'Confidence': confidence,
            'Message': alert_message
        })
    
    
    def _format_buy_alert(self, 
                         price: float,
                         upside_pct: float,
                         confidence: float,
                         stop_loss: float = None,
                         take_profit: float = None,
                         timestamp: str = None) -> str:
        """Format BUY signal alert."""
        days_estimate = "7-30"  # Based on 7-30 day forecast
        
        message = f"""
🔥 BUY SIGNAL TRIGGERED 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: {timestamp}
Current Price: ${price:.2f}
Expected Upside: {upside_pct:.2f}% over {days_estimate} days
Confidence Level: {confidence:.0f}%

Technical Setup:
✓ Positive momentum detected
✓ Price near support level
✓ Favorable technical indicators

Risk Management:
"""
        if stop_loss:
            message += f"Stop Loss: ${stop_loss:.2f}\n"
        if take_profit:
            message += f"Take Profit: ${take_profit:.2f}\n"
        
        message += """
⚠️  DISCLAIMER: This is a statistical forecast, NOT financial advice.
Past performance does not guarantee future results.
Always conduct your own research before trading.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return message
    
    
    def _format_sell_alert(self,
                          price: float,
                          downside_pct: float,
                          confidence: float,
                          timestamp: str = None) -> str:
        """Format SELL signal alert."""
        
        message = f"""
⚠️ SELL SIGNAL TRIGGERED ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: {timestamp}
Current Price: ${price:.2f}
Downside Risk: {abs(downside_pct):.2f}%
Confidence Level: {confidence:.0f}%

Technical Setup:
✓ Downtrend detected in forecast
✓ Price near resistance level
✓ Caution indicators activated

Action: Consider closing positions or reducing exposure.

⚠️  DISCLAIMER: This is a statistical forecast, NOT financial advice.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return message
    
    
    def _format_hold_alert(self, price: float, timestamp: str = None) -> str:
        """Format HOLD signal alert."""
        
        message = f"""
📊 HOLD SIGNAL 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: {timestamp}
Current Price: ${price:.2f}

Action: Hold current position. Mixed signals detected.
Wait for clearer setup before entering new positions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return message
    
    
    def _print_console_alert(self, emoji: str, signal_type: str, message: str):
        """Print alert to console."""
        print(f"\n{emoji} {signal_type} ALERT {emoji}")
        print(message)
    
    
    def _send_telegram_alert(self, emoji: str, signal_type: str, message: str):
        """Send alert via Telegram."""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Alert sent via Telegram")
            else:
                print(f"❌ Telegram alert failed: {response.text}")
        except Exception as e:
            print(f"⚠️ Could not send Telegram alert: {e}")
    
    
    def _send_email_alert(self, emoji: str, signal_type: str, message: str):
        """Send alert via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"{emoji} SOL-USD {signal_type} Signal Alert"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            print("✅ Alert sent via Email")
        except Exception as e:
            print(f"⚠️ Could not send email alert: {e}")
    
    
    def get_alerts_log(self) -> list:
        """Get all alerts sent."""
        return self.alerts_log
