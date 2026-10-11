import yfinance as yf, pandas as pd, requests, os
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"
def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=20)
try:
    df = yf.download("CL=F", period="2d", interval="1h", auto_adjust=True)
    price = float(df['Close'].values.flatten()[-1])
    send(f"🛢️ US crude oil: ${price:.2f} - ТУУРА БАА!")
except Exception as e:
    send(f"❌ {e}")
