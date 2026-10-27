import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SYMBOLS = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK", "SENSEX": "^BSESN"}

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def check(name, sym):
    try:
        data = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        if len(data) < 22:
            return
        data['E10'] = data['Close'].ewm(span=10).mean()
        data['E20'] = data['Close'].ewm(span=20).mean()
        p = data.iloc[-2]
        c = data.iloc[-1]
        p10, p20 = float(p['E10']), float(p['E20'])
        c10, c20 = float(c['E10']), float(c['E20'])
        price = float(c['Close'])
        t = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m %H:%M IST')
        if p10 < p20 and c10 > c20:
            send(f"🟢 *{name} BUY*\nEMA10 crossed ABOVE EMA20\nPrice: {price:.2f}\n{t}")
        elif p10 > p20 and c10 < c20:
            send(f"🔴 *{name} SELL*\nEMA10 crossed BELOW EMA20\nPrice: {price:.2f}\n{t}")
    except Exception as e:
        print(e)

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
if now.weekday() < 5 and not (now.hour==9 and now.minute<15) and 9 <= now.hour <= 15:
    for n,s in SYMBOLS.items():
        check(n,s)
