# Seller Performance — Huey Ling

## Domain
Create dashboard for Seller Performance with the following:
Metrics: 
- Revenue per seller
- Orders per seller
- Average order value per seller
- Seller geographic distribution
Dashboard Views: 
- Top sellers leaderboard by revenue, review score
- Seller sales distribution
- Seller location map
Insights: 
- Marketplace concentration
- Identification of power sellers
- At-risk seller flag: sellers with low rating

## Gold Tables Used
- `Dim_Sellers`
- `Fact_Orders`
- `Dim_Reviews`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/huey_ling/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Gradio Dashboard - Run standalone
```bash
python dashboards/huey_ling/app.py
# Opens at http://localhost:7866
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7866 |
| Via main app | 7860 (shared) |
