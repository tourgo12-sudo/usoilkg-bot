import os, time, threading, requests, yfinance as yf
from flask import Flask
TOKEN=os.getenv("BOT_TOKEN")
CHANNEL="@xauusdakyl"
DISPLAY="USOIL"
SYMBOL="CL=F"
app=Flask(__name__)
@app.route('/')
def home(): return "CRUDE OIL PERCENT LIVE"
LAST=0
def send(m):
    try:
        r=requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHANNEL,"text":m,"parse_mode":"HTML"},timeout=15)
        print(f"SEND {r.status_code}",flush=True)
        return r.ok
    except Exception as e:
        print(f"ERR {e}",flush=True)
        return False
def get_candles():
    try:
        df=yf.download(SYMBOL,period="5d",interval="5m",progress=False,auto_adjust=True)
        if len(df)>=120:
            try:
                c=df['Close'].values.flatten().tolist()
                h=df['High'].values.flatten().tolist()
                l=df['Low'].values.flatten().tolist()
                v=df['Volume'].values.flatten().tolist()
            except:
                c=df['Close'].iloc[:,0].values.tolist()
                h=df['High'].iloc[:,0].values.tolist()
                l=df['Low'].iloc[:,0].values.tolist()
                v=df['Volume'].iloc[:,0].values.tolist()
            return c[-150:],h[-150:],l[-150:],v[-150:]
    except Exception as e:
        print(f"YF ERR {e}",flush=True)
    try:
        url=f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?interval=5m&range=5d"
        j=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15).json()
        res=j["chart"]["result"][0]
        q=res["indicators"]["quote"][0]
        c=[x for x in q["close"] if x is not None]
        h=[x for x in q["high"] if x is not None]
        l=[x for x in q["low"] if x is not None]
        v=[x for x in q["volume"] if x is not None]
        if len(c)>120:
            return c[-150:],h[-150:],l[-150:],v[-150:]
    except Exception as e:
        print(f"YAHOO ERR {e}",flush=True)
    return [],[],[],[]
def rsi(c,p=14):
    g=l_=0.0
    for i in range(1,p+1):
        d=c[-i]-c[-i-1]
        if d>0: g+=d
        else: l_+=abs(d)
    g/=p;l_/=p
    return 100-(100/(1+g/l_)) if l_!=0 else 50.0
def ema(c,p):
    k=2/(p+1);e=sum(c[:p])/p
    for x in c[p:]: e=x*k+e*(1-k)
    return e
def loop():
    global LAST
    print("CRUDE OIL YFINANCE STARTED",flush=True)
    while True:
        try:
            c,h,l,v=get_candles()
            if len(c)<120:
                print(f"WAIT CANDLES {len(c)}",flush=True)
                time.sleep(60);continue
            price=c[-1];e20=ema(c,20);e50=ema(c,50);e200=ema(c,200);r=rsi(c);e12=ema(c,12);e26=ema(c,26);macd=e12-e26
            vol_avg=sum(v[-20:])/20 if len(v)>=20 else 1
            buy=sell=0
            if e20>e50: buy+=30
            if e20<e50: sell+=30
            if r>50 and macd>0: buy+=20
            if r<50 and macd<0: sell+=20
            if v[-1]>vol_avg: buy+=10;sell+=10
            if e20>e50>e200: buy+=20
            if e20<e50<e200: sell+=20
            if c[-1]>c[-2]: buy+=20
            if c[-1]<c[-2]: sell+=20
            best=max(buy,sell);sig="BUY" if buy>sell else "SELL"
            print(f"CHECK OIL {price:.2f} BUY {buy}% SELL {sell}% -> {sig}",flush=True)
            if best>=60 and time.time()-LAST>1800:
                risk=0.35
                if sig=="BUY":
                    sl=price-risk;tp1=price+risk;tp2=price+risk*2;tp3=price+risk*3
                    msg="<b>"+DISPLAY+" "+sig+" "+str(best)+"%</b>\n\nBuy at: "+f"{price:.
