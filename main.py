import os, time, threading, requests, yfinance as yf
from flask import Flask
TOKEN=os.getenv("BOT_TOKEN")
CHANNEL="@xauusdakyl"
DISPLAY="USOIL"
SYMBOL="CL=F"
app=Flask(__name__)
@app.route('/')
def home():
    return "CRUDE OIL LIVE"
LAST=0
def send(m):
    try:
        r=requests.post("https://api.telegram.org/bot%s/sendMessage" % TOKEN, json={"chat_id":CHANNEL,"text":m,"parse_mode":"HTML"}, timeout=15)
        print("SEND %s" % r.status_code, flush=True)
        return r.ok
    except Exception as e:
        print("ERR %s" % e, flush=True)
        return False
def get_candles():
    try:
        df=yf.download(SYMBOL, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df) >= 120:
            c=df['Close'].to_numpy().flatten().tolist()
            h=df['High'].to_numpy().flatten().tolist()
            l=df['Low'].to_numpy().flatten().tolist()
            v=df['Volume'].to_numpy().flatten().tolist()
            return c[-150:], h[-150:], l[-150:], v[-150:]
    except Exception as e:
        print("YF ERR %s" % e, flush=True)
    try:
        url="https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=5m&range=5d" % SYMBOL
        j=requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()
        res=j["chart"]["result"][0]
        q=res["indicators"]["quote"][0]
        c=[x for x in q["close"] if x is not None]
        h=[x for x in q["high"] if x is not None]
        l=[x for x in q["low"] if x is not None]
        v=[x for x in q["volume"] if x is not None]
        if len(c) > 120:
            return c[-150:], h[-150:], l[-150:], v[-150:]
    except Exception as e:
        print("YAHOO ERR %s" % e, flush=True)
    return [], [], [], []
def rsi(c, p=14):
    g=l_=0.0
    for i in range(1, p+1):
        d=c[-i]-c[-i-1]
        if d>0:
            g+=d
        else:
            l_+=abs(d)
    g/=p
    l_/=p
    if l_==0:
        return 50.0
    return 100-(100/(1+g/l_))
def ema(c, p):
    k=2/(p+1)
    e=sum(c[:p])/p
    for x in c[p:]:
        e=x*k+e*(1-k)
    return e
def loop():
    global LAST
    print("CRUDE OIL FIXED STARTED", flush=True)
    while True:
        try:
            c,h,l,v=get_candles()
            if len(c) < 120:
                print("WAIT CANDLES %s" % len(c), flush=True)
                time.sleep(60)
                continue
            price=c[-1]
            e20=ema(c,20)
            e50=ema(c,50)
            e200=ema(c,200)
            r=rsi(c)
            e12=ema(c,12)
            e26=ema(c,26)
            macd=e12-e26
            vol_avg=sum(v[-20:])/20 if len(v)>=20 else 1
            buy=0
            sell=0
            if e20>e50:
                buy+=30
            if e20<e50:
                sell+=30
            if r>50 and macd>0:
                buy+=20
            if r<50 and macd<0:
                sell+=20
            if v[-1]>vol_avg:
                buy+=10
                sell+=10
            if e20>e50>e200:
                buy+=20
            if e20<e50<e200:
                sell+=20
            if c[-1]>c[-2]:
                buy+=20
            if c[-1]<c[-2]:
                sell+=20
            best=buy if buy>sell else sell
            sig="BUY" if buy>sell else "SELL"
            print("CHECK OIL %.2f BUY %s%% SELL %s%% -> %s" % (price, buy, sell, sig), flush=True)
            if best>=60 and time.time()-LAST>1800:
                risk=0.35
                if sig=="BUY":
                    sl=price-risk
                    tp1=price+risk
                    tp2=price+risk*2
                    tp3=price+risk*3
                    msg="<b>%s %s %s%%</b>\n\nBuy at: %.2f\nSL: %.2f\nTP1: %.2f\nTP2: %.2f\nTP3: %.2f\n\nRSI:%.0f #USOIL" % (DISPLAY, sig, best, price, sl, tp1, tp2, tp3, r)
                else:
                    sl=price+risk
                    tp1=price-risk
                    tp2=price-risk*2
                    tp3=price-risk*3
                    msg="<b>%s %s %s%%</b>\n\nSell at: %.2f\nSL: %.2f\nTP1: %.2f\nTP2: %.2f\nTP3: %.2f\n\nRSI:%.0f #USOIL" % (DISPLAY, sig, best, price, sl, tp1, tp2, tp3, r)
                if send(msg):
                    LAST=time.time()
            time.sleep(60)
        except Exception as e:
            print("LOOP ERR %s" % e, flush=True)
            time.sleep(30)
threading.Thread(target=loop, daemon=True).start()
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
