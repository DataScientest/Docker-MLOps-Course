"""sillage-api : API de veille media.

Quatre points d'entree :
  GET  /health   liveness, ne depend d'aucun service externe
  POST /index    encode le corpus et l'indexe dans Qdrant
  POST /search   recherche semantique
  POST /digest   resume d'une selection d'articles via un modele de langage
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import models

from app import config, digest
from app.embeddings import Embedder
from app.store import Store

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("sillage")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Le sujet recherche.")
    limit: int = Field(3, ge=1, le=20, description="Nombre de resultats.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chargement du modele d'embeddings. Declenche le telechargement au premier
    # demarrage, dans le cache Hugging Face.
    logger.info("Chargement du modele d'embeddings '%s'...", config.EMBED_MODEL)
    app.state.embedder = Embedder()

    # Connexion a Qdrant, en mode best effort : on ne bloque pas le demarrage.
    app.state.store = Store()
    if app.state.store.ping():
        app.state.store.ensure_collection()
        logger.info("Qdrant joignable, collection prete.")
    else:
        logger.warning(
            "Qdrant n'est pas joignable au demarrage. L'API demarre quand meme ; "
            "les endpoints /index et /search echoueront tant que Qdrant est absent."
        )
    logger.info("sillage-api prete, en ecoute sur le port 8000.")
    yield


app = FastAPI(title="sillage-api", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    """Liveness. Ne depend d'aucun service externe, par conception."""
    return {"status": "ok"}


@app.post("/index")
def index() -> dict:
    """Encode le corpus fourni et l'indexe dans Qdrant."""
    try:
        articles = json.loads(config.DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(500, f"Corpus introuvable : {config.DATA_PATH}") from exc

    vectors = app.state.embedder.encode([a["body"] for a in articles])
    points = [
        models.PointStruct(id=a["id"], vector=v, payload=a)
        for a, v in zip(articles, vectors)
    ]
    try:
        app.state.store.ensure_collection()
        app.state.store.upsert(points)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Qdrant injoignable : {exc}") from exc

    return {"indexed": len(points)}


@app.post("/search")
def search(req: SearchRequest) -> dict:
    """Recherche semantique dans le corpus indexe."""
    vector = app.state.embedder.encode_one(req.query)
    try:
        hits = app.state.store.search(vector, req.limit)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Qdrant injoignable : {exc}") from exc

    return {
        "query": req.query,
        "results": [
            {
                "title": h.payload["title"],
                "category": h.payload.get("category"),
                "score": round(h.score, 4),
                "snippet": h.payload["body"][:160],
            }
            for h in hits
        ],
    }


@app.post("/digest")
def digest_endpoint(req: SearchRequest) -> dict:
    """Resume d'une selection d'articles pertinents pour la requete."""
    if not digest.is_configured():
        raise HTTPException(
            503,
            "Resume non configure : definissez DIGEST_URL (modele local ou distant).",
        )

    vector = app.state.embedder.encode_one(req.query)
    try:
        hits = app.state.store.search(vector, req.limit)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Qdrant injoignable : {exc}") from exc

    articles = [{"title": h.payload["title"], "body": h.payload["body"]} for h in hits]
    summary = digest.summarize(req.query, articles)
    return {
        "query": req.query,
        "summary": summary,
        "sources": [a["title"] for a in articles],
    }
