import os

# Render puts the port in the environment variable PORT
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"
workers = 4
accesslog = "-"
errorlog = "-"
