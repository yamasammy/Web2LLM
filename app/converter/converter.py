"""
Module de conversion du HTML en Markdown.
"""
import os
import logging
import re
from typing import Optional, Dict, Any
from html2markdown import convert
from bs4 import BeautifulSoup
import markdown
from urllib.parse import urlparse, urljoin

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarkdownConverter:
    """Classe pour convertir le HTML en Markdown avec options de nettoyage avancées."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialise le convertisseur.
        
        Args:
            base_url: URL de base pour résoudre les liens relatifs
        """
        self.base_url = base_url
    
    def fix_relative_urls(self, html_content: str, base_url: Optional[str] = None) -> str:
        """
        Remplace les URLs relatives par des URLs absolues.
        
        Args:
            html_content: Le contenu HTML
            base_url: L'URL de base pour résoudre les liens relatifs
            
        Returns:
            HTML avec liens absolus
        """
        if not base_url and not self.base_url:
            return html_content
            
        url_to_use = base_url if base_url else self.base_url
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Corriger les liens
        for a_tag in soup.find_all('a', href=True):
            if not a_tag['href'].startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                a_tag['href'] = urljoin(url_to_use, a_tag['href'])
        
        # Corriger les images
        for img_tag in soup.find_all('img', src=True):
            if not img_tag['src'].startswith(('http://', 'https://', 'data:')):
                img_tag['src'] = urljoin(url_to_use, img_tag['src'])
        
        return str(soup)
    
    def pre_process_html(self, html_content: str) -> str:
        """
        Pré-traitement du HTML pour améliorer la conversion en Markdown.
        
        Args:
            html_content: Le contenu HTML
            
        Returns:
            HTML pré-traité
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer tous les scripts et styles - Première passe critique
        for element in soup.find_all(['script', 'style', 'noscript', 'iframe']):
            element.decompose()
        
        # Supprimer les attributs JavaScript inline et styles
        for tag in soup.find_all(True):
            # Liste pour stocker les attributs à supprimer
            attrs_to_remove = []
            
            for attr in tag.attrs:
                # Supprimer style et attributs JavaScript
                if attr == 'style' or attr.startswith('on'):
                    attrs_to_remove.append(attr)
            
            # Supprimer les attributs identifiés
            for attr in attrs_to_remove:
                del tag[attr]
        
        # Convertir les divs qui se comportent comme des paragraphes en paragraphes réels
        for div in soup.find_all('div'):
            if not div.find(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'ul', 'ol']):
                div.name = 'p'
        
        # S'assurer que les listes sont correctement formatées
        for ul in soup.find_all(['ul', 'ol']):
            for child in ul.children:
                if child.name != 'li' and child.name is not None:
                    # Convertir ou envelopper dans un li
                    if child.string and child.string.strip():
                        new_li = soup.new_tag('li')
                        child.wrap(new_li)
        
        # Traiter les tableaux pour une meilleure conversion
        for table in soup.find_all('table'):
            # S'assurer que chaque tableau a un thead et tbody
            if not table.find('thead'):
                thead = soup.new_tag('thead')
                first_tr = table.find('tr')
                if first_tr:
                    first_tr.wrap(thead)
            
            # S'assurer que tbody existe
            if not table.find('tbody'):
                tbody = soup.new_tag('tbody')
                for tr in table.find_all('tr')[1:]:
                    tr.wrap(tbody)
        
        # Nettoyer les balises span inutiles
        for span in soup.find_all('span'):
            if not span.attrs:  # Si span n'a pas d'attributs
                span.unwrap()
        
        # Supprimer les objets JavaScript/Flash/etc.
        for obj in soup.find_all(['object', 'embed']):
            obj.decompose()
        
        # Supprimer les formulaires (souvent inutiles pour l'extraction de contenu)
        for form in soup.find_all('form'):
            form.decompose()
        
        # Retourner le HTML pré-traité
        return str(soup)
    
    def clean_markdown(self, markdown_content: str) -> str:
        """
        Nettoie le markdown généré.
        
        Args:
            markdown_content: Le contenu Markdown
            
        Returns:
            Markdown nettoyé
        """
        # Supprimer les lignes vides consécutives
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # Nettoyer les liens qui ont pu être mal convertis
        markdown_content = re.sub(r'\[(.+?)\]\s*\[\]', r'\1', markdown_content)
        
        # Supprimer les blocs de scripts JavaScript
        markdown_content = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', markdown_content)
        
        # Supprimer les blocs de style CSS
        markdown_content = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', markdown_content)
        
        # Supprimer les blocs CDATA qui pourraient contenir du JavaScript ou CSS
        markdown_content = re.sub(r'<!\[CDATA\[[\s\S]*?\]\]>', '', markdown_content)
        
        # Nettoyer TOUTES les balises HTML, pas seulement certaines
        markdown_content = re.sub(r'</?[a-zA-Z][^>]*>', '', markdown_content)
        
        # Nettoyer les balises <br> et les remplacer par des sauts de ligne
        markdown_content = re.sub(r'<br\s*/?>',  '\n', markdown_content)
        
        # Nettoyer les espaces excessifs
        markdown_content = re.sub(r' {2,}', ' ', markdown_content)
        
        # Nettoyer les attributs HTML restants et toutes les balises avec leurs attributs
        markdown_content = re.sub(r'<([a-z0-9]+)(?:\s+[a-z0-9-]+(?:=(?:"[^"]*"|\'[^\']*\'))?)*\s*>', '', markdown_content)
        markdown_content = re.sub(r'</[a-z0-9]+>', '', markdown_content)
        
        # Supprimer les commentaires HTML
        markdown_content = re.sub(r'<!--[\s\S]*?-->', '', markdown_content)
        
        # Supprimer tous les caractères d'échappement HTML comme &nbsp;
        markdown_content = re.sub(r'&[a-zA-Z]+;', ' ', markdown_content)
        
        # Supprimer les styles et scripts qui pourraient être intégrés dans des blocs de code
        markdown_content = re.sub(r'```(?:javascript|js|css|style)[\s\S]*?```', '', markdown_content)
        
        # Supprimer les lignes qui ressemblent à du CSS (propriété: valeur;)
        markdown_content = re.sub(r'^[a-z-]+:\s*[^;]+;\s*$', '', markdown_content, flags=re.MULTILINE)
        
        # Supprimer les lignes qui ressemblent à des déclarations JavaScript
        markdown_content = re.sub(r'^var\s+[a-zA-Z0-9_$]+\s*=', '', markdown_content, flags=re.MULTILINE)
        markdown_content = re.sub(r'^function\s+[a-zA-Z0-9_$]+\s*\(', '', markdown_content, flags=re.MULTILINE)
        markdown_content = re.sub(r'^const\s+[a-zA-Z0-9_$]+\s*=', '', markdown_content, flags=re.MULTILINE)
        markdown_content = re.sub(r'^let\s+[a-zA-Z0-9_$]+\s*=', '', markdown_content, flags=re.MULTILINE)
        
        # Supprimer les accolades isolées qui pourraient provenir de code
        markdown_content = re.sub(r'^\s*[{}]\s*$', '', markdown_content, flags=re.MULTILINE)
        
        # Supprimer les doubles espaces après avoir enlevé les balises
        markdown_content = re.sub(r' {2,}', ' ', markdown_content)
        
        # Nettoyer les lignes vides multiples qui peuvent être créées après suppression des balises
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # Supprimer les lignes qui ne contiennent que des caractères non significatifs
        markdown_content = re.sub(r'^\s*[;:.,_\-*+#]+\s*$', '', markdown_content, flags=re.MULTILINE)
        
        return markdown_content.strip()
    
    def html_to_markdown(self, html_content: str, url: Optional[str] = None) -> str:
        """
        Convertit le HTML en Markdown.
        
        Args:
            html_content: Le contenu HTML
            url: L'URL source pour résoudre les liens relatifs
            
        Returns:
            Contenu au format Markdown
        """
        try:
            # Pré-traiter le HTML
            html_content = self.pre_process_html(html_content)
            
            # Fixer les URLs relatives si une URL est fournie
            base_url = url or self.base_url
            if base_url:
                html_content = self.fix_relative_urls(html_content, base_url)
            
            # Approche 1: Utiliser html2markdown (la bibliothèque standard)
            markdown_content_1 = convert(html_content)
            markdown_content_1 = self.clean_markdown(markdown_content_1)
            
            # Si le résultat semble bon, on le retourne
            if not ('<' in markdown_content_1 and '>' in markdown_content_1):
                return markdown_content_1
            
            # Approche 2: Extraction directe avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            content_parts = []
            
            # Ajouter le titre
            if soup.title:
                content_parts.append(f"# {soup.title.string.strip()}\n\n")
            
            # Ajouter les titres et sous-titres
            for i in range(1, 7):
                for header in soup.find_all(f'h{i}'):
                    content_parts.append(f"{'#' * i} {header.get_text().strip()}\n\n")
            
            # Ajouter les paragraphes
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text:
                    content_parts.append(f"{text}\n\n")
            
            # Ajouter les listes non ordonnées
            for ul in soup.find_all('ul'):
                for li in ul.find_all('li'):
                    content_parts.append(f"* {li.get_text().strip()}\n")
                content_parts.append("\n")
            
            # Ajouter les listes ordonnées
            for ol in soup.find_all('ol'):
                for i, li in enumerate(ol.find_all('li')):
                    content_parts.append(f"{i+1}. {li.get_text().strip()}\n")
                content_parts.append("\n")
            
            # Ajouter les tableaux (version simple)
            for table in soup.find_all('table'):
                for tr in table.find_all('tr'):
                    row = []
                    for cell in tr.find_all(['td', 'th']):
                        row.append(cell.get_text().strip())
                    if row:
                        content_parts.append("| " + " | ".join(row) + " |\n")
                content_parts.append("\n")
            
            # Ajouter les citations
            for blockquote in soup.find_all('blockquote'):
                lines = blockquote.get_text().strip().split('\n')
                for line in lines:
                    if line.strip():
                        content_parts.append(f"> {line.strip()}\n")
                content_parts.append("\n")
            
            # Ajouter les blocs de code
            for pre in soup.find_all('pre'):
                content_parts.append("```\n")
                content_parts.append(pre.get_text().strip() + "\n")
                content_parts.append("```\n\n")
            
            # Ajouter les images
            for img in soup.find_all('img'):
                alt = img.get('alt', '')
                src = img.get('src', '')
                if src:
                    content_parts.append(f"![{alt}]({src})\n\n")
            
            # Ajouter les liens
            for a in soup.find_all('a'):
                text = a.get_text().strip()
                href = a.get('href', '')
                if href and text:
                    content_parts.append(f"[{text}]({href})\n\n")
            
            # Autres blocs de texte significatifs
            for div in soup.find_all(['div', 'article', 'section', 'main']):
                # Éviter les div qui contiennent déjà des éléments traités
                if not div.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
                    text = div.get_text().strip()
                    if len(text) > 100:  # Contenu significatif
                        content_parts.append(f"{text}\n\n")
            
            markdown_content_2 = ''.join(content_parts)
            
            # Approche 3: Extraction de texte brut en dernier recours
            if not markdown_content_2 or len(markdown_content_2) < 200:
                markdown_content_3 = soup.get_text(separator='\n\n', strip=True)
                # Nettoyer et structurer le texte brut
                paragraphs = [p.strip() for p in markdown_content_3.split('\n\n') if p.strip()]
                markdown_content_3 = '\n\n'.join(paragraphs)
                
                # Si cette approche donne un meilleur résultat, l'utiliser
                if len(markdown_content_3) > len(markdown_content_2):
                    markdown_content_2 = markdown_content_3
            
            # Nettoyer le résultat final
            markdown_content_2 = self.clean_markdown(markdown_content_2)
            
            # Sélectionner la meilleure approche
            if len(markdown_content_1) > len(markdown_content_2) and '<' not in markdown_content_1:
                return markdown_content_1
            else:
                return markdown_content_2
                
        except Exception as e:
            logger.error(f"Erreur lors de la conversion en Markdown: {str(e)}")
            # Fallback: extraction simple du texte
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator='\n\n', strip=True)
            return self.clean_markdown(text)
    
    def save_markdown(self, markdown_content: str, filepath: str) -> bool:
        """
        Enregistre le contenu Markdown dans un fichier.
        
        Args:
            markdown_content: Le contenu Markdown
            filepath: Chemin où sauvegarder le fichier
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # S'assurer que le répertoire existe
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Contenu Markdown sauvegardé avec succès dans {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier Markdown: {str(e)}")
            return False
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """
        Convertit le Markdown en HTML (utile pour la prévisualisation).
        
        Args:
            markdown_content: Le contenu Markdown
            
        Returns:
            Contenu au format HTML
        """
        try:
            return markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        except Exception as e:
            logger.error(f"Erreur lors de la conversion du Markdown en HTML: {str(e)}")
            return f"<pre>{markdown_content}</pre>"


# Fonctions utilitaires pour une utilisation rapide
def html_to_markdown(html_content: str, url: Optional[str] = None) -> str:
    """
    Fonction utilitaire pour convertir HTML en Markdown.
    
    Args:
        html_content: Le contenu HTML
        url: L'URL source pour résoudre les liens relatifs
        
    Returns:
        Contenu au format Markdown
    """
    converter = MarkdownConverter(base_url=url)
    return converter.html_to_markdown(html_content, url)

def save_markdown(markdown_content: str, filepath: str) -> bool:
    """
    Fonction utilitaire pour sauvegarder du Markdown dans un fichier.
    
    Args:
        markdown_content: Le contenu Markdown
        filepath: Chemin où sauvegarder le fichier
        
    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    converter = MarkdownConverter()
    return converter.save_markdown(markdown_content, filepath) 