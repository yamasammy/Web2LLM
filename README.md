# Web Scraper et Convertisseur Markdown

Un outil Python avancé pour extraire des données à partir de sites web, nettoyer le contenu et le convertir en Markdown de haute qualité pour une utilisation optimale par des LLM.

## Fonctionnalités

- **Extraction intelligente de contenu** de pages web avec élimination des éléments non pertinents
- **Nettoyage avancé du contenu** :
  - Suppression des headers, footers, navbars et sidebars
  - Élimination complète du CSS et JavaScript
  - Détection intelligente des éléments de navigation par analyse de contenu
- **Conversion optimisée en Markdown** avec plusieurs méthodes en cascade
- **API REST** pour l'intégration dans des workflows
- **Sauvegarde locale** en fichiers .md avec génération de noms pertinents

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### En ligne de commande

```bash
# Scraper une URL et afficher le résultat
python run.py scrape https://example.com

# Scraper une URL et sauvegarder en Markdown
python run.py scrape https://example.com --save

# Spécifier un nom de fichier de sortie
python run.py scrape https://example.com --save --output mon-fichier.md
```

### Démarrer l'API

```bash
python -m app.main
```

### Utiliser en tant que bibliothèque

```python
from app.scraper import scrape_url
from app.converter import html_to_markdown

# Scraper une URL
result = scrape_url("https://example.com")
html_content = result["html"]

# Convertir en markdown
markdown_content = html_to_markdown(html_content)

# Enregistrer dans un fichier
with open("output.md", "w") as f:
    f.write(markdown_content)
```

## API Endpoints

- `POST /scrape` : Scrape une URL et retourne le contenu en Markdown
- `POST /scrape/save` : Scrape une URL et sauvegarde le contenu en fichier Markdown

## Améliorations majeures

### 1. Extraction intelligente du contenu

- **Suppression complète des headers et footers** via une liste exhaustive de sélecteurs CSS
- **Détection avancée des navbars et sidebars** :
  - Par sélecteurs CSS standards
  - Par analyse de densité de liens (menus avec nombreux liens courts)
  - Par analyse de contenu textuel (termes comme "menu", "navigation")
  - Par position dans la page (premiers/derniers éléments)
  - Par attributs CSS (largeur réduite typique des sidebars)
- **Extraction de contenu supplémentaire** si Readability n'extrait pas suffisamment
- **Approche équilibrée et adaptative** :
  - Préservation du contenu riche (>1000 caractères)
  - Application conditionnelle des méthodes de nettoyage
  - Seuils ajustables pour différents types de sites

### 2. Élimination complète du CSS et JavaScript

- **Suppression de toutes les balises script et style** et leur contenu
- **Élimination des attributs JavaScript** (onclick, onload, etc.)
- **Suppression des styles inline** et classes liées au JavaScript
- **Filtrage des blocs de code** ressemblant à du CSS ou JavaScript
- **Nettoyage des sections CDATA** pouvant contenir du code

### 3. Conversion Markdown optimisée

- **Approche multi-méthodes en cascade** :
  - Utilisation de html2markdown comme méthode principale
  - Extraction structurée avec BeautifulSoup en secours
  - Extraction du texte brut en dernier recours
- **Nettoyage complet des balises HTML résiduelles**
- **Traitement spécifique** pour tableaux, citations, blocs de code, images
- **Double nettoyage** des espaces et sauts de ligne

### 4. Gestion robuste des erreurs

- **Sauvegarde du HTML brut** en cas d'échec de conversion
- **Extraction du texte** comme alternative si la conversion échoue
- **Meilleure détection de l'encodage** des pages web
- **Génération de noms de fichiers** significatifs et robustes

## Paramètres ajustables

Pour adapter l'outil à des sites spécifiques, vous pouvez modifier :

1. **Seuils de détection** dans `detect_nav_by_content()` :
   - Nombre de liens (actuellement 8)
   - Pourcentage de liens courts (actuellement 85%)
   - Longueur de texte considérée comme significative (actuellement 50 caractères par lien)

2. **Sélecteurs CSS** dans `remove_headers_footers()` :
   - Ajouter des sélecteurs spécifiques pour certains sites
   - Modifier les listes `header_selectors`, `footer_selectors`, etc.

3. **Seuils de contenu** dans `clean_html()` :
   - Modifier le seuil de 500 caractères pour l'extraction supplémentaire
   - Ajuster le seuil de 70% pour l'application de la détection avancée

## Exemples de résultats

Avec ces améliorations, le scraper produit :
- Un contenu Markdown propre sans balises HTML
- Aucun script JavaScript ou style CSS
- Aucune barre de navigation ou barre latérale
- Uniquement le contenu principal informatif

## Maintenance et dépannage

Si vous rencontrez des problèmes avec certains sites :

1. **Vérifiez la structure HTML** du site pour identifier des éléments particuliers
2. **Ajoutez des sélecteurs CSS spécifiques** dans les listes appropriées
3. **Ajustez les seuils de détection** pour être plus ou moins agressif
4. **Utilisez l'option de sauvegarde du HTML brut** pour analyser le contenu original

## Configuration

Voir le fichier `.env.example` pour les options de configuration disponibles. 
