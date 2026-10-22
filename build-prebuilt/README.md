# Image pré-construite `sillage-api:1.0.0`

Ce dossier sert **uniquement à l'équipe pédagogique**, pas aux apprenants.

Les chapitres 02, 03 et 04 s'appuient sur une image déjà construite et publiée,
`ghcr.io/datascientest/sillage-api:1.0.0`, que les apprenants se contentent de
`docker pull`. Ils n'ont pas encore appris à écrire un Dockerfile (c'est l'objet
du chapitre 05), donc on la leur fournit toute faite.

## Caractéristiques voulues

Cette image reproduit l'état « avant optimisation » que le chapitre 05 critique :

- elle tourne en **root** (d'où le cache modèle dans `/root/.cache/huggingface`,
  emplacement attendu par le TP de persistance du chapitre 04) ;
- elle embarque **curl** (le chapitre 02 fait tester `/health` depuis l'intérieur
  du conteneur avec `docker exec ... curl`) ;
- elle respecte les contrats de l'application : sortie en code 1 avec message
  clair si `QDRANT_URL` est absente, démarrage dégradé si Qdrant est injoignable.

## Construire et publier

Depuis la **racine** du dépôt (le contexte de build doit contenir `app/`,
`data/`, `pyproject.toml` et `uv.lock`) :

```shell
docker build -f build-prebuilt/Dockerfile -t ghcr.io/datascientest/sillage-api:1.0.0 .
docker push ghcr.io/datascientest/sillage-api:1.0.0
```

Rendez ensuite le paquet **public** dans les réglages du package GHCR, pour que
les apprenants puissent le `pull` sans authentification.
