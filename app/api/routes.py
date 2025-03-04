"""
Routes de l'API.
"""
import os
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse

from app.main import WebToMarkdown
from app.api.models import (
    ScrapeRequest, ScrapeResponse, 
    MultipleScrapeRequest, MultipleScrapeResponse
)

router = APIRouter()
processor = WebToMarkdown()


@router.post("/scrape", response_model=ScrapeResponse, tags=["Scraping"])
async def scrape_url(request: ScrapeRequest) -> Dict[str, Any]:
    """
    Scrape une URL et convertit le contenu en Markdown.
    
    - **url**: L'URL à scraper
    - **save**: Si True, sauvegarde le résultat en fichier Markdown
    - **filename**: Nom du fichier pour la sauvegarde (optionnel)
    - **clean**: Si True, nettoie le HTML avant conversion
    
    Retourne le contenu en Markdown et d'autres informations.
    """
    result = processor.process_url(
        url=request.url, 
        save=request.save, 
        filename=request.filename
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du scraping: {result.get('error', 'Erreur inconnue')}"
        )
    
    return result


@router.post("/scrape/save", tags=["Scraping"])
async def scrape_and_save(request: ScrapeRequest) -> Dict[str, Any]:
    """
    Scrape une URL, convertit en Markdown et sauvegarde dans un fichier.
    
    - **url**: L'URL à scraper
    - **filename**: Nom du fichier pour la sauvegarde (optionnel)
    - **clean**: Si True, nettoie le HTML avant conversion
    
    Retourne le chemin du fichier sauvegardé et d'autres informations.
    """
    # Force la sauvegarde
    request.save = True
    
    result = processor.process_url(
        url=request.url, 
        save=True, 
        filename=request.filename
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du scraping: {result.get('error', 'Erreur inconnue')}"
        )
    
    if not result["saved"] or not result["saved_path"]:
        raise HTTPException(
            status_code=500, 
            detail="Échec de l'enregistrement du fichier"
        )
    
    return {
        "success": True,
        "file_path": result["saved_path"],
        "title": result["title"],
        "url": result["url"]
    }


@router.post("/scrape/download", tags=["Scraping"])
async def scrape_and_download(request: ScrapeRequest) -> FileResponse:
    """
    Scrape une URL, convertit en Markdown et renvoie directement le fichier.
    
    - **url**: L'URL à scraper
    - **filename**: Nom du fichier pour la sauvegarde (optionnel)
    - **clean**: Si True, nettoie le HTML avant conversion
    
    Retourne directement le fichier Markdown pour téléchargement.
    """
    # Force la sauvegarde
    request.save = True
    
    result = processor.process_url(
        url=request.url, 
        save=True, 
        filename=request.filename
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du scraping: {result.get('error', 'Erreur inconnue')}"
        )
    
    if not result["saved"] or not result["saved_path"]:
        raise HTTPException(
            status_code=500, 
            detail="Échec de l'enregistrement du fichier"
        )
    
    return FileResponse(
        path=result["saved_path"],
        media_type="text/markdown",
        filename=os.path.basename(result["saved_path"])
    )


@router.post("/scrape/multiple", response_model=MultipleScrapeResponse, tags=["Scraping multiple"])
async def scrape_multiple_urls(
    request: MultipleScrapeRequest, 
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Scrape plusieurs URLs en parallèle.
    
    - **urls**: Liste d'URLs à scraper
    - **save**: Si True, sauvegarde les résultats en fichiers Markdown
    
    Retourne les résultats pour toutes les URLs.
    """
    if len(request.urls) > 10:
        # Pour de nombreuses URLs, traiter en arrière-plan
        background_tasks.add_task(
            processor.process_multiple_urls, 
            urls=request.urls, 
            save=request.save
        )
        return {
            "total": len(request.urls),
            "success": None,  # Inconnu car traitement en arrière-plan
            "results": [],
            "message": f"Traitement de {len(request.urls)} URLs en arrière-plan"
        }
    
    # Pour peu d'URLs, traiter immédiatement
    result = processor.process_multiple_urls(
        urls=request.urls, 
        save=request.save
    )
    
    return result 