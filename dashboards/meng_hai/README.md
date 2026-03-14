# Payment Analytics — Meng Hai

## Domain
- Payment method breakdown (credit card, boleto, voucher, debit card)
- Instalment analysis and distribution
- Monthly revenue by payment type
- Average Order Value (AOV) by method
- Cancellation rate trends

## Gold Tables Used
- `Fact_Orders`
- `Dim_Payments`

## Setup
1. Copy `config/gcp_config_template.yaml` → `dashboards/meng_hai/config/gcp_config.yaml`
2. Fill in your GCP `project_id`, `dataset`, and auth method
3. See `quick-setup.md` for full instructions

## Run standalone
```bash
python dashboards/meng_hai/app.py
# Opens at http://localhost:7863
```

## Ports
| Mode | Port |
|------|------|
| Standalone | 7863 |
| Via main app | 7860 (shared) |
