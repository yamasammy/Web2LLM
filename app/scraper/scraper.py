"""
Module de scraping pour extraire le contenu des pages web.
"""
import os
import logging
from typing import Dict, Optional, Union, List
import requests
from bs4 import BeautifulSoup
from readability import Document
from dotenv import load_dotenv
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration par défaut
DEFAULT_USER_AGENT = os.getenv(
    'USER_AGENT', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
)
DEFAULT_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
DEFAULT_MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

class WebScraper:
    """Classe pour scraper des pages web et nettoyer leur contenu."""
    
    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, 
                 timeout: int = DEFAULT_TIMEOUT,
                 max_retries: int = DEFAULT_MAX_RETRIES):
        """
        Initialise le scraper.
        
        Args:
            user_agent: User-Agent à utiliser pour les requêtes HTTP
            timeout: Délai d'attente en secondes pour les requêtes
            max_retries: Nombre maximal de tentatives en cas d'échec
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def fetch_url(self, url: str) -> Optional[str]:
        """
        Récupère le contenu HTML d'une URL.
        
        Args:
            url: L'URL à scraper
            
        Returns:
            Le contenu HTML ou None en cas d'échec
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentative {attempt + 1}/{self.max_retries} de récupération de {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Détection de l'encodage
                encoding = response.encoding
                
                # Si le site ne spécifie pas d'encodage ou qu'il est incorrect, essayer de le détecter
                if encoding == 'ISO-8859-1' or not encoding:
                    detected_encoding = response.apparent_encoding
                    if detected_encoding:
                        response.encoding = detected_encoding
                
                return response.text
            except requests.RequestException as e:
                logger.error(f"Erreur lors de la récupération de {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Échec après {self.max_retries} tentatives.")
                    return None
        return None
    
    def extract_additional_content(self, soup: BeautifulSoup) -> str:
        """
        Extrait du contenu supplémentaire qui pourrait être ignoré par Readability.
        
        Args:
            soup: Objet BeautifulSoup contenant la page HTML
            
        Returns:
            Contenu HTML supplémentaire
        """
        additional_html = ""
        
        # Rechercher des sections de contenu courantes qui pourraient être manquées
        content_selectors = [
            'article', '.article', '.post', '.content', '.main-content',
            'main', '#main', '#content', '.body', '.entry-content',
            '.page-content', '[role="main"]', '[itemprop="articleBody"]',
            '.blog-post', '.text', '.publication-content', '.story'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    additional_html += str(element)
        
        # Si aucun contenu n'a été trouvé avec les sélecteurs, essayer d'autres méthodes
        if not additional_html:
            # Obtenir tous les paragraphes qui ont un contenu substantiel
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                # Considérer uniquement les paragraphes avec un contenu significatif
                if len(text) > 50:  # Paragraphes d'au moins 50 caractères
                    paragraphs.append(str(p))
            
            if paragraphs:
                additional_html = "\n".join(paragraphs)
        
        return additional_html
    
    def remove_headers_footers(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Supprime les headers, footers, scripts, styles et autres éléments non désirés des pages web,
        avec une approche plus modérée pour préserver davantage de contenu.
        
        Args:
            soup: L'objet BeautifulSoup contenant le HTML
            
        Returns:
            L'objet BeautifulSoup nettoyé
        """
        # Liste des sélecteurs pour les headers et footers courants - version allégée
        header_selectors = [
            'header', '#header', '.header', '.site-header', 
            '.masthead', '[role="banner"]'
        ]
        
        footer_selectors = [
            'footer', '#footer', '.footer', '.site-footer',
            '.copyright', '[role="contentinfo"]'
        ]
        
        # Sélecteurs essentiels pour les navbars
        navbar_selectors = [
            'nav', '.navbar', '.main-nav', 
            '#navbar', '#navigation', '#menu',
            '[role="navigation"]'
        ]
        
        # Sélecteurs essentiels pour les sidebars
        sidebar_selectors = [
            'aside', '.sidebar', '#sidebar',
            '[role="complementary"]'
        ]
        
        # Éléments non désirés les plus courants et intrusifs
        unwanted_selectors = [
            '.ads', '.advertisement', '.banner', '.cookie-notice', 
            '.popup', '.modal', '.newsletter-signup', 
            '.cookie-banner', '.adsbygoogle', '.ad-container',
            '.gdpr'
        ]
        
        # Combiner tous les sélecteurs
        all_selectors = header_selectors + footer_selectors + navbar_selectors + sidebar_selectors + unwanted_selectors
        
        # Supprimer tous ces éléments
        for selector in all_selectors:
            for element in soup.select(selector):
                # Vérifier si l'élément contient du contenu significatif
                text_content = element.get_text(strip=True)
                
                # Ignorer les éléments avec beaucoup de contenu textuel 
                # (probablement du contenu principal mal classé)
                if len(text_content) > 1000 and selector not in ['.ads', '.advertisement', '.cookie-notice', '.popup', '.modal']:
                    # Ne pas supprimer - contient trop de contenu pour être juste un élément de navigation
                    continue
                
                element.decompose()
        
        # Supprimer tous les scripts
        for script in soup.find_all('script'):
            script.decompose()
        
        # Supprimer tous les styles CSS
        for style in soup.find_all('style'):
            style.decompose()
        
        # Supprimer tous les noscript
        for noscript in soup.find_all('noscript'):
            noscript.decompose()
            
        # Supprimer tous les iframes
        for iframe in soup.find_all('iframe'):
            iframe.decompose()
            
        # Supprimer les attributs de style, onclick, onload, etc.
        for tag in soup.find_all(True):
            # Créer une liste des attributs à supprimer
            attrs_to_remove = []
            for attr in tag.attrs:
                # Supprimer les attributs de style
                if attr == 'style':
                    attrs_to_remove.append(attr)
                # Supprimer les gestionnaires d'événements JavaScript (onclick, onload, etc.)
                elif attr.startswith('on'):
                    attrs_to_remove.append(attr)
                # Supprimer les classes qui pourraient indiquer des scripts/publicités
                elif attr == 'class':
                    classes = tag.get('class', [])
                    if any(cls in ' '.join(classes) for cls in ['js-', 'ad-', 'ads-', 'script-', 'tracking']):
                        attrs_to_remove.append(attr)
            
            # Supprimer les attributs identifiés
            for attr in attrs_to_remove:
                del tag[attr]
        
        return soup

    def detect_nav_by_content(self, soup: BeautifulSoup) -> None:
        """
        Détecte et supprime les éléments de navigation et barres latérales 
        en analysant leur contenu et leur position, de manière moins agressive.
        
        Args:
            soup: L'objet BeautifulSoup à nettoyer
        """
        # 1. Détecter les éléments qui contiennent de nombreux liens
        all_divs = soup.find_all(['div', 'section', 'ul', 'ol'])
        for element in all_divs:
            links = element.find_all('a')
            
            # Si un élément contient beaucoup de liens, c'est probablement un menu ou une barre latérale
            # Augmenté le seuil de 5 à 8 liens pour être moins agressif
            if len(links) > 8:
                # Vérifier si les liens sont courts (typique des menus)
                short_links = [link for link in links if len(link.get_text(strip=True)) < 20]
                
                # Augmenté le seuil de 70% à 85% pour être sûr que c'est vraiment un menu
                if len(short_links) > len(links) * 0.85:
                    # Vérifier s'il contient du texte informatif substantiel
                    text_content = element.get_text(strip=True)
                    # Si le contenu textuel est substantiel par rapport au nombre de liens, ne pas supprimer
                    if len(text_content) > len(links) * 50:  # En moyenne 50 caractères de contenu par lien
                        continue
                    element.decompose()
                    continue
            
            # Vérifier si c'est une liste de catégories, tags, etc.
            # Liste plus restreinte de termes pour être moins agressif
            list_terms = ['menu', 'navigation', 'liens', 'links']
            
            # Vérifier le texte de l'élément pour des indices, plus strict
            element_text = element.get_text().lower()
            if any(term in element_text for term in list_terms) and len(links) > 4:
                # Vérifier la proportion de texte vs liens
                if len(element_text) < 200:  # Seulement supprimer les petits éléments de navigation
                    element.decompose()
                continue
                
        # 2. Détecter les éléments par leur position (uniquement la première div)
        main_content = soup.find('body')
        if main_content:
            # Examiner seulement le premier enfant direct du body (souvent la navigation)
            # Réduit de 3 à 1 pour être moins agressif
            children = list(main_content.children)
            if children and len(children) > 0:
                child = children[0]
                if child.name in ['div', 'nav'] and not child.find(['h1', 'h2', 'article', 'p']):
                    # Vérifier si c'est probablement une navigation sans contenu substantiel
                    if child.find_all('a', limit=5) and len(child.get_text(strip=True)) < 200:
                        child.decompose()
                
            # Examiner uniquement le dernier enfant direct du body (souvent le footer)
            # Réduit à seulement le dernier enfant
            if len(children) > 0:
                child = children[-1]
                if child.name in ['div', 'footer'] and not child.find(['h1', 'h2', 'article']):
                    if 'copyright' in child.get_text().lower() or (
                        child.find_all('a', limit=3) and len(child.get_text(strip=True)) < 150):
                        child.decompose()
        
        # 3. Supprimer les éléments qui ont une largeur très réduite (sidebars)
        # Réduit de 40% à 25% pour être moins agressif
        for element in soup.find_all(True):
            if 'style' in element.attrs:
                style = element['style'].lower()
                if 'width' in style:
                    # Seulement si la largeur est très petite (moins de 25%)
                    width_match = re.search(r'width\s*:\s*(\d+)%', style)
                    if width_match and int(width_match.group(1)) < 25:
                        # Vérifier qu'il s'agit bien d'un élément de navigation
                        if element.find_all('a', limit=4) and not element.find(['p', 'article']) and len(element.get_text(strip=True)) < 300:
                            element.decompose()

    def clean_html(self, html_content: str) -> str:
        """
        Nettoie le HTML en utilisant readability-lxml pour extraire le contenu principal.
        Version moins agressive pour préserver plus de contenu original.
        
        Args:
            html_content: Le contenu HTML brut
            
        Returns:
            Le HTML nettoyé avec le contenu principal
        """
        try:
            # Parser le HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Récupérer la longueur du contenu original pour analyse
            original_content_length = len(soup.get_text(strip=True))
            
            # Supprimer les headers, footers et autres éléments non désirés
            soup = self.remove_headers_footers(soup)
            
            # Récupérer la longueur du contenu après première passe de nettoyage
            post_header_footer_length = len(soup.get_text(strip=True))
            
            # Si on a déjà perdu plus de 30% du contenu, on ne fait pas de détection avancée
            # qui risquerait de trop supprimer de contenu
            if post_header_footer_length > original_content_length * 0.7:
                # Détection avancée des éléments de navigation par leur contenu
                self.detect_nav_by_content(soup)
            
            # Extraire le titre
            title = soup.title.string if soup.title else "Sans titre"
            
            # Utiliser Readability pour extraire le contenu principal
            doc = Document(html_content)
            clean_html = doc.summary()
            readability_title = doc.title()
            
            # Si le titre de Readability est plus informatif, l'utiliser
            if readability_title and len(readability_title) > len(title):
                title = readability_title
            
            # Parser le HTML nettoyé par Readability
            clean_soup = BeautifulSoup(clean_html, 'html.parser')
            
            # Récupérer la longueur du contenu extrait par Readability
            readability_content_length = len(clean_soup.get_text(strip=True))
            
            # Nettoyer aussi les headers et footers du contenu extrait par Readability
            clean_soup = self.remove_headers_footers(clean_soup)
            
            # Appliquer la détection avancée uniquement si le contenu est conséquent
            # et on ne veut pas trop perdre de contenu
            if readability_content_length > 1000:
                self.detect_nav_by_content(clean_soup)
            
            # Vérifier si le contenu extrait est suffisant
            clean_text = clean_soup.get_text()
            if len(clean_text) < 500:  # Si moins de 500 caractères, c'est probablement incomplet
                # Extraire du contenu supplémentaire
                additional_content = self.extract_additional_content(soup)
                if additional_content:
                    # Ajouter ce contenu au HTML nettoyé
                    additional_soup = BeautifulSoup(additional_content, 'html.parser')
                    
                    # Nettoyer également ce contenu supplémentaire
                    additional_soup = self.remove_headers_footers(additional_soup)
                    self.detect_nav_by_content(additional_soup)
                    
                    # Créer un nouvel élément div pour contenir le contenu supplémentaire
                    div = BeautifulSoup("<div class='additional-content'></div>", 'html.parser')
                    div_tag = div.div
                    
                    # Ajouter chaque élément de contenu supplémentaire
                    for element in additional_soup.children:
                        if element.name:  # Ignorer les nœuds de texte
                            div_tag.append(element)
                    
                    clean_soup.body.append(div_tag)
                    clean_html = str(clean_soup)
            
            # Construire un HTML propre avec le titre et le contenu
            full_html = f"<html><head><title>{title}</title></head><body><h1>{title}</h1>{clean_html}</body></html>"
            
            return full_html
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du HTML: {str(e)}")
            # En cas d'erreur, retourner le HTML original
            return html_content
    
    def get_text_content(self, html_content: str) -> str:
        """
        Extrait le texte brut à partir du HTML.
        
        Args:
            html_content: Le contenu HTML
            
        Returns:
            Le texte extrait sans balises HTML
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer les scripts et styles qui ne contiennent pas de contenu utile
        for script_or_style in soup(['script', 'style', 'meta', 'noscript']):
            script_or_style.decompose()
        
        # Obtenir le texte avec des sauts de ligne entre les éléments
        text = soup.get_text(separator='\n', strip=True)
        
        # Nettoyer les sauts de ligne multiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def scrape(self, url: str, clean: bool = True, extract_text: bool = False) -> Dict[str, Union[str, None]]:
        """
        Scrape une URL et retourne différentes versions du contenu.
        
        Args:
            url: L'URL à scraper
            clean: Si True, nettoie le HTML
            extract_text: Si True, extrait également le texte brut
            
        Returns:
            Dictionnaire contenant les différentes formes du contenu
        """
        result = {
            "url": url,
            "raw_html": None,
            "clean_html": None,
            "text_content": None,
            "title": None,
        }
        
        # Récupération du HTML
        html_content = self.fetch_url(url)
        if not html_content:
            return result
        
        result["raw_html"] = html_content
        
        # Extraction du titre
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result["title"] = soup.title.string.strip() if soup.title else None
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du titre: {str(e)}")
            pass
        
        # Nettoyage du HTML si demandé
        if clean:
            result["clean_html"] = self.clean_html(html_content)
        
        # Extraction du texte si demandé
        if extract_text:
            if result["clean_html"]:
                result["text_content"] = self.get_text_content(result["clean_html"])
            else:
                result["text_content"] = self.get_text_content(html_content)
        
        return result


# Fonction pratique pour une utilisation rapide
def scrape_url(url: str, clean: bool = True, extract_text: bool = False) -> Dict[str, Union[str, None]]:
    """
    Fonction utilitaire pour scraper rapidement une URL.
    
    Args:
        url: L'URL à scraper
        clean: Si True, nettoie le HTML
        extract_text: Si True, extrait également le texte brut
        
    Returns:
        Dictionnaire contenant les différentes formes du contenu
    """
    scraper = WebScraper()
    return scraper.scrape(url, clean, extract_text) 