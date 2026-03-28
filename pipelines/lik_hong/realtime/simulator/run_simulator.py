"""
pipelines/lik_hong/realtime/simulator/run_simulator.py
────────────────────────────────────────────────────────
Fabricated real-time order event generator.
Writes synthetic events to Redis list `rt:events` (capped at 10,000 entries).
Falls back to stdout dry-run if Redis is unavailable.

Usage:
    python pipelines/lik_hong/realtime/simulator/run_simulator.py [--rate 5]

This script is also triggered via:
    make pipeline-rt-start
    Admin Panel → Start Real-time Agent
"""

import json
import random
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Resolve project root so `shared` is importable ────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Constants ─────────────────────────────────────────────────
REDIS_KEY      = "rt:events"
REDIS_CAP      = 10_000   # max events kept in list
EVENT_TYPES    = ["new_order", "status_update", "payment_confirmed", "delivered"]
PAYMENT_TYPES  = ["credit_card", "boleto", "voucher", "debit_card"]
ORDER_STATUSES = ["created", "approved", "processing", "shipped", "delivered", "canceled"]
STATES = ["SP","RJ","MG","RS","PR","SC","BA","GO","ES","PE","CE","MA","MT","MS",
          "PA","RN","AM","PI","AL","SE","RO","TO","PB","AC","AP","RR","DF"]


# ── Fake data generators ──────────────────────────────────────

def fake_order_event(event_type: str = None) -> dict:
    event_type = event_type or random.choice(EVENT_TYPES)
    return {
        "order_id":             str(uuid.uuid4()),
        "customer_id":          str(uuid.uuid4()),
        "seller_id":            str(uuid.uuid4()),
        "product_id":           str(uuid.uuid4()),
        "event_type":           event_type,
        "order_status":         random.choice(ORDER_STATUSES),
        "payment_type":         random.choices(
            PAYMENT_TYPES, weights=[0.74, 0.19, 0.05, 0.02]
        )[0],
        "payment_value":        round(random.lognormvariate(4.5, 0.8), 2),
        "payment_installments": random.choices(
            range(1, 13), weights=[0.4,0.15,0.1,0.08,0.07,0.05,0.04,0.03,0.03,0.02,0.02,0.01]
        )[0],
        "customer_state":       random.choice(STATES),
        "seller_state":         random.choice(STATES),
        "timestamp":            datetime.now(timezone.utc).isoformat(),
        "review_score":         random.choices(
            [1, 2, 3, 4, 5], weights=[0.05, 0.05, 0.1, 0.2, 0.6]
        )[0] if event_type == "delivered" else None,
    }


# ── Redis writer ──────────────────────────────────────────────

def _connect_redis():
    """Return a connected Redis client, or None if unavailable."""
    try:
        import redis as redis_lib
        import os
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        r = redis_lib.Redis(host=host, port=port, db=0, decode_responses=True)
        r.ping()
        return r
    except Exception as exc:
        print(f"[simulator] Redis unavailable ({exc}) — falling back to dry-run stdout.", flush=True)
        return None


# ── Main loop ─────────────────────────────────────────────────

def run(rate: float):
    r = _connect_redis()
    if r:
        print(f"[simulator] Writing to Redis key '{REDIS_KEY}' at {rate} event/s — Ctrl+C to stop",
              flush=True)
    else:
        print(f"[simulator] DRY RUN — printing events to stdout at {rate} event/s", flush=True)

    count = 0
    try:
        while True:
            event = fake_order_event()
            data  = json.dumps(event)

            if r:
                try:
                    pipe = r.pipeline()
                    pipe.lpush(REDIS_KEY, data)
                    pipe.ltrim(REDIS_KEY, 0, REDIS_CAP - 1)
                    pipe.execute()
                except Exception as exc:
                    print(f"[simulator] Redis write error: {exc}", flush=True)
            else:
                print(f"[dry-run] {event['event_type']:20s} order={event['order_id'][:8]}... "
                      f"R${event['payment_value']:8.2f} via {event['payment_type']}", flush=True)

            count += 1
            if count % 10 == 0:
                print(f"[simulator] {count} events published | {datetime.now().strftime('%H:%M:%S')}",
                      flush=True)

            time.sleep(1.0 / rate)

    except KeyboardInterrupt:
        print(f"\n[simulator] Stopped. Total events published: {count}", flush=True)
        sys.exit(0)


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Olist real-time order event simulator")
    parser.add_argument("--rate", type=float, default=2.0, help="Events per second (default: 2)")
    args = parser.parse_args()

    def _handle_sigterm(sig, frame):
        print("\n[simulator] SIGTERM received — shutting down.", flush=True)
        sys.exit(0)
    signal.signal(signal.SIGTERM, _handle_sigterm)

    run(rate=args.rate)
