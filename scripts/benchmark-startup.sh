#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-/usr/bin/python3}"
NATIVE="${NATIVE_EXECUTABLE:-$ROOT/dist/native/navegador-maluco-native}"
RUNS="${BENCHMARK_RUNS:-5}"
OUT="${BENCHMARK_OUTPUT:-$ROOT/dist/startup-benchmark.csv}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [[ ! -x "$NATIVE" ]]; then
  echo "Executável nativo não encontrado: $NATIVE" >&2
  exit 2
fi
mkdir -p "$(dirname "$OUT")"
printf 'mode,run,elapsed_seconds,max_rss_kb\n' > "$OUT"

run_case() {
  local mode="$1"
  local run="$2"
  local metrics="$TMP/metrics"
  local -a command
  if [[ "$mode" == "python" ]]; then
    command=("$PYTHON" "$ROOT/app/navegador_maluco.py" --smoke-test)
  else
    command=("$NATIVE" --smoke-test)
  fi
  mkdir -p "$TMP/$mode-$run/config" "$TMP/$mode-$run/data"
  /usr/bin/time -f '%e,%M' -o "$metrics" \
    timeout 25s xvfb-run -a env \
      NM_SMOKE_TEST=1 \
      XDG_CONFIG_HOME="$TMP/$mode-$run/config" \
      XDG_DATA_HOME="$TMP/$mode-$run/data" \
      "${command[@]}" >/dev/null 2>&1
  local elapsed rss
  IFS=, read -r elapsed rss < "$metrics"
  printf '%s,%s,%s,%s\n' "$mode" "$run" "$elapsed" "$rss" >> "$OUT"
}

for mode in python native; do
  for ((run=1; run<=RUNS; run++)); do
    run_case "$mode" "$run"
  done
done

python3 - "$OUT" <<'PY'
import csv
import statistics
import sys

rows = list(csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8")))
for mode in ("python", "native"):
    group = [row for row in rows if row["mode"] == mode]
    elapsed = [float(row["elapsed_seconds"]) for row in group]
    memory = [int(row["max_rss_kb"]) for row in group]
    print(
        f"{mode}: median startup={statistics.median(elapsed):.2f}s; "
        f"median max RSS={statistics.median(memory):.0f} KiB; "
        f"runs={len(group)}"
    )
if len(rows) != 2 * int(__import__("os").environ.get("BENCHMARK_RUNS", "5")):
    raise SystemExit("Benchmark incompleto: número de execuções inesperado.")
PY
echo "CSV comparativo salvo em: $OUT"
