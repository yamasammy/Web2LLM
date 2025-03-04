"""
Modèles de données pour l'API.
"""
from typing import List, Optional, Dict, Union, Any
from pydantic import BaseModel, HttpUrl, validator, Field


class ScrapeRequest(BaseModel):
    """Modèle pour une requête de scraping."""
    url: str = Field(..., description="URL à scraper")
    save: bool = Field(False, description="Sauvegarder le résultat en fichier Markdown")
    filename: Optional[str] = Field(None, description="Nom du fichier pour la sauvegarde")
    clean: bool = Field(True, description="Nettoyer le HTML avant conversion")

    @validator('url')
    def url_must_be_valid(cls, v):
        """Validation de l'URL."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL doit commencer par http:// ou https://')
        return v


class MultipleScrapeRequest(BaseModel):
    """Modèle pour une requête de scraping multiple."""
    urls: List[str] = Field(..., description="Liste d'URLs à scraper")
    save: bool = Field(True, description="Sauvegarder les résultats en fichiers Markdown")
    
    @validator('urls')
    def urls_must_be_valid(cls, v):
        """Validation des URLs."""
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'URL {url} doit commencer par http:// ou https://')
        return v


class ScrapeResponse(BaseModel):
    """Modèle pour la réponse de scraping."""
    url: str = Field(..., description="URL scrapée")
    title: Optional[str] = Field(None, description="Titre de la page")
    markdown: Optional[str] = Field(None, description="Contenu en Markdown")
    saved: bool = Field(False, description="Indique si le fichier a été sauvegardé")
    saved_path: Optional[str] = Field(None, description="Chemin du fichier sauvegardé")
    success: bool = Field(..., description="Indique si le scraping a réussi")
    error: Optional[str] = Field(None, description="Message d'erreur éventuel")


class MultipleScrapeResponse(BaseModel):
    """Modèle pour la réponse de scraping multiple."""
    total: int = Field(..., description="Nombre total d'URLs traitées")
    success: int = Field(..., description="Nombre d'URLs traitées avec succès")
    results: List[ScrapeResponse] = Field(..., description="Résultats pour chaque URL") 