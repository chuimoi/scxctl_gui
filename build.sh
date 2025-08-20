#!/bin/bash
set -ex

APP=scxctl_gui
ICON=scxctl_gui.png
PYFILE=scxctl_gui.py

# 1. Compile avec nom forcé
pyinstaller --noconsole --onefile --name "$APP" "$PYFILE"

# 2. Crée AppDir et copie binaire
mkdir -p AppDir/usr/bin
cp "dist/$APP" AppDir/usr/bin/

# 3. Fichier .desktop
cat > AppDir/$APP.desktop <<EOF
[Desktop Entry]
Name=SCXCTL GUI
Exec=$APP
Icon=$APP
Type=Application
Categories=Utility;
EOF

# 4. Ajoute icône si présente
if [ -f "$ICON" ]; then
  cp "$ICON" AppDir/$APP.png
fi

# 5. Télécharge appimagetool si absent
if [ ! -f appimagetool ]; then
  wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
fi

# 6. Crée AppImage avec nom + version
OUTPUT="${APP}-${GITHUB_REF_NAME}-x86_64.AppImage"
./appimagetool AppDir "$OUTPUT"

# 7. Déplace uniquement si le fichier n'est pas déjà à la racine
if [ "$(dirname "$OUTPUT")" != "." ]; then
  mv "$OUTPUT" .
fi

echo "✅ AppImage générée et prête."
