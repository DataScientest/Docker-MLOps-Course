"""Configuration des tests.

Les tests interrogent l'API par le reseau, a l'adresse donnee par la variable
d'environnement API_URL. En local, c'est http://localhost:8000 ; dans un
conteneur de test sur le reseau Docker, c'est http://sillage-api:8000.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def api_url() -> str:
    return os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
