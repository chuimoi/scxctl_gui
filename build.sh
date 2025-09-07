#!/bin/bash
set -e

# -------------------------
# Configuration
# -------------------------
APP=scxctl_gui
PYFILE=scxctl_gui.py
ICON=scxctl_gui.png

# Nettoyage éventuel
rm -rf build dist AppDir *.AppImage

# -------------------------
# 1️⃣ Compile avec PyInstaller
# -------------------------
echo "🔹 Compilation avec PyInstaller..."
pyinstaller --noconsole --onefile "$PYFILE"

# -------------------------
# 2️⃣ Crée AppDir
# -------------------------
echo "🔹 Création de l'AppDir..."
mkdir -p AppDir/usr/bin
cp "dist/$APP" AppDir/usr/bin/
chmod +x AppDir/usr/bin/$APP

# -------------------------
# 3️⃣ Fichier .desktop
# -------------------------
echo "🔹 Création du fichier .desktop..."
cat > AppDir/$APP.desktop <<EOF
[Desktop Entry]
Name=SCXCTL GUI
Exec=$APP
Icon=$APP
Type=Application
Categories=Utility;
EOF

# -------------------------
# 4️⃣ Ajoute l'icône si existante
# -------------------------
if [ -f "$ICON" ]; then
    cp "$ICON" AppDir/$APP.png
fi

# -------------------------
# 5️⃣ Crée AppRun
# -------------------------
echo "🔹 Création de AppRun..."
cat > AppDir/AppRun <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/scxctl_gui" "$@"
EOF
chmod +x AppDir/AppRun

# -------------------------
# 6️⃣ Télécharge appimagetool si nécessaire
# -------------------------
if [ ! -f appimagetool ]; then
    echo "🔹 Téléchargement de appimagetool..."
    wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
    chmod +x appimagetool
fi

# -------------------------
# 7️⃣ Génère l'AppImage
# -------------------------
echo "🔹 Création de l'AppImage..."
./appimagetool AppDir

echo "✅ AppImage générée avec succès !"
