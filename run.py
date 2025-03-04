#!/usr/bin/env python
"""
Script d'entrée pour le Web Scraper et Convertisseur Markdown.
"""
import os
import argparse
import sys
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()


def parse_args():
    """Analyse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Web Scraper et Convertisseur Markdown"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande de scraping
    scrape_parser = subparsers.add_parser("scrape", help="Scraper une URL")
    scrape_parser.add_argument("url", help="URL à scraper")
    scrape_parser.add_argument(
        "--save", action="store_true", help="Sauvegarder en fichier Markdown"
    )
    scrape_parser.add_argument(
        "--output", help="Nom du fichier de sortie", default=None
    )
    scrape_parser.add_argument(
        "--dir", help="Répertoire de sortie", 
        default=os.getenv("OUTPUT_DIR", "./output")
    )
    
    # Commande de démarrage du serveur API
    api_parser = subparsers.add_parser("api", help="Démarrer le serveur API")
    api_parser.add_argument(
        "--host", help="Hôte à écouter", 
        default=os.getenv("API_HOST", "0.0.0.0")
    )
    api_parser.add_argument(
        "--port", help="Port à écouter", type=int,
        default=int(os.getenv("API_PORT", 8000))
    )
    
    # Commande d'information sur la version
    subparsers.add_parser("version", help="Afficher la version")
    
    return parser.parse_args()


def main():
    """Fonction principale."""
    args = parse_args()
    
    if args.command == "scrape":
        from app.main import WebToMarkdown
        
        processor = WebToMarkdown(output_dir=args.dir)
        result = processor.process_url(args.url, save=args.save, filename=args.output)
        
        if result["success"]:
            print(f"Titre: {result['title']}")
            print("\nContenu Markdown:")
            print("-------------------")
            # Afficher un extrait du markdown
            print(result["markdown"][:500] + "..." if len(result["markdown"]) > 500 else result["markdown"])
            
            if result["saved"]:
                print(f"\nFichier sauvegardé: {result['saved_path']}")
        else:
            print(f"Erreur: {result['error']}")
            return 1
    
    elif args.command == "api":
        os.environ["API_HOST"] = args.host
        os.environ["API_PORT"] = str(args.port)
        
        from app.api.server import start
        print(f"Démarrage du serveur API sur {args.host}:{args.port}")
        start()
    
    elif args.command == "version":
        from app import __version__
        print(f"Web Scraper et Convertisseur Markdown v{__version__}")
    
    else:
        from app import __version__
        print(f"Web Scraper et Convertisseur Markdown v{__version__}")
        print("Utilisez -h pour afficher l'aide")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 