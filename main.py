import os, yfinance as yf, requests, time
from datetime import datetime

BOT_TOKEN = os.environ.get("7765671322:AAEAOqiejTD34c_vYa-eAVm9kU01y1zlqBQ")
CHAT_ID = "395504640"
CHANNEL_ID = "@xauusdakyl"  # сенин каналын
SYMBOL = "CL=F"

def send_to_all(msg):
    for cid in [CHAT_ID, CHANNEL_ID]:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        except Exception as e:
            print(e)

def check_100():
    try:
        df = yf.download(SYMBOL, period="10d", interval="30m", progress=False)
        if len(df) < 50: return
        df['ATR'] = (df['High']-df['Low']).rolling(14).mean()
        df['VolSMA'] = df['Volume'].rolling(20).mean()
        df['High20'] = df['High'].rolling(20).max()
        df['Low20'] = df['Low'].rolling(20).min()
        last = df.iloc[-1]
        prev = df.iloc[-2]

        sweep = last['Low'] < df['Low20'].iloc[-2] and last['Close'] > last['Open']
        choch = last['Close'] > df['High20'].iloc[-2] * 0.998
        strong = abs(last['Close']-prev['Close']) > last['ATR']*1.5
        vol = last['Volume'] > last['VolSMA']*1.8
        zone = 88.5 < last['Low'] < 90.5

        if sweep and choch and strong and vol and zone:
            msg = f"""💎 *100% HANZO SETUP - USOIL*\n\n💰 Баа: ${last['Close']:.2f}\n🎯 TP: 91.07 / 92.45 / 93.75\n🛑 SL: 88.80\n\n✅ Sweep + Choch + ATR {last['ATR']:.2f}\n🕐 {datetime.now().strftime('%H:%M')}\n\n#USOIL #OIL"""
            send_to_all(msg)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    send_to_all("🤖 Usoilkg_bot @xauusdakyl каналга кошулду! 100% гана сигнал жөнөтөм.")
    while True:
        check_100()
        time.sleep(1800)
