# Ajustements pour rendre le nettoyage moins agressif

Suite à vos commentaires sur le caractère trop agressif du scraper, nous avons apporté des modifications pour trouver un meilleur équilibre entre :
- Suppression des éléments de navigation non pertinents 
- Préservation du contenu principal

## 1. Réduction des sélecteurs CSS

Nous avons considérablement réduit la liste des sélecteurs CSS utilisés dans `remove_headers_footers()` :

- **Sélecteurs pour les headers** : réduits de 14 à 6 sélecteurs essentiels
- **Sélecteurs pour les footers** : réduits de 15 à 6 sélecteurs essentiels
- **Sélecteurs pour les navbars** : réduits de 30+ à 7 sélecteurs essentiels
- **Sélecteurs pour les sidebars** : réduits de 20+ à 4 sélecteurs essentiels
- **Autres éléments non désirés** : réduits de 30+ à 6 éléments vraiment intrusifs

Cela limite le nettoyage aux éléments les plus standardisés et évidents.

## 2. Protection du contenu riche

Un mécanisme de protection a été ajouté dans `remove_headers_footers()` :
```python
# Ignorer les éléments avec beaucoup de contenu textuel
if len(text_content) > 1000 and selector not in ['.ads', '.advertisement', '.cookie-notice', '.popup', '.modal']:
    # Ne pas supprimer - contient trop de contenu pour être juste un élément de navigation
    continue
```

Cela évite de supprimer des sections qui, bien qu'identifiées par un sélecteur ciblé, contiennent en réalité du contenu significatif.

## 3. Détection intelligente plus prudente

La méthode `detect_nav_by_content()` a été rendue moins agressive avec :

- **Seuil de détection des menus** : augmenté de 5 à 8 liens
- **Critère de liens courts** : plus strict (de 70% à 85% des liens)
- **Protection du contenu textuel** : préservation des blocs contenant du texte informatif
- **Termes de détection** : liste réduite aux termes les plus spécifiques
- **Analyse de position** : limitée au premier et dernier élément uniquement
- **Critère de largeur** : plus strict (de 40% à 25%) pour les sidebars

## 4. Application conditionnelle des méthodes

La fonction `clean_html()` intègre maintenant une logique pour éviter une sur-application des nettoyages :

1. **Contrôle après le premier nettoyage** :
   ```python
   # Si on a déjà perdu plus de 30% du contenu, on ne fait pas de détection avancée
   if post_header_footer_length > original_content_length * 0.7:
       self.detect_nav_by_content(soup)
   ```

2. **Contrôle avant nettoyage du contenu Readability** :
   ```python
   # Appliquer la détection avancée uniquement si le contenu est conséquent
   if readability_content_length > 1000:
       self.detect_nav_by_content(clean_soup)
   ```

## Résultat attendu

Ces modifications permettent de :

1. Conserver davantage de contenu informatif
2. Éliminer uniquement les éléments de navigation les plus évidents
3. Adapter le niveau de nettoyage à la richesse du contenu
4. Protéger les parties importantes qui pourraient être mal identifiées

Le résultat devrait être un meilleur équilibre entre un contenu propre et complet.

## Test

Vous pouvez tester ces modifications avec la même commande :

```bash
python run.py scrape https://example.com --save
```

Les résultats devraient maintenant contenir davantage de contenu original tout en restant relativement épurés des éléments de navigation les plus intrusifs. 