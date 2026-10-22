# syntax=docker/dockerfile:1
# Conteneur de tests : une image legere qui interroge l'API par le reseau.
# Il n'embarque pas l'application, seulement de quoi lancer pytest contre elle.
# C'est ce qui permet de garder l'image de production depourvue d'outils de test.
FROM python:3.12-slim

RUN pip install --no-cache-dir pytest==8.3.* requests==2.32.*

WORKDIR /tests
COPY tests/ ./

# API_URL est fournie par Compose (http://api:8000). Les tests attendent que
# l'API soit joignable ; le depends_on: service_healthy s'en charge cote Compose.
ENTRYPOINT ["pytest", "-v"]
