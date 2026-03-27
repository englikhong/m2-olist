# Huey Ling — Batch Pipeline

## Overview

Loads Olist seller and order data into your personal GCP BigQuery Gold dataset.

## Flow

```
/data/*.csv → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery
```

## Gold Tables Required

| Table | Purpose |
|-------|---------|
| `Dim_Sellers` | seller_id, seller_state, seller_city |
| `Fact_Orders` | Order facts incl. seller_id, delivery timestamps, payment_value |
| `Dim_Reviews` | review_score, review dates — join to orders for per-seller ratings |

---

## Steps

### 1. Set up your GCP project & auth

Follow **Steps 1–5** in `quick-setup.md` - Done.

### 2. Configure Meltano

- GCS bucket name → my-shl-project-olist-bronze
- BigQuery project → my-shl-project-olist
- Source files: Extracts all Olist CSVs and loads raw Parquet files into GCS Bronze bucket.

### 3. Run Meltano (CSV → GCS Bronze)

```bash
cd pipelines/huey_ling/batch/meltano
meltano install   # first time only
meltano run tap-csv target-gcs
```

Meltano tracks a high-water mark — re-running will not re-ingest already-loaded files.

### 4. Configure dbt

Copy `pipelines/lik_hong/batch/dbt/profiles.yml` and update with your project/dataset.

### 5. Run dbt (Bronze → Silver → Gold)

```bash
cd pipelines/huey_ling/batch/dbt
dbt run          # incremental by default — safe to re-run
dbt test
```

Full refresh (only if schema changes):
```bash
dbt run --full-refresh
```

### 6. Verify in BigQuery

```sql
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Sellers`;
SELECT COUNT(*) FROM `<your_project>.olist_gold.Fact_Orders`
WHERE seller_id IS NOT NULL;
```

### 7. Run your dashboard

```bash
make dev-hueying   # http://localhost:7866
```

---

## Reference Implementation

See `pipelines/lik_hong/batch/` for working Meltano configs, dbt models, and the
`run_batch.py` runner. Use it as your template.

---

## Optional: Real-time via Admin Panel

Lik Hong's real-time simulator publishes live order events including `seller_id`.
You can optionally connect to it for a live seller performance feed:

1. Ask Lik Hong to grant access to his Pub/Sub topic (`olist-orders-live`)
   and his BigQuery Gold dataset.
2. In the main Gradio app, go to **Admin Panel → Real-time Controls** to
   start/stop the simulator and monitor event throughput.
3. Your dbt incremental models will pick up new events on the next batch run.

Real-time is **optional** — your batch pipeline is fully self-contained without it.
