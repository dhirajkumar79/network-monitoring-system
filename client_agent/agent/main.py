import time
import sys

from agent import registration
from agent.config import Config, TOKEN_FILE
from agent.heartbeat import send_heartbeat
from agent.metrics import collect_metrics, measure_latency


def banner():
    print("=" * 55)
    print(" Client Agent - Network Monitoring System")
    print(f" Server:    {Config.SERVER_URL}")
    print(f" Interval:  {Config.HEARTBEAT_INTERVAL}s")
    print("=" * 55)


def run():
    banner()

    token = registration.ensure_registered()
    if not token:
        print("[main] Registration failed. Exiting.")
        sys.exit(1)

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