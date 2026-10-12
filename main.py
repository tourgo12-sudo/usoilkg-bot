import os, requests, time, threading, yfinance as yf
import pandas as pd
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@xauusdakyl")

app = Flask(__name__)
@app.route("/")
def home(): return "USOIL PRO LIVE - @xauusdakyl"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHANNEL_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(f"SEND -> {r.text}")
    except Exception as e:
        print(f"SEND ERROR {e}")

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_loop():
    time.sleep(10)
    send(f"✅ *USOIL BOT ИШКЕ КИРДИ*\nКанал: {CHANNEL_ID}\nБааны текшерип баштайт...")
    while True:
        try:
            # USOIL баасы - CL=F (Crude Oil Futures)
            data = yf.download("CL=F", period="5d", interval="1h", progress=False)
            if len(data) < 60:
                time.sleep(60)
                continue

            close = data['Close']
            ema50 = close.ewm(span=50).mean().iloc[-1]
            rsi = get_rsi(close).iloc[-1]
            price = float(close.iloc[-1])

            # Логика
            if isinstance(price, pd.Series): price = price.iloc[0]
            if isinstance(ema50, pd.Series): ema50 = ema50.iloc[0]
            if isinstance(rsi, pd.Series): rsi = rsi.iloc[0]

            signal = None
            if price > ema50 and rsi > 55 and rsi < 75:
                signal = "LONG 🟢"
            elif price < ema50 and rsi < 45 and rsi > 25:
                signal = "SHORT 🔴"

            log = f"CHECK ${price:.2f} RSI {rsi:.0f} EMA50 {ema50:.2f} {signal or 'WAIT'}"
            print(log)

            if signal:
                msg = f"🛢️ *USOIL / WTI PRO SIGNAL*\n\n💰 Баа: ${price:.2f}\n📊 RSI: {rsi:.0f}\n📈 EMA50: ${ema50:.2f}\n\n🎯 СИГНАЛ: *{signal}*\n\n⏰ {time.strftime('%H:%M %d-%m-%Y')} Bishkek\n📢 @xauusdakyl"
                send(msg)

        except Exception as e:
            print(f"ERROR {e}")
        time.sleep(1800) # ар 30 мүнөттө текшер

threading.Thread(target=check_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
