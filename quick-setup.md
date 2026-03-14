# Quick Setup Guide — Olist Data Product

**Read this first.** Complete every step before running any dashboard or pipeline.
All commands are run from the **project root** (`m2-olist/`) unless stated otherwise.

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.11+ | `python --version` |
| pip | latest | `pip --version` |
| gcloud CLI | latest | `gcloud --version` |
| Git | any | `git --version` |

Install gcloud: https://cloud.google.com/sdk/docs/install

---

## Step 1 — Clone the repo & install dependencies

```bash
git clone <repo-url>
cd m2-olist
make install
```

> **Lik Hong only** — also install real-time dependencies:
> ```bash
> make install-rt
> ```

---

## Step 2 — Create your GCP project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `olist-likhong`, `olist-menghai`, etc.)
3. Note your **Project ID** — shown in the project selector dropdown
4. Enable APIs (Console → APIs & Services → Enable APIs):

| Developer | APIs to enable |
|-----------|---------------|
| All | BigQuery API, Cloud Storage JSON API |
| Lik Hong only | Cloud Pub/Sub API, Cloud Memorystore for Redis API |

---

## Step 3 — Create GCP resources

### BigQuery dataset (all developers)
```bash
bq mk --dataset --location=US <YOUR_PROJECT_ID>:olist_gold
```

### GCS buckets (all developers — needed for batch pipeline)
```bash
# Bronze bucket — raw Meltano output
gcloud storage buckets create gs://<YOUR_PROJECT_ID>-bronze --location=US

# Raw staging dataset for dbt sources
bq mk --dataset --location=US <YOUR_PROJECT_ID>:olist_raw
```

### Additional resources (Lik Hong only)
```bash
# Streaming bucket
gcloud storage buckets create gs://<YOUR_PROJECT_ID>-streaming --location=US

# Pub/Sub topic + subscription
gcloud pubsub topics create olist-orders-live
gcloud pubsub subscriptions create olist-orders-sub \
    --topic=olist-orders-live \
    --ack-deadline=60
```

---

## Step 4 — Authenticate with GCP

### Option A — Application Default Credentials ✅ Recommended

```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

This opens a browser. Log in with your Google account. Credentials are cached locally and used automatically by BigQuery and GCS clients.

### Option B — Service Account Key (CI / no-browser environments)

1. GCP Console → IAM & Admin → Service Accounts → Create
2. Grant roles: `BigQuery Data Editor`, `BigQuery Job User`, `Storage Object Admin`
3. Keys → Add Key → JSON → download
4. Move the file:
   ```bash
   mv ~/Downloads/<key>.json dashboards/<your_name>/config/service_account.json
   ```

---

## Step 5 — Configure gcp_config.yaml

Copy the template to your dashboard config folder:

```bash
cp config/gcp_config_template.yaml dashboards/<your_name>/config/gcp_config.yaml
```

Edit the file — **ADC (Option A):**
```yaml
auth_method: adc
project_id: <YOUR_PROJECT_ID>        # e.g. olist-likhong-123456
dataset: olist_gold
location: US
```

**Service Account (Option B):**
```yaml
auth_method: service_account
project_id: <YOUR_PROJECT_ID>
dataset: olist_gold
location: US
key_path: dashboards/<your_name>/config/service_account.json
```

> **Security:** `gcp_config.yaml` and `*.json` key files are gitignored. Never commit them.

---

## Step 6 — Run your batch pipeline

Each developer runs their **own** pipeline. Follow your pipeline README:

```
pipelines/<your_name>/batch/README.md
```

Quick reference:

| Developer | Pipeline command |
|-----------|-----------------|
| Lik Hong | `make pipeline-batch` |
| Meng Hai | `cd pipelines/meng_hai/batch && meltano run tap-csv target-gcs && dbt run` |
| Lanson | `cd pipelines/lanson/batch && meltano run tap-csv target-gcs && dbt run` |
| Ben | `cd pipelines/ben/batch && meltano run tap-csv target-gcs && dbt run` |
| Huey Ling | `cd pipelines/huey_ling/batch && meltano run tap-csv target-gcs && dbt run` |
| Kendra | `cd pipelines/kendra/batch && meltano run tap-csv target-gcs && dbt run` |

> Your pipeline must complete before your dashboard can load data from BigQuery.

---

## Step 7 — Run your dashboard

**Standalone dev mode** (run from project root):

```bash
make dev-likhong    # → http://localhost:7862
make dev-menghai    # → http://localhost:7863
make dev-lanson     # → http://localhost:7864
make dev-ben        # → http://localhost:7865
make dev-hueying    # → http://localhost:7866
make dev-kendra     # → http://localhost:7867
make dev-home       # → http://localhost:7861
make dev-admin      # → http://localhost:7860
```

**Full app (all dashboards merged):**
```bash
make run
# Opens at http://localhost:7860
```

> If you see `ModuleNotFoundError: No module named 'shared'`, you are not running from
> the project root. Always run `make` commands from `m2-olist/`.

---

## Step 8 — (Lik Hong only) Real-time pipeline

### Start / stop the order event simulator
```bash
make pipeline-rt-start   # starts in background, publishes to olist-orders-live
make pipeline-rt-stop    # sends SIGTERM to the simulator process
```

Or use the **Admin Panel** → Start Agent / Stop Agent button.

### Start the Pub/Sub consumer
```bash
python pipelines/lik_hong/realtime/consumer/consumer.py \
    --project <YOUR_PROJECT_ID> \
    --batch-size 50 \
    --flush-secs 30
```

### Refresh Redis cache (after each batch run)
```bash
python pipelines/lik_hong/realtime/redis_cache/load_cache.py
```

### Redis — local dev
```bash
# Ubuntu/Debian
sudo apt install redis-server && redis-server

# macOS
brew install redis && brew services start redis
```

### Dagster orchestration (optional)
```bash
cd pipelines/lik_hong/dagster
dagster dev   # UI at http://localhost:3000
```

---

## Step 9 — Verify everything works

```bash
make lint                   # syntax-check all dashboard modules
make dev-<yourname>         # launch your dashboard
```

In your dashboard, if charts show `"GCP not configured"`, your pipeline has not run yet
or your `gcp_config.yaml` has an incorrect `project_id`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FileNotFoundError: gcp_config.yaml` | `cp config/gcp_config_template.yaml dashboards/<name>/config/gcp_config.yaml` |
| `DefaultCredentialsError` | `gcloud auth application-default login` |
| `403 Access Denied (BigQuery)` | Service account needs `BigQuery Job User` + `BigQuery Data Editor` roles |
| `ModuleNotFoundError: shared` | Run from project root; all `make` commands handle this automatically |
| `Chart shows "GCP not configured"` | `gcp_config.yaml` missing or `project_id` wrong |
| Port already in use | `lsof -ti:<port> | xargs kill -9` |
| `meltano: command not found` | `pip install meltano` |
| `dbt: command not found` | `pip install dbt-bigquery` |

---

## Port Reference

| Dashboard | `make` target | Port |
|-----------|--------------|------|
| Main App (all tabs) | `make run` | 7860 |
| Home / Launchpad | `make dev-home` | 7861 |
| Lik Hong — Customer 360 | `make dev-likhong` | 7862 |
| Meng Hai — Payments | `make dev-menghai` | 7863 |
| Lanson — Reviews | `make dev-lanson` | 7864 |
| Ben — Products | `make dev-ben` | 7865 |
| Huey Ling — Sellers | `make dev-hueying` | 7866 |
| Kendra — Geography | `make dev-kendra` | 7867 |
