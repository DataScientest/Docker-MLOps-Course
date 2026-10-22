"""Encodage de texte en vecteurs.

On s'appuie sur fastembed, qui execute le modele all-MiniLM-L6-v2 au format
ONNX sur CPU, sans dependance a torch. Le modele est telecharge au premier
usage dans le cache Hugging Face, ce qui rend la question du cache (chapitre
sur la persistance) tres concrete : sans volume monte, ce telechargement est
rejoue a chaque demarrage.
"""

from __future__ import annotations

import os

# Desactive le client Xet (hf-xet / CAS server) de Hugging Face Hub, qui echoue
# sur les requetes non authentifiees (erreur de reconstruction CAS).
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from fastembed import TextEmbedding

from app import config


class Embedder:
    """Enveloppe minimale autour du modele d'embeddings."""

    def __init__(self, model_name: str = config.EMBED_MODEL) -> None:
        # Le constructeur declenche le telechargement du modele s'il n'est pas
        # deja dans le cache.
        self._model = TextEmbedding(model_name=model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode une liste de textes en liste de vecteurs."""
        return [vector.tolist() for vector in self._model.embed(texts)]

    def encode_one(self, text: str) -> list[float]:
        """Encode un seul texte en un vecteur."""
        return self.encode([text])[0]
