import yfinance as yf, requests, os, pandas as pd
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(msg):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)

try:
    usoil = yf.download("USO", period="5d", interval="1h", auto_adjust=True)
    if len(usoil) < 30:
        send("⚠️ USOIL маалымат аз")
    else:
        close = usoil['Close']
        rsi = 100 - (100 / (1 + close.diff().where(close.diff()>0,0).rolling(14).mean() / -close.diff().where(close.diff()<0,0).rolling(14).mean()))
        curr_rsi = float(rsi.iloc[-1])
        price = float(close.iloc[-1])
        ema = float(close.ewm(span=21).mean().iloc[-1])
        
        if curr_rsi < 35 and price > ema:
            send(f"🟢 <b>USOIL 100% BUY</b>\nБаа: {price:.2f}\nRSI: {curr_rsi:.1f}\nTP: +2% SL: -1%")
        elif curr_rsi > 65 and price < ema:
            send(f"🔴 <b>USOIL 100% SELL</b>\nБаа: {price:.2f}\nRSI: {curr_rsi:.1f}\nTP: -2% SL: +1%")
        else:
            send(f"✅ Бот текшерилди\nUSOIL: {price:.2f} RSI: {curr_rsi:.1f}\n100% сигнал жок")
except Exception as e:
    send(f"❌ Ката: {e}")
