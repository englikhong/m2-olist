.PHONY: run dev install install-rt lint pipeline-batch pipeline-rt-start pipeline-rt-stop help

# ── Main app ──────────────────────────────────────────────────
run:
	@echo "Starting Olist Data Product..."
	python app.py

# ── Individual developer dashboards ──────────────────────────
dev-likhong:
	PYTHONPATH=. python dashboards/lik_hong/app.py

dev-menghai:
	PYTHONPATH=. python dashboards/meng_hai/app.py

dev-lanson:
	PYTHONPATH=. python dashboards/lanson/app.py

dev-ben:
	PYTHONPATH=. python dashboards/ben/app.py

dev-hueying:
	PYTHONPATH=. python dashboards/huey_ling/app.py

dev-kendra:
	PYTHONPATH=. python dashboards/kendra/app.py

dev-home:
	PYTHONPATH=. python dashboards/home/app.py

dev-admin:
	PYTHONPATH=. python dashboards/admin/app.py

# ── Setup ─────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

install-rt:
	pip install -r requirements.txt -r requirements-realtime.txt

# ── Linting ───────────────────────────────────────────────────
lint:
	python -m py_compile shared/theme.py shared/utils.py shared/components.py
	@for d in lik_hong meng_hai lanson ben huey_ling kendra home admin; do \
		python -m py_compile dashboards/$$d/app.py || exit 1; \
	done
	@for d in lik_hong meng_hai lanson ben huey_ling kendra; do \
		python -m py_compile dashboards/$$d/queries.py || exit 1; \
	done
	@echo "All files compile cleanly."

# ── Pipelines (Lik Hong) ─────────────────────────────────────
pipeline-batch:
	@echo "Running batch pipeline (CDC mode)..."
	python pipelines/lik_hong/batch/run_batch.py

pipeline-batch-full:
	@echo "Running batch pipeline (FULL REFRESH — use with caution)..."
	python pipelines/lik_hong/batch/run_batch.py --mode full

pipeline-rt-start:
	@echo "Starting real-time order simulator..."
	python pipelines/lik_hong/realtime/simulator/run_simulator.py &

pipeline-rt-stop:
	@echo "Stopping real-time simulator..."
	pkill -f run_simulator.py || echo "Simulator not running."

# ── Help ─────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make run               — Launch full Gradio app (all dashboards)"
	@echo "  make dev-likhong       — Run Lik Hong's dashboard standalone      (port 7862)"
	@echo "  make dev-menghai       — Run Meng Hai's dashboard standalone      (port 7863)"
	@echo "  make dev-lanson        — Run Lanson's dashboard standalone        (port 7864)"
	@echo "  make dev-ben           — Run Ben's dashboard standalone           (port 7865)"
	@echo "  make dev-hueying       — Run Huey Ling's dashboard standalone     (port 7866)"
	@echo "  make dev-kendra        — Run Kendra's dashboard standalone        (port 7867)"
	@echo "  make dev-home          — Run Home launchpad standalone            (port 7861)"
	@echo "  make dev-admin         — Run Admin panel standalone               (port 7860)"
	@echo "  make install           — Install core Python dependencies"
	@echo "  make install-rt        — Install core + real-time dependencies (Lik Hong)"
	@echo "  make lint              — Syntax-check all dashboard and shared modules"
	@echo "  make pipeline-batch    — Run batch ELT pipeline (incremental/CDC)"
	@echo "  make pipeline-batch-full — Run batch pipeline with full refresh"
	@echo "  make pipeline-rt-start — Start real-time order simulator"
	@echo "  make pipeline-rt-stop  — Stop real-time simulator"
	@echo ""
