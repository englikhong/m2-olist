# Seller Performance — Huey Ling

## Domain
- Seller leaderboard by revenue, fulfilment speed, and review score
- Delivery latency: actual vs estimated (distribution chart)
- Review score heatmap by seller state
- At-risk seller flagging (low rating OR high late delivery)
- Seller geographic coverage

## Gold Tables Used
- `Dim_Sellers`
- `Fact_Orders`
- `Dim_Reviews`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/huey_ling/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/huey_ling/app.py
# Opens at http://localhost:7866
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7866 |
| Via main app | 7860 (shared) |
