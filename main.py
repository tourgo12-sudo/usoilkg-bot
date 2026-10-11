import yfinance as yf, requests, os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=15)

try:
    d = yf.download("USO", period="1d", interval="1h", auto_adjust=True)
    # Жаңы yfinance үчүн оңдоо
    close = d['Close']
    try:
        price = float(close.iloc[-1])
    except:
        price = float(close.iloc[-1].iloc[0])

    send(f"✅ БОТ ИШТЕДИ!\nUSOIL: {price:.2f}\nБот даяр, ар 30 мүнөттө иштейт")
except Exception as e:
    send(f"❌ Ката: {e}")
