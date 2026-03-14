# Reviews & Satisfaction — Lanson

## Domain
- Review score distribution (1–5 stars)
- Average score trend over time
- Review score vs delivery delay correlation
- CSAT / satisfaction trend
- Low-score order alert list
- **Sentiment analysis (Cloud Function) — later phase, owned by Lanson**

## Gold Tables Used
- `Dim_Reviews`
- `Fact_Orders`
- `Dim_Customers`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/lanson/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/lanson/app.py
# Opens at http://localhost:7864
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7864 |
| Via main app | 7860 (shared) |

## Notes
- Sentiment analysis via Cloud Functions is deferred — will be integrated after batch pipeline stabilises
