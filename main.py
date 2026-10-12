import os, requests, time, threading
from flask import Flask
import yfinance as yf
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@xauusdakyl")
app = Flask(__name__)

@app.route("/")
def home():
    return "USOIL PRO LIVE OK"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"}
        r = requests.post(url, json=data, timeout=15)
        print(f"SEND STATUS: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"SEND ERR {e}")

def get_rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    rs = g/l
    return 100-(100/(1+rs))

def worker():
    time.sleep(5)
    send("✅ *USOIL BOT ИШКЕ КИРДИ*\nБот Live болду, баа текшерилет.")
    while True:
        try:
            df = yf.download("CL=F", period="5d", interval="1h", progress=False)
            close = df['Close']
            if len(close) < 55:
                time.sleep(60)
                continue
            price = float(close.iloc[-1])
            ema50 = float(close.ewm(span=50).mean().iloc[-1])
            rsi = float(get_rsi(close).iloc[-1])
            print(f"CHECK ${price:.2f} RSI {rsi:.0f} EMA {ema50:.2f}")

            sig = None
            if price > ema50 and 55 < rsi < 75:
                sig = "LONG 🟢"
            elif price < ema50 and 25 < rsi < 45:
                sig = "SHORT 🔴"

            if sig:
                txt = f"🛢️ *USOIL / WTI SIGNAL*\n\n💰 ${price:.2f}\n📊 RSI {rsi:.0f}\n📈 EMA50 {ema50:.2f}\n\n🎯 *{sig}*\n\n⏰ {time.strftime('%H:%M %d-%m-%Y')} Bishkek\n📢 @xauusdakyl"
                send(txt)

        except Exception as e:
            print(f"LOOP ERR {e}")
        time.sleep(1800)

threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
