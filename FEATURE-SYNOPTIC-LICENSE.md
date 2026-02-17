# Feature: Restriction de la page synoptique aux licences actives

## Description
La page synoptique (`/synoptic`) est maintenant restreinte aux utilisateurs possédant une licence active.

## Comportement

### 🔓 Avec licence active
- Accès normal à la page synoptique
- Toutes les fonctionnalités disponibles

### 🔒 Sans licence active
- **Message affiché:** "Vous devez avoir une licence active pour accéder à la page synoptique."
- **Code HTTP:** 403 Forbidden
- **Page d'erreur:** Template élégant avec options de navigation
- **Boutons disponibles:**
  - 🏠 Retour à l'accueil
  - ⚙️ Administration (si utilisateur admin)

## Implémentation

### Fichiers modifiés
1. **src/web/routes/main_routes.py**
   - Ajout de la vérification `lic.verify_license()` dans la route `/synoptic`
   - Code HTTP 403 si licence invalide

2. **src/web/templates/error.html** (nouveau)
   - Template d'erreur moderne et responsive
   - Design cohérent avec l'application
   - Animations et gradients
   - Informations contextuelles

### Code de la vérification
```python
@main_bp.route('/synoptic')
@WebAuth.any_login_required
def synoptic():
    try:
        # Vérification de la licence
        from src import lic
        if not lic.verify_license():
            # Licence invalide - afficher une page d'erreur
            error_message = "Vous devez avoir une licence active pour accéder à la page synoptique."
            return render_template('error.html', 
                                 error_title="Licence requise",
                                 error_message=error_message,
                                 is_admin=session.get('role') == 'admin',
                                 username=session.get('username', '')), 403
        
        # Licence valide - afficher la page normalement
        is_admin = session.get('role') == 'admin'
        username = session.get('username', '')
        return render_template('synoptic.html', is_admin=is_admin, username=username)
    except Exception as e:
        logger.error(f"Erreur rendu synoptic: {e}", exc_info=True)
        return jsonify({'error': 'Template introuvable'}), 500
```

## Caractéristiques du template error.html

### Design
- ✅ Gradient de fond moderne (violet/bleu)
- ✅ Carte blanche centrée avec ombre portée
- ✅ Icône animée (🔒 avec effet bounce)
- ✅ Animation d'apparition (slideIn)
- ✅ Responsive et mobile-friendly

### Informations affichées
- Titre de l'erreur (personnalisable)
- Message d'erreur détaillé
- Code d'erreur optionnel
- Boîte d'information contextuelle
- Nom d'utilisateur connecté

### Navigation
- Bouton "Retour à l'accueil" (toujours visible)
- Bouton "Administration" (si admin)

## Extensibilité

Le template `error.html` est générique et peut être réutilisé pour d'autres erreurs:

```python
return render_template('error.html', 
                     error_title="Titre personnalisé",
                     error_message="Message d'erreur",
                     error_code="ERR_CODE",  # optionnel
                     is_admin=is_admin,
                     username=username), 403
```

## Test

### Avec licence valide
```bash
# Démarrer l'application avec licence
python Pingu.py --start
# Naviguer vers http://localhost:5000/synoptic
# → Page synoptique affichée normalement
```

### Sans licence
```bash
# Simuler une licence invalide (désactiver temporairement dans lic.py)
# Naviguer vers http://localhost:5000/synoptic
# → Page d'erreur avec message "Licence requise"
```

## Screenshots conceptuels

```
┌─────────────────────────────────────────┐
│                                         │
│              🔒                         │
│                                         │
│         Licence requise                 │
│                                         │
│  Vous devez avoir une licence active    │
│  pour accéder à la page synoptique.     │
│                                         │
│  ┌───────────────────────────────┐     │
│  │ ℹ️ Pourquoi cette erreur ?     │     │
│  │ La page synoptique est une     │     │
│  │ fonctionnalité premium...      │     │
│  └───────────────────────────────┘     │
│                                         │
│  [ 🏠 Retour à l'accueil ]              │
│  [ ⚙️ Administration ]                  │
│                                         │
│  Connecté en tant que: username         │
└─────────────────────────────────────────┘
```

## Avantages

1. **Protection de la fonctionnalité premium** 🔐
2. **Message clair pour l'utilisateur** 💬
3. **Design professionnel** 🎨
4. **Navigation facile** 🧭
5. **Template réutilisable** ♻️

## Notes

- La vérification se fait côté serveur (impossible de contourner)
- L'authentification est toujours requise (login avant vérification licence)
- Le template error.html peut être personnalisé selon vos besoins
- Compatible avec le système de licence existant
