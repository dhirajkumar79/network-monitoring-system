import os
import threading
import time


def start_offline_checker(app):
    """Start a background thread that periodically marks stale devices offline."""
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return

    def loop():
        time.sleep(10)
        while True:
            try:
                with app.app_context():
                    from app.services.device_service import mark_stale_devices_offline
                    timeout = app.config.get("HEARTBEAT_TIMEOUT_SECONDS", 60)
                    count = mark_stale_devices_offline(timeout)
                    if count:
                        print(f"[offline-checker] Marked {count} device(s) OFFLINE")
            except Exception as exc:
                print(f"[offline-checker] Error: {exc}")
            time.sleep(30)

    thread = threading.Thread(target=loop, daemon=True, name="offline-checker")
    thread.start()
    print("[offline-checker] Started.")