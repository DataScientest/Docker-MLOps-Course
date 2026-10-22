# Sillage — projet fil rouge du cours Docker

Bienvenue sur le dépôt du projet **Sillage**, le fil rouge du module Docker du
parcours AI Engineer. Vous allez le faire grandir chapitre après chapitre,
jusqu'à savoir le conteneuriser, l'orchestrer, le tester et le publier.

## Le contexte

*Sillage* est une jeune entreprise de veille média. Ses clients reçoivent chaque
jour bien plus d'articles de presse qu'ils ne peuvent en lire. Ils veulent
retrouver, dans ce flux, ceux qui parlent de leur sujet, même quand l'article
n'emploie pas les mots auxquels ils auraient pensé, et en obtenir un résumé.

L'équipe a écrit `sillage-api`, une API FastAPI avec quatre points d'entrée :

| Point d'entrée | Rôle |
|---|---|
| `GET /health` | Indique si le service est opérationnel |
| `POST /index` | Encode le corpus d'articles et l'indexe |
| `POST /search` | Recherche les articles pertinents pour une requête |
| `POST /digest` | Produit un résumé d'une sélection d'articles |

Le service s'appuie sur un petit modèle d'embeddings (`all-MiniLM-L6-v2`,
exécuté sur CPU) et sur une base vectorielle (Qdrant).

> **Le sujet du cours n'est pas Sillage.** Le code de l'application vous est
> fourni, vous n'aurez jamais à écrire de Python ici. Sillage est un prétexte
> réaliste : toute la difficulté du module est dans le Docker, aucune dans le
> métier.

## Prérequis

- Linux, bash, Git, les bases de Docker (acquises dans le cours amont).
- Une VM ou une machine avec Docker Engine. Pas besoin de GPU : tout tourne
  sur CPU.

## Démarrer

Ce dépôt se **forke** : vous travaillez sur votre copie, ce qui vous permet de
committer votre travail et, au chapitre 7, de publier votre image via votre
propre chaîne d'intégration.

```shell
# après avoir forké depuis l'interface GitHub
git clone https://github.com/<votre-utilisateur>/Docker-MLOps-Course.git
cd Docker-MLOps-Course
```

Le dépôt propose **une branche par chapitre**, `chapitre-01` à `chapitre-08`,
contenant l'état du projet au début du chapitre concerné. Si un exercice vous
résiste, repartez de la branche suivante sans rester bloqué.

```shell
git checkout chapitre-02
```

## Structure du projet

```text
.
├── app/                  code de l'API (vous n'avez pas à le modifier)
│   ├── config.py         configuration par l'environnement
│   ├── embeddings.py     encodage de texte en vecteurs (fastembed, CPU)
│   ├── store.py          accès à la base vectorielle Qdrant
│   ├── digest.py         résumé via un modèle de langage (API compatible OpenAI)
│   └── main.py           l'application FastAPI et ses endpoints
├── data/
│   └── articles.json     ~200 articles fictifs (corpus de démonstration)
├── tests/                tests d'intégration, exécutés à travers le réseau
├── pyproject.toml        dépendances du projet
└── uv.lock               versions figées, pour des builds reproductibles
```

Les fichiers Docker (`Dockerfile`, `compose.yaml`, workflow CI) n'existent pas
au début : **c'est vous qui les écrirez**, à partir du chapitre 5.

## Note sur le corpus

Le corpus `data/articles.json` est un jeu de **fixtures** : il accompagne
l'application comme donnée de démonstration et voyage avec l'image. C'est
acceptable parce qu'il est petit et stable. Un vrai jeu de données, volumineux
et évolutif, n'aurait pas sa place dans l'image : il vivrait dans un volume ou
un stockage objet, comme le cours l'explique au chapitre sur la persistance.

Pour le régénérer :

```shell
python scripts/gen_articles.py
```
