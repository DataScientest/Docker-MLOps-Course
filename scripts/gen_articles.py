"""Genere le corpus d'articles fictifs de Sillage.

Produit data/articles.json : environ 200 courts articles de presse fictifs,
repartis sur une dizaine de themes, avec un vocabulaire volontairement varie
pour que la recherche semantique soit demontrable (une requete sur "voiture
electrique en ville" doit ramener des articles sur la mobilite douce ou les
transports urbains, meme sans les memes mots).

Lance : python scripts/gen_articles.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

random.seed(42)

# Chaque theme : une liste de (titre, corps). Les corps emploient des
# synonymes et des reformulations pour creer de vrais voisinages semantiques.
THEMES: dict[str, list[tuple[str, str]]] = {
    "mobilite": [
        ("La voiture electrique gagne les centres-villes",
         "De plus en plus de metropoles encouragent les vehicules electriques pour reduire la pollution urbaine. Les bornes de recharge se multiplient dans les quartiers residentiels."),
        ("Le velo s'impose comme mode de deplacement quotidien",
         "La pratique du velo en ville progresse fortement. Les collectivites amenagent des pistes cyclables continues pour securiser les trajets domicile-travail."),
        ("Les zones a faibles emissions se generalisent",
         "Plusieurs agglomerations restreignent la circulation des vehicules les plus polluants. La mobilite douce et les transports en commun sont presentes comme les alternatives principales."),
        ("Trottinettes et mobilites partagees en plein essor",
         "Les services de mobilite partagee transforment les deplacements urbains. Les operateurs promettent une alternative a la voiture individuelle pour les trajets courts."),
        ("Le train de nuit revient sur les rails europeens",
         "Les liaisons ferroviaires nocturnes connaissent un regain d'interet. Les voyageurs y voient une option moins polluante que l'avion pour les moyennes distances."),
        ("Les bornes de recharge rapide se deploient sur autoroute",
         "Le reseau de recharge pour vehicules electriques s'etend le long des grands axes. L'autonomie n'est plus percue comme un frein pour les longs trajets."),
    ],
    "energie": [
        ("Le solaire photovoltaique bat des records d'installation",
         "Les installations de panneaux solaires progressent a un rythme inedit. Les particuliers comme les entreprises investissent dans l'autoconsommation."),
        ("L'eolien en mer entre en service au large des cotes",
         "Les premiers parcs eoliens offshore produisent desormais de l'electricite. Ils doivent contribuer a la transition energetique du pays."),
        ("La sobriete energetique devient un reflexe collectif",
         "Face a la hausse des prix, menages et collectivites revoient leur consommation. Isolation des batiments et reduction du chauffage sont au programme."),
        ("Le stockage par batteries stabilise le reseau electrique",
         "Les grandes batteries permettent de lisser la production intermittente des renouvelables. Le reseau gagne en souplesse face aux pics de demande."),
        ("L'hydrogene vert suscite espoirs et prudence",
         "Produire de l'hydrogene a partir d'electricite renouvelable interesse l'industrie. Les couts de production restent toutefois eleves pour l'instant."),
    ],
    "alimentation": [
        ("Les circuits courts seduisent les consommateurs",
         "Acheter directement aux producteurs locaux gagne du terrain. Les marches de producteurs et les paniers hebdomadaires se multiplient."),
        ("Les alternatives vegetales s'installent dans les rayons",
         "Les substituts a la viande occupent une place croissante en supermarche. L'offre de produits a base de legumineuses s'elargit."),
        ("Le gaspillage alimentaire recule dans la restauration",
         "Restaurants et cantines adoptent des mesures pour limiter les pertes. Le don des invendus se structure autour d'associations."),
        ("L'agriculture urbaine verdit les toits des villes",
         "Potagers partages et fermes sur les toits se developpent en milieu urbain. Ils rapprochent la production alimentaire des habitants."),
        ("La traçabilite des aliments rassure les acheteurs",
         "Connaitre l'origine exacte des produits devient un critere d'achat. Les etiquettes detaillees et les codes a scanner se repandent."),
    ],
    "sante": [
        ("La teleconsultation s'ancre dans les habitudes",
         "Consulter un medecin a distance est devenu courant. Les plateformes de teleconsultation desengorgent les cabinets dans les zones peu dotees."),
        ("La prevention prend le pas sur le soin curatif",
         "Les politiques de sante publique insistent sur la prevention. Depistage precoce et hygiene de vie sont mis en avant."),
        ("L'activite physique prescrite comme un traitement",
         "Des medecins prescrivent desormais du sport adapte. L'exercice regulier est reconnu comme un levier contre les maladies chroniques."),
        ("Le sommeil, nouveau pilier de la sante publique",
         "La qualite du sommeil fait l'objet d'une attention croissante. Les campagnes alertent sur les effets du manque de repos."),
        ("Les deserts medicaux cherchent des solutions",
         "L'acces aux soins reste difficile dans certaines regions. Maisons de sante et incitations a l'installation sont experimentees."),
    ],
    "technologie": [
        ("L'intelligence artificielle s'invite dans les entreprises",
         "Les outils d'IA generative se diffusent dans de nombreux metiers. Les organisations cherchent a encadrer leur usage."),
        ("La cybersecurite devient une priorite des PME",
         "Les petites entreprises sont de plus en plus visees par les attaques. La protection des donnees et la sauvegarde deviennent essentielles."),
        ("Le cloud souverain cherche sa place en Europe",
         "Heberger les donnees sur des infrastructures europeennes rassure les acteurs publics. La question de la dependance aux fournisseurs etrangers se pose."),
        ("Les puces specialisees accelerent le calcul",
         "De nouveaux processeurs sont concus pour les charges de travail intensives. Ils promettent des gains d'efficacite energetique notables."),
        ("La fracture numerique persiste dans les campagnes",
         "L'acces a un internet rapide reste inegal selon les territoires. Le deploiement de la fibre se poursuit mais a un rythme variable."),
    ],
    "economie": [
        ("Le teletravail redessine le marche de l'immobilier de bureau",
         "La demande de surfaces de bureau evolue avec le travail hybride. Les entreprises reduisent ou reamenagent leurs espaces."),
        ("Les circuits de reparation freinent l'obsolescence",
         "Reparer plutot que jeter devient un argument economique. Les ateliers de reparation et l'indice de reparabilite gagnent en visibilite."),
        ("Les monnaies locales tissent des reseaux de proximite",
         "Des territoires experimentent des monnaies complementaires. Elles visent a maintenir la richesse dans l'economie locale."),
        ("L'economie circulaire redonne vie aux materiaux",
         "Reemploi et recyclage structurent de nouvelles filieres. Les dechets d'hier deviennent des ressources."),
        ("Les commerces de centre-ville se reinventent",
         "Face a la concurrence en ligne, les commercants misent sur l'experience. Animations et services de proximite tentent d'attirer les clients."),
    ],
    "environnement": [
        ("La renaturation des villes fait baisser la temperature",
         "Planter des arbres et desimpermeabiliser les sols rafraichit les villes. Ces amenagements luttent contre les ilots de chaleur urbains."),
        ("La gestion de l'eau devient un enjeu quotidien",
         "La rarefaction de la ressource impose de nouveaux usages. Recuperation des eaux de pluie et reduction des fuites sont encouragees."),
        ("La biodiversite ordinaire se reinvite en ville",
         "Prairies fleuries et haies favorisent le retour des insectes. Les collectivites revoient l'entretien des espaces verts."),
        ("Le tri des dechets se simplifie pour les habitants",
         "De nouvelles consignes facilitent le geste de tri. Les filieres de recyclage s'adaptent a des flux plus volumineux."),
        ("Les forets urbaines absorbent le carbone",
         "Planter des bosquets denses en ville capte du carbone et abrite la faune. Ces micro-forets poussent plus vite qu'attendu."),
    ],
    "culture": [
        ("Les bibliotheques deviennent des tiers-lieux",
         "Au-dela du pret de livres, les bibliotheques accueillent ateliers et rencontres. Elles se posent en espaces de vie partages."),
        ("Le cinema independant resiste grace aux festivals",
         "Les petites salles misent sur une programmation exigeante. Les festivals locaux soutiennent la diffusion de films rares."),
        ("Le podcast s'affirme comme un media a part entiere",
         "L'ecoute de contenus audio a la demande progresse. Les formats longs et documentaires trouvent leur public."),
        ("Les musees ouvrent leurs collections en ligne",
         "La numerisation rend accessibles des oeuvres jusque-la invisibles. Les visites virtuelles completent l'experience sur place."),
        ("Le spectacle vivant renoue avec son public",
         "Theatres et salles de concert retrouvent leur frequentation. La billetterie flexible accompagne de nouveaux comportements."),
    ],
    "education": [
        ("Les competences numeriques entrent a l'ecole",
         "Apprendre a utiliser les outils numeriques de maniere critique devient un objectif. Les programmes integrent l'education aux medias."),
        ("La formation continue devient un reflexe de carriere",
         "Se former tout au long de la vie s'impose face aux mutations des metiers. Les dispositifs de financement se diversifient."),
        ("L'apprentissage par projet gagne les salles de classe",
         "Mettre les eleves en situation concrete renforce la motivation. Les pedagogies actives se repandent."),
        ("Le soutien scolaire se reinvente en ligne",
         "Les plateformes d'accompagnement personnalise se multiplient. Elles promettent un suivi adapte au rythme de chaque eleve."),
        ("Les tiers-lieux etudiants favorisent l'entraide",
         "Des espaces de travail partages accueillent les etudiants. Ils y trouvent methode, materiel et soutien entre pairs."),
    ],
    "sport": [
        ("La marche a pied, sport le plus pratique du pays",
         "Accessible et gratuite, la marche seduit tous les ages. Les applications de suivi encouragent la regularite."),
        ("Les clubs amateurs peinent a recruter des benevoles",
         "L'engagement associatif recule dans le sport amateur. Les clubs cherchent a renouveler leurs encadrants."),
        ("Le sport feminin gagne en visibilite mediatique",
         "La couverture des competitions feminines progresse. Les audiences records nourrissent de nouvelles vocations."),
        ("Les equipements sportifs de plein air se multiplient",
         "Agres et parcours de sante fleurissent dans les parcs. Ils rendent l'activite physique accessible sans abonnement."),
        ("Le running urbain structure des communautes",
         "Courir en groupe devient un rendez-vous social. Les collectifs de coureurs animent les villes le soir et le week-end."),
    ],
}

# Variations pour atteindre ~200 articles sans repetition mecanique.
ANGLES = [
    "Enquete",
    "Reportage",
    "Analyse",
    "Decryptage",
    "Temoignages",
    "Point de vue",
    "Dossier",
]
LIEUX = [
    "a Lyon", "a Nantes", "en Bretagne", "dans le Grand Est", "a Marseille",
    "en Occitanie", "a Lille", "dans la metropole bordelaise", "a Strasbourg",
    "en Ile-de-France",
]


def build() -> list[dict]:
    articles: list[dict] = []
    article_id = 1
    # On repete les themes en variant l'angle et le lieu jusqu'a ~200.
    target = 200
    while len(articles) < target:
        for category, entries in THEMES.items():
            for title, body in entries:
                if len(articles) >= target:
                    break
                angle = random.choice(ANGLES)
                lieu = random.choice(LIEUX)
                full_title = f"{title}" if article_id <= len(_flatten()) else f"{angle} : {title} {lieu}"
                full_body = body if article_id <= len(_flatten()) else f"{body} {angle} {lieu}."
                articles.append(
                    {
                        "id": article_id,
                        "title": full_title.strip(),
                        "body": full_body.strip(),
                        "category": category,
                    }
                )
                article_id += 1
    return articles[:target]


def _flatten() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for entries in THEMES.values():
        out.extend(entries)
    return out


if __name__ == "__main__":
    data = build()
    out_path = Path("data/articles.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{len(data)} articles ecrits dans {out_path}")
