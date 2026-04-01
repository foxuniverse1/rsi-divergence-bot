import ccxt
import pandas as pd
import time
import requests
from datetime import datetime

import os
# Add this to make Render happy on free Web Service
port = int(os.environ.get("PORT", 10000))
print(f"Listening on port {port} (for Render free tier)")

# === EASY SETTINGS TO CHANGE ===
SYMBOL = 'TAO/USDT'      # Change coin here (e.g. 'ETH/USDT')
TIMEFRAME = '5m'        # Change timeframe here ('5m', '15m', '30m', '1h')
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488641396456820827/lxSndRn1_JKzhkk4KI9MtuKr3vyYweo6WMg2IynvbkaZokFKl3PIGf-MU_SdBd1ypdAD"  # ← Paste your real Discord webhook

exchange = ccxt.binance({'enableRateLimit': True})

def send_to_discord(message):
    if "YOUR_WEBHOOK_URL_HERE" in DISCORD_WEBHOOK_URL:
        print("Discord webhook not set yet")
        return
    payload = {"content": message, "username": "RSI Divergence Bot"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print("✅ Alert sent to Discord")
    except Exception as e:
        print("Discord send error:", e)

# Simple RSI calculation (no pandas_ta needed)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Check for divergences
def check_for_divergence():
    try:
        bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=300)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate RSI manually
        df['rsi'] = calculate_rsi(df['close'])
        
        if len(df) < 80:
            return
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        
        # Basic Bullish Divergence
        recent_price_low = df['low'].iloc[-40:].min()
        earlier_price_low = df['low'].iloc[-80:-40].min()
        recent_rsi_low = df['rsi'].iloc[-40:].min()
        earlier_rsi_low = df['rsi'].iloc[-80:-40].min()
        
        if (recent_price_low < earlier_price_low and 
            recent_rsi_low > earlier_rsi_low and 
            current_rsi < 45):
            
            msg = f"🚀 **Bullish RSI Divergence Detected!**\n" \
                  f"Symbol: {SYMBOL}\n" \
                  f"Timeframe: {TIMEFRAME}\n" \
                  f"Price: {current_price:.4f}\n" \
                  f"RSI: {current_rsi:.2f}\n" \
                  f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            send_to_discord(msg)
            print(msg)
        
        # Basic Bearish Divergence
        recent_price_high = df['high'].iloc[-40:].max()
        earlier_price_high = df['high'].iloc[-80:-40].max()
        recent_rsi_high = df['rsi'].iloc[-40:].max()
        earlier_rsi_high = df['rsi'].iloc[-80:-40].max()
        
        if (recent_price_high > earlier_price_high and 
            recent_rsi_high < earlier_rsi_high and 
            current_rsi > 55):
            
            msg = f"🔻 **Bearish RSI Divergence Detected!**\n" \
                  f"Symbol: {SYMBOL}\n" \
                  f"Timeframe: {TIMEFRAME}\n" \
                  f"Price: {current_price:.4f}\n" \
                  f"RSI: {current_rsi:.2f}\n" \
                  f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            send_to_discord(msg)
            print(msg)
            
    except Exception as e:
        print("Error:", e)

print(f"✅ Bot started watching {SYMBOL} on {TIMEFRAME}...")
while True:
    check_for_divergence()
    time.sleep(300)  # Check every 5 minutes
