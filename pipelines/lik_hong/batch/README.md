# Lik Hong — Batch Pipeline

## Flow
CSV files (`/data/`) → Meltano (EL) → GCS Bronze → dbt → Silver → Gold → BigQuery

## Components

### 1. Meltano (`meltano/`)
Extracts all Olist CSVs and loads raw Parquet files into GCS Bronze bucket.

```bash
cd pipelines/lik_hong/batch/meltano
meltano install
meltano run tap-csv target-gcs
```

### 2. dbt (`dbt/`)
Transforms Bronze → Silver (cleanse, PII mask) → Gold (star schema).

```bash
cd pipelines/lik_hong/batch/dbt
dbt deps
dbt run --profiles-dir .
```

**Models:**
- `staging/` — Bronze → Silver (type casting, null handling, PII masking)
- `marts/` — Silver → Gold star schema:
  - `Fact_Orders`
  - `Dim_Customers`
  - `Dim_Payments`
  - `Dim_Reviews`
  - `Dim_Products`
  - `Dim_Sellers`
  - `Dim_Geolocation`

## run_batch.py
Top-level batch runner called by `make pipeline-batch` and the Admin Panel.
Supports `--mode cdc` for incremental/CDC run.

```bash
python pipelines/batch/run_batch.py           # Full refresh
python pipelines/batch/run_batch.py --mode cdc  # Incremental CDC
```
