#!/usr/bin/env bash
set -u
section() { printf '\n===== %s =====\n' "$1"; }
section "Sistema"
uname -sr
. /etc/os-release 2>/dev/null || true
printf '%s %s\n' "${NAME:-Linux}" "${VERSION_ID:-}"
printf 'Sessão gráfica: %s\n' "${XDG_SESSION_TYPE:-desconhecida}"
section "CPU e memória"
grep -m1 'model name' /proc/cpuinfo 2>/dev/null || true
free -h 2>/dev/null || true
printf '\nSwap:\n'
swapon --show 2>/dev/null || true
printf '\nMemória disponível:\n'
grep -E '^(MemAvailable|SwapFree):' /proc/meminfo 2>/dev/null || true
printf '\nPressão de memória (PSI):\n'
cat /proc/pressure/memory 2>/dev/null || echo "PSI indisponível"
printf '\nPressão de CPU (PSI):\n'
cat /proc/pressure/cpu 2>/dev/null || echo "PSI indisponível"
printf '\nPressão de I/O (PSI):\n'
cat /proc/pressure/io 2>/dev/null || echo "PSI indisponível"
printf '\nZRAM:\n'
if command -v zramctl >/dev/null 2>&1; then zramctl; else echo "zramctl não instalado"; fi
section "WebKitGTK"
if command -v pkg-config >/dev/null 2>&1; then
  pkg-config --modversion webkit2gtk-4.1 2>/dev/null || pkg-config --modversion webkit2gtk-4.0 2>/dev/null || echo "WebKitGTK não localizado pelo pkg-config"
fi
section "GPU e vídeo"
ls -l /dev/dri 2>/dev/null || echo "Dispositivos DRM não encontrados"
if command -v vainfo >/dev/null 2>&1; then vainfo 2>&1 | head -n 35; else echo "vainfo não instalado"; fi
if command -v lspci >/dev/null 2>&1; then lspci -nnk | grep -A3 -Ei 'VGA|Display|3D' || true; fi
section "Processos por memória residente"
ps -eo pid,comm,%cpu,%mem,rss --sort=-rss 2>/dev/null | head -n 15 || true
section "Memória proporcional (PSS) dos processos do navegador"
if [ -r /proc/self/smaps_rollup ]; then
  ps -eo pid=,comm= | while read -r pid comm; do
    case "$comm" in
      navegador-maluco|python3|WebKitWebProces*|WebKitNetworkPr*)
        rollup="/proc/$pid/smaps_rollup"
        if [ -r "$rollup" ]; then
          pss=$(awk '/^Pss:/ {print $2}' "$rollup" 2>/dev/null)
          rss=$(awk '/^Rss:/ {print $2}' "$rollup" 2>/dev/null)
          printf 'PID=%s processo=%s RSS=%s KiB PSS=%s KiB\n' "$pid" "$comm" "${rss:-?}" "${pss:-?}"
        fi
        ;;
    esac
  done
else
  echo "smaps_rollup indisponível no kernel"
fi
printf '\nRSS inclui páginas compartilhadas; PSS as distribui proporcionalmente. Nenhum histórico, cookie, senha ou conteúdo de página é coletado.\n'
