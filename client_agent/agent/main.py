import threading
import time
import sys

from agent import registration
from agent.config import Config, TOKEN_FILE
from agent.heartbeat import send_heartbeat
from agent.metrics import collect_metrics, measure_latency
from agent import remote


def banner():
    print("=" * 55)
    print(" Client Agent - Network Monitoring System")
    print(f" Server:    {Config.SERVER_URL}")
    print(f" Interval:  {Config.HEARTBEAT_INTERVAL}s")
    print("=" * 55)


# Track sessions we've already handled so we don't loop on them
_handled_sessions = set()


def session_poller(token_getter):
    """Background thread: poll for remote-session requests every 10s."""
    while True:
        try:
            token = token_getter()
            if token:
                sess = remote.poll_pending_session(token)
                if sess:
                    sid = sess.get("session_id")
                    if sid and sid not in _handled_sessions:
                        print(f"[remote] session {sid} requested")
                        # Acknowledge by reporting CONNECTED
                        ok = remote.report_session_status(token, sid, "CONNECTED")
                        if ok:
                            print(f"[remote] session {sid} -> CONNECTED")
                            _handled_sessions.add(sid)
                            # Demo: open Windows Remote Desktop client
                            target = Config.REMOTE_DESKTOP_TARGET or ""
                            remote.launch_remote_desktop(target)
        except Exception as exc:
            print(f"[remote] poller error: {exc}")
        time.sleep(10)


def run():
    banner()

    token = registration.ensure_registered()
    if not token:
        print("[main] Registration failed. Exiting.")
        sys.exit(1)

    # Holder so thread can access current token even after re-registration
    token_holder = {"value": token}

    def get_token():
        return token_holder["value"]

    # Start the session poller thread
    t = threading.Thread(target=session_poller, args=(get_token,), daemon=True)
    t.start()

    print("[main] Starting heartbeat loop. Press Ctrl+C to stop.")
    while True:
        try:
            metrics = collect_metrics()
            latency = measure_latency()
            if latency is not None:
                metrics["latency_ms"] = latency

            ok = send_heartbeat(token, metrics)
            if not ok:
                print("[main] Re-registering device...")
                if TOKEN_FILE.exists():
                    TOKEN_FILE.unlink()
                token = registration.ensure_registered()
                token_holder["value"] = token
                if not token:
                    print("[main] Re-registration failed.")

            status = "OK" if ok else "FAIL"
            print(
                f"[{status}] cpu={metrics['cpu_usage']}% "
                f"mem={metrics['memory_usage']}% "
                f"disk={metrics['disk_usage']}% "
                f"lat={metrics.get('latency_ms', 'n/a')}ms"
            )

            time.sleep(Config.HEARTBEAT_INTERVAL)

        except KeyboardInterrupt:
            print("\n[main] Stopped by user.")
            break
        except Exception as exc:
            print(f"[main] Unexpected error: {exc}")
            time.sleep(Config.HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    run()