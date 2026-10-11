import yfinance as yf, pandas as pd, requests, os
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@xauusdakyl"

def send(t):
    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                 params={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=20)

try:
    # ТУУРА ТИКЕР - ЧЫНЫГЫ НЕФТЬ БААСЫ
    df = yf.download("CL=F", period="5d", interval="15m", auto_adjust=True)
    close = df['Close'].values.flatten()
    
    delta = pd.Series(close).diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rsi = 100 - (100 / (1 + gain/loss))
    rsi_now = float(rsi.iloc[-1])

    ema50 = float(pd.Series(close).ewm(span=50).mean().iloc[-1])
    ema200 = float(pd.Series(close).ewm(span=200).mean().iloc[-1])
    price = float(close[-1])

    # ЛОГ - баа туурабы текшерүү үчүн
    send(f"✅ USOIL туура баа: ${price:.2f}\nRSI: {rsi_now:.1f} | EMA50: {ema50:.2f}\nЭми толук сигнал кодун салабыз")

except Exception as e:
    send(f"❌ Ката: {e}")
