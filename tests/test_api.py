"""Tests d'integration de sillage-api, a travers le reseau.

Ces tests ne s'executent pas en isolation : ils supposent que l'API et sa base
vectorielle tournent et sont joignables a l'adresse API_URL. C'est le principe
d'un test de l'artefact reel, tel qu'il tournera en production, et non du code
sur la machine de build.
"""

from __future__ import annotations

import requests

TIMEOUT = 30


def test_health(api_url: str) -> None:
    """Le service repond et se declare en bonne sante."""
    resp = requests.get(f"{api_url}/health", timeout=TIMEOUT)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_index(api_url: str) -> None:
    """L'indexation du corpus reussit et indexe au moins un article."""
    resp = requests.post(f"{api_url}/index", timeout=TIMEOUT * 4)
    assert resp.status_code == 200
    assert resp.json()["indexed"] > 0


def test_search_is_semantic(api_url: str) -> None:
    """Une requete ramene des resultats pertinents par le sens.

    On cherche "la voiture electrique en ville" : le meilleur resultat doit
    relever de la mobilite, meme si l'article ne reprend pas ces mots exacts.
    """
    requests.post(f"{api_url}/index", timeout=TIMEOUT * 4)
    resp = requests.post(
        f"{api_url}/search",
        json={"query": "la voiture electrique en ville", "limit": 3},
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 3
    assert results[0]["category"] == "mobilite"


def test_search_validates_input(api_url: str) -> None:
    """Une requete mal formee est rejetee proprement."""
    resp = requests.post(
        f"{api_url}/search",
        json={"query": "test", "limit": 999},
        timeout=TIMEOUT,
    )
    assert resp.status_code == 422


def test_digest_behaviour(api_url: str) -> None:
    """Le resume repond, ou signale proprement qu'il n'est pas configure.

    Selon le profil actif (digest-local, digest-remote, ou aucun), /digest
    produit un resume ou renvoie 503. Les deux sont des comportements valides.
    """
    requests.post(f"{api_url}/index", timeout=TIMEOUT * 4)
    resp = requests.post(
        f"{api_url}/digest",
        json={"query": "la voiture electrique en ville", "limit": 3},
        timeout=TIMEOUT * 4,
    )
    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        assert resp.json()["summary"]
