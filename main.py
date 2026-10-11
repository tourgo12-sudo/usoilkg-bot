import yfinance as yf, requests, os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=15)

try:
    d = yf.download("USO", period="2d", interval="1h", auto_adjust=True)
    # Series катасын 100% оңдоо
    c = d['Close']
    if hasattr(c, 'columns'):
        c = c.iloc[:, 0]
    price = float(c.iloc[-1])
    send(f"✅ USOIL БОТ ДАЯР!\nБаа: ${price:.2f}\nЭми ар 30 мүнөттө автоматтык анализ берет")
except Exception as e:
    import traceback
    send(f"❌ Ката калды: {e}")
