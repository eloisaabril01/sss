from flask import Flask, jsonify, send_file, request
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


def log(message: str) -> None:
    print(f"[{fmt_ist_ts()} IST] {message}", flush=True)


@app.before_request
def request_logger():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "Unknown")
    log(f"🌐 {request.method} {request.path} | IP: {ip} | UA: {ua}")


def self_ping_loop() -> None:
    while True:
        time.sleep(PING_INTERVAL)

        try:
            ping_url = f"{SELF_URL}/api/status"

            log(f"🏓 Sending self-ping → {ping_url}")

            response = requests.get(
                ping_url,
                timeout=15,
                headers={
                    "User-Agent": "Render-Self-Ping/1.0"
                }
            )

            log(
                f"🏓 Self-ping SUCCESS | "
                f"Status: {response.status_code} | "
                f"Response: {response.text[:120]}"
            )

        except Exception as exc:
            log(f"❌ Self-ping FAILED: {exc}")


def start_self_ping() -> None:
    global _started_ping

    with _ping_lock:
        if _started_ping:
            log("⚠️ Self-ping already running")
            return

        _started_ping = True

        if not SELF_URL:
            log("⚠️ RENDER_EXTERNAL_URL not set — self-ping disabled")
            return

        thread = threading.Thread(
            target=self_ping_loop,
            daemon=True
        )

        thread.start()

        log(f"🏓 Self-ping started → {SELF_URL}/api/status")
        log(f"⏱️ Ping interval: {PING_INTERVAL} seconds")


@app.route("/")
def index():
    log("📄 Serving index.html")
    return send_file("index.html")


@app.route("/ping")
def ping():
    log("🏓 Manual ping endpoint hit")

    return jsonify(
        {
            "status": "alive",
            "time": fmt_ist_ts(),
        }
    )


@app.route("/api/status")
def api_status():
    uptime = int(time.time() - _started_at)

    log(f"📊 Status requested | Uptime: {uptime}s")

    return jsonify(
        {
            "uptime": uptime,
            "serverTime": f"{fmt_ist_ts()} IST",
            "renderActive": True,
            "selfPingUrl": f"{SELF_URL}/api/status",
        }
    )


@app.route("/health")
def health():
    log("💚 Health check requested")

    return jsonify(
        {
            "ok": True,
            "time": fmt_ist_ts(),
        }
    )


start_self_ping()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    log(f"🚀 Flask server starting on port {port}")
    log(f"🌍 SELF_URL: {SELF_URL}")

    app.run(
        host="0.0.0.0",
        port=port,
        threaded=True
    )
