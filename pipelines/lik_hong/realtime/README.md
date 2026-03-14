# Lik Hong — Real-time Pipeline

## Flow
Order Simulator → Pub/Sub (`olist-orders-live`) → GCS Streaming Bucket → dbt (incremental) → Gold

## Components

### 1. Simulator (`simulator/run_simulator.py`)
Fabricates realistic order events based on Olist data distributions and publishes to Pub/Sub.

```bash
python pipelines/lik_hong/realtime/simulator/run_simulator.py
# Or via Admin Panel → Start Real-time Agent
# Or: make pipeline-rt-start
```

Events published per message:
- `order_id`, `customer_id`, `seller_id`, `product_id`
- `event_type`: `new_order` | `status_update` | `payment_confirmed` | `delivered`
- `timestamp`, `payment_value`, `payment_type`

### 2. Consumer (`consumer/`)
Pub/Sub subscriber that writes incoming events to GCS Streaming Bucket (raw JSON landing zone).

### 3. Redis Cache (`redis_cache/`)
Product and seller dimension data pre-loaded into Google Memorystore (Redis) for
low-latency lookup during real-time processing.

## CDC Mode
When the Admin Panel triggers CDC recreation:
1. dbt `--full-refresh` rebuilds Gold tables with CDC/incremental config
2. Dagster sensor resets its cursor to the start of the streaming bucket
3. New streaming events flow incrementally on top of the rebuilt Gold

## Pub/Sub Topic
- Topic: `olist-orders-live`
- Subscription: `olist-orders-sub`
- Create in your GCP project before starting the simulator.
