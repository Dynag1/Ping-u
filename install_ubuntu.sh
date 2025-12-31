#!/bin/bash
#
# Script d'installation simple pour Ping ü sur Ubuntu/Debian
# Ce script installe Ping ü dans /opt/pingu avec une icône dans le menu
#

set -e

# Vérifier si le script est exécuté avec sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Ce script doit être exécuté avec sudo."
    echo "Usage: sudo ./install_ubuntu.sh"
    exit 1
fi

echo "========================================="
echo "  Installation de Ping ü pour Ubuntu"
echo "========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Répertoires
INSTALL_DIR="/opt/pingu"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}[1/7]${NC} Vérification des dépendances..."
# Vérifier si Python 3 est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erreur: Python 3 n'est pas installé${NC}"
    echo "Installez-le avec: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo -e "${GREEN}  ✓ Python $(python3 --version) détecté${NC}"

echo -e "${YELLOW}[2/7]${NC} Création du répertoire d'installation..."
# Créer le répertoire d'installation
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/bd"
mkdir -p "$INSTALL_DIR/fichier/plugin"
mkdir -p "$INSTALL_DIR/cle"

echo -e "${YELLOW}[3/7]${NC} Copie des fichiers de l'application..."
# Copier les fichiers
cp "$SCRIPT_DIR/Pingu.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/LICENSE.txt" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/fichier" "$INSTALL_DIR/" 2>/dev/null || mkdir -p "$INSTALL_DIR/fichier/plugin"

# Copier les bases de données si elles existent
if [ -d "$SCRIPT_DIR/bd" ]; then
    cp "$SCRIPT_DIR/bd"/*.db "$INSTALL_DIR/bd/" 2>/dev/null || true
fi

# Créer le script de lancement
cat > "$INSTALL_DIR/pingu.sh" << 'EOF'
#!/bin/bash
cd /opt/pingu
if [ -d ".venv" ]; then
    source .venv/bin/activate
    python3 Pingu.py "$@"
else
    echo "Erreur: L'environnement virtuel n'est pas installé."
    echo "Veuillez réinstaller Ping ü."
    exit 1
fi
EOF

chmod +x "$INSTALL_DIR/pingu.sh"

echo -e "${YELLOW}[4/7]${NC} Installation de l'icône..."
# Copier l'icône
if [ -f "$SCRIPT_DIR/logoP.png" ]; then
    cp "$SCRIPT_DIR/logoP.png" /usr/share/pixmaps/pingu.png
    echo -e "${GREEN}  ✓ Icône installée${NC}"
else
    echo -e "${YELLOW}  ⚠ Icône non trouvée (logoP.png)${NC}"
fi

echo -e "${YELLOW}[5/7]${NC} Création du fichier .desktop..."
# Créer le fichier .desktop
cat > /usr/share/applications/pingu.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Ping ü
Name[fr]=Ping ü
Name[en]=Ping ü
Comment=Outil professionnel de monitoring réseau
Comment[fr]=Outil professionnel de monitoring réseau
Comment[en]=Professional network monitoring tool
GenericName=Network Monitor
GenericName[fr]=Moniteur réseau
GenericName[en]=Network Monitor
Exec=/opt/pingu/pingu.sh
Icon=pingu
Terminal=false
Categories=Network;Monitor;System;Utility;
Keywords=ping;network;monitoring;surveillance;réseau;
StartupNotify=true
StartupWMClass=Ping ü
EOF

echo -e "${YELLOW}[6/7]${NC} Installation des dépendances Python..."
# Créer un environnement virtuel et installer les dépendances
cd "$INSTALL_DIR"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}  → Installation en cours (cela peut prendre quelques minutes)...${NC}"
.venv/bin/pip install -r requirements.txt

echo -e "${YELLOW}[7/7]${NC} Configuration finale..."
# Créer le répertoire /usr/local/bin s'il n'existe pas
mkdir -p /usr/local/bin

# Créer le lien symbolique
ln -sf "$INSTALL_DIR/pingu.sh" /usr/local/bin/pingu

# Définir les permissions
chmod -R 755 "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/Pingu.py"

# Mettre à jour la base de données des applications
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✓ Installation terminée avec succès !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Ping ü a été installé dans: $INSTALL_DIR"
echo ""
echo "Pour lancer l'application:"
echo -e "  ${YELLOW}• Depuis le menu Applications${NC} (cherchez 'Ping ü')"
echo -e "  ${YELLOW}• Depuis le terminal:${NC} pingu"
echo ""
echo "Pour désinstaller:"
echo -e "  ${YELLOW}sudo rm -rf /opt/pingu${NC}"
echo -e "  ${YELLOW}sudo rm /usr/share/applications/pingu.desktop${NC}"
echo -e "  ${YELLOW}sudo rm /usr/share/pixmaps/pingu.png${NC}"
echo -e "  ${YELLOW}sudo rm /usr/local/bin/pingu${NC}"
echo ""
