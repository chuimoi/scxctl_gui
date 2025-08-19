#!/bin/bash
set -ex  # 'e' = stop si erreur / 'x' = affiche chaque commande

# Variables
APP=scxctl_gui
ICON=scxctl_gui.png
PYFILE=scxctl_gui.py

# 1. Compile avec nom forcé
pyinstaller --noconsole --onefile --name "$APP" "$PYFILE"

# 2. Crée AppDir et ajoute binaire
mkdir -p AppDir/usr/bin
cp "dist/$APP" AppDir/usr/bin/

# 3. Ajoute le .desktop
cat > AppDir/$APP.desktop <<EOF
[Desktop Entry]
Name=SCXCTL GUI
Exec=$APP
Icon=$APP
Type=Application
Categories=Utility;
EOF

# 4. Ajoute icône si elle existe
if [ -f "$ICON" ]; then
  cp "$ICON" AppDir/$APP.png
fi

# 5. Télécharge appimagetool si absent
if [ ! -f appimagetool ]; then
  wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
fi

# 6. Crée l'AppImage avec nom versionné
./appimagetool AppDir "${APP}-${GITHUB_REF_NAME}-x86_64.AppImage"

# 7. Déplace à la racine pour l’upload
mv *.AppImage .
echo "✅ AppImage générée et prête."
