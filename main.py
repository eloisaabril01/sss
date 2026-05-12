from flask import Flask, jsonify, send_file
import os
import threading
import time
import requests

app = Flask(__name__)

SELF_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:5000")
PING_INTERVAL = 10 * 60  # 10 minutes
_started_ping = False
_ping_lock = threading.Lock()
_started_at = time.time()


def fmt_ist_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 19800))


def self_ping_loop() -> None:
    while True:
        time.sleep(PING_INTERVAL)
        try:
            requests.get(f"{SELF_URL}/api/status", timeout=15)
            print(f"🏓 Self-ping OK [{fmt_ist_ts()} IST]")
        except Exception as exc:
            print(f"🏓 Self-ping failed: {exc}")


def start_self_ping() -> None:
    global _started_ping
    with _ping_lock:
        if _started_ping:
            return
        _started_ping = True
        if not SELF_URL:
            print("⚠️ RENDER_EXTERNAL_URL not set — self-ping disabled")
            return
        thread = threading.Thread(target=self_ping_loop, daemon=True)
        thread.start()
        print(f"🏓 Self-ping started → {SELF_URL}/api/status")


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/ping")
def ping():
    return jsonify(
        {
            "status": "alive",
            "time": fmt_ist_ts(),
        }
    )


@app.route("/api/status")
def api_status():
    uptime = int(time.time() - _started_at)
    return jsonify(
        {
            "uptime": uptime,
            "serverTime": f"{fmt_ist_ts()} IST",
            "renderActive": True,
            "selfPingUrl": f"{SELF_URL}/api/status",
        }
    )


start_self_ping()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
