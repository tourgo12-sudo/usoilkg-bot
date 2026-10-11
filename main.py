import os, yfinance as yf, requests, time
from datetime import datetime

BOT_TOKEN = os.environ.get("7765671322:AAEAOqiejTD34c_vYa-eAVm9kU01y1zlqBQ")
CHAT_ID = "395504640"
SYMBOL = "CL=F"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def check_100_percent():
    df = yf.download(SYMBOL, period="10d", interval="30m", progress=False)
    if len(df) < 50: return
    
    df['ATR'] = (df['High']-df['Low']).rolling(14).mean()
    df['VolSMA'] = df['Volume'].rolling(20).mean()
    df['High20'] = df['High'].rolling(20).max()
    df['Low20'] = df['Low'].rolling(20).min()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0
    reasons = []

    # 1. LIQUIDITY SWEEP (30%) - эң маанилүү
    if last['Low'] < df['Low20'].iloc[-2] and last['Close'] > last['Open'] and last['Close'] > df['Low20'].iloc[-2]:
        score += 30
        reasons.append("✅ Sweep ликвидди алды")
    else:
        return # Sweep жок болсо такыр жөнөтпөйбүз

    # 2. CHOCH / BOS (25%)
    if last['Close'] > df['High20'].iloc[-2] * 0.998: # структура бузулду
        score += 25
        reasons.append("✅ Choch + BOS")
    else:
        return

    # 3. ATR КҮЧТҮҮ (20%) - Hanzo талабы
    if abs(last['Close']-prev['Close']) > last['ATR']*1.5:
        score += 20
        reasons.append(f"✅ ATR күчтүү {last['ATR']:.2f}")
    else:
        return

    # 4. VOLUME + GUARD (15%)
    if last['Volume'] > last['VolSMA']*1.8:
        score += 15
        reasons.append("✅ Volume Guard")
    
    # 5. ЗОНА 88.5-90.5 ичинде (10%) - твой 89.83
    if 88.5 < last['Low'] < 90.5:
        score += 10
        reasons.append("✅ 89.83 Зона")
    else:
        return

    # 100% болсо гана жөнөт
    if score >= 100:
        msg = f"""
💎 *100% HANZO SETUP - USOIL*

💰 Баа: ${last['Close']:.2f}
📍 Entry: {last['Close']:.2f}
🎯 TP1: 91.07 | TP2: 92.45 | TP3: 93.75
🛑 SL: 88.80

{chr(10).join(reasons)}

ATR: {last['ATR']:.2f}
Убакыт: {datetime.now().strftime('%d.%m %H:%M')} Osh

@Usoilkg_bot
"""
        send(msg)
        print(f"100% ЖӨНӨТҮЛДҮ! {last['Close']}")
    else:
        print(f"{score}% - өтпөдү: {last['Close']}")

if __name__ == "__main__":
    send("🤖 100% фильтр күйдү. Tom, эми спам жок - 5/5 болгондо гана жөнөтөм.")
    while True:
        check_100_percent()
        time.sleep(1800) # 30 мин
