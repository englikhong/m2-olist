# Customer 360 + Next Best Action — Lik Hong

## Domain
- 360° customer profile lookup
- RFM segmentation (Recency, Frequency, Monetary)
- Churn probability scoring (in-pipeline ML)
- Next Best Action recommendations
- Real-time order feed (when simulator is active)

## Gold Tables Used
- `Fact_Orders`
- `Dim_Customers`
- `Dim_Reviews`
- `Dim_Payments`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/lik_hong/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/lik_hong/app.py
# Opens at http://localhost:7862
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7862 |
| Via main app | 7860 (shared) |

## Notes
- This dashboard also owns the **batch + real-time pipeline** (see `pipelines/`)
- Owns the **Admin Panel** (`dashboards/admin/`)
- Real-time order feed requires the simulator to be running (`make pipeline-rt-start`)
