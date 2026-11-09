#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Este instalador destina-se ao Linux." >&2
  exit 1
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
sudo apt-get update
sudo apt-get install -y python3 python3-gi gir1.2-gtk-3.0
if apt-cache show gir1.2-webkit2-4.1 >/dev/null 2>&1; then
  sudo apt-get install -y gir1.2-webkit2-4.1
else
  sudo apt-get install -y gir1.2-webkit2-4.0
fi
PACKAGE="$(find "$ROOT/dist" -maxdepth 1 -type f -name 'navegador-maluco_*.deb' -print -quit)"
if [[ -n "$PACKAGE" ]]; then
  sudo apt-get install -y "$PACKAGE"
else
  echo "Pacote Debian Python não encontrado em dist/." >&2
  exit 2
fi
