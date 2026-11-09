#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
OUT="$ROOT/dist/native"

command -v gcc >/dev/null 2>&1 || {
    echo "gcc não encontrado; instale build-essential." >&2
    exit 1
}
"$PYTHON" -m nuitka --version
mkdir -p "$OUT"

"$PYTHON" -m nuitka \
    --mode=accelerated \
    --follow-imports \
    --jobs=2 \
    --output-dir="$OUT" \
    --output-filename=navegador-maluco-native \
    --include-data-dir="$ROOT/app/assets=assets" \
    "$ROOT/app/navegador_maluco.py"

test -x "$OUT/navegador-maluco-native"
echo "Executável experimental criado em: $OUT/navegador-maluco-native"
echo "Este modo depende da versão de Python e das bibliotecas GTK/WebKitGTK do sistema."
