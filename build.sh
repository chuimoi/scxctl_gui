#!/bin/bash
set -ex

APP=scxctl_gui
ICON=scxctl_gui.png
PYFILE=scxctl_gui.py

# Vérification des dépendances minimales
command -v python3 >/dev/null || { echo "❌ Python3 est requis"; exit 1; }
command -v pyinstaller >/dev/null || { echo "❌ PyInstaller est requis (pip install pyinstaller)"; exit 1; }
command -v wget >/dev/null || { echo "❌ wget est requis"; exit 1; }

# 1. Build initial
pyinstaller --noconsole --onefile --name "$APP" "$PYFILE"

# 2. Inclusion auto des bibliothèques natives
ADD_BIN_ARGS=""
for lib in $(ldd dist/$APP | awk '{print $3}' | grep -E '^/'); do
    ADD_BIN_ARGS+=" --add-binary \"$lib:.\""
done

# Forcer l’ajout de libEGL si elle n’est pas détectée
if [ -f /usr/lib/x86_64-linux-gnu/libEGL.so.1 ]; then
    ADD_BIN_ARGS+=" --add-binary /usr/lib/x86_64-linux-gnu/libEGL.so.1:."
fi


# 3. Rebuild avec libs incluses
rm -rf build dist
eval pyinstaller --noconsole --onefile --name "$APP" $ADD_BIN_ARGS "$PYFILE"

# 4. Construction AppDir
mkdir -p AppDir/usr/bin
cp "dist/$APP" AppDir/usr/bin/

cat > AppDir/$APP.desktop <<EOF
[Desktop Entry]
Name=SCXCTL GUI
Exec=$APP
Icon=$APP
Type=Application
Categories=Utility;
EOF

if [ -f "$ICON" ]; then
  cp "$ICON" AppDir/$APP.png
fi

# 5. Récupération appimagetool si absent
if [ ! -f appimagetool ]; then
  wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
fi

# 6. Création AppImage finale dans un dossier séparé
mkdir -p build_out
VERSION="${GITHUB_REF_NAME:-local}"
OUTPUT="build_out/${APP}-${VERSION}-x86_64.AppImage"
./appimagetool AppDir "$OUTPUT"
echo "✅ AppImage générée : $OUTPUT"
