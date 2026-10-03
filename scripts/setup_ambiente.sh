#!/usr/bin/env bash
# Prepara o ambiente (nuvem ou máquina nova) para monitor TikTok + card de imagem.
# Uso: bash scripts/setup_ambiente.sh
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -q -r requirements.txt
python3 -m playwright install --with-deps chromium 2>/dev/null || python3 -m playwright install chromium

command -v yt-dlp >/dev/null || export PATH="$(python3 -m site --user-base)/bin:$PATH"
yt-dlp --version >/dev/null && echo "yt-dlp ok"
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
print("chromium ok")
PY
echo "Lembrete: conector Chatiops (MCP) precisa estar conectado na conta Claude."
