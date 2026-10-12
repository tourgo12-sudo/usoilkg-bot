import os, requests, time, threading
from flask import Flask
import yfinance as yf
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@xauusdakyl")
app = Flask(__name__)

@app.route("/")
def home(): return "USOIL AMD PRO LIVE"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"SEND OK")
    except Exception as e: print(f"ERR {e}")

def get_rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    return 100-(100/(1+g/l))

def check_amd(df):
    try:
        # Азия сессиясы 22:00-06:00 Bishkek
        # yfinance UTC берет, ошондуктан акыркы 12 саатты Азия деп алабыз
        asia = df.tail(12)
        asia_high = asia['High'].max()
        asia_low = asia['Low'].min()
        price = float(df['Close'].iloc[-1])
        high2 = float(df['High'].iloc[-2])
        close2 = float(df['Close'].iloc[-2])
        
        print(f"ASIA {asia_low:.2f}-{asia_high:.2f} PRICE {price:.2f}")

        # Манипуляция + Дистрибуция
        if high2 > asia_high and price < asia_high and price < asia_low:
            return f"SHORT 🔴 AMD\nАзия High {asia_high:.2f} алдап, ылдый сындырды"
        if float(df['Low'].iloc[-2]) < asia_low and price > asia_low and price > asia_high:
            return f"LONG 🟢 AMD\nАзия Low {asia_low:.2f} алдап, өйдө сындырды"
        return None
    except Exception as e:
        print(f"AMD ERR {e}")
        return None

def worker():
    time.sleep(5)
    send("✅ *USOIL AMD PRO ИШКЕ КИРДИ*\nАккумуляция → Манипуляция → Дистрибуция логикасы активдүү")
    while True:
        try:
            df = yf.download("CL=F", period="2d", interval="1h", progress=False)
            if len(df) < 20: 
                time.sleep(60); continue
            
            close = df['Close']
            price = float(close.iloc[-1])
            ema50 = float(close.ewm(span=50).mean().iloc[-1])
            rsi = float(get_rsi(close).iloc[-1])

            amd_signal = check_amd(df)
            if amd_signal:
                txt = f"🛢️ *USOIL AMD SIGNAL*\n\n💰 ${price:.2f}\n📊 RSI {rsi:.0f} | EMA50 {ema50:.2f}\n\n🎯 *{amd_signal}*\n\n⏰ {time.strftime('%H:%M')} Bishkek\n📢 @xauusdakyl"
                send(txt)

        except Exception as e: print(f"LOOP ERR {e}")
        time.sleep(900) # ар 15 мүнөттө

threading.Thread(target=worker, daemon=True).start()
if __name__ == "__main__": app.run(host="0.0.0.0", port=10000)
