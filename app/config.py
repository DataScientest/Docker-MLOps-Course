"""Configuration de sillage-api.

Toute la configuration vient de l'environnement. C'est volontaire : l'image
est un artefact figé, et c'est la configuration qui l'adapte a son
environnement d'execution (developpement, test, production). Aucune valeur
sensible n'est ecrite en dur ici.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# QDRANT_URL est obligatoire. Sans elle, l'application ne peut pas savoir ou
# se trouve sa base vectorielle. On echoue immediatement, avec un message
# clair, plutot que de demarrer dans un etat inutilisable.
# --------------------------------------------------------------------------
QDRANT_URL = os.environ.get("QDRANT_URL")
if not QDRANT_URL:
    print(
        "ERROR: la variable d'environnement QDRANT_URL est obligatoire. "
        "Exemple : QDRANT_URL=http://qdrant:6333",
        file=sys.stderr,
    )
    sys.exit(1)

# Collection Qdrant qui stocke les articles encodes.
COLLECTION = os.environ.get("SILLAGE_COLLECTION", "articles")

# Modele d'embeddings. all-MiniLM-L6-v2 produit des vecteurs de dimension 384,
# tourne tres bien sur CPU, et pese environ 90 Mo. Il est telecharge au premier
# demarrage dans le cache Hugging Face (voir HF_HOME dans le Dockerfile).
EMBED_MODEL = os.environ.get(
    "SILLAGE_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
EMBED_DIM = 384

# Corpus d'articles fourni avec l'application.
DATA_PATH = Path(os.environ.get("SILLAGE_DATA", "data/articles.json"))

# --------------------------------------------------------------------------
# Configuration du resume (/digest). Optionnelle : si DIGEST_URL n'est pas
# definie, l'endpoint /digest repond 503 et le reste de l'API fonctionne.
# Les deux backends (modele local via Model Runner, ou API distante type Groq)
# exposent une API compatible OpenAI, donc seule change l'adresse et la cle.
# --------------------------------------------------------------------------
DIGEST_URL = os.environ.get("DIGEST_URL")
DIGEST_MODEL = os.environ.get("DIGEST_MODEL", "ai/smollm2")


def _read_digest_key() -> str:
    """Lit la cle d'API du backend de resume.

    On cherche d'abord un secret monte en fichier (mecanisme `secrets` de
    Compose, le plus sur), puis a defaut une variable d'environnement, puis
    on retombe sur une valeur factice suffisante pour un modele local qui
    n'exige aucune authentification.
    """
    secret_file = Path("/run/secrets/groq_api_key")
    if secret_file.exists():
        return secret_file.read_text(encoding="utf-8").strip()
    return os.environ.get("GROQ_API_KEY", "sk-no-key-required")


DIGEST_KEY = _read_digest_key()
