"""
Apercu des donnees Eurostat -- version grand public, langage simplifie
"""

import pandas as pd
from pathlib import Path

RAW_DIR  = Path(__file__).parent.parent / "data" / "raw"
OUT_FILE = Path(__file__).parent.parent / "reports" / "apercu_donnees.html"

BG, CARD, HEADER, BLUE, GREEN, ORANGE, RED, TEXT, SUB, GRID = (
    "#1e1e2e", "#2a2a3e", "#16162a", "#00b4d8", "#06d6a0",
    "#ff6b35", "#ef233c", "#e0e0e0", "#9e9e9e", "#3a3a4e"
)

# ── Traduction des noms de colonnes ────────────────────────────────────────
COL_NAMES = {
    "freq":     "Frequence de mesure",
    "unit":     "Unite",
    "sex":      "Genre",
    "age":      "Tranche d'age",
    "isced11":  "Niveau d'etudes",
    "geo":      "Pays",
    "time":     "Annee",
    "value":    "Valeur mesuree",
    "training": "En formation ?",
    "wstatus":  "Situation professionnelle",
    "nace_r2":  "Secteur d'activite",
}

# ── Traduction des valeurs codes ───────────────────────────────────────────
VAL_LABELS = {
    # Frequence
    "A": "Annuelle",
    # Unite
    "PC":      "Pourcentage (%)",
    "PC_ACT":  "% des personnes en activite",
    "PC_POP":  "% de la population",
    "THS_PER": "Milliers de personnes",
    # Genre
    "T": "Tous (hommes + femmes)",
    "M": "Hommes",
    "F": "Femmes",
    # Age
    "Y15-24": "15 a 24 ans",
    "Y15-29": "15 a 29 ans",
    "Y25-34": "25 a 34 ans",
    # Niveau d'etudes (ISCED)
    "ED0-2":   "Sans diplome ou brevet",
    "ED3_4":   "Baccalaureat",
    "ED34_44": "Bac general ou technologique",
    "ED35_45": "Bac professionnel",
    "ED5-8":   "Etudes superieures (BTS, Licence, Master, Doctorat)",
    "NRP":     "Non renseigne",
    "TOTAL":   "Tous niveaux confondus",
    # Pays notables
    "EU27_2020": "Moyenne europeenne (27 pays)",
    "EA21":      "Zone euro",
    "AT": "Autriche", "BE": "Belgique",  "BG": "Bulgarie",
    "CY": "Chypre",   "CZ": "Tcheque",   "DE": "Allemagne",
    "DK": "Danemark", "EE": "Estonie",   "EL": "Grece",
    "ES": "Espagne",  "FI": "Finlande",  "FR": "France",
    "HR": "Croatie",  "HU": "Hongrie",   "IE": "Irlande",
    "IT": "Italie",   "LT": "Lituanie",  "LU": "Luxembourg",
    "LV": "Lettonie", "MT": "Malte",     "NL": "Pays-Bas",
    "PL": "Pologne",  "PT": "Portugal",  "RO": "Roumanie",
    "SE": "Suede",    "SI": "Slovenie",  "SK": "Slovaquie",
    "IS": "Islande",  "NO": "Norvege",   "CH": "Suisse",
    "UK": "Royaume-Uni", "TR": "Turquie", "BA": "Bosnie",
    "RS": "Serbie",   "ME": "Montenegro","MK": "Macedoine",
    # Situation pro (NEET)
    "NEMP":          "Sans emploi",
    "NO_FE_NO_NFE":  "Aucune formation suivie",
    # Secteurs NACE
    "A": "Agriculture",
    "B": "Mines et carrieres",
    "C": "Industrie",
    "D": "Energie",
    "E": "Eau et environnement",
    "F": "Construction / BTP",
    "G": "Commerce",
    "H": "Transport et logistique",
    "I": "Hotellerie et restauration",
    "J": "Technologie et informatique",
    "K": "Banque et assurance",
    "L": "Immobilier",
    "M": "Conseil et recherche",
    "N": "Services administratifs",
    "O": "Administration publique",
    "P": "Education",
    "Q": "Sante et action sociale",
    "R": "Arts et loisirs",
    "S": "Autres services",
}

# ── Description et contexte de chaque fichier ─────────────────────────────
FILES = {
    "emploi_education": {
        "titre":   "Qui travaille parmi les jeunes ? (selon leur diplome)",
        "source":  "Eurostat lfsa_ergaed",
        "intro":   "Ce tableau montre, pour chaque pays europeen, quelle proportion des jeunes de 15 a 24 ans occupent un emploi, selon leur niveau d'etudes. Par exemple : en France en 2023, 70 % des jeunes diplomes du superieur avaient un emploi, contre 30 % seulement pour ceux sans diplome.",
        "pourquoi": "Ces donnees permettent de mesurer la valeur du diplome sur le marche du travail et de comparer les situations entre pays.",
    },
    "chomage_education": {
        "titre":   "Combien de jeunes sont au chomage ? (selon leur diplome)",
        "source":  "Eurostat lfsa_urgaed",
        "intro":   "Ce tableau indique le taux de chomage des jeunes de 15 a 24 ans selon leur niveau d'etudes, dans chaque pays europeen. Un taux de 20 % signifie que 20 jeunes sur 100 en recherche d'emploi ne trouvent pas de travail.",
        "pourquoi": "C'est l'un des indicateurs les plus suivis par les gouvernements pour mesurer les difficultes d'insertion des jeunes sur le marche du travail.",
    },
    "neet": {
        "titre":   "Les jeunes ni en emploi, ni en formation (NEET)",
        "source":  "Eurostat edat_lfse_22",
        "intro":   "Le terme 'NEET' designe les jeunes qui ne travaillent pas, ne sont pas en etudes et ne suivent aucune formation. C'est une mesure large du decrochage des jeunes. Un taux NEET de 15 % signifie que 15 jeunes sur 100 sont dans cette situation.",
        "pourquoi": "C'est un signal d'alerte social important : un jeune NEET risque de s'eloigner durablement du marche du travail et de perdre en competences.",
    },
    "emploi_secteur": {
        "titre":   "Dans quels secteurs travaillent les jeunes ?",
        "source":  "Eurostat lfsa_egan2",
        "intro":   "Ce tableau recense le nombre de jeunes de 15 a 24 ans qui travaillent dans chaque grand secteur d'activite (commerce, technologie, sante...), exprime en milliers de personnes.",
        "pourquoi": "Savoir dans quels secteurs les jeunes sont concentres permet d'anticiper l'impact de l'intelligence artificielle sur leur emploi.",
    },
}

# ── Description simple de chaque colonne par dataset ──────────────────────
COL_DEFS = {
    "freq": (
        "Frequence de mesure",
        "A quelle frequence la mesure est-elle realisee ?",
        {"A": "Une fois par an"},
    ),
    "unit": (
        "Unite de mesure",
        "Dans quelle unite est exprimee la valeur ?",
        {
            "PC":      "En pourcentage (ex. 14,5 %)",
            "PC_ACT":  "En % des personnes qui cherchent ou ont un emploi",
            "PC_POP":  "En % de toute la population de cet age",
            "THS_PER": "En milliers de personnes (ex. 320 = 320 000 personnes)",
        },
    ),
    "sex": (
        "Genre",
        "Quel groupe de genre est concerne ?",
        {"T": "Hommes et femmes ensemble", "M": "Hommes uniquement", "F": "Femmes uniquement"},
    ),
    "age": (
        "Tranche d'age",
        "Quelle tranche d'age est observee ?",
        {"Y15-24": "15 a 24 ans", "Y15-29": "15 a 29 ans", "Y25-34": "25 a 34 ans"},
    ),
    "isced11": (
        "Niveau d'etudes",
        "Quel est le diplome le plus eleve obtenu par la personne ?",
        {
            "ED0-2":   "Sans diplome ou brevet des colleges",
            "ED3_4":   "Baccalaureat (general, techno ou pro)",
            "ED34_44": "Bac general ou technologique",
            "ED35_45": "Bac professionnel",
            "ED5-8":   "Etudes superieures : BTS, Licence, Master, Doctorat",
            "NRP":     "Information non disponible",
            "TOTAL":   "Tous diplomes confondus",
        },
    ),
    "geo": (
        "Pays",
        "Quel pays ou zone geographique est concerne ?",
        {
            "EU27_2020": "Moyenne des 27 pays de l'Union Europeenne",
            "FR": "France", "DE": "Allemagne", "IT": "Italie",
            "ES": "Espagne", "EL": "Grece", "PL": "Pologne",
            "...": "(et tous les autres pays europeens)",
        },
    ),
    "time": (
        "Annee",
        "Pour quelle annee cette mesure a-t-elle ete faite ?",
        {
            "2010": "Debut de la serie de donnees",
            "2020": "Annee du COVID-19 (forte perturbation)",
            "2025": "Annee la plus recente disponible",
        },
    ),
    "value": (
        "Valeur mesuree",
        "Le chiffre lui-meme : le taux ou le nombre mesure. Peut etre vide si la donnee n'est pas disponible.",
        {
            "ex. 14.5": "14,5 % de jeunes au chomage dans ce pays cette annee-la",
            "ex. 320.0": "320 000 jeunes employes dans ce secteur",
            "vide": "Donnee non disponible ou non communiquee par le pays",
        },
    ),
    "training": (
        "En formation ?",
        "Le jeune suit-il une formation en parallele ? (specifique aux donnees NEET)",
        {"NO_FE_NO_NFE": "Non — ni cours du soir, ni formation en ligne, rien"},
    ),
    "wstatus": (
        "Situation professionnelle",
        "Le jeune a-t-il un emploi ? (specifique aux donnees NEET)",
        {"NEMP": "Non — sans emploi"},
    ),
    "nace_r2": (
        "Secteur d'activite",
        "Dans quel grand domaine professionnel le jeune travaille-t-il ?",
        {
            "A": "Agriculture et peche",
            "C": "Industrie et fabrication",
            "F": "Construction et BTP",
            "G": "Commerce (magasins, grande distribution)",
            "I": "Hotellerie et restauration",
            "J": "Technologie et informatique",
            "Q": "Sante et aide a la personne",
            "TOTAL": "Tous secteurs confondus",
        },
    ),
}


def translate_val(v):
    if pd.isna(v):
        return '<span class="na">donnee manquante</span>'
    s = str(v)
    label = VAL_LABELS.get(s)
    if label:
        return f'<span class="translated" title="{s}">{label}</span>'
    return s


def dict_section(df: pd.DataFrame) -> str:
    rows = ""
    for col in df.columns:
        if col not in COL_DEFS:
            continue
        nom, description, valeurs = COL_DEFS[col]
        val_rows = "".join(
            f'<div class="val-row"><span class="val-code">{code}</span>'
            f'<span class="val-arrow">&#8594;</span>'
            f'<span class="val-plain">{plain}</span></div>'
            for code, plain in valeurs.items()
        )
        rows += f"""
        <tr>
          <td class="col-tech">{col}</td>
          <td class="col-nom">{nom}</td>
          <td class="col-desc">{description}</td>
          <td>{val_rows}</td>
        </tr>"""
    if not rows:
        return ""
    return f"""
    <div class="section-label">Que signifie chaque colonne ?</div>
    <div class="table-wrap">
    <table class="dict">
      <thead><tr>
        <th>Nom technique</th>
        <th>Ce que ca veut dire</th>
        <th>Question a laquelle ca repond</th>
        <th>Valeurs possibles</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""


def preview_section(df: pd.DataFrame) -> str:
    preview = df.head(10).copy()
    headers = "".join(
        f"<th>{COL_NAMES.get(c, c)}<br><small>{c}</small></th>"
        for c in preview.columns
    )
    body = ""
    for _, row in preview.iterrows():
        cells = ""
        for col, v in row.items():
            if col == "value" and not pd.isna(v):
                cells += f'<td class="num">{v:.1f}</td>'
            elif col == "time":
                cells += f"<td>{int(v)}</td>"
            else:
                cells += f"<td>{translate_val(v)}</td>"
        body += f"<tr>{cells}</tr>"
    return f"""
    <div class="section-label">Les 10 premieres lignes du fichier</div>
    <div class="table-wrap">
    <table class="data">
      <thead><tr>{headers}</tr></thead>
      <tbody>{body}</tbody>
    </table>
    </div>"""


def stats_section(df: pd.DataFrame) -> str:
    num = df.select_dtypes(include="number").columns
    num = [c for c in num if c != "time"]
    if not num:
        return ""
    rows = ""
    for col in num:
        s = df[col].dropna()
        nom = COL_NAMES.get(col, col)
        unit_col = df.get("unit")
        unite = VAL_LABELS.get(unit_col.iloc[0], unit_col.iloc[0]) if unit_col is not None else ""
        rows += (
            f"<tr><td class='col-nom'>{nom}</td>"
            f"<td class='num'>{s.min():.1f}</td>"
            f"<td class='num'>{s.max():.1f}</td>"
            f"<td class='num'>{s.mean():.1f}</td>"
            f"<td class='sub'>{unite}</td></tr>"
        )
    return f"""
    <div class="section-label">Chiffres cles (sur l'ensemble du fichier)</div>
    <div class="table-wrap">
    <table class="stats">
      <thead><tr><th>Indicateur</th><th>Valeur minimale</th><th>Valeur maximale</th><th>Valeur moyenne</th><th>Unite</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    </div>"""


def card_html(key: str, meta: dict) -> str:
    df = pd.read_csv(RAW_DIR / f"{key}.csv")
    n_rows = f"{len(df):,}".replace(",", " ")
    return f"""
<section class="card">
  <div class="card-top">
    <div>
      <h2>{meta['titre']}</h2>
      <p class="source">{meta['source']} &nbsp;|&nbsp; {n_rows} observations</p>
    </div>
  </div>
  <div class="intro-box">
    <p>{meta['intro']}</p>
    <p class="pourquoi"><strong>Pourquoi c'est utile :</strong> {meta['pourquoi']}</p>
  </div>
  {dict_section(df)}
  {preview_section(df)}
  {stats_section(df)}
</section>"""


# ── Generation HTML ────────────────────────────────────────────────────────
print("Generation de la page grand public...")
cards = "\n".join(card_html(k, v) for k, v in FILES.items())

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Les donnees sur l'emploi des jeunes en Europe -- Guide de lecture</title>
<style>
*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:{BG}; color:{TEXT}; font-family:"Segoe UI",Arial,sans-serif; font-size:14px; line-height:1.6; }}

/* ── Header ── */
.site-header {{ background:{HEADER}; border-bottom:3px solid {BLUE}; padding:28px 40px; }}
.site-header h1 {{ font-size:22px; color:#fff; margin-bottom:6px; }}
.site-header .subtitle {{ color:{SUB}; font-size:13px; }}
.intro-global {{ background:{CARD}; border-left:4px solid {GREEN}; margin:0 40px 32px; padding:20px 24px; border-radius:0 8px 8px 0; line-height:1.8; }}
.intro-global p {{ margin-bottom:8px; }}
.intro-global p:last-child {{ margin:0; }}
.intro-global strong {{ color:{GREEN}; }}

/* ── Navigation ── */
.nav {{ display:flex; gap:10px; flex-wrap:wrap; padding:20px 40px 0; }}
.nav a {{ background:{CARD}; color:{BLUE}; border:1px solid {GRID}; border-radius:20px; padding:6px 16px; font-size:12px; text-decoration:none; }}
.nav a:hover {{ background:{BLUE}; color:#fff; }}

/* ── Cards ── */
.cards {{ padding:28px 40px; display:flex; flex-direction:column; gap:32px; }}
.card {{ background:{CARD}; border-radius:12px; overflow:hidden; }}
.card-top {{ padding:22px 28px 0; border-bottom:1px solid {GRID}; padding-bottom:16px; }}
.card h2 {{ font-size:17px; color:#fff; margin-bottom:4px; }}
.source {{ font-size:11px; color:{SUB}; }}

/* ── Intro box ── */
.intro-box {{ background:{HEADER}; margin:20px 28px; padding:16px 20px; border-radius:8px; border-left:3px solid {ORANGE}; }}
.intro-box p {{ font-size:13px; color:{TEXT}; margin-bottom:8px; }}
.intro-box p:last-child {{ margin:0; }}
.pourquoi {{ color:{SUB} !important; }}
.pourquoi strong {{ color:{ORANGE}; }}

/* ── Section label ── */
.section-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.8px; color:{SUB}; padding:20px 28px 10px; font-weight:600; }}

/* ── Tables ── */
.table-wrap {{ overflow-x:auto; padding:0 28px 20px; }}
table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
thead tr {{ background:{HEADER}; }}
th {{ padding:10px 14px; text-align:left; font-weight:600; border-bottom:2px solid {GRID}; white-space:nowrap; }}
td {{ padding:9px 14px; border-bottom:1px solid {GRID}; vertical-align:top; }}
tbody tr:hover {{ background:rgba(255,255,255,.03); }}

/* ── Dict table ── */
.dict th {{ color:{ORANGE}; }}
.dict th:nth-child(1) {{ width:10%; }}
.dict th:nth-child(2) {{ width:16%; }}
.dict th:nth-child(3) {{ width:26%; }}
.dict th:nth-child(4) {{ width:48%; }}
.col-tech {{ font-family:monospace; font-size:12px; color:{BLUE}; font-weight:700; white-space:nowrap; }}
.col-nom  {{ color:#fff; font-weight:500; }}
.col-desc {{ color:{SUB}; font-size:12px; }}
.val-row  {{ display:flex; align-items:baseline; gap:6px; margin-bottom:5px; flex-wrap:wrap; }}
.val-code  {{ font-family:monospace; background:{HEADER}; border:1px solid {GRID}; border-radius:4px; padding:2px 8px; font-size:11px; color:{GREEN}; white-space:nowrap; }}
.val-arrow {{ color:{GRID}; font-size:11px; }}
.val-plain {{ font-size:12px; color:{TEXT}; }}

/* ── Data preview table ── */
.data th {{ color:{BLUE}; font-size:11px; }}
.data th small {{ display:block; color:{SUB}; font-weight:400; font-family:monospace; font-size:10px; margin-top:2px; }}
.translated {{ color:{TEXT}; }}
.na {{ color:{RED}; font-style:italic; font-size:11px; }}
.num {{ font-family:monospace; color:{GREEN}; text-align:right; }}

/* ── Stats table ── */
.stats th {{ color:{GREEN}; }}
.sub {{ color:{SUB}; font-size:11px; }}

footer {{ text-align:center; padding:24px; color:{SUB}; font-size:11px; border-top:1px solid {GRID}; margin-top:8px; }}
</style>
</head>
<body>

<div class="site-header">
  <h1>L'emploi des jeunes en Europe &mdash; Guide de lecture des donnees</h1>
  <p class="subtitle">Source : Eurostat &nbsp;|&nbsp; 4 tableaux de donnees &nbsp;|&nbsp; Pays europeens &nbsp;|&nbsp; 2010-2025</p>
</div>

<div class="intro-global">
  <p>Ces donnees ont ete collectees par <strong>Eurostat</strong>, l'office statistique officiel de l'Union Europeenne, qui recense chaque annee des informations sur l'emploi dans tous les pays membres.</p>
  <p>Elles permettent de repondre a des questions simples : <strong>Est-ce qu'avoir un diplome aide vraiment a trouver un travail ?</strong> Quels pays d'Europe ont le plus de jeunes au chomage ? Dans quels metiers les jeunes travaillent-ils aujourd'hui ?</p>
  <p>Cette analyse s'interesse particulierement a l'impact de <strong>l'intelligence artificielle sur l'emploi des jeunes</strong> : certains secteurs sont plus menaces que d'autres par l'automatisation.</p>
</div>

<nav class="nav">
  <a href="#emploi_education">Emploi selon le diplome</a>
  <a href="#chomage_education">Chomage selon le diplome</a>
  <a href="#neet">Jeunes decrocheurs (NEET)</a>
  <a href="#emploi_secteur">Emploi par secteur</a>
</nav>

<div class="cards">
  {cards}
</div>

<footer>
  Source : Eurostat (lfsa_ergaed, lfsa_urgaed, edat_lfse_22, lfsa_egan2) &nbsp;|&nbsp;
  Donnees 2010-2025 &nbsp;|&nbsp; Jeunes de 15 a 34 ans &nbsp;|&nbsp; 27 pays de l'UE
</footer>

</body>
</html>"""

OUT_FILE.write_text(html, encoding="utf-8")
print(f"Genere : {OUT_FILE}  ({OUT_FILE.stat().st_size // 1024} Ko)")
