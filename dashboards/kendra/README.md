# Geography Analytics — Kendra

## Domain
- Customer density choropleth by Brazilian state
- Seller distribution by state
- Average delivery time by state (colour-coded)
- Customer geolocation scatter map (sample points)
- Underserved region opportunity analysis (customer/seller ratio)

## Gold Tables Used
- `Dim_Customers`
- `Dim_Sellers`
- `Dim_Geolocation`
- `Fact_Orders`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/kendra/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/kendra/app.py
# Opens at http://localhost:7867
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7867 |
| Via main app | 7860 (shared) |

## Notes
- Choropleth map requires internet access to fetch the Brazil GeoJSON boundary file
- Scatter map uses `carto-darkmatter` tile — works offline-first for points
