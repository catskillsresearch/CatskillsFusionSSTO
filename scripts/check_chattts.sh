#!/usr/bin/env bash
# Quick ChatTTS sanity check (same Poetry env as pb11_reactor_sim/run.sh).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
exec poetry run python - <<'PY'
import sys

print("python:", sys.executable)
import torch

print("torch:", torch.__version__)
import torchaudio

print("torchaudio:", torchaudio.__version__)
if not torch.__version__.split("+")[0].startswith(torchaudio.__version__.split("+")[0][:4]):
    print("WARN: torch and torchaudio major/minor should match (e.g. both 2.10.x)")

import ChatTTS

chat = ChatTTS.Chat()
if not chat.load(source="huggingface"):
    raise SystemExit("ChatTTS model load failed")
wavs = chat.infer(["Reactor shot sequence check."])
print("ChatTTS infer OK, samples:", len(wavs[0]))
PY
