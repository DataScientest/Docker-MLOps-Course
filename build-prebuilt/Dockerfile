# syntax=docker/dockerfile:1
#
# Image PRE-CONSTRUITE de sillage-api, publiee par DataScientest sous
# ghcr.io/datascientest/sillage-api:1.0.0 et utilisee dans les chapitres 02 a 04.
#
# Elle tourne volontairement en ROOT, avec le cache des modeles dans
# /root/.cache/huggingface. C'est l'etat que le chapitre 05 viendra critiquer
# et ameliorer (passage en utilisateur non privilegie). Ne pas confondre avec
# le Dockerfile de production, a la racine du depot, que les apprenants ecrivent.
#
# Construire depuis la RACINE du depot :
#   docker build -f build-prebuilt/Dockerfile -t ghcr.io/datascientest/sillage-api:1.0.0 .
#   docker push ghcr.io/datascientest/sillage-api:1.0.0

FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY app/ ./app/
COPY data/ ./data/
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS final
# curl est requis pour que les apprenants testent /health depuis l'interieur
# du conteneur au chapitre 02 (docker exec ... curl localhost:8000/health).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl procps \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app /app
# Pas de USER : on reste root. Le cache ira dans /root/.cache/huggingface,
# emplacement attendu par le TP de persistance du chapitre 04.
ENV PATH="/app/.venv/bin:$PATH" \
    HF_HUB_DISABLE_XET=1
EXPOSE 8000
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
