# Organisation des branches du dépôt

Ce fichier est une **note pour l'équipe pédagogique**, pas pour les apprenants.
Il décrit quel fichier doit être présent sur quelle branche.

## Principe

La branche `chapitre-NN` contient l'état du projet **au début du chapitre NN**,
c'est-à-dire à l'issue du chapitre précédent. Ce que l'apprenant écrit pendant
un chapitre est donc déjà présent sur la branche du chapitre suivant.

Rappel de ce qui est écrit par l'apprenant, et quand :
- **Chapitre 05** : il écrit le `Dockerfile` et le `.dockerignore`.
- **Chapitre 06** : il écrit les fichiers `compose*.yaml` et le `.env`.
- **Chapitre 07** : la chaîne d'intégration lui est **fournie**, et il écrit
  le `compose.prod.yaml` final.

## Matrice des fichiers par branche

Légende : ✅ présent · ⬚ absent (pas encore écrit à ce stade).

| Fichier / dossier | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `app/`, `data/`, `tests/*.py` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `pyproject.toml`, `uv.lock` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `README.md`, `.gitignore`, `scripts/` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `Dockerfile`, `.dockerignore` | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ✅ | ✅ | ✅ |
| `compose.yaml` + `.local`/`.remote` | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ✅ | ✅ |
| `.env.example`, `tests/Dockerfile` | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ✅ | ✅ |
| `.github/workflows/docker-ci.yml` | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ✅ | ✅ |
| `compose.prod.yaml` | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ⬚ | ✅ |

Les branches 01 à 05 sont donc **identiques** (le squelette seul). Les Docker
files apparaissent en 06, l'orchestration et la CI en 07, le compose de
production en 08.

Le dossier `build-prebuilt/` n'apparaît sur **aucune** branche apprenant : il
sert uniquement à construire et publier l'image `1.0.0`. Gardez-le sur une
branche interne ou hors du dépôt public.

## Génération automatique

Le script `make_branches.sh` crée ces huit branches à partir d'un dépôt
contenant tous les fichiers sur `main`. Voir ce script pour l'usage.
