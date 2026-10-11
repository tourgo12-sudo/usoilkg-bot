import yfinance as yf, pandas as pd, requests, os
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=20)

try:
    df = yf.download("CL=F", period="5d", interval="15m", auto_adjust=True)
    close = df['Close'].values.flatten()
    
    s = pd.Series(close)
    delta = s.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rsi = 100 - (100 / (1 + gain/loss))
    rsi_now = float(rsi.iloc[-1])
    ema50 = float(s.ewm(span=50).mean().iloc[-1])
    ema200 = float(s.ewm(span=200).mean().iloc[-1])
    price = float(close[-1])

    # 100% СТРАТЕГИЯ - US CRUDE OIL
    if price > ema50 > ema200 and 55 < rsi_now < 75:
        sl = price * 0.993
        tp1 = price * 1.008
        tp2 = price * 1.018
        msg = f"""🛢️ <b>US crude oil 100% LONG</b>
💰 Entry: ${price:.2f}
❌ SL: ${sl:.2f}
✅ TP1: ${tp1:.2f}
✅ TP2: ${tp2:.2f}
📊 RSI: {rsi_now:.1f} | EMA50: ${ema50:.2f}
RR 1:2.5"""
        send(msg)
    elif price < ema50 < ema200 and 25 < rsi_now < 45:
        sl = price * 1.007
        tp1 = price * 0.992
        tp2 = price * 0.982
        msg = f"""🛢️ <b>US crude oil 100% SHORT</b>
💰 Entry: ${price:.2f}
❌ SL: ${sl:.2f}
✅ TP1: ${tp1:.2f}
✅ TP2: ${tp2:.2f}
📊 RSI: {rsi_now:.1f} | EMA50: ${ema50:.2f}
RR 1:2.5"""
        send(msg)

except Exception as e:
    send(f"❌ {e}")
