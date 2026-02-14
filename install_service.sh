#!/bin/bash
# Script d'installation du service Systemd pour Ping ü

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Installation du service Systemd pour Ping ü ===${NC}"

# Vérifier que le script est lancé en root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Erreur : Ce script doit être exécuté en tant que root (sudo).${NC}"
  echo "Usage: sudo ./install_service.sh"
  exit 1
fi

# Obtenir le répertoire courant (où se trouve le script et l'application)
APP_DIR=$(dirname "$(readlink -f "$0")")
echo -e "Répertoire de l'application : ${GREEN}$APP_DIR${NC}"

# Obtenir l'utilisateur courant (pas root qui a lancé le sudo)
REAL_USER=${SUDO_USER:-$USER}
REAL_GROUP=$(id -gn $REAL_USER)
echo -e "Utilisateur du service : ${GREEN}$REAL_USER:$REAL_GROUP${NC}"

# Détecter Python (venv ou système)
if [ -d "$APP_DIR/.venv" ]; then
    PYTHON_CMD="$APP_DIR/.venv/bin/python"
    echo -e "Environnement virtuel détecté : ${GREEN}$PYTHON_CMD${NC}"
else
    PYTHON_CMD=$(which python3)
    echo -e "Utilisation de Python système : ${GREEN}$PYTHON_CMD${NC}"
fi

# Créer le fichier service à partir du template
SERVICE_FILE="/etc/systemd/system/pingu.service"
echo -e "Création du fichier de service : ${GREEN}$SERVICE_FILE${NC}"

cp "$APP_DIR/pingu.service.template" "$SERVICE_FILE"

# Remplacer les placeholders
sed -i "s|USER_PLACEHOLDER|$REAL_USER|g" "$SERVICE_FILE"
sed -i "s|DIR_PLACEHOLDER|$APP_DIR|g" "$SERVICE_FILE"
sed -i "s|PYTHON_PLACEHOLDER|$PYTHON_CMD|g" "$SERVICE_FILE"

# Recharger systemd
echo -e "${BLUE}Rechargement de systemd...${NC}"
systemctl daemon-reload

# Activer le service au démarrage
echo -e "${BLUE}Activation du service au démarrage...${NC}"
systemctl enable pingu.service

# Démarrer le service maintenant ?
read -p "Voulez-vous démarrer le service maintenant ? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    echo -e "${BLUE}Démarrage du service...${NC}"
    systemctl start pingu.service
    
    # Vérifier l'état
    if systemctl is-active --quiet pingu.service; then
        echo -e "${GREEN}✅ Le service Ping ü a démarré avec succès !${NC}"
        echo "Interface web accessible sur : http://localhost:9090/admin"
    else
        echo -e "${RED}❌ Erreur au démarrage du service. Vérifiez les logs :${NC}"
        echo "sudo journalctl -u pingu.service -n 50 --no-pager"
    fi
else
    echo "Vous pourrez démarrer le service plus tard avec : sudo systemctl start pingu.service"
fi

echo -e "${BLUE}=== Installation terminée ===${NC}"
