"""Optional Cursor-agent (or template) R&D gap narrative for unobtanium knobs."""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ssto.orbitron.experiment.cursor_credentials import apply_cursor_api_key_to_env, tokens_yaml_path
from ssto.orbitron.experiment.gap_pipeline import gap_factors

_REPO_ROOT = Path(__file__).resolve().parents[3]
_UNOBTANIUM_MD = _REPO_ROOT / "ssto" / "orbitron" / "UNOBTANIUM.md"

_KNOB_LABELS: dict[str, str] = {
    "field_emission_margin": "U1 cathode field emission margin (600 kV, no arc)",
    "max_wall_heat_flux_W_m2": "U2 max wall heat flux [W/m²]",
    "ch4_cooling_effectiveness": "U2 CH₄ loop cooling effectiveness",
    "hts_capability_scale": "U3 HTS bore field capability scale (2 T nominal)",
    "fusion_reactivity_scale": "U4 p-¹¹B fusion reactivity / confinement scale",
    "beam_coupling_scale": "U4 ion beam coupling scale",
}


def _gap_table_md(step09: dict[str, Any]) -> str:
    req = step09.get("unobtanium_required") or {}
    nom = step09.get("unobtanium_nominal") or {}
    factors = gap_factors(step09)
    lines = [
        "| Knob | Nominal | Required (inverse) | Gap factor |",
        "|------|---------|-------------------|------------|",
    ]
    max_f = max(factors.values(), default=1.0)
    for key in sorted(req.keys()):
        label = _KNOB_LABELS.get(key, key)
        n = float(nom.get(key, 1.0))
        r = float(req[key])
        f = factors.get(key, 1.0)
        flag = " ← largest gap" if f == max_f and f > 1.05 else ""
        lines.append(f"| {label} | {n:.4g} | {r:.4g} | {f:.3f}×{flag} |")
    return "\n".join(lines)


def _build_agent_prompt(
    *,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
) -> str:
    unob_md = ""
    if _UNOBTANIUM_MD.is_file():
        unob_md = _UNOBTANIUM_MD.read_text(encoding="utf-8")[:8000]

    proof_validated = step08_proof.get("design_validated") if step08_proof else None
    factors = gap_factors(step09)
    top = sorted(factors.items(), key=lambda kv: abs(kv[1] - 1.0), reverse=True)[:3]

    return f"""You are a fusion materials and plasma-engineering analyst.

## Task
Review the Orbitron p-¹¹B unobtanium gap from a **stress inverse** (literature-class ⟨σv⟩,
NOT the design-calibrated curve). Minimum performance scales to hit {step09.get('target_mw', 3.5)} MW
while passing U1–U4 gates. Use general knowledge and **web search** where helpful (2024–2026).

**Do not claim the reactor is proven.** Distinguish Tier-1 calibrated closure from physics evidence.

## Experiment
- Name: {experiment_name}
- Proof-forward Tier-1 design_validated: {proof_validated}
- Stress inverse success: {step09.get('success')} (mode={step09.get('inverse_mode', 'stress')})
- Forward confirmation (design σv @ required knobs): {step09.get('forward_confirmation_passes')}
- Confirmation P_gross [MW]: {step09.get('forward_confirmation_mw')}
- Residual MW at stress solve: {step09.get('residual_mw')}

## Geometry / fuel (summary)
{parameters.get('geometry', {})}
injectants: {parameters.get('injectants', {})}

## Gap table (required / nominal)
{_gap_table_md(step09)}

Largest gaps: {top}

## Design basis excerpt (UNOBTANIUM.md)
{unob_md}

## Output format (Markdown)
Write a concise report with these sections:

1. **Executive summary** — Can this close with near-term R&D? Overall likelihood (low/medium/high) with 2–3 sentences.
2. **Knob-by-knob** — For each knob with gap factor > 1.05× or < 0.95×: state of the art, gap vs SOTA, difficulty.
3. **Recommended R&D program** — Ordered list of materials/plasma experiments (6–10 bullets).
4. **Risks & unknowns** — What the 0D model may over/under-state.
5. **Sources** — Cite URLs or papers you used from search.

Be honest about uncertainty. Do not claim the reactor is proven.
"""


def _template_fallback(
    *,
    experiment_name: str,
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
    reason: str,
) -> str:
    factors = gap_factors(step09)
    top = sorted(factors.items(), key=lambda kv: abs(kv[1] - 1.0), reverse=True)
    proof_ok = step08_proof.get("design_validated") if step08_proof else False

    lines = [
        "# Unobtanium technology gap (template — no Cursor agent)\n\n",
        f"*Agent skipped: {reason}*\n\n",
        f"**Experiment:** {experiment_name}  \n",
        f"**Proof-forward validated:** {proof_ok}  \n",
        f"**Inverse solve success:** {step09.get('success')}\n\n",
        "## Gap table\n\n",
        _gap_table_md(step09) + "\n\n",
        "## Interpretation\n\n",
    ]
    if proof_ok:
        lines.append(
            "Forward proof chain already met the power target at nominal unobtanium scales. "
            "Inverse factors near 1.0× mean the model does not require exotic margins beyond "
            "the design basis — any gap is numerical tolerance, not a materials crisis.\n\n"
        )
    else:
        lines.append(
            "Forward proof chain missed the target at scale=1.0. Factors above 1.0× are the "
            "**minimum performance multipliers** the optimizer needs on each knob. "
            "Prioritize R&D on the largest factors first.\n\n"
        )
        lines.append("### Largest gaps\n\n")
        for key, fac in top[:4]:
            label = _KNOB_LABELS.get(key, key)
            lines.append(f"- **{label}**: {fac:.3f}× vs nominal\n")

    lines.append(
        "\n### Knob definitions (U1–U4)\n\n"
        "**U1** field-emission margin — cathode surface field vs vacuum arc limit. "
        "**U2** max wall heat flux and CH₄ cooling effectiveness. "
        "**U3** HTS capability scale at 2 T bore. "
        "**U4** fusion reactivity scale and beam coupling scale for p-¹¹B burn.\n"
    )
    return "".join(lines)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emit(log: Callable[[str], None] | None, msg: str) -> None:
    """Write to run log and stderr so long agent runs show progress in the terminal."""
    if log is not None:
        log(msg)
    sys.stderr.write(msg)
    sys.stderr.flush()


def _heartbeat_interval_s() -> float:
    raw = os.environ.get("ORBITRON_GAP_AGENT_HEARTBEAT_S", "30")
    try:
        return max(5.0, float(raw))
    except ValueError:
        return 30.0


def _write_gap_timing(report_dir: Path, timing: dict[str, Any]) -> None:
    path = report_dir / "gap_agent_timing.json"
    path.write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")


def _run_cursor_agent(
    *,
    prompt: str,
    report_dir: Path,
    model: str,
    api_key: str,
    log: Callable[[str], None] | None,
) -> tuple[Any, dict[str, Any]]:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    opts = AgentOptions(
        api_key=api_key,
        model=model,
        local=LocalAgentOptions(cwd=str(_REPO_ROOT)),
    )
    heartbeat_s = _heartbeat_interval_s()
    started_utc = _utc_now()
    t0 = time.monotonic()
    done = threading.Event()
    timing: dict[str, Any] = {
        "started_utc": started_utc,
        "model": model,
        "heartbeat_interval_s": heartbeat_s,
        "verbose_stream": os.environ.get("ORBITRON_GAP_AGENT_VERBOSE", "").lower() in ("1", "true", "yes"),
    }

    _emit(
        log,
        f"\n  Cursor gap agent started {started_utc} (model={model})\n"
        f"  Web search + analysis typically takes 2–10 min; heartbeat every {heartbeat_s:.0f}s.\n"
        f"  Tail progress: tail -f {report_dir / 'run.log'}\n",
    )

    def _heartbeat() -> None:
        while not done.wait(heartbeat_s):
            elapsed = time.monotonic() - t0
            _emit(log, f"  [gap agent] still running… {elapsed:.0f}s elapsed\n")

    hb = threading.Thread(target=_heartbeat, name="gap-agent-heartbeat", daemon=True)
    hb.start()

    result: Any = None
    try:
        if timing["verbose_stream"]:
            _emit(log, "  [gap agent] verbose stream ON (ORBITRON_GAP_AGENT_VERBOSE=1)\n")
            agent = Agent.create(opts)
            run = agent.send(prompt)
            timing["run_id"] = getattr(run, "id", None)
            timing["agent_id"] = getattr(agent, "agent_id", None)
            for msg in run.messages():
                mtype = getattr(msg, "type", type(msg).__name__)
                if mtype == "status":
                    _emit(log, f"  [gap agent] status: {getattr(msg, 'status', msg)!s}\n")
                elif mtype == "assistant":
                    content = getattr(getattr(msg, "message", None), "content", None) or []
                    for block in content:
                        if getattr(block, "type", None) == "text":
                            t = getattr(block, "text", "") or ""
                            if t.strip():
                                preview = t.strip().replace("\n", " ")[:120]
                                _emit(log, f"  [gap agent] … {preview}\n")
            result = run.wait()
        else:
            result = Agent.prompt(prompt, opts)
    finally:
        done.set()

    elapsed_s = time.monotonic() - t0
    finished_utc = _utc_now()
    timing.update(
        {
            "finished_utc": finished_utc,
            "elapsed_s": round(elapsed_s, 2),
            "status": getattr(result, "status", None) if result is not None else "error",
            "duration_ms": getattr(result, "duration_ms", None) if result is not None else None,
            "result_chars": len(getattr(result, "result", "") or "") if result is not None else 0,
            "run_id": timing.get("run_id") or getattr(result, "id", None),
        }
    )
    _write_gap_timing(report_dir, timing)
    sdk_ms = timing.get("duration_ms")
    sdk_note = f", SDK duration_ms={sdk_ms}" if sdk_ms is not None else ""
    _emit(
        log,
        f"  Cursor gap agent finished {finished_utc} — elapsed {elapsed_s:.1f}s{sdk_note}, "
        f"status={timing.get('status')}, result_chars={timing.get('result_chars')}\n",
    )
    return result, timing


def write_template_gap_analysis(
    *,
    report_dir: Path,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
    reason: str,
) -> tuple[str, str, dict[str, Any]]:
    """Write UNOBTANIUM_GAP.md from the deterministic template (no Cursor call)."""
    out_path = report_dir / "UNOBTANIUM_GAP.md"
    body = _template_fallback(
        experiment_name=experiment_name,
        step09=step09,
        step08_proof=step08_proof,
        reason=reason,
    )
    out_path.write_text(body, encoding="utf-8")
    timing = {"mode": "template", "reason": reason, "finished_utc": _utc_now(), "elapsed_s": 0.0}
    _write_gap_timing(report_dir, timing)
    return str(out_path), "template", timing


def _reuse_existing_gap_analysis(report_dir: Path) -> tuple[str, str, dict[str, Any]] | None:
    """Return prior gap write if ``UNOBTANIUM_GAP.md`` should be kept (not a Cursor transcript cache)."""
    out_path = report_dir / "UNOBTANIUM_GAP.md"
    if not out_path.is_file() or out_path.stat().st_size < 32:
        return None
    timing_path = report_dir / "gap_agent_timing.json"
    timing: dict[str, Any] = {"mode": "reused", "finished_utc": _utc_now(), "elapsed_s": 0.0}
    if timing_path.is_file():
        try:
            prior = json.loads(timing_path.read_text(encoding="utf-8"))
            if isinstance(prior, dict):
                timing = {**prior, "mode": "reused", "reused_utc": _utc_now(), "elapsed_s": 0.0}
        except json.JSONDecodeError:
            pass
    _write_gap_timing(report_dir, timing)
    return str(out_path), "reused", timing


def run_gap_agent_analysis(
    *,
    report_dir: Path,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
    log: Callable[[str], None] | None = None,
    reuse_if_present: bool = False,
) -> tuple[str, str, dict[str, Any]]:
    """
    Write ``UNOBTANIUM_GAP.md``. Returns (path, mode, timing) where mode is ``cursor``, ``template``, or ``reused``.

    There is **no** cache of the Cursor agent conversation — only the markdown file on disk.
    Set ``reuse_if_present`` (or ``ORBITRON_REUSE_GAP_ANALYSIS=1``) to skip a new agent call when
    ``UNOBTANIUM_GAP.md`` already exists (e.g. re-run into the same ``--report-dir``).
    """
    if reuse_if_present or os.environ.get("ORBITRON_REUSE_GAP_ANALYSIS", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        reused = _reuse_existing_gap_analysis(report_dir)
        if reused is not None:
            _emit(log, "  Reusing existing UNOBTANIUM_GAP.md (no Cursor agent call)\n")
            return reused

    out_path = report_dir / "UNOBTANIUM_GAP.md"
    prompt = _build_agent_prompt(
        experiment_name=experiment_name,
        parameters=parameters,
        step09=step09,
        step08_proof=step08_proof,
    )
    (report_dir / "gap_agent_prompt.txt").write_text(prompt, encoding="utf-8")

    api_key = apply_cursor_api_key_to_env()
    if not api_key:
        tok = tokens_yaml_path()
        body = _template_fallback(
            experiment_name=experiment_name,
            step09=step09,
            step08_proof=step08_proof,
            reason=f"no Cursor API key (set CURSOR_API_KEY or {tok})",
        )
        out_path.write_text(body, encoding="utf-8")
        timing = {
            "mode": "template",
            "reason": f"no Cursor API key (set CURSOR_API_KEY or {tok})",
            "finished_utc": _utc_now(),
            "elapsed_s": 0.0,
        }
        _write_gap_timing(report_dir, timing)
        return str(out_path), "template", timing

    try:
        from cursor_sdk import Agent  # noqa: F401 — import check only
    except ImportError:
        reason = "cursor-sdk not installed (pip install cursor-sdk)"
        body = _template_fallback(
            experiment_name=experiment_name,
            step09=step09,
            step08_proof=step08_proof,
            reason=reason,
        )
        out_path.write_text(body, encoding="utf-8")
        timing = {"mode": "template", "reason": reason, "finished_utc": _utc_now(), "elapsed_s": 0.0}
        _write_gap_timing(report_dir, timing)
        return str(out_path), "template", timing

    model = os.environ.get("ORBITRON_GAP_AGENT_MODEL", "default")
    try:
        result, timing = _run_cursor_agent(
            prompt=prompt,
            report_dir=report_dir,
            model=model,
            api_key=api_key,
            log=log,
        )
        text = (result.result or "").strip()
        if not text:
            text = _template_fallback(
                experiment_name=experiment_name,
                step09=step09,
                step08_proof=step08_proof,
                reason=f"Cursor agent returned empty result (status={result.status})",
            )
            timing["mode"] = "template"
            timing["fallback_reason"] = "empty result"
        else:
            timing["mode"] = "cursor"
        header = f"<!-- Cursor agent model={model} status={result.status} elapsed_s={timing.get('elapsed_s')} -->\n\n"
        out_path.write_text(header + text, encoding="utf-8")
        _write_gap_timing(report_dir, timing)
        mode = "cursor" if timing.get("mode") == "cursor" else "template"
        return str(out_path), mode, timing
    except Exception as exc:
        reason = f"Cursor agent error: {exc}"
        body = _template_fallback(
            experiment_name=experiment_name,
            step09=step09,
            step08_proof=step08_proof,
            reason=reason,
        )
        out_path.write_text(body, encoding="utf-8")
        timing = {"mode": "template", "reason": reason, "finished_utc": _utc_now(), "elapsed_s": 0.0}
        _write_gap_timing(report_dir, timing)
        return str(out_path), "template", timing
