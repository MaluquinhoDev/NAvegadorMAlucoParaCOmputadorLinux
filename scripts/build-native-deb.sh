#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${APP_VERSION:-0.4.4}"
ARCH="${DEB_ARCH:-amd64}"
PKG="navegador-maluco-native"
BIN="${NATIVE_EXECUTABLE:-$ROOT/dist/native/navegador-maluco-native}"
STAGE="$ROOT/build/native-deb-root"
OUT="$ROOT/dist"

if [[ "$ARCH" != "amd64" ]]; then
  echo "A compilação nativa atual é direcionada a amd64; recebido: $ARCH" >&2
  exit 2
fi
if [[ ! -x "$BIN" ]]; then
  echo "Executável Nuitka não encontrado ou não executável: $BIN" >&2
  exit 2
fi

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/lib/$PKG/assets" \
  "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps"

install -m 755 "$BIN" "$STAGE/usr/lib/$PKG/navegador-maluco-native"
install -m 644 "$ROOT/app/assets/youtube-focus.js" "$STAGE/usr/lib/$PKG/assets/"
cat > "$STAGE/usr/bin/navegador-maluco-native" <<'LAUNCHER'
#!/bin/sh
exec /usr/lib/navegador-maluco-native/navegador-maluco-native "$@"
LAUNCHER
chmod 755 "$STAGE/usr/bin/navegador-maluco-native"

sed \
  -e 's/^Name=.*/Name=Navegador Maluco (Nativo)/' \
  -e 's/^Exec=.*/Exec=navegador-maluco-native %U/' \
  -e 's/^Icon=.*/Icon=navegador-maluco-native/' \
  "$ROOT/packaging/navegador-maluco.desktop" \
  > "$STAGE/usr/share/applications/navegador-maluco-native.desktop"
install -m 644 "$ROOT/packaging/navegador-maluco.svg" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps/navegador-maluco-native.svg"

cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $VERSION
Section: web
Priority: optional
Architecture: $ARCH
Maintainer: Navegador Maluco contributors
Depends: python3 (>= 3.12), python3 (<< 3.13), python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1 | gir1.2-webkit2-4.0
Description: Navegador Maluco desktop browser (Nuitka native build)
 Executable compiled with Nuitka. GTK, PyGObject and WebKitGTK remain
 system dependencies; this package is built for amd64 Linux systems.
CONTROL

dpkg-deb --root-owner-group --build "$STAGE" "$OUT/${PKG}_${VERSION}_${ARCH}.deb"
dpkg-deb --info "$OUT/${PKG}_${VERSION}_${ARCH}.deb"
echo "Pacote nativo criado: $OUT/${PKG}_${VERSION}_${ARCH}.deb"
