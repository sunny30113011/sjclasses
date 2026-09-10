import os

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
