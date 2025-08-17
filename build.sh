#!/bin/bash
set -e

# Préparation
APP=scxctl_gui
ICON=scxctl_gui.png  # Mets ici le nom de ton icône si tu en as une
PYFILE=scxctl_gui.py

# 1. Compile avec PyInstaller
pyinstaller --noconsole --onefile $PYFILE

# 2. Crée AppDir
mkdir -p AppDir/usr/bin
cp dist/$APP AppDir/usr/bin/

# 3. Ajoute le .desktop
cat > AppDir/$APP.desktop <<EOF
[Desktop Entry]
Name=scxctl gui
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
  wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
  chmod +x appimagetool
fi

# 6. Crée l'AppImage
./appimagetool AppDir

echo "✅ AppImage générée avec succès."
