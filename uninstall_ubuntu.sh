#!/bin/bash
#
# Script de désinstallation pour Ping ü sur Ubuntu/Debian
#

set -e

# Vérifier si le script est exécuté avec sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Ce script doit être exécuté avec sudo."
    echo "Usage: sudo ./uninstall_ubuntu.sh"
    exit 1
fi

echo "========================================="
echo "  Désinstallation de Ping ü"
echo "========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Demander confirmation
read -p "Êtes-vous sûr de vouloir désinstaller Ping ü ? (o/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "Désinstallation annulée."
    exit 0
fi

echo -e "${YELLOW}[1/5]${NC} Suppression des fichiers de l'application..."
if [ -d "/opt/pingu" ]; then
    rm -rf /opt/pingu
    echo -e "${GREEN}  ✓ Fichiers supprimés${NC}"
else
    echo -e "${YELLOW}  ⚠ Répertoire /opt/pingu non trouvé${NC}"
fi

echo -e "${YELLOW}[2/5]${NC} Suppression du fichier .desktop..."
if [ -f "/usr/share/applications/pingu.desktop" ]; then
    rm /usr/share/applications/pingu.desktop
    echo -e "${GREEN}  ✓ Fichier .desktop supprimé${NC}"
else
    echo -e "${YELLOW}  ⚠ Fichier .desktop non trouvé${NC}"
fi

echo -e "${YELLOW}[3/5]${NC} Suppression de l'icône..."
if [ -f "/usr/share/pixmaps/pingu.png" ]; then
    rm /usr/share/pixmaps/pingu.png
    echo -e "${GREEN}  ✓ Icône supprimée${NC}"
else
    echo -e "${YELLOW}  ⚠ Icône non trouvée${NC}"
fi

echo -e "${YELLOW}[4/5]${NC} Suppression du lien symbolique..."
if [ -L "/usr/local/bin/pingu" ]; then
    rm /usr/local/bin/pingu
    echo -e "${GREEN}  ✓ Lien symbolique supprimé${NC}"
else
    echo -e "${YELLOW}  ⚠ Lien symbolique non trouvé${NC}"
fi

echo -e "${YELLOW}[5/5]${NC} Mise à jour de la base de données des applications..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q
    echo -e "${GREEN}  ✓ Base de données mise à jour${NC}"
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✓ Désinstallation terminée !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Ping ü a été complètement supprimé de votre système."
echo ""
