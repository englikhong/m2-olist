# Product Analytics — Ben

## Domain
- Top and bottom performing products by revenue and order count
- Product category performance matrix
- Category review score vs volume scatter
- Monthly category revenue trend
- Product demand signals (order frequency proxy)

## Gold Tables Used
- `Fact_Orders`
- `Dim_Products`
- `Dim_Reviews`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/ben/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/ben/app.py
# Opens at http://localhost:7865
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7865 |
| Via main app | 7860 (shared) |
