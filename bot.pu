import ccxt
import pandas as pd
import pandas_ta as ta
import time
import requests
import os
from datetime import datetime
import numpy as np
from scipy.signal import argrelextrema

# === CHANGE THESE SETTINGS ===
SYMBOL = 'TAO/USDT'      # Change to your pair, e.g. 'ETH/USDT'
TIMEFRAME = '5m'        # Options: '5m', '15m', '30m', '1h'
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488641396456820827/lxSndRn1_JKzhkk4KI9MtuKr3vyYweo6WMg2IynvbkaZokFKl3PIGf-MU_SdBd1ypdAD"  # ← Paste your Discord webhook URL here

exchange = ccxt.binance({'enableRateLimit': True})

def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL or "YOUR_WEBHOOK_URL_HERE" in DISCORD_WEBHOOK_URL:
        print("Discord webhook not set up yet")
        return
    payload = {
        "content": message,
        "username": "RSI Divergence Bot"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print("✅ Alert sent to Discord")
    except Exception as e:
        print("Could not send to Discord:", e)

# Simple RSI Divergence Checker (Bullish & Bearish)
def check_for_divergence():
    try:
        bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=300)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        if len(df) < 60:
            return
        
        # Basic Bullish Divergence: Price makes lower low, RSI makes higher low (and RSI oversold-ish)
        recent_price_low = df['low'].iloc[-40:].min()
        earlier_price_low = df['low'].iloc[-80:-40].min()
        recent_rsi_low = df['rsi'].iloc[-40:].min()
        earlier_rsi_low = df['rsi'].iloc[-80:-40].min()
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        
        if (recent_price_low < earlier_price_low and 
            recent_rsi_low > earlier_rsi_low and 
            current_rsi < 45):  # RSI is relatively low
            
            msg = f"🚀 **Bullish RSI Divergence Detected!**\n" \
                  f"Symbol: {SYMBOL}\n" \
                  f"Timeframe: {TIMEFRAME}\n" \
                  f"Current Price: {current_price:.4f}\n" \
                  f"Current RSI: {current_rsi:.2f}\n" \
                  f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            send_to_discord(msg)
            print(msg)
        
        # Basic Bearish Divergence: Price makes higher high, RSI makes lower high (and RSI overbought-ish)
        recent_price_high = df['high'].iloc[-40:].max()
        earlier_price_high = df['high'].iloc[-80:-40].max()
        recent_rsi_high = df['rsi'].iloc[-40:].max()
        earlier_rsi_high = df['rsi'].iloc[-80:-40].max()
        
        if (recent_price_high > earlier_price_high and 
            recent_rsi_high < earlier_rsi_high and 
            current_rsi > 55):  # RSI is relatively high
            
            msg = f"🔻 **Bearish RSI Divergence Detected!**\n" \
                  f"Symbol: {SYMBOL}\n" \
                  f"Timeframe: {TIMEFRAME}\n" \
                  f"Current Price: {current_price:.4f}\n" \
                  f"Current RSI: {current_rsi:.2f}\n" \
                  f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            send_to_discord(msg)
            print(msg)
            
    except Exception as e:
        print("Error fetching data or checking divergence:", e)

# Main loop - checks roughly every 5 minutes (adjust if needed)
print(f"Bot started watching {SYMBOL} on {TIMEFRAME}...")
while True:
    check_for_divergence()
    time.sleep(300)  # 300 seconds = 5 minutes
