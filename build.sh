#!/bin/bash
set -ex

APP=scxctl_gui
ICON=scxctl_gui.png
PYFILE=scxctl_gui.py

# 1. Build initial pour détecter les libs
pyinstaller --noconsole --onefile --name "$APP" "$PYFILE"

# 2. Récupération automatique des libs natives
ADD_BIN_ARGS=""
for lib in $(ldd dist/$APP | awk '{print $3}' | grep -E '^/'); do
    ADD_BIN_ARGS+=" --add-binary \"$lib:.\""
done

# 3. Rebuild complet avec toutes les libs embarquées
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

# 5. appimagetool
if [ ! -f appimagetool ]; then
  wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
fi

# 6. Création finale
OUTPUT="${APP}-${GITHUB_REF_NAME}-x86_64.AppImage"
./appimagetool AppDir "$OUTPUT"

echo "✅ AppImage autonome générée : $OUTPUT"
