import ccxt
import pandas as pd
import time
import requests
from datetime import datetime

# === YOUR SETTINGS ===
SYMBOL = 'TAO/USDT'          # Change to your coin
TIMEFRAME = '5m'            # Change to '5m', '30m', '1h' etc.
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488641396456820827/lxSndRn1_JKzhkk4KI9MtuKr3vyYweo6WMg2IynvbkaZokFKl3PIGf-MU_SdBd1ypdAD"  # ← Paste your real one

exchange = ccxt.binance({'enableRateLimit': True})

def send_to_discord(message):
    payload = {"content": message, "username": "RSI Divergence Bot"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print("✅ Sent to Discord")
    except Exception as e:
        print("Discord error:", e)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_for_divergence():
    try:
        bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=300)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['rsi'] = calculate_rsi(df['close'])
        
        if len(df) < 80:
            return
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        
        # Bullish Divergence
        if (df['low'].iloc[-40:].min() < df['low'].iloc[-80:-40].min() and
            df['rsi'].iloc[-40:].min() > df['rsi'].iloc[-80:-40].min() and
            current_rsi < 45):
            msg = f"🚀 **Bullish RSI Divergence!**\n{SYMBOL} {TIMEFRAME}\nPrice: {current_price:.4f}\nRSI: {current_rsi:.2f}\n{datetime.now().strftime('%H:%M')}"
            send_to_discord(msg)
            print(msg)
        
        # Bearish Divergence
        if (df['high'].iloc[-40:].max() > df['high'].iloc[-80:-40].max() and
            df['rsi'].iloc[-40:].max() < df['rsi'].iloc[-80:-40].max() and
            current_rsi > 55):
            msg = f"🔻 **Bearish RSI Divergence!**\n{SYMBOL} {TIMEFRAME}\nPrice: {current_price:.4f}\nRSI: {current_rsi:.2f}\n{datetime.now().strftime('%H:%M')}"
            send_to_discord(msg)
            print(msg)
            
    except Exception as e:
        print("Error:", e)

print(f"✅ Bot watching {SYMBOL} on {TIMEFRAME}...")
while True:
    check_for_divergence()
    time.sleep(300)  # 5 minutes
