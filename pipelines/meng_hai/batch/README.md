# Meng Hai — Batch Pipeline

## Overview

Loads Olist payment data into your personal GCP BigQuery Gold dataset.

## Flow

```
/data/*.csv → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery
```

## Gold Tables Required

| Table | Purpose |
|-------|---------|
| `Fact_Orders` | Order-level facts: status, timestamps, payment_value, product info |
| `Dim_Payments` | payment_type, payment_installments, payment_value per order |

---

## Steps

### 1. Set up your GCP project & auth

Follow **Steps 1–5** in `quick-setup.md`.

### 2. Configure Meltano

Copy the reference config from `pipelines/lik_hong/batch/meltano/` and update:
- GCS bucket name → your bucket (`olist-bronze-<yourname>`)
- BigQuery project → your `project_id`
- Source files: `olist_orders_dataset.csv`, `olist_order_payments_dataset.csv`

### 3. Run Meltano (CSV → GCS Bronze)

```bash
cd pipelines/meng_hai/batch/meltano
meltano run tap-spreadsheets-anywhere target-gcs
```

Meltano tracks a high-water mark — re-running will not re-ingest already-loaded files.

### 4. Configure dbt

Copy `pipelines/lik_hong/batch/dbt/profiles.yml` and update with your project/dataset.

### 5. Run dbt (Bronze → Silver → Gold)

```bash
cd pipelines/meng_hai/batch/dbt
dbt run          # incremental by default — safe to re-run
dbt test         # validate row counts and not-null constraints
```

Full refresh (only if schema changes):
```bash
dbt run --full-refresh
```

### 6. Verify in BigQuery

```sql
SELECT COUNT(*) FROM `<your_project>.olist_gold.Fact_Orders`;
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Payments`;
```

### 7. Run your dashboard

```bash
make dev-menghai   # http://localhost:7863
```

---

## Reference Implementation

See `pipelines/lik_hong/batch/` for working Meltano configs, dbt models, and the
`run_batch.py` runner. Use it as your template.

---

## Optional: Real-time via Admin Panel

Lik Hong's real-time simulator publishes live order events to Pub/Sub.
You can optionally connect to it for a live payment feed:

1. Ask Lik Hong to grant your service account access to his Pub/Sub topic
   (`olist-orders-live`) and his BigQuery Gold dataset.
2. In the main Gradio app, go to **Admin Panel → Real-time Controls** to
   start/stop the simulator and monitor event throughput.
3. Your dbt incremental models will pick up new events on the next batch run.

Real-time is **optional** — your batch pipeline is fully self-contained without it.
