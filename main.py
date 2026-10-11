import yfinance as yf, requests, os
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": t}, timeout=15)

try:
    df = yf.download("USO", period="1d", interval="1h", auto_adjust=True)
    # Эң ишенимдүү жол
    val = df['Close'].values.flatten()[-1]
    price = float(val)
    send(f"✅ ДАЯР! USOIL ${price:.2f}\nБот толук оңдолду!")
except Exception as e:
    send(f"❌ {e}")
