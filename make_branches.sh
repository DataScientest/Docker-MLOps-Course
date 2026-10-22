#!/usr/bin/env bash
#
# Crée les branches chapitre-01 à chapitre-08 à partir d'un dépôt contenant
# TOUS les fichiers du projet sur la branche courante (typiquement main).
#
# Usage :
#   cd <depot>            # dépôt git avec tous les fichiers committés sur main
#   bash make_branches.sh
#   git push origin --all # pour pousser toutes les branches
#
# Le script est idempotent : relancé, il recrée les branches à l'identique.

set -euo pipefail

BASE="$(git rev-parse --abbrev-ref HEAD)"
echo "Branche de base : $BASE"

# Groupes de fichiers, par palier d'apparition.
DOCKER="Dockerfile .dockerignore"
COMPOSE="compose.yaml compose.local.yaml compose.remote.yaml .env.example tests/Dockerfile .github"
PROD="compose.prod.yaml"
# build-prebuilt/ ne doit jamais se trouver sur une branche apprenant.
INTERNAL="build-prebuilt BRANCHES.md make_branches.sh"

make_branch () {
  local name="$1"; shift
  echo "==> $name"
  git checkout -B "$name" "$BASE" >/dev/null 2>&1
  for f in "$@" $INTERNAL; do
    git rm -rf --quiet --ignore-unmatch "$f" >/dev/null 2>&1 || true
  done
  git commit -m "Point de départ : $name" --quiet 2>/dev/null || true
}

# Branches 01 à 05 : squelette seul (ni Docker, ni Compose, ni prod).
for n in 01 02 03 04 05; do
  make_branch "chapitre-$n" $DOCKER $COMPOSE $PROD
done

# Branche 06 : + Dockerfile et .dockerignore.
make_branch "chapitre-06" $COMPOSE $PROD

# Branche 07 : + Compose et chaîne d'intégration.
make_branch "chapitre-07" $PROD

# Branche 08 : projet complet (sans les fichiers internes).
make_branch "chapitre-08"

git checkout "$BASE" >/dev/null 2>&1
echo "Terminé. Branches créées : chapitre-01 … chapitre-08."
echo "Poussez-les avec : git push origin --all"
