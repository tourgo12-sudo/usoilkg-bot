import os, time, threading, requests
from flask import Flask
import math

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@usoilkg" # өзүңдүн мунай каналың
SYMBOL = "CL=F" # US Crude Oil
app = Flask(__name__)
LAST_SIGNAL = 0

def send(msg):
    if not TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHANNEL, "text": msg, "parse_mode":"HTML"}, timeout=10)
    except: pass

def get_candles():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval=15m&range=5d"
        j = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        closes = [c for c in j['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
        return closes
    except: return None

def ema(data, n):
    if len(data)<n: return sum(data)/len(data)
    k=2/(n+1); e=sum(data[:n])/n
    for p in data[n:]: e=p*k+e*(1-k)
    return e

def rsi(data, n=14):
    gains=losses=0
    for i in range(1,n+1):
        d=data[-i]-data[-i-1]
        if d>0: gains+=d
        else: losses-=d
    if losses==0: return 70
    rs=(gains/n)/(losses/n)
    return 100-(100/(1+rs))

def loop():
    global LAST_SIGNAL
    print("USOIL PRO STARTED", flush=True)
    time.sleep(10)
    while True:
        try:
            closes=get_candles()
            if closes and len(closes)>200:
                price=closes[-1]
                ema50=ema(closes,50)
                ema200=ema(closes,200)
                r=rsi(closes)
                atr=sum(abs(closes[i]-closes[i-1]) for i in range(-14,0))/14

                # 100% СТРАТЕГИЯ - SENIKИ, БИРОК КУЧОТУЛГОН
                side=None
                if price > ema50 > ema200 and 55 < r < 75:
                    side="LONG"
                elif price < ema50 < ema200 and 25 < r < 45:
                    side="SHORT"

                print(f"CHECK ${price:.2f} RSI {r:.0f} EMA50 {ema50:.2f} {side}", flush=True)

                if side and (time.time()-LAST_SIGNAL)>5400: # 1.5 саатта 1 сигнал
                    if side=="LONG":
                        sl=price-atr*1.2
                        tp1=price+atr*1.5
                        tp2=price+atr*3
                    else:
                        sl=price+atr*1.2
                        tp1=price-atr*1.5
                        tp2=price-atr*3

                    emoji="🛢️🟢 LONG 100%" if side=="LONG" else "🛢️🔴 SHORT 100%"
                    txt=f"<b>{emoji}</b>\n\n"
                    txt+=f"<b>Entry:</b> ${price:.2f}\n"
                    txt+=f"<b>❌ SL:</b> ${sl:.2f}\n"
                    txt+=f"<b>✅ TP1:</b> ${tp1:.2f}\n"
                    txt+=f"<b>✅ TP2:</b> ${tp2:.2f}\n\n"
                    txt+=f"<b>📊 RSI:</b> {r:.1f} | <b>EMA50:</b> ${ema50:.2f}\n"
                    txt+=f"RR 1:2.5 🔥\n\n#USOIL #OIL"
                    send(txt)
                    LAST_SIGNAL=time.time()
        except Exception as e:
            print(f"err {e}", flush=True)
        time.sleep(300)

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home(): return "USOIL PRO Live"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
