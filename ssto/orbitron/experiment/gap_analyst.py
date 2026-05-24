"""Optional Cursor-agent (or template) R&D gap narrative for unobtanium knobs."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

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
        "\n## Enable AI analysis\n\n"
        "Install `cursor-sdk`, then either export `CURSOR_API_KEY` or place it in "
        f"`{tokens_yaml_path()}` (outside repo; override path with `ORBITRON_TOKENS_YAML`).\n\n"
        "```bash\npip install cursor-sdk\n"
        "./scripts/run_orbitron_experiment.sh experiments/your.yaml\n```\n\n"
        "See `ssto/orbitron/UNOBTANIUM.md` for knob definitions.\n"
    )
    return "".join(lines)


def write_template_gap_analysis(
    *,
    report_dir: Path,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
    reason: str,
) -> tuple[str, str]:
    """Write UNOBTANIUM_GAP.md from the deterministic template (no Cursor call)."""
    out_path = report_dir / "UNOBTANIUM_GAP.md"
    body = _template_fallback(
        experiment_name=experiment_name,
        step09=step09,
        step08_proof=step08_proof,
        reason=reason,
    )
    out_path.write_text(body, encoding="utf-8")
    return str(out_path), "template"


def run_gap_agent_analysis(
    *,
    report_dir: Path,
    experiment_name: str,
    parameters: dict[str, Any],
    step09: dict[str, Any],
    step08_proof: dict[str, Any] | None,
) -> tuple[str, str]:
    """
    Write ``UNOBTANIUM_GAP.md``. Returns (path, mode) where mode is ``cursor`` or ``template``.
    """
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
        return str(out_path), "template"

    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
    except ImportError:
        body = _template_fallback(
            experiment_name=experiment_name,
            step09=step09,
            step08_proof=step08_proof,
            reason="cursor-sdk not installed (pip install cursor-sdk)",
        )
        out_path.write_text(body, encoding="utf-8")
        return str(out_path), "template"

    # Local SDK bridge accepts listed models but often errors on named IDs; "default" works.
    model = os.environ.get("ORBITRON_GAP_AGENT_MODEL", "default")
    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(cwd=str(_REPO_ROOT)),
            ),
        )
        text = (result.result or "").strip()
        if not text:
            text = _template_fallback(
                experiment_name=experiment_name,
                step09=step09,
                step08_proof=step08_proof,
                reason=f"Cursor agent returned empty result (status={result.status})",
            )
        header = f"<!-- Cursor agent model={model} status={result.status} -->\n\n"
        out_path.write_text(header + text, encoding="utf-8")
        return str(out_path), "cursor"
    except Exception as exc:
        body = _template_fallback(
            experiment_name=experiment_name,
            step09=step09,
            step08_proof=step08_proof,
            reason=f"Cursor agent error: {exc}",
        )
        out_path.write_text(body, encoding="utf-8")
        return str(out_path), "template"
