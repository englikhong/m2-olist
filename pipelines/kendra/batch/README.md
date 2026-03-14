# Kendra — Batch Pipeline

## Overview

Loads Olist geolocation, customer, and seller data into your personal GCP BigQuery Gold dataset.

## Flow

```
/data/*.csv → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery
```

## Gold Tables Required

| Table | Purpose |
|-------|---------|
| `Dim_Customers` | customer_state, customer_city, customer_zip_code_prefix |
| `Dim_Sellers` | seller_state, seller_city — for customer/seller ratio analysis |
| `Dim_Geolocation` | lat/lng per zip code prefix — deduplicate by prefix in dbt |
| `Fact_Orders` | Order facts with delivery timestamps for regional delivery times |

---

## Steps

### 1. Set up your GCP project & auth

Follow **Steps 1–5** in `quick-setup.md`.

### 2. Configure Meltano

Copy the reference config from `pipelines/lik_hong/batch/meltano/` and update:
- GCS bucket name → your bucket (`olist-bronze-<yourname>`)
- BigQuery project → your `project_id`
- Source files: `olist_customers_dataset.csv`, `olist_sellers_dataset.csv`,
  `olist_geolocation_dataset.csv`, `olist_orders_dataset.csv`

### 3. Run Meltano (CSV → GCS Bronze)

```bash
cd pipelines/kendra/batch/meltano
meltano run tap-spreadsheets-anywhere target-gcs
```

Meltano tracks a high-water mark — re-running will not re-ingest already-loaded files.

### 4. Configure dbt

Copy `pipelines/lik_hong/batch/dbt/profiles.yml` and update with your project/dataset.

> **Important — geolocation deduplication:** `olist_geolocation_dataset.csv`
> has ~1M rows with duplicate zip code prefixes.
> In your dbt Silver model, deduplicate by `geolocation_zip_code_prefix`
> (e.g. `ROW_NUMBER() OVER (PARTITION BY zip_prefix ORDER BY lat) = 1`)
> to keep the Gold table manageable (~5,000 rows).

### 5. Run dbt (Bronze → Silver → Gold)

```bash
cd pipelines/kendra/batch/dbt
dbt run          # incremental by default — safe to re-run
dbt test
```

Full refresh (only if schema changes):
```bash
dbt run --full-refresh
```

### 6. Verify in BigQuery

```sql
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Geolocation`;
-- Should be ~5,000 rows after deduplication (not ~1M)
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Customers`;
```

### 7. Run your dashboard

```bash
make dev-kendra   # http://localhost:7867
```

---

## Reference Implementation

See `pipelines/lik_hong/batch/` for working Meltano configs, dbt models, and the
`run_batch.py` runner. Use it as your template.

---

## Optional: Real-time via Admin Panel

Lik Hong's real-time simulator publishes live order events with customer location data.
You can optionally connect to it for live geographic demand signals:

1. Ask Lik Hong to grant access to his Pub/Sub topic (`olist-orders-live`)
   and his BigQuery Gold dataset.
2. In the main Gradio app, go to **Admin Panel → Real-time Controls** to
   start/stop the simulator and monitor event throughput.
3. Your dbt incremental models will pick up new events on the next batch run.

Real-time is **optional** — your batch pipeline is fully self-contained without it.
