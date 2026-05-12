from flask import Flask, render_template, jsonify
import threading
import time
import requests
import os

app = Flask(__name__)

SELF_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
PING_INTERVAL = 5 * 60  # 5 minutes

_ping_thread_started = False


def self_ping():
    while True:
        time.sleep(PING_INTERVAL)
        try:
            requests.get(f"{SELF_URL}/ping", timeout=10)
            print(f"[ping] Self-ping OK at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"[ping] Self-ping failed: {e}")


def start_self_ping_thread():
    global _ping_thread_started
    if _ping_thread_started:
        return
    _ping_thread_started = True
    thread = threading.Thread(target=self_ping, daemon=True)
    thread.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ping")
def ping():
    return jsonify({"status": "alive", "time": time.strftime("%H:%M:%S")})


start_self_ping_thread()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
