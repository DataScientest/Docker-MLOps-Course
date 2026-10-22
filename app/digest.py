"""Resume d'une selection d'articles via un modele de langage.

Le backend est joint par une API compatible OpenAI. Que le modele tourne en
local (Docker Model Runner) ou a distance (fournisseur type Groq), seule
l'adresse (DIGEST_URL) et la cle (DIGEST_KEY) changent : le code, lui, ne
bouge pas. C'est la demonstration concrete que la configuration sort de
l'image.
"""

from __future__ import annotations

from openai import OpenAI

from app import config

_SYSTEM = (
    "Tu es un assistant de veille media. On te donne des extraits d'articles "
    "de presse. Redige en francais un resume synthetique et neutre, en trois "
    "phrases maximum, de ce que ces articles disent du sujet demande."
)


def is_configured() -> bool:
    return bool(config.DIGEST_URL)


def summarize(query: str, articles: list[dict]) -> str:
    """Produit un resume des articles fournis, pour la requete donnee."""
    client = OpenAI(base_url=config.DIGEST_URL, api_key=config.DIGEST_KEY)

    corpus = "\n\n".join(
        f"- {a['title']} : {a['body']}" for a in articles
    )
    user = f"Sujet : {query}\n\nArticles :\n{corpus}"

    response = client.chat.completions.create(
        model=config.DIGEST_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()
