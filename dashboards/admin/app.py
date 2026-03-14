"""
dashboards/admin/app.py — Admin Control Panel
──────────────────────────────────────────────
Owner: Lik Hong

Sections:
  1. Batch Ingestion Pipeline  — 6-stage gauge progress tracker
  2. Cache Management          — Redis flush
  3. Real-time Simulator       — Start / Stop agent
  4. Pipeline Status           — Quick health check

Exports: dashboard (gr.Blocks)
"""

import atexit
import os
import gradio as gr
import plotly.graph_objects as go
import subprocess
import threading
import time
from datetime import datetime

from shared.theme import CUSTOM_CSS, COLORS
from shared.components import page_header, section_title, alert_box

# ── Simulator state ────────────────────────────────────────────
_simulator_proc: subprocess.Popen | None = None
_simulator_lock = threading.Lock()


def _cleanup_simulator():
    global _simulator_proc
    if _simulator_proc and _simulator_proc.poll() is None:
        _simulator_proc.terminate()
        try:
            _simulator_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _simulator_proc.kill()

atexit.register(_cleanup_simulator)


def _ts() -> str:
    return datetime.utcnow().strftime("[%H:%M:%S]")


# ══════════════════════════════════════════════════════════════
# Section 1 — Batch Ingestion Pipeline gauges
# ══════════════════════════════════════════════════════════════

_STAGES = [
    ("Extract→Bronze",  "Meltano/GCS tap",    "pipelines/lik_hong/batch/meltano",
     ["meltano", "run", "tap-csv", "target-gcs"]),
    ("Load→BigQuery",   "Bronze→olist_raw",   None,
     ["python", "pipelines/lik_hong/batch/run_batch.py", "--step", "gcs-to-bq"]),
    ("dbt Silver",      "PII mask · CDC",     "pipelines/lik_hong/batch/dbt",
     ["dbt", "run", "--select", "staging", "--profiles-dir", ".", "--full-refresh"]),
    ("dbt Gold",        "Star Schema",        "pipelines/lik_hong/batch/dbt",
     ["dbt", "run", "--select", "marts",   "--profiles-dir", ".", "--full-refresh"]),
    ("Feature Store",   "Redis cache",        None,
     ["python", "pipelines/lik_hong/realtime/redis_cache/load_cache.py"]),
    ("Dagster Sensor",  "Cursor advance",     None, None),
]


def _gauge(pct: float, title: str, state: str = "idle") -> go.Figure:
    if state == "done":
        bar_col = "#00C851";  num_col = "#00C851"
    elif state == "active":
        bar_col = "#FF8C00";  num_col = "#FFD700"
    elif state == "error":
        bar_col = "#FF4444";  num_col = "#FF4444"
    else:
        bar_col = "rgba(80,50,0,0.35)"; num_col = "rgba(180,140,60,0.35)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": " %", "font": {"size": 21, "color": num_col, "family": "Courier New"}},
        title={"text": title, "font": {"size": 9, "color": "rgba(200,170,80,0.7)", "family": "Courier New"}},
        gauge={
            "axis": {
                "range": [0, 100], "tickwidth": 1,
                "tickcolor": "rgba(255,255,255,0.08)",
                "tickfont": {"size": 7, "color": "rgba(255,200,100,0.2)"},
            },
            "bar": {"color": bar_col, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [{"range": [0, 100], "color": "rgba(40,20,0,0.65)"}],
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(6,3,0,0.97)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=28, b=4),
        height=148,
        font=dict(family="Courier New"),
    )
    return fig


def _pipe_status_html(state: str, stage_label: str = "") -> str:
    if state == "running":
        bg, col, label = "rgba(255,140,0,0.1)", "#FF8C00", f"▶  Running…  {stage_label}"
    elif state == "done":
        bg, col, label = "rgba(0,200,81,0.1)", "#00C851", "✓  Pipeline Complete"
    elif state == "error":
        bg, col, label = "rgba(255,68,68,0.1)", "#FF4444", "✗  Stage Failed — see log"
    else:
        bg, col, label = "rgba(60,40,0,0.1)", "rgba(180,140,60,0.4)", "◈  Idle — click Run to start"
    return (
        f'<div style="padding:9px 18px;background:{bg};border:1px solid {col};border-radius:4px;'
        f'font-family:Courier New,monospace;font-size:11px;color:{col};letter-spacing:2px;">'
        f'{label}</div>'
    )


def _idle_gauges():
    return tuple(_gauge(0, f"Stage {i+1}<br>{_STAGES[i][0]}", "idle") for i in range(6))


def _run_pipeline_gen(mode: str):
    """Generator: runs real pipeline stages, yields (g1…g6, status_html, log)."""
    progress = [0.0] * 6
    states   = ["idle"] * 6
    log_lines: list[str] = []

    def emit(state_key: str = "running", stage_lbl: str = ""):
        figs = [_gauge(progress[i], f"Stage {i+1}<br>{_STAGES[i][0]}", states[i]) for i in range(6)]
        return (*figs, _pipe_status_html(state_key, stage_lbl), "\n".join(log_lines[-40:]))

    log_lines.append(f"{_ts()} === Batch Pipeline Start (mode={mode}) ===")
    yield emit("running")

    fr_flag = [] if mode == "cdc" else ["--full-refresh"]

    for idx, (label, desc, cwd, cmd) in enumerate(_STAGES):
        states[idx] = "active"
        log_lines.append(f"{_ts()} ▶ Stage {idx+1}: {label}  ({desc})")
        yield emit("running", f"Stage {idx+1} · {label}")

        if cmd is None:
            # Informational/no-op stage
            for p in range(0, 101, 8):
                progress[idx] = float(p)
                yield emit("running", f"Stage {idx+1} · {label}")
                time.sleep(0.06)
            progress[idx] = 100.0
            states[idx] = "done"
            log_lines.append(f"{_ts()} ✓ Stage {idx+1} complete")
            yield emit("running", f"Stage {idx+1} · {label}")
            continue

        # Patch dbt commands with --full-refresh / CDC flag
        effective_cmd = list(cmd)
        if "dbt" in effective_cmd and "--full-refresh" in effective_cmd and mode == "cdc":
            effective_cmd.remove("--full-refresh")

        result: list = []

        def _run(c=effective_cmd, d=cwd):
            r = subprocess.run(c, cwd=d, capture_output=True, text=True, timeout=900)
            result.append(r)

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        p = 0.0
        while t.is_alive():
            p = min(90.0, p + 1.2)
            progress[idx] = p
            yield emit("running", f"Stage {idx+1} · {label}")
            time.sleep(0.35)

        t.join()

        if result and result[0].returncode == 0:
            progress[idx] = 100.0
            states[idx] = "done"
            for line in (result[0].stdout or "").splitlines()[-6:]:
                log_lines.append(f"  {line}")
            log_lines.append(f"{_ts()} ✓ Stage {idx+1} complete ({int((idx+1)/6*100)} %)")
        else:
            states[idx] = "error"
            if result:
                for line in (result[0].stderr or "").splitlines()[-8:]:
                    log_lines.append(f"  ERR: {line}")
            log_lines.append(f"{_ts()} ✗ Stage {idx+1} failed — stopping.")
            yield emit("error")
            return

        yield emit("running", f"Stage {idx+1} · done")

    log_lines.append(f"{_ts()} === Pipeline Complete ===")
    yield emit("done")


# ══════════════════════════════════════════════════════════════
# Section 2 — Cache / CDC / Simulator
# ══════════════════════════════════════════════════════════════

def action_clear_cache() -> str:
    lines = [f"{_ts()} Starting cache clear..."]
    try:
        from shared.utils import get_redis_client
        r = get_redis_client()
        n = r.dbsize(); r.flushdb()
        lines.append(f"{_ts()} ✓ Redis flushed — {n} keys cleared.")
    except Exception as e:
        lines.append(f"{_ts()} ⚠ Redis unavailable: {e}  (skipping)")
    lines.append(f"{_ts()} ✓ Cache clear complete.")
    return "\n".join(lines)


def action_start_simulator() -> str:
    global _simulator_proc
    with _simulator_lock:
        if _simulator_proc and _simulator_proc.poll() is None:
            return f"{_ts()} ⚠ Simulator already running (PID {_simulator_proc.pid})."
        try:
            _simulator_proc = subprocess.Popen(
                ["python", "pipelines/lik_hong/realtime/simulator/run_simulator.py"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            time.sleep(1)
            if _simulator_proc.poll() is not None:
                return f"{_ts()} ✗ Simulator exited immediately."
            return (
                f"{_ts()} ✓ Simulator started (PID {_simulator_proc.pid}).\n"
                f"{_ts()}   Publishing events to olist-orders-live…"
            )
        except FileNotFoundError:
            return f"{_ts()} ⚠ Simulator script not found. Build real-time pipeline first."


def action_stop_simulator() -> str:
    global _simulator_proc
    with _simulator_lock:
        if _simulator_proc is None or _simulator_proc.poll() is not None:
            return f"{_ts()} ℹ Simulator is not running."
        pid = _simulator_proc.pid
        _simulator_proc.terminate()
        try:
            _simulator_proc.wait(timeout=10)
            return f"{_ts()} ✓ Simulator stopped (PID {pid})."
        except subprocess.TimeoutExpired:
            _simulator_proc.kill()
            return f"{_ts()} ✓ Simulator force-killed (PID {pid})."


def get_pipeline_status() -> str:
    sim_running = _simulator_proc is not None and _simulator_proc.poll() is None
    return "\n".join([
        f"{_ts()} Pipeline Status Report",
        "─" * 48,
        f"  Real-time Simulator : {'🟢 RUNNING' if sim_running else '⚫ STOPPED'}",
        f"  Dagster UI          : http://localhost:3000",
        "─" * 48,
        "  Gold Tables (BigQuery) — run pipeline to populate.",
    ])


# ══════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════

_GAUGE_CSS = CUSTOM_CSS + """
.gauge-row .block { background: rgba(6,3,0,0.97) !important;
                    border: 1px solid rgba(255,140,0,0.22) !important;
                    border-radius: 6px !important; padding: 0 !important; }
.pipe-section { background: rgba(5,2,0,0.98); border: 1px solid rgba(255,140,0,0.25);
                border-radius: 8px; padding: 16px 18px; margin-bottom: 10px; }
.pipe-hdr { font-size: 11px; font-weight: bold; color: #FF8C00; letter-spacing: 2px;
            text-transform: uppercase; margin-bottom: 3px; }
.pipe-sub { font-size: 10px; color: rgba(255,200,100,0.45); margin-bottom: 10px; }
"""

with gr.Blocks(analytics_enabled=False, title="Admin Panel — Lik Hong") as dashboard:

    page_header(
        "Admin Control Panel",
        subtitle="Pipeline management · Cache control · Real-time agent",
        icon="⚙️",
    )

    alert_box(
        "Admin actions affect the shared pipeline and data state. "
        "Coordinate with the team before running destructive operations.",
        level="warn",
    )

    # ── 1. Batch Ingestion Pipeline ──────────────────────────────
    gr.HTML("""<div class="pipe-section">
        <div class="pipe-hdr">1 · Batch Ingestion Pipeline</div>
        <div class="pipe-sub">
            Simulates the full GCP pipeline:
            <strong>Meltano → Bronze (GCS/BQ) → dbt Silver (PII masking, CDC)
            → dbt Gold (Star Schema) → Redis Feature Store → Dagster sensor.</strong>
        </div>
    </div>""")

    with gr.Row():
        run_full_btn = gr.Button("▶  Run Full Refresh", variant="primary",  scale=3)
        run_cdc_btn  = gr.Button("⟳  Run CDC Mode",     variant="secondary", scale=3)
        reset_btn    = gr.Button("↺  Reset",             variant="secondary", scale=1)

    pipe_status = gr.HTML(_pipe_status_html("idle"))

    with gr.Row(elem_classes=["gauge-row"]):
        g1 = gr.Plot(value=_gauge(0, "Stage 1<br>Extract→Bronze",  "idle"), show_label=False)
        g2 = gr.Plot(value=_gauge(0, "Stage 2<br>Load→BigQuery",   "idle"), show_label=False)
        g3 = gr.Plot(value=_gauge(0, "Stage 3<br>dbt Silver",      "idle"), show_label=False)
        g4 = gr.Plot(value=_gauge(0, "Stage 4<br>dbt Gold",        "idle"), show_label=False)
        g5 = gr.Plot(value=_gauge(0, "Stage 5<br>Feature Store",   "idle"), show_label=False)
        g6 = gr.Plot(value=_gauge(0, "Stage 6<br>Dagster Sensor",  "idle"), show_label=False)

    pipe_log = gr.Textbox(
        label="Pipeline Log", lines=5, interactive=False,
        placeholder="Click Run to start the batch pipeline…",
    )

    _pipe_outs = [g1, g2, g3, g4, g5, g6, pipe_status, pipe_log]
    run_full_btn.click(fn=lambda: _run_pipeline_gen("full"), outputs=_pipe_outs)
    run_cdc_btn.click( fn=lambda: _run_pipeline_gen("cdc"),  outputs=_pipe_outs)
    reset_btn.click(
        fn=lambda: (*_idle_gauges(), _pipe_status_html("idle"), ""),
        outputs=_pipe_outs,
    )

    # ── 2. Cache + Real-time ──────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=1):
            section_title("Cache Management", accent="gold")
            gr.HTML(f'<p style="color:{COLORS["text_secondary"]};font-size:0.85rem;margin:0 0 10px 0">'
                    'Flushes Redis Memorystore and in-memory Gradio state. Safe at any time.</p>')
            clear_cache_btn = gr.Button("🗑 Clear App Cache", variant="secondary")
            cache_log = gr.Textbox(label="Output", lines=5, interactive=False,
                                   placeholder="Cache clear log will appear here…")
            clear_cache_btn.click(fn=action_clear_cache, outputs=cache_log)

        with gr.Column(scale=1):
            section_title("Real-time Order Simulator", accent="green")
            gr.HTML(f'<p style="color:{COLORS["text_secondary"]};font-size:0.85rem;margin:0 0 10px 0">'
                    'Publishes synthetic order events to Pub/Sub <code>olist-orders-live</code>.</p>')
            with gr.Row():
                start_btn = gr.Button("▶ Start Agent", variant="primary")
                stop_btn  = gr.Button("■ Stop Agent",  variant="stop")
            sim_log = gr.Textbox(label="Simulator Output", lines=5, interactive=False,
                                 placeholder="Simulator log will appear here…")
            start_btn.click(fn=action_start_simulator, outputs=sim_log)
            stop_btn.click( fn=action_stop_simulator,  outputs=sim_log)

            section_title("Pipeline Status", accent="orange")
            status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
            status_log = gr.Textbox(label="Status", lines=6, interactive=False,
                                    placeholder="Click Refresh Status…")
            status_btn.click(fn=get_pipeline_status, outputs=status_log)


if __name__ == "__main__":
    dashboard.launch(server_port=7860, show_error=True, css=_GAUGE_CSS)
