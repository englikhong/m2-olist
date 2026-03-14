# Lanson — Batch Pipeline

## Overview

Loads Olist review and order data into your personal GCP BigQuery Gold dataset.

## Flow

```
/data/*.csv → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery
```

## Gold Tables Required

| Table | Purpose |
|-------|---------|
| `Fact_Orders` | Order-level facts: status, timestamps, delivery dates |
| `Dim_Reviews` | review_score, review_comment_message, review dates |
| `Dim_Customers` | customer_state, customer_city for regional breakdowns |

---

## Steps

### 1. Set up your GCP project & auth

Follow **Steps 1–5** in `quick-setup.md`.

### 2. Configure Meltano

Copy the reference config from `pipelines/lik_hong/batch/meltano/` and update:
- GCS bucket name → your bucket (`olist-bronze-<yourname>`)
- BigQuery project → your `project_id`
- Source files: `olist_orders_dataset.csv`, `olist_order_reviews_dataset.csv`,
  `olist_customers_dataset.csv`

### 3. Run Meltano (CSV → GCS Bronze)

```bash
cd pipelines/lanson/batch/meltano
meltano run tap-spreadsheets-anywhere target-gcs
```

Meltano tracks a high-water mark — re-running will not re-ingest already-loaded files.

### 4. Configure dbt

Copy `pipelines/lik_hong/batch/dbt/profiles.yml` and update with your project/dataset.

### 5. Run dbt (Bronze → Silver → Gold)

```bash
cd pipelines/lanson/batch/dbt
dbt run          # incremental by default — safe to re-run
dbt test
```

Full refresh (only if schema changes):
```bash
dbt run --full-refresh
```

### 6. Verify in BigQuery

```sql
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Reviews`;
SELECT COUNT(*) FROM `<your_project>.olist_gold.Fact_Orders`;
```

### 7. Run your dashboard

```bash
make dev-lanson   # http://localhost:7864
```

---

## Reference Implementation

See `pipelines/lik_hong/batch/` for working Meltano configs, dbt models, and the
`run_batch.py` runner. Use it as your template.

---

## Future: Sentiment Analysis (Cloud Function)

When your sentiment pipeline is ready (later phase):
1. Read `review_comment_message` from `Dim_Reviews`
2. Call a Cloud Function for sentiment scoring
3. Write results back to a `Dim_Reviews_Sentiment` Gold table
4. Your dashboard will read from that enriched table

This feature is deferred — build the batch pipeline first.

---

## Optional: Real-time via Admin Panel

Lik Hong's real-time simulator publishes live order events to Pub/Sub.
You can optionally connect to it for a live review feed:

1. Ask Lik Hong to grant access to his Pub/Sub topic (`olist-orders-live`)
   and his BigQuery Gold dataset.
2. In the main Gradio app, go to **Admin Panel → Real-time Controls** to
   start/stop the simulator and monitor event throughput.
3. Your dbt incremental models will pick up new events on the next batch run.

Real-time is **optional** — your batch pipeline is fully self-contained without it.
