import requests
import pandas as pd
import json
import os
from rsi_divergence import calculate_rsi, find_divergences

# ================== CONFIG ==================
BASE_URL = "https://fapi.binance.com"
SYMBOL = "TAOUSDT"          # TAO on Binance spot
INTERVAL = "5m"
LIMIT = 1000                # Max klines Binance allows (covers ~3.5 days)
WEBHOOK_URL = "https://discord.com/api/webhooks/1488641396456820827/lxSndRn1_JKzhkk4KI9MtuKr3vyYweo6WMg2IynvbkaZokFKl3PIGf-MU_SdBd1ypdAD"  # ← CHANGE THIS
STATE_FILE = "last_notified.json"
# ===========================================

def fetch_klines():
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": SYMBOL, "interval": INTERVAL, "limit": LIMIT}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    df = df.astype(float)
    return df

def send_discord_notification(kind: str, row):
    message = f"""**🚨 TAO 5m Divergence Detected!**

**Type:** {kind.replace('_', ' ').title()}
**Price Pivot 1:** {row['p1_price']:.4f} @ {row['p1_idx']}
**Price Pivot 2:** {row['p2_price']:.4f} @ {row['p2_idx']}
**RSI Pivot 1:** {row['r1_val']:.2f}
**RSI Pivot 2:** {row['r2_val']:.2f}

Current price: {row['p2_price']:.4f} (latest candle)"""
    
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

# ================== MAIN ==================
if __name__ == "__main__":
    print(f"[{pd.Timestamp.now()}] Fetching TAO 5m data...")
    df = fetch_klines()
    prices = df['close']
    
    rsi = calculate_rsi(prices, period=14)
    divs = find_divergences(
        prices=prices,
        rsi=rsi,
        rsi_period=14,
        include_hidden=True
    )
    
    if divs.empty:
        print("No divergences found.")
    else:
        # Load last notified timestamp
        last_notified = None
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                last_notified = pd.to_datetime(data['last_p2_idx'])
        
        # Filter only NEW divergences
        new_divs = divs[divs['p2_idx'] > last_notified] if last_notified is not None else divs
        
        if not new_divs.empty:
            print(f"Found {len(new_divs)} new divergence(s)!")
            for _, row in new_divs.iterrows():
                kind = row['kind']
                send_discord_notification(kind, row)
                print(f"→ Notified: {kind}")
            
            # Update state with the newest pivot time
            max_p2 = new_divs['p2_idx'].max()
            with open(STATE_FILE, 'w') as f:
                json.dump({'last_p2_idx': str(max_p2)}, f)
        else:
            print("No new divergences since last check.")