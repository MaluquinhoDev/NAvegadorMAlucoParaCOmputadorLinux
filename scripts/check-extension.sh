#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT="$ROOT/extension/youtube-focus"
DIST="$ROOT/dist"

command -v node >/dev/null 2>&1 || { echo "Erro: Node.js não encontrado." >&2; exit 1; }
command -v zip >/dev/null 2>&1 || { echo "Erro: zip não encontrado." >&2; exit 1; }

echo "[1/4] Validando manifesto JSON"
node -e 'const fs=require("fs"); const p=process.argv[1]; const m=JSON.parse(fs.readFileSync(p,"utf8")); if(m.manifest_version!==2) throw Error("manifest_version deve ser 2 para o alvo Firefox atual"); if(!m.content_scripts?.length) throw Error("Nenhum content_script declarado"); for(const s of m.content_scripts) for(const f of s.js||[]) if(!fs.existsSync(require("path").join(require("path").dirname(p),f))) throw Error("Arquivo ausente: "+f); console.log(m.name+" "+m.version)' "$EXT/manifest.json"

echo "[2/4] Verificando sintaxe JavaScript"
node --check "$EXT/content.js"

echo "[3/4] Gerando pacote"
mkdir -p "$DIST"
rm -f "$DIST/youtube-focus-firefox.zip"
(cd "$EXT" && zip -q -r "$DIST/youtube-focus-firefox.zip" manifest.json content.js)

echo "[4/4] Resultado"
ls -lh "$DIST/youtube-focus-firefox.zip"
