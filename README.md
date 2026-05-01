# Emploi des jeunes diplomes en Europe

Une analyse des donnees Eurostat sur le chomage des 15-24 ans en Europe,
avec un eclairage sur l'impact de l'intelligence artificielle sur l'emploi des jeunes.

---

## C'est quoi ce projet ?

Chaque annee, l'Union Europeenne collecte des statistiques sur l'emploi des jeunes
dans les 27 pays membres. Ce projet recupere ces donnees officielles et les transforme
en graphiques et textes lisibles par tout le monde — pas seulement par des specialistes.

**Question centrale :** Est-ce que l'intelligence artificielle va aggraver ou ameliorer
la situation des jeunes sur le marche du travail europeen ?

---

## Les trois pages du projet

### 1. Dashboard interactif
**`reports/emploi_jeunes_europe.html`**

La vue d'ensemble : cartes, graphiques et chiffres cles pour comparer les pays,
suivre l'evolution depuis 2010 et voir quels secteurs emploient le plus les jeunes.

### 2. Guide de lecture des donnees
**`reports/apercu_donnees.html`**

Pour comprendre d'ou viennent les chiffres : les 4 tableaux de donnees Eurostat
expliques en langage simple, avec la signification de chaque colonne.

### 3. Conclusions
**`reports/conclusions.html`**

L'essentiel en clair : la situation pays par pays expliquee comme a un ami,
et 5 messages cles sur l'emploi des jeunes et l'IA en Europe.

---

## Les donnees

Toutes les donnees viennent d'**Eurostat**, l'office statistique officiel de l'UE.
Elles sont telechargees automatiquement via l'API publique, sans inscription.

| Fichier | Ce qu'il contient |
|---|---|
| `emploi_education.csv` | Taux d'emploi par pays, age et niveau de diplome |
| `chomage_education.csv` | Taux de chomage par pays, age et niveau de diplome |
| `neet.csv` | Jeunes ni en emploi ni en formation (indicateur NEET) |
| `emploi_secteur.csv` | Emploi par secteur d'activite (agriculture, tech, sante...) |

Periode couverte : **2010 a 2025** — 27 pays de l'Union Europeenne.

---

## Comment reproduire l'analyse

Il faut Python installe sur votre ordinateur. Ensuite, dans l'ordre :

```
python scripts/download_data.py      # Telecharge les donnees Eurostat
python scripts/generate_report.py   # Cree le dashboard interactif
python scripts/generate_preview.py  # Cree le guide de lecture
python scripts/generate_conclusions.py  # Cree la page de conclusions
```

Les fichiers HTML sont generes dans le dossier `reports/`.
Ouvrez-les directement dans votre navigateur, sans serveur ni installation supplementaire.

---

## Structure du projet

```
emploi-jeunes-europe/
├── data/
│   └── raw/          # Donnees Eurostat telechargees (CSV)
├── reports/          # Pages HTML generees
├── scripts/          # Scripts Python
└── README.md
```

---

## Auteur

Mohamed — Analyste data, expert Power BI.
Projet realise avec Python, Pandas et Plotly.
