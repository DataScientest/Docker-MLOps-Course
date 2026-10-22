"""Acces a la base vectorielle Qdrant.

La connexion est tentee au demarrage mais n'est jamais bloquante : si Qdrant
est injoignable, l'application demarre quand meme (l'endpoint /health reste
vert), et les operations qui ont besoin de la base echouent proprement au
moment ou on les appelle. C'est ce qui permet, dans les premiers chapitres,
de lancer l'API sans avoir encore mis en place le reseau vers Qdrant.
"""

from __future__ import annotations

import logging

from qdrant_client import QdrantClient, models

from app import config

logger = logging.getLogger("sillage.store")


class Store:
    def __init__(self, url: str = config.QDRANT_URL) -> None:
        self._client = QdrantClient(url=url, timeout=5.0)

    def ensure_collection(self) -> None:
        """Cree la collection si elle n'existe pas deja."""
        existing = {c.name for c in self._client.get_collections().collections}
        if config.COLLECTION not in existing:
            self._client.create_collection(
                collection_name=config.COLLECTION,
                vectors_config=models.VectorParams(
                    size=config.EMBED_DIM,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info("Collection '%s' creee.", config.COLLECTION)

    def ping(self) -> bool:
        """Verifie que Qdrant repond, sans lever d'exception."""
        try:
            self._client.get_collections()
            return True
        except Exception as exc:  # noqa: BLE001 - on veut tout attraper ici
            logger.warning("Qdrant injoignable : %s", exc)
            return False

    def upsert(self, points: list[models.PointStruct]) -> None:
        self._client.upsert(collection_name=config.COLLECTION, points=points)

    def search(self, vector: list[float], limit: int):
        result = self._client.query_points(
            collection_name=config.COLLECTION,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return result.points

    def count(self) -> int:
        return self._client.count(collection_name=config.COLLECTION).count
