#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${APP_VERSION:-0.4.4}"
ARCH="${DEB_ARCH:-all}"
PKG="navegador-maluco"
STAGE="$ROOT/build/deb-root"
OUT="$ROOT/dist"

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/lib/$PKG/app/assets" "$STAGE/usr/bin" "$STAGE/usr/share/applications" "$STAGE/usr/share/icons/hicolor/scalable/apps" "$OUT"

cp "$ROOT/app/core.py" "$ROOT/app/navegador_maluco.py" "$STAGE/usr/lib/$PKG/app/"
cp "$ROOT/app/assets/youtube-focus.js" "$STAGE/usr/lib/$PKG/app/assets/"
cat > "$STAGE/usr/bin/navegador-maluco" <<'LAUNCHER'
#!/bin/sh
exec /usr/bin/python3 /usr/lib/navegador-maluco/app/navegador_maluco.py "$@"
LAUNCHER
chmod 755 "$STAGE/usr/bin/navegador-maluco"
cp "$ROOT/packaging/navegador-maluco.desktop" "$STAGE/usr/share/applications/"
cp "$ROOT/packaging/navegador-maluco.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/"

cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $VERSION
Section: web
Priority: optional
Architecture: $ARCH
Maintainer: Navegador Maluco contributors
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1 | gir1.2-webkit2-4.0
Description: Navegador Maluco desktop browser
 Navegador web desktop com abas, favoritos, historico, downloads,
 controle de velocidade e ferramentas de foco para YouTube.
CONTROL

dpkg-deb --root-owner-group --build "$STAGE" "$OUT/${PKG}_${VERSION}_${ARCH}.deb"
echo "Pacote criado: $OUT/${PKG}_${VERSION}_${ARCH}.deb"
