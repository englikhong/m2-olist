# Ben — Batch Pipeline

## Overview

Loads Olist product and order data into your personal GCP BigQuery Gold dataset.

## Flow

```
/data/*.csv → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery
```

## Gold Tables Required

| Table | Purpose |
|-------|---------|
| `Fact_Orders` | Order facts incl. product_id, category, payment_value |
| `Dim_Products` | Product dimensions: category (PT + EN), weight, dimensions |
| `Dim_Reviews` | review_score joined to orders for per-product quality metrics |

---

## Steps

### 1. Set up your GCP project & auth

Follow **Steps 1–5** in `quick-setup.md`.

### 2. Configure Meltano

Copy the reference config from `pipelines/lik_hong/batch/meltano/` and update:
- GCS bucket name → your bucket (`olist-bronze-<yourname>`)
- BigQuery project → your `project_id`
- Source files: `olist_orders_dataset.csv`, `olist_products_dataset.csv`,
  `olist_order_reviews_dataset.csv`, `product_category_name_translation.csv`

### 3. Run Meltano (CSV → GCS Bronze)

```bash
cd pipelines/ben/batch/meltano
meltano run tap-spreadsheets-anywhere target-gcs
```

Meltano tracks a high-water mark — re-running will not re-ingest already-loaded files.

### 4. Configure dbt

Copy `pipelines/lik_hong/batch/dbt/profiles.yml` and update with your project/dataset.

> **Important — category translation:** In your dbt Silver → Gold model, join
> `product_category_name_translation.csv` so that
> `product_category_name_english` is populated in `Fact_Orders`.
> Without this join, category filters in your dashboard will return no results.

### 5. Run dbt (Bronze → Silver → Gold)

```bash
cd pipelines/ben/batch/dbt
dbt run          # incremental by default — safe to re-run
dbt test
```

Full refresh (only if schema changes):
```bash
dbt run --full-refresh
```

### 6. Verify in BigQuery

```sql
SELECT COUNT(*) FROM `<your_project>.olist_gold.Dim_Products`;
SELECT COUNT(*) FROM `<your_project>.olist_gold.Fact_Orders`
WHERE product_category_name_english IS NOT NULL;
```

### 7. Run your dashboard

```bash
make dev-ben   # http://localhost:7865
```

---

## Reference Implementation

See `pipelines/lik_hong/batch/` for working Meltano configs, dbt models, and the
`run_batch.py` runner. Use it as your template.

---

## Optional: Real-time via Admin Panel

Lik Hong's real-time simulator publishes live order events to Pub/Sub.
You can optionally connect to it for live product demand signals:

1. Ask Lik Hong to grant access to his Pub/Sub topic (`olist-orders-live`)
   and his BigQuery Gold dataset.
2. In the main Gradio app, go to **Admin Panel → Real-time Controls** to
   start/stop the simulator and monitor event throughput.
3. Your dbt incremental models will pick up new events on the next batch run.

Real-time is **optional** — your batch pipeline is fully self-contained without it.
