import time
import requests
import schedule

TELEGRAM_TOKEN = "8661344486:AAFZ5-x5hxTz0I6eTJKVmKcmXEYmWedPw2Y"
# Replace with your Telegram Chat ID
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
FASTAPI_URL = "http://localhost:8000/run_blueprint"

WATCHLIST = ["EURUSD=X", "GBPUSD=X"]

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text[:4000], "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send telegram msg: {e}")

def run_scheduled_scan():
    print("⏰ Starting scheduled market analysis...")
    for symbol in WATCHLIST:
        task = f"Analyze market setup for {symbol} on 15m timeframe and give trade parameters"
        try:
            res = requests.post(FASTAPI_URL, json={"task": task, "max_iterations": 2}, timeout=180)
            if res.status_code == 200:
                data = res.json()
                output = data.get("worker_output", "")
                status = data.get("review_status", "")
                
                msg = f"📊 **Automated Scan Alert: {symbol}**\nStatus: {status}\n\n{output}"
                send_telegram(msg)
        except Exception as e:
            print(f"Scan error for {symbol}: {e}")

# Schedule job every 1 hour
schedule.every(1).hours.do(run_scheduled_scan)

if __name__ == "__main__":
    print("🚀 Market Watcher Scheduler Active...")
    while True:
        schedule.run_pending()
        time.sleep(10)
