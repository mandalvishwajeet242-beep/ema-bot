import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SYMBOLS = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}

def send(msg):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print("Token missing")
            return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(r.text)
    except Exception as e:
        print(f"Error: {e}")

def check(name, sym):
    try:
        data = yf.download(sym, period="1mo", interval="1d", progress=False)
        if len(data) < 22:
            return
        data['E10'] = data['Close'].ewm(span=10).mean()
        data['E20'] = data['Close'].ewm(span=20).mean()
        p = data.iloc[-2]
        c = data.iloc[-1]
        c10, c20 = float(c['E10']), float(c['E20'])
        p10, p20 = float(p['E10']), float(p['E20'])
        price = float(c['Close'])
        t = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d-%b %I:%M %p")
        if p10 < p20 and c10 > c20:
            send(f"🟢 *{name} BUY*\nPrice: {price:.2f}\nTime: {t}")
        elif p10 > p20 and c10 < c20:
            send(f"🔴 *{name} SELL*\nPrice: {price:.2f}\nTime: {t}")
        else:
            send(f"✅ *EMA Bot Working!*\n{name}: {price:.2f} - No cross\nTime: {t}")
    except Exception as e:
        send(f"Error {name}: {e}")

for n,s in SYMBOLS.items():
    check(n,s)
