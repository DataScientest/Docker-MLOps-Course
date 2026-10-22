# syntax=docker/dockerfile:1

# ---- Etage 1 : build ----
# On installe les dependances dans un environnement isole. Cet etage contient
# uv et les fichiers intermediaires ; il ne sera pas livre.
FROM python:3.12-slim AS build

# Binaire uv recupere depuis son image officielle, a une version figee.
COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /bin/uv

# Reglages uv adaptes au conteneur.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# D'abord les dependances SEULES : cette couche est mise en cache tant que
# pyproject.toml et uv.lock ne changent pas. Le code, qui change souvent,
# vient apres.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Ensuite seulement, le code et le corpus.
COPY app/ ./app/
COPY data/ ./data/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- Etage 2 : image finale ----
# On repart d'une base propre et minimale. uv n'y existe pas.
FROM python:3.12-slim AS final

# curl est necessaire au HEALTHCHECK.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Un utilisateur non privilegie : on ne tourne jamais en root en production.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# On copie l'environnement construit a l'etage 1, et le code. Rien d'autre.
COPY --from=build --chown=appuser:appuser /app /app

# L'environnement virtuel dans le PATH, et le cache des modeles dans le dossier
# de l'utilisateur (on n'est plus root, donc plus de /root/.cache).
ENV PATH="/app/.venv/bin:$PATH" \
    HF_HOME=/home/appuser/.cache/huggingface

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
