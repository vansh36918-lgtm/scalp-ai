import time
import urllib.request

url = "https://scalp-ai-scnh.onrender.com/"

print(f"Starting Keep-Alive daemon for {url}...")
while True:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ScalpAI-KeepAlive/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping status: {status} OK")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping notice: {e}")
    
    time.sleep(240) # Ping every 4 minutes (before 15min Render idle timeout)
