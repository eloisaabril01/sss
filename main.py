from flask import Flask, render_template, jsonify, request
import threading
import time
import requests
import os

app = Flask(__name__)

SELF_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
PING_INTERVAL = 5 * 60  # 5 minutes

def self_ping():
    while True:
        time.sleep(PING_INTERVAL)
        try:
            requests.get(f"{SELF_URL}/ping", timeout=10)
            print(f"[ping] Self-ping OK at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"[ping] Self-ping failed: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return jsonify({"status": "alive", "time": time.strftime("%H:%M:%S")})

if __name__ == "__main__":
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
