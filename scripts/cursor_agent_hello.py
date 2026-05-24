#!/usr/bin/env python3
"""
Minimal Cursor SDK smoke test + verbose debug when a run returns status=error.

Loads CURSOR_API_KEY from ~/Desktop/tokens_ssto.yaml (see cursor_credentials.py).

Usage:
  ./scripts/run_orbitron_experiment.sh  # not needed
  poetry run python scripts/cursor_agent_hello.py
  poetry run python scripts/cursor_agent_hello.py --verbose
  poetry run python scripts/cursor_agent_hello.py --model composer-2.5-fast
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import asdict, is_dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from ssto.orbitron.experiment.cursor_credentials import (  # noqa: E402
    apply_cursor_api_key_to_env,
    tokens_yaml_path,
)


def _to_jsonable(obj: object) -> object:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in asdict(obj).items() if v is not None}
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    return repr(obj)


def _mask_key(key: str) -> str:
    if len(key) <= 12:
        return "(set, len=%d)" % len(key)
    return f"{key[:8]}…{key[-4:]} (len={len(key)})"


def _print_models(api_key: str) -> None:
    from cursor_sdk import Cursor

    print("\n=== Cursor.models.list() ===")
    try:
        models = Cursor.models.list(api_key=api_key)
        items = getattr(models, "items", models)
        if items is None:
            print("(empty)")
            return
        for m in list(items)[:12]:
            mid = getattr(m, "id", None) or (m.get("id") if isinstance(m, dict) else m)
            print(f"  - {mid}")
        n = len(list(items)) if hasattr(items, "__iter__") else "?"
        if n != "?":
            print(f"  ({n} models total; showing up to 12)")
    except Exception as exc:
        print(f"  FAILED: {type(exc).__name__}: {exc}")


def _dump_run_result(result: object, *, label: str) -> None:
    print(f"\n=== {label} ===")
    for attr in ("id", "agent_id", "status", "duration_ms", "created_at", "model", "git"):
        if hasattr(result, attr):
            print(f"  {attr}: {_to_jsonable(getattr(result, attr))}")
    text = getattr(result, "result", "") or ""
    print(f"  result_len: {len(text)}")
    if text.strip():
        print("  result_preview:")
        print(text[:2000] + ("…" if len(text) > 2000 else ""))
    else:
        print("  result_preview: (empty)")


def _stream_run(agent: object, prompt: str) -> object:
    from cursor_sdk import Agent

    print("\n=== Agent.create + send (streaming) ===")
    run = agent.send(prompt)
    print(f"  run.id: {getattr(run, 'id', '?')}")
    print(f"  agent_id: {getattr(agent, 'agent_id', '?')}")

    for i, msg in enumerate(run.messages()):
        mtype = getattr(msg, "type", type(msg).__name__)
        print(f"\n--- message[{i}] type={mtype} ---")
        if mtype == "assistant":
            content = getattr(getattr(msg, "message", None), "content", None) or []
            for block in content:
                btype = getattr(block, "type", "?")
                if btype == "text":
                    t = getattr(block, "text", "") or ""
                    print(t[:1500] + ("…" if len(t) > 1500 else ""))
                else:
                    print(f"  block type={btype}: {_to_jsonable(block)}")
        elif mtype == "status":
            print(_to_jsonable(msg))
        else:
            print(_to_jsonable(msg)[:4000])

    if run.supports("conversation"):
        print("\n=== run.conversation() ===")
        try:
            conv = run.conversation()
            print(json.dumps(_to_jsonable(conv), indent=2)[:8000])
        except Exception as exc:
            print(f"  conversation() failed: {exc}")

    return run.wait()


def _oneshot(prompt: str, *, api_key: str, model: str, cwd: str) -> int:
    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions

    opts = AgentOptions(
        api_key=api_key,
        model=model,
        local=LocalAgentOptions(cwd=cwd),
    )

    print("\n=== Agent.prompt (one-shot) ===")
    print(f"  cwd: {cwd}")
    print(f"  model: {model}")
    print(f"  prompt: {prompt!r}")

    try:
        result = Agent.prompt(prompt, opts)
    except CursorAgentError as exc:
        print(f"\nCursorAgentError (run never started): {exc}")
        print(f"  retryable: {getattr(exc, 'is_retryable', None)}")
        return 1
    except Exception:
        traceback.print_exc()
        return 1

    _dump_run_result(result, label="RunResult")
    if str(getattr(result, "status", "")) == "error":
        return 2
    if not (getattr(result, "result", "") or "").strip():
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Cursor SDK hello / debug")
    parser.add_argument(
        "--prompt",
        default="Reply with exactly: hello from cursor-sdk",
        help="One-shot prompt",
    )
    parser.add_argument(
        "--model",
        default="default",
        help="Model id (local bridge: use 'default'; named models like composer-2.5 often error)",
    )
    parser.add_argument(
        "--try-models",
        action="store_true",
        help="Probe common model ids and print status/result_len (diagnostic)",
    )
    parser.add_argument("--cwd", default=str(_REPO), help="Local agent cwd")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Use Agent.create+send and print all stream messages",
    )
    parser.add_argument("--list-models", action="store_true", help="Only list models")
    args = parser.parse_args()

    api_key = apply_cursor_api_key_to_env()
    tok_path = tokens_yaml_path()
    print("=== credentials ===")
    print(f"  tokens file: {tok_path} ({'found' if tok_path.is_file() else 'missing'})")
    if not api_key:
        print("  ERROR: no API key (set CURSOR_API_KEY or fix tokens YAML)", file=sys.stderr)
        return 1
    print(f"  api_key: {_mask_key(api_key)}")

    if args.list_models:
        _print_models(api_key)
        return 0

    if args.try_models:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

        probe = ["default", "composer-2.5", "composer-2", "gpt-5.5", "claude-sonnet-4-6"]
        print("\n=== model probe (local agent) ===")
        for mid in probe:
            try:
                r = Agent.prompt(
                    "Reply with exactly: ok",
                    AgentOptions(
                        api_key=api_key,
                        model=mid,
                        local=LocalAgentOptions(cwd=args.cwd),
                    ),
                )
                print(f"  {mid:20} status={r.status} result_len={len(r.result or '')}")
            except Exception as exc:
                print(f"  {mid:20} EXCEPTION {type(exc).__name__}: {exc}")
        return 0

    _print_models(api_key)

    if args.verbose:
        from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions

        opts = AgentOptions(
            api_key=api_key,
            model=args.model,
            local=LocalAgentOptions(cwd=args.cwd),
        )
        try:
            with Agent.create(opts) as agent:
                result = _stream_run(agent, args.prompt)
        except CursorAgentError as exc:
            print(f"\nCursorAgentError: {exc}")
            return 1
        except Exception:
            traceback.print_exc()
            return 1
        _dump_run_result(result, label="RunResult after wait()")
        if str(getattr(result, "status", "")) == "error":
            return 2
        if not (getattr(result, "result", "") or "").strip():
            return 2
        return 0

    return _oneshot(args.prompt, api_key=api_key, model=args.model, cwd=args.cwd)


if __name__ == "__main__":
    raise SystemExit(main())
