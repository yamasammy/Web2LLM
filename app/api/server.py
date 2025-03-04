"""
Configuration du serveur FastAPI.
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app import __version__
from app.api.routes import router

# Chargement des variables d'environnement
load_dotenv()

# Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Création de l'application FastAPI
app = FastAPI(
    title="Web Scraper et Convertisseur Markdown API",
    description="""
    API pour scraper des sites web, nettoyer le contenu et le convertir en Markdown.
    Idéal pour préparer des données pour les systèmes d'IA.
    """,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour la production, limitez aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(router, prefix="/api")

# Gestionnaire d'exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global des exceptions."""
    logging.error(f"Exception non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erreur interne du serveur: {str(exc)}"}
    )

# Route racine
@app.get("/", tags=["Informations"])
async def root():
    """Page d'accueil de l'API."""
    return {
        "name": "Web Scraper et Convertisseur Markdown API",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Vérification de la santé de l'API
@app.get("/health", tags=["Informations"])
async def health_check():
    """Vérification de la santé de l'API."""
    return {"status": "ok", "version": __version__}


def start():
    """Démarrage du serveur avec uvicorn."""
    import uvicorn
    uvicorn.run(
        "app.api.server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )


if __name__ == "__main__":
    start() 