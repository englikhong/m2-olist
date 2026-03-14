# CLAUDE.md — Olist Data Product

Master guide for all developers. Read this before writing any code.

---

## Project Overview
End-to-end data product on GCP using the Brazil Olist e-commerce dataset.
Six developers each build a domain dashboard; all dashboards merge into one Gradio app.

**Stack:** GCS · BigQuery · Meltano · dbt · Dagster · Pub/Sub · Redis · Gradio · Plotly

---

## Team & Ports

| Developer | Domain | Standalone Port |
|-----------|--------|----------------|
| Lik Hong | Customer 360 + NBA + Pipeline Lead | 7862 |
| Meng Hai | Payment Analytics | 7863 |
| Lanson | Reviews & Satisfaction | 7864 |
| Ben | Product Analytics | 7865 |
| Huey Ling | Seller Performance | 7866 |
| Kendra | Geography Analytics | 7867 |
| Main App | All dashboards | 7860 |
| Admin Panel | Pipeline management | 7860 (tab) |

---

## Key Commands

```bash
make install           # Install all Python dependencies
make run               # Launch full app (all 6 dashboards + home + admin)
make dev-likhong       # Run Lik Hong's dashboard standalone
make dev-menghai       # Run Meng Hai's dashboard standalone
make dev-lanson        # Run Lanson's dashboard standalone
make dev-ben           # Run Ben's dashboard standalone
make dev-hueying       # Run Huey Ling's dashboard standalone
make dev-kendra        # Run Kendra's dashboard standalone
make lint              # Syntax-check all dashboard modules
make pipeline-batch    # Run batch ELT pipeline (Lik Hong)
make pipeline-rt-start # Start real-time simulator (Lik Hong)
make pipeline-rt-stop  # Stop real-time simulator (Lik Hong)
./launch.sh --port 7860 --share  # Launch with public share link
```

---

## Project Structure

```
m2-olist/
├── CLAUDE.md              ← You are here
├── project-plan.md        ← Full project plan and decisions
├── quick-setup.md         ← GCP setup instructions (read first!)
├── app.py                 ← Main Gradio app (all tabs)
├── requirements.txt
├── Makefile
├── launch.sh
├── .gitignore
│
├── shared/
│   ├── theme.py           ← Dark theme, colour palette, Plotly defaults
│   ├── utils.py           ← GCP client factory (ADC + service account)
│   └── components.py      ← Reusable UI components (headers, KPI cards, etc.)
│
├── config/
│   └── gcp_config_template.yaml   ← Copy this to your dashboard/config/
│
├── data/                  ← Olist CSVs (source of truth)
│
├── pipelines/
│   ├── README.md
│   ├── lik_hong/          ← Full batch + real-time pipeline (Lik Hong leads)
│   │   ├── batch/         ← Meltano + dbt + run_batch.py
│   │   ├── realtime/      ← Simulator + consumer + Redis
│   │   └── dagster/       ← Orchestration
│   ├── meng_hai/batch/    ← Batch only (reference: lik_hong/batch/)
│   ├── lanson/batch/
│   ├── ben/batch/
│   ├── huey_ling/batch/
│   └── kendra/batch/
│
├── dashboards/
│   ├── home/app.py        ← Launchpad (Lik Hong)
│   ├── admin/app.py       ← Admin Panel (Lik Hong)
│   ├── lik_hong/          ← Customer 360 + NBA
│   ├── meng_hai/          ← Payment
│   ├── lanson/            ← Reviews
│   ├── ben/               ← Products
│   ├── huey_ling/         ← Sellers
│   └── kendra/            ← Geography
│
└── docs/
    ├── FUNCTIONAL_TESTING.md
    ├── UX_TESTING.md
    ├── PERFORMANCE_TESTING.md
    └── INDEPENDENT_TESTING.md
```

---

## Merge Contract — MANDATORY for all developers

Your `dashboards/<name>/app.py` **must** follow these rules:

1. **Export a `dashboard` object** of type `gr.Blocks`:
   ```python
   with gr.Blocks(...) as dashboard:
       ...  # your UI
   ```

2. **Never call `dashboard.launch()` at module level** — only under:
   ```python
   if __name__ == "__main__":
       dashboard.launch(server_port=YOUR_PORT, show_error=True)
   ```

3. **Import theme from shared, not inline CSS:**
   ```python
   from shared.theme import olist_theme, CUSTOM_CSS
   with gr.Blocks(theme=olist_theme, css=CUSTOM_CSS, ...) as dashboard:
   ```

4. **Load GCP client via shared utils:**
   ```python
   from shared.utils import dev_config_path, make_bq_client_getter
   _get_client = make_bq_client_getter(dev_config_path("<your_name>"))
   # then in each data loader: client, cfg, err = _get_client()
   ```

5. **Tab title format:** `"<Icon> <Domain> — <Your Name>"`
   (set in `app.py`, not in your dashboard)

6. **Run `make lint` before submitting** your dashboard for integration.

---

## GCP Configuration

Each developer has their own GCP project. Config file lives at:
```
dashboards/<your_name>/config/gcp_config.yaml
```
This file is **gitignored** — never commit it.

Copy the template:
```bash
cp config/gcp_config_template.yaml dashboards/<your_name>/config/gcp_config.yaml
```

Full instructions: `quick-setup.md`

---

## Theme & Style Rules

- All charts must use `PLOTLY_LAYOUT` from `shared/theme.py` as the base layout dict
- All UI must use `olist_theme` and `CUSTOM_CSS` from `shared/theme.py`
- Colour usage:
  - `#FF4444` red   — alerts, errors, critical metrics, losses
  - `#FF8C00` orange — primary accent, revenue, neutral highlights
  - `#FFD700` gold   — secondary accent, averages, info
  - `#00C851` green  — positive trends, on-time, good performance
- No inline CSS that overrides the dark background

---

## Coding Conventions

- Python 3.11+, type hints where practical
- All queries in `queries.py` — no SQL in `app.py`
- Data loading functions must handle GCP errors gracefully and return an empty chart/table (not crash)
- No `print()` in dashboard code — use `gr.Warning()` or `gr.Info()` for user-visible messages
- Keep `app.py` under 200 lines — complex logic goes in `queries.py` or helper modules

---

## Real-time Data (Lik Hong leads)

- Real-time pipeline is **Lik Hong's responsibility**
- Other developers may opt in by subscribing to the Pub/Sub topic — coordinate with Lik Hong
- Real-time is controlled via Admin Panel → Start/Stop Agent

---

## Testing

See `docs/` for detailed checklists:
- `docs/FUNCTIONAL_TESTING.md`
- `docs/UX_TESTING.md`
- `docs/PERFORMANCE_TESTING.md`
- `docs/INDEPENDENT_TESTING.md`
