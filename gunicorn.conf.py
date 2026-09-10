import os
import threading
import time
import urllib.request

# Port assigned by Render (defaults to 10000 or 8000 if running locally)
port = os.environ.get('PORT', '10000')

# Bind to 0.0.0.0 on the assigned port so Render's internal port scanner detects HTTP immediately
bind = f"0.0.0.0:{port}"

# Concurrency settings optimized for Render Free Tier (512MB RAM)
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
threads = 2
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

def _keep_alive_loop():
    """
    Lightweight background worker to keep Render instance warm 24/7.
    Render free tier sleeps after 15 minutes of inactivity causing 50-second cold starts.
    Pinging every 10 minutes prevents sleep and ensures instant page loads.
    """
    time.sleep(180)  # Wait 3 minutes after initial boot
    hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'sj-tech-classes.onrender.com')
    url = f"https://{hostname}/"

    while True:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SJClasses-KeepAlive/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                pass
        except Exception:
            pass
        time.sleep(600)  # 10 minutes

def when_ready(server):
    """Hook executed by Gunicorn master process upon successful start."""
    if os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
        t = threading.Thread(target=_keep_alive_loop, daemon=True, name="render_keepalive")
        t.start()

