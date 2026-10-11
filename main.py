import yfinance as yf, requests, os
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"
def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=15)
try:
    d = yf.download("USO", period="5d", interval="1h", auto_adjust=True)
    price = float(d['Close'].iloc[-1])
    send(f"✅ Бот иштеп баштады!\nUSOIL баасы: {price:.2f}\nЭми ар 30 мүнөттө текшерип турат")
except Exception as e:
    send(f"❌ Ката: {e}")
