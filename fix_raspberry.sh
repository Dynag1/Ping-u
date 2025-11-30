#!/bin/bash
# Script de correction complet pour Raspberry Pi

echo "================================================"
echo "  CORRECTION PING Ü - RASPBERRY PI"
echo "================================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Configurer les permissions ping
echo -e "${YELLOW}[1/4]${NC} Configuration des permissions ping..."
if sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"; then
    echo -e "${GREEN}✅ Permissions ping configurées${NC}"
    
    # Rendre permanent
    if ! grep -q "net.ipv4.ping_group_range" /etc/sysctl.conf 2>/dev/null; then
        echo "net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.conf > /dev/null
        echo -e "${GREEN}✅ Configuration rendue permanente${NC}"
    fi
else
    echo -e "${RED}❌ Échec de configuration des permissions${NC}"
fi
echo ""

# 2. Créer les fichiers de configuration
echo -e "${YELLOW}[2/4]${NC} Création des fichiers de configuration..."
if python3 init_raspberry.py; then
    echo -e "${GREEN}✅ Fichiers créés${NC}"
else
    echo -e "${RED}❌ Erreur lors de la création des fichiers${NC}"
fi
echo ""

# 3. Vérifier les dépendances Python
echo -e "${YELLOW}[3/4]${NC} Vérification des dépendances Python..."
if [ -f "requirements.txt" ]; then
    if pip3 list | grep -q "PySide6"; then
        echo -e "${GREEN}✅ Dépendances OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Installation des dépendances...${NC}"
        pip3 install -r requirements.txt
    fi
else
    echo -e "${YELLOW}⚠️  Fichier requirements.txt non trouvé${NC}"
fi
echo ""

# 4. Test de ping
echo -e "${YELLOW}[4/4]${NC} Test de ping..."
if ping -c 1 -W 1 8.8.8.8 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ping fonctionne correctement${NC}"
else
    echo -e "${RED}❌ Le ping ne fonctionne pas${NC}"
    echo -e "${YELLOW}💡 Essayez avec sudo ou vérifiez les permissions${NC}"
fi
echo ""

echo "================================================"
echo -e "${GREEN}✅ Correction terminée !${NC}"
echo "================================================"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Arrêter l'application si elle tourne:"
echo "      ./stop_headless.sh"
echo ""
echo "   2. Relancer l'application:"
echo "      ./start_headless.sh"
echo ""
echo "   3. Vérifier les logs:"
echo "      tail -f pingu_headless.log"
echo ""
echo "   4. Accéder à l'interface web:"
echo "      http://$(hostname -I | awk '{print $1}'):6666"
echo "      Identifiants: admin / admin"
echo ""

