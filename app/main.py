"""
Module principal de l'application Web Scraper et Convertisseur Markdown.
"""
import os
import logging
import time
from typing import Dict, Optional, Union, List
from urllib.parse import urlparse
import pathlib
from dotenv import load_dotenv

from app.scraper.scraper import WebScraper
from app.converter.converter import MarkdownConverter

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
DEFAULT_FILENAME = os.getenv('DEFAULT_FILENAME', 'scraped_content')

class WebToMarkdown:
    """Classe principale combinant le scraping et la conversion en Markdown."""
    
    def __init__(self, output_dir: str = OUTPUT_DIR):
        """
        Initialise l'outil.
        
        Args:
            output_dir: Répertoire où sauvegarder les fichiers Markdown
        """
        self.scraper = WebScraper()
        self.converter = MarkdownConverter()
        self.output_dir = output_dir
        
        # S'assurer que le répertoire de sortie existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_filename(self, url: str, title: Optional[str] = None, extension: str = '.md') -> str:
        """
        Génère un nom de fichier valide à partir de l'URL ou du titre.
        
        Args:
            url: L'URL de la page
            title: Le titre de la page (optionnel)
            extension: L'extension du fichier (.md par défaut)
            
        Returns:
            Un nom de fichier valide
        """
        if title:
            # Nettoyer le titre pour en faire un nom de fichier valide
            safe_title = "".join([c if c.isalnum() or c in [' ', '-', '_'] else "_" for c in title])
            safe_title = safe_title.strip()
            filename = safe_title[:100]  # Limiter la longueur mais permettre des noms plus longs
        else:
            # Utiliser l'URL
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc
            path = parsed_url.path.strip('/')
            filename = f"{hostname}_{path}".replace('/', '_')
        
        # Remplacer les espaces par des tirets
        filename = filename.replace(' ', '-')
        
        # S'assurer que le nom se termine par l'extension spécifiée
        if not filename.endswith(extension):
            filename += extension
        
        return filename
    
    def save_raw_html(self, html_content: str, filepath: str) -> bool:
        """
        Sauvegarde le contenu HTML brut dans un fichier.
        
        Args:
            html_content: Le contenu HTML
            filepath: Chemin où sauvegarder le fichier
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # S'assurer que le répertoire existe
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Contenu HTML sauvegardé avec succès dans {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier HTML: {str(e)}")
            return False
    
    def process_url(self, url: str, save: bool = False, 
                  filename: Optional[str] = None) -> Dict[str, Union[str, None, bool]]:
        """
        Traite une URL: scraping, nettoyage et conversion en Markdown.
        
        Args:
            url: L'URL à traiter
            save: Si True, sauvegarde le résultat dans un fichier
            filename: Nom du fichier pour la sauvegarde
            
        Returns:
            Dictionnaire avec les résultats et le statut
        """
        result = {
            "url": url,
            "title": None,
            "markdown": None,
            "saved": False,
            "saved_path": None,
            "success": False,
            "error": None,
            "html_saved": False,
            "html_saved_path": None
        }
        
        try:
            # Définir l'URL de base pour la conversion des liens relatifs
            self.converter.base_url = url
            
            # Scraper l'URL
            logger.info(f"Scraping de l'URL: {url}")
            scraped_data = self.scraper.scrape(url, clean=True, extract_text=True)
            
            # Stocker le titre
            result["title"] = scraped_data["title"]
            
            if not scraped_data["clean_html"]:
                result["error"] = "Impossible de récupérer ou nettoyer le contenu HTML"
                return result
            
            # Conversion en Markdown
            logger.info("Conversion du HTML en Markdown")
            markdown_content = self.converter.html_to_markdown(
                scraped_data["clean_html"], url)
            
            # Vérifier si la conversion a produit un résultat significatif
            if not markdown_content or len(markdown_content) < 100:
                logger.warning("Conversion en Markdown insuffisante, tentative avec le texte brut")
                
                # Si le texte brut est disponible, l'utiliser comme alternative
                if scraped_data["text_content"]:
                    markdown_content = scraped_data["text_content"]
                else:
                    # Dernière tentative: extraire le texte à partir du HTML nettoyé
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(scraped_data["clean_html"], 'html.parser')
                    markdown_content = soup.get_text(separator='\n\n', strip=True)
            
            # Mise à jour du résultat
            result["markdown"] = markdown_content
            result["success"] = True
            
            # Sauvegarde si demandée
            if save:
                # Générer un nom de fichier si non spécifié
                if not filename:
                    filename = self.generate_filename(url, result["title"])
                # S'assurer que l'extension est .md
                elif not filename.endswith('.md'):
                    filename += '.md'
                
                filepath = os.path.join(self.output_dir, filename)
                
                # Enregistrer le fichier Markdown
                saved = self.converter.save_markdown(markdown_content, filepath)
                result["saved"] = saved
                result["saved_path"] = filepath if saved else None
                
                # Si la conversion en Markdown n'est pas optimale, sauvegarder aussi le HTML
                if len(markdown_content) < 500 or "<" in markdown_content:
                    html_filename = filename.replace('.md', '.html')
                    html_filepath = os.path.join(self.output_dir, html_filename)
                    html_saved = self.save_raw_html(scraped_data["clean_html"], html_filepath)
                    result["html_saved"] = html_saved
                    result["html_saved_path"] = html_filepath if html_saved else None
                    
                    if html_saved:
                        logger.info(f"Le HTML a été sauvegardé en complément dans {html_filepath}")
            
            return result
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'URL {url}: {str(e)}")
            result["error"] = str(e)
            
            # En cas d'erreur, tenter de sauvegarder le HTML brut si disponible
            if save and scraped_data and "raw_html" in scraped_data and scraped_data["raw_html"]:
                if not filename:
                    filename = self.generate_filename(url, result["title"], '.html')
                else:
                    filename = filename.replace('.md', '.html')
                
                html_filepath = os.path.join(self.output_dir, filename)
                html_saved = self.save_raw_html(scraped_data["raw_html"], html_filepath)
                
                result["html_saved"] = html_saved
                result["html_saved_path"] = html_filepath if html_saved else None
                
                if html_saved:
                    logger.info(f"Sauvegarde de secours du HTML brut dans {html_filepath}")
            
            return result
    
    def process_multiple_urls(self, urls: List[str], save: bool = True) -> Dict[str, List[Dict]]:
        """
        Traite plusieurs URLs en parallèle.
        
        Args:
            urls: Liste d'URLs à traiter
            save: Si True, sauvegarde les résultats
            
        Returns:
            Dictionnaire contenant les résultats pour chaque URL
        """
        results = []
        
        for url in urls:
            result = self.process_url(url, save=save)
            results.append(result)
        
        return {
            "total": len(urls),
            "success": sum(1 for r in results if r["success"]),
            "results": results
        }


# Fonction pour une utilisation rapide en ligne de commande
def process_url(url: str, save: bool = False, filename: Optional[str] = None) -> Dict:
    """
    Fonction utilitaire pour traiter rapidement une URL.
    
    Args:
        url: L'URL à traiter
        save: Si True, sauvegarde le résultat
        filename: Nom du fichier pour la sauvegarde
        
    Returns:
        Dictionnaire avec les résultats
    """
    processor = WebToMarkdown()
    return processor.process_url(url, save, filename)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scraper et convertisseur Markdown")
    parser.add_argument("url", help="URL à scraper")
    parser.add_argument("--save", action="store_true", help="Sauvegarder en fichier Markdown")
    parser.add_argument("--output", help="Nom du fichier de sortie")
    parser.add_argument("--dir", help="Répertoire de sortie", default=OUTPUT_DIR)
    
    args = parser.parse_args()
    
    processor = WebToMarkdown(output_dir=args.dir)
    result = processor.process_url(args.url, save=args.save, filename=args.output)
    
    if result["success"]:
        print(f"Titre: {result['title']}")
        print("\nContenu Markdown:")
        print("-------------------")
        print(result["markdown"][:500] + "..." if len(result["markdown"]) > 500 else result["markdown"])
        
        if result["saved"]:
            print(f"\nFichier sauvegardé: {result['saved_path']}")
        if result["html_saved"]:
            print(f"\nFichier HTML sauvegardé: {result['html_saved_path']}")
    else:
        print(f"Erreur: {result['error']}")
        if result["html_saved"]:
            print(f"\nFichier HTML de secours sauvegardé: {result['html_saved_path']}") 