# Pipelines

Each developer maintains their own pipeline folder to ingest data into their personal GCP project.

## Structure

```
pipelines/
├── lik_hong/          ← LEAD — Full batch + real-time pipeline
│   ├── batch/
│   │   ├── meltano/   ← Extract & Load: CSV → GCS Bronze
│   │   └── dbt/       ← Transform: Bronze → Silver → Gold (star schema)
│   ├── realtime/
│   │   ├── simulator/ ← Fabricated order event publisher (Pub/Sub)
│   │   ├── consumer/  ← Pub/Sub subscriber → GCS Streaming Bucket
│   │   └── redis_cache/ ← Memorystore config
│   └── dagster/       ← Orchestration: batch jobs + real-time sensors
│
├── meng_hai/batch/    ← Batch only (CSV → GCS → dbt → BigQuery)
├── lanson/batch/
├── ben/batch/
├── huey_ling/batch/
└── kendra/batch/
```

## For Lik Hong (Lead)
Full pipeline — batch + real-time. See `pipelines/lik_hong/` for all components.

## For All Other Developers (Meng Hai, Lanson, Ben, Huey Ling, Kendra)
Batch pipeline only. Use the template in your `pipelines/<name>/batch/` folder.
Real-time pipeline is optional — if you want to consume live data, coordinate with Lik Hong.

## Quick Start (Batch)
```bash
# Run your batch pipeline
cd pipelines/<your_name>/batch
# Follow instructions in the README inside your batch folder
```

## Real-time (Lik Hong only, or by arrangement)
```bash
make pipeline-rt-start   # Start order simulator
make pipeline-rt-stop    # Stop simulator
# Or use the Admin Panel in the Gradio app
```
