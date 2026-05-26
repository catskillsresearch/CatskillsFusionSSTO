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
from ssto.orbitron.experiment.narrative import strip_software_implementation_references

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
        flag = " ← largest material gap" if f == max_f and 0.95 < f < 1.05 else ""
        if f >= 10:
            flag = " ← η_react dominates" if key == "fusion_reactivity_scale" else flag
        lines.append(f"| {label} | {n:.4g} | {r:.4g} | {f:.3f}×{flag} |")
    return "\n".join(lines)


def _stress_summary_md(step09: dict[str, Any]) -> str:
    stress = step09.get("stress_inverse") or {}
    branch = stress.get("sigma_v_design_over_literature")
    eta = stress.get("fusion_reactivity_scale_required")
    lines = ["## Stress inverse (constrained, literature ⟨σv⟩)\n"]
    if step09.get("success"):
        lines.append(
            f"- **Feasible minimum:** yes — U1–U4 pass at **{step09.get('target_mw', 3.5)} MW**.\n"
        )
        if eta is not None:
            lines.append(f"- **Minimum η_react scale:** {float(eta):.1f}× (on top of literature σv branch).\n")
        if branch is not None:
            lines.append(f"- **⟨σv⟩ design/literature at solve:** {float(branch):.1f}×\n")
    else:
        lines.append(
            "- **Feasible minimum:** **no** — no point satisfies literature ⟨σv⟩, "
            f"**{step09.get('target_mw', 3.5)} MW**, and U1–U4 within bounds.\n"
        )
        if branch is not None:
            lines.append(
                f"- **⟨σv⟩ branch (design/literature):** ~{float(branch):.0f}× — "
                "this is the dominant gap, not 5% material knobs.\n"
            )
        if eta is not None:
            lines.append(
                f"- Optimizer η_react at best effort: {float(eta):.1f}× "
                "(not a validated operating point).\n"
            )
    conf = step09.get("forward_confirmation_passes")
    conf_mw = step09.get("forward_confirmation_mw")
    lines.append(
        f"- **Margin back-solve (design σv):** confirmation "
        f"{'PASS' if conf else 'FAIL'} @ {conf_mw} MW — checks (a) pretends internal consistency.\n"
    )
    return "".join(lines)


def _build_agent_prompt(
    *,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
) -> str:
    unob_md = ""
    if _UNOBTANIUM_MD.is_file():
        raw = _UNOBTANIUM_MD.read_text(encoding="utf-8")
        start = raw.find("## U1")
        if start < 0:
            start = 0
        unob_md = strip_software_implementation_references(raw[start : start + 8000])

    proof_validated = step08_proof.get("design_validated") if step08_proof else None
    stress = step09.get("stress_inverse") or {}

    return f"""You are a fusion materials and plasma-physics analyst writing for a benchmark report audience
(nuclear/plasma specialists who read many facility and design studies).

## Task
Interpret the **three-scenario** Orbitron p-¹¹B in-silico benchmark:
- **(a) Pretend:** design-calibrated ⟨σv⟩, 600 kV design point (level-1 plant closure).
- **(b) Today:** literature ⟨σv⟩, Avalanche-class 300 kV, experimental wall/HTS limits, same fueling as (a).
- **(c) Minimum:** **constrained** stress inverse on literature ⟨σv⟩ — minimize η_react subject to U1–U4 and power.
  If stress inverse success is **False**, (c) is **infeasible** — state that clearly.

Use web search for 2024–2026 literature where helpful.

**Do not claim the reactor is proven.** WarpX validates electron loading (validation level 2), not fusion gain.

## Audience
- Write like a **benchmark memo**, not marketing copy.
- No repository paths, module names, or software install instructions.
- Lead with the **~10³× ⟨σv⟩ branch** when stress inverse is infeasible or η_react ≫ 1.
- Do **not** describe forward confirmation at design σv as a physical demonstration of fusion power.

## Experiment
- Name: {experiment_name}
- (a) Level-1 design validated: {proof_validated}
- Constrained stress inverse success: {step09.get('success')}
- σv design/literature branch: {stress.get('sigma_v_design_over_literature', '—')}
- η_react required (if reported): {stress.get('fusion_reactivity_scale_required', '—')}
- Residual MW: {step09.get('residual_mw')}
- Margin confirmation @ design σv: {step09.get('forward_confirmation_passes')} ({step09.get('forward_confirmation_mw')} MW)

## Geometry / fuel
{parameters.get('geometry', {})}
injectants: {parameters.get('injectants', {})}

{_stress_summary_md(step09)}

## Gap table (only if stress feasible; else explain infeasibility)
{_gap_table_md(step09) if step09.get('success') else '*Table omitted — no feasible constrained minimum.*'}

## Design basis (U1–U4)
{unob_md}

## Output format (Markdown)
1. **Executive summary** — Is (c) feasible on literature physics? Overall R&D likelihood (low/medium/high).
2. **Scenario interpretation** — One short subsection each for (a), (b), (c) in plain physics language.
3. **Dominant gap** — ⟨σv⟩ branch vs materials; quantify order of magnitude.
4. **Knob-by-knob** — Only for material knobs if a **feasible** (c) exists; otherwise one paragraph on why η_react dominates.
5. **Recommended R&D program** — 6–10 ordered experiments (measurements that would collapse uncertainty).
6. **Risks & unknowns** — What the 0D plant may over/under-state (beam-target, Ti/Te, PIC tier).
7. **Conclusions** — Short synthesis for a skeptical reader.
8. **References** — Numbered list, journals/preprints/URLs only (no repo paths).

Be direct. If literature path is infeasible, that **is** the main scientific result.
"""


def _template_fallback(
    *,
    experiment_name: str,
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
    reason: str,
) -> str:
    proof_ok = step08_proof.get("design_validated") if step08_proof else False
    stress = step09.get("stress_inverse") or {}
    branch = stress.get("sigma_v_design_over_literature")

    lines = [
        "# Technology gap — constrained stress inverse (template)\n\n",
        f"*Narrative agent skipped: {reason}*\n\n",
        f"**Experiment:** {experiment_name}  \n",
        f"**(a) level-1 design validated:** {proof_ok}  \n",
        f"**(c) constrained stress inverse feasible:** {step09.get('success')}  \n\n",
        _stress_summary_md(step09),
        "\n",
    ]
    if step09.get("success"):
        lines.append("## Material knob table\n\n" + _gap_table_md(step09) + "\n\n")
    else:
        lines.append(
            "## Interpretation\n\n"
            "Under literature-class p-¹¹B reactivity, the plant model finds **no** operating point that "
            "simultaneously meets the gross-power target and the U1–U4 inequality gates within the "
            "allowed knob bounds. The benchmark should be read as mapping the **reactivity mountain** "
            f"(design/literature ⟨σv⟩ branch ≈ **{float(branch or 1000):.0f}×** when quoted), not as a near-term "
            "materials-only engineering fix.\n\n"
        )
    lines.append(
        "### U1–U4 (definitions)\n\n"
        "**U1** cathode surface field vs vacuum arc limit. **U2** wall heat flux and CH₄ cooling. "
        "**U3** HTS bore field vs 2 T target. **U4** beam, density proxy, and fusion-thermal power.\n"
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
    out_path.write_text(_gap_output_text(body), encoding="utf-8")
    timing = {"mode": "template", "reason": reason, "finished_utc": _utc_now(), "elapsed_s": 0.0}
    _write_gap_timing(report_dir, timing)
    return str(out_path), "template", timing


def _gap_output_text(body: str, *, header: str = "") -> str:
    """Normalize agent/template gap markdown before writing ``UNOBTANIUM_GAP.md``."""
    from ssto.orbitron.experiment.report_narrative import normalize_gap_markdown_for_report

    return header + normalize_gap_markdown_for_report(body.strip()) + "\n"


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
        out_path.write_text(_gap_output_text(body), encoding="utf-8")
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
        out_path.write_text(_gap_output_text(body), encoding="utf-8")
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
        out_path.write_text(_gap_output_text(text, header=header), encoding="utf-8")
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
        out_path.write_text(_gap_output_text(body), encoding="utf-8")
        timing = {"mode": "template", "reason": reason, "finished_utc": _utc_now(), "elapsed_s": 0.0}
        _write_gap_timing(report_dir, timing)
        return str(out_path), "template", timing
