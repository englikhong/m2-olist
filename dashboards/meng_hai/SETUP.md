# Payment Analytics — Setup Guide

Connect to Meng Hai's BigQuery so the Payment Analytics tab shows live data.

## Steps

### 1. Get the service account key

Ask Meng Hai for the JSON key file (shared privately via Telegram/email — **never committed to git**).

### 2. Save the key file

```bash
# From the repo root:
mkdir -p dashboards/meng_hai/config
# Save the JSON key Meng Hai sent you as:
dashboards/meng_hai/config/service_account.json
```

### 3. Create the GCP config

Create `dashboards/meng_hai/config/gcp_config.yaml` with this exact content:

```yaml
auth_method: service_account
project_id: olist-dsai
dataset: olist_gold
location: US
key_path: dashboards/meng_hai/config/service_account.json
```

### 4. Run the app

```bash
make run            # Full app on port 7860
# or
make dev-menghai    # Standalone on port 7863
```

The Payment Analytics tab will connect to BigQuery and show live data.

## Notes

- Both `gcp_config.yaml` and `service_account.json` are gitignored — they will not be committed.
- No `.env` file is needed.
- If you don't have the key, the dashboard will show empty charts with a graceful error message.
