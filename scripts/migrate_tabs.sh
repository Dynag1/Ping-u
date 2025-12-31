#!/bin/bash
###############################################################################
# Script de migration des fichiers tab vers bd/tabs/
# Migration automatique des fichiers de configuration
###############################################################################

# Se placer à la racine du projet (parent du dossier scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

echo "=============================================================="
echo "  Migration des fichiers tab vers bd/tabs/"
echo "  Ping ü - Configuration Migration Script"
echo "=============================================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fichiers à migrer
FILES=("tab" "tab4" "tabG" "tabr")
MIGRATED=0
ALREADY_MOVED=0
NOT_FOUND=0

echo -e "${BLUE}📁 Vérification de la structure des dossiers...${NC}"

# Créer le dossier bd/tabs s'il n'existe pas
if [ ! -d "bd/tabs" ]; then
    echo -e "${YELLOW}   ⚠️  Le dossier bd/tabs n'existe pas${NC}"
    echo -e "${BLUE}   📁 Création du dossier bd/tabs...${NC}"
    mkdir -p bd/tabs
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ Dossier bd/tabs créé avec succès${NC}"
    else
        echo -e "${RED}   ❌ Erreur lors de la création du dossier${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}   ✅ Le dossier bd/tabs existe déjà${NC}"
fi

echo ""
echo -e "${BLUE}🔄 Migration des fichiers de configuration...${NC}"
echo ""

# Migrer chaque fichier
for file in "${FILES[@]}"; do
    echo -e "${BLUE}📄 Traitement de '${file}'...${NC}"
    
    # Vérifier si le fichier existe à la racine
    if [ -f "$file" ]; then
        # Vérifier si le fichier existe déjà dans bd/tabs
        if [ -f "bd/tabs/$file" ]; then
            echo -e "${YELLOW}   ⚠️  Le fichier existe déjà dans bd/tabs/${NC}"
            echo -e "${YELLOW}   ⏭️  Création d'une sauvegarde : bd/tabs/${file}.backup${NC}"
            cp "bd/tabs/$file" "bd/tabs/${file}.backup"
        fi
        
        # Déplacer le fichier
        mv "$file" "bd/tabs/"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}   ✅ ${file} → bd/tabs/${file}${NC}"
            ((MIGRATED++))
        else
            echo -e "${RED}   ❌ Erreur lors du déplacement de ${file}${NC}"
        fi
    elif [ -f "bd/tabs/$file" ]; then
        echo -e "${GREEN}   ✓  Déjà dans bd/tabs/${NC}"
        ((ALREADY_MOVED++))
    else
        echo -e "${YELLOW}   ⏭️  Fichier non trouvé (sera créé au besoin)${NC}"
        ((NOT_FOUND++))
    fi
    echo ""
done

# Résumé
echo "=============================================================="
echo -e "${BLUE}📊 Résumé de la migration${NC}"
echo "=============================================================="
echo -e "  ${GREEN}✅ Fichiers migrés      : ${MIGRATED}${NC}"
echo -e "  ${YELLOW}⏭️  Déjà migrés          : ${ALREADY_MOVED}${NC}"
echo -e "  ${YELLOW}⏭️  Non trouvés          : ${NOT_FOUND}${NC}"
echo "=============================================================="
echo ""

# Vérifier le contenu final de bd/tabs
echo -e "${BLUE}📁 Contenu de bd/tabs/ :${NC}"
ls -lh bd/tabs/ 2>/dev/null || echo -e "${YELLOW}   (vide)${NC}"
echo ""

# Instructions finales
if [ $MIGRATED -gt 0 ] || [ $ALREADY_MOVED -gt 0 ]; then
    echo -e "${GREEN}✅ Migration terminée avec succès !${NC}"
    echo ""
    echo -e "${BLUE}📝 Prochaines étapes :${NC}"
    echo "   1. Vérifiez que l'application démarre correctement"
    echo "   2. Vérifiez que vos paramètres sont toujours présents"
    echo "   3. En cas de problème, restaurez depuis bd/tabs/*.backup"
else
    echo -e "${YELLOW}⚠️  Aucun fichier n'a été migré${NC}"
    echo ""
    echo -e "${BLUE}💡 Informations :${NC}"
    echo "   - Si c'est une nouvelle installation, les fichiers seront créés automatiquement"
    echo "   - Si vous avez déjà migré, tout est OK !"
fi

echo ""
echo -e "${GREEN}✨ Script terminé${NC}"
