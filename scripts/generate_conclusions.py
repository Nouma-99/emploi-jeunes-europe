"""
Page de conclusions -- version grand public, langage simple
"""

import pandas as pd
from pathlib import Path

RAW_DIR  = Path(__file__).parent.parent / "data" / "raw"
OUT_FILE = Path(__file__).parent.parent / "reports" / "conclusions.html"

# ── Palette ────────────────────────────────────────────────────────────────
BG     = "#1e1e2e"
CARD   = "#2a2a3e"
DARK   = "#16162a"
BLUE   = "#00b4d8"
GREEN  = "#06d6a0"
ORANGE = "#ff6b35"
RED    = "#ef233c"
PURPLE = "#9d4edd"
TEXT   = "#e0e0e0"
SUB    = "#9e9e9e"
GRID   = "#3a3a4e"

# ── Chargement donnees ─────────────────────────────────────────────────────
print("Chargement et calcul des indicateurs...")
df_cho  = pd.read_csv(RAW_DIR / "chomage_education.csv")
df_emp  = pd.read_csv(RAW_DIR / "emploi_education.csv")
df_neet = pd.read_csv(RAW_DIR / "neet.csv")

EXCLUS = {"EU27_2020","EA21","TR","RS","ME","MK","BA","IS","NO","CH","UK"}
PAYS_EU = [g for g in df_cho["geo"].unique() if g not in EXCLUS]

def latest(df, geo, isced="TOTAL", age="Y15-24"):
    q = df[(df["geo"]==geo) & (df["age"]==age)]
    if "isced11" in df.columns:
        q = q[q["isced11"]==isced]
    q = q.dropna(subset=["value"]).sort_values("time")
    return (round(q.iloc[-1]["value"],1), int(q.iloc[-1]["time"])) if not q.empty else (None,None)

def trend(df, geo, isced="TOTAL", age="Y15-24"):
    q = df[(df["geo"]==geo)&(df["age"]==age)]
    if "isced11" in df.columns:
        q = q[q["isced11"]==isced]
    q = q.dropna(subset=["value"]).sort_values("time")
    if len(q) < 2:
        return 0
    return round(q.iloc[-1]["value"] - q.iloc[-3]["value"] if len(q)>=3 else q.iloc[-1]["value"] - q.iloc[-2]["value"], 1)

# Calcul stats par pays
stats = {}
for p in PAYS_EU:
    cho, yr  = latest(df_cho, p)
    cho_hi,_ = latest(df_cho, p, isced="ED5-8")
    cho_lo,_ = latest(df_cho, p, isced="ED0-2")
    neet,_   = latest(df_neet, p)
    delta    = trend(df_cho, p)
    cho_2010 = df_cho[(df_cho["geo"]==p)&(df_cho["isced11"]=="TOTAL")&(df_cho["age"]=="Y15-24")&(df_cho["time"]==2010)]["value"].mean()
    stats[p] = dict(cho=cho, yr=yr, cho_hi=cho_hi, cho_lo=cho_lo,
                    neet=neet, delta=delta,
                    cho_2010=round(cho_2010,1) if not pd.isna(cho_2010) else None)

# Moyenne EU27
eu_cho,_ = latest(df_cho, "EU27_2020")
eu_neet,_= latest(df_neet, "EU27_2020")

# ── Donnees par pays : texte + configuration ───────────────────────────────
PAYS_INFO = {
    "DE": {
        "nom": "Allemagne",
        "flag": "DE",
        "texte": (
            "L'Allemagne est la meilleure eleve d'Europe. Sur 100 jeunes qui cherchent un emploi, "
            "seulement 7 ne trouvent pas. C'est comme une classe entiere ou presque tout le monde "
            "trouverait un stage. Le secret ? Un systeme d'apprentissage tres developpe : beaucoup "
            "de jeunes apprennent directement en entreprise, ce qui facilite l'embauche."
        ),
    },
    "NL": {
        "nom": "Pays-Bas",
        "flag": "NL",
        "texte": (
            "Les Pays-Bas fonctionnent tres bien pour les jeunes. Le marche du travail est flexible "
            "et les entreprises embauchent facilement. Petit point d'attention : beaucoup de ces "
            "emplois sont a temps partiel. Un jeune neerlandais peut travailler 20 heures par semaine "
            "tout en faisant des etudes, ce qui gonfle un peu les bons chiffres."
        ),
    },
    "CZ": {
        "nom": "Tcheque",
        "flag": "CZ",
        "texte": (
            "La Republique tcheque a fait un chemin impressionnant. En 2010, 18 jeunes sur 100 "
            "etaient au chomage. Aujourd'hui, c'est 10. Concrètement, c'est comme si la moitie "
            "des jeunes sans emploi avaient trouve un travail en 15 ans. L'industrie automobile "
            "et la fabrication sont les grands employeurs des jeunes ici."
        ),
    },
    "AT": {
        "nom": "Autriche",
        "flag": "AT",
        "texte": (
            "L'Autriche ressemble beaucoup a l'Allemagne : l'apprentissage en entreprise est "
            "tres courant et les jeunes entrent vite dans la vie active. La situation s'est "
            "toutefois legerement degradee ces dernieres annees, passant de 10 % a 11,5 %. "
            "Rien d'alarmant, mais un chiffre a surveiller."
        ),
    },
    "MT": {
        "nom": "Malte",
        "flag": "MT",
        "texte": (
            "Malte est une bonne surprise. Cette petite ile mediterraneenne affiche un taux "
            "de chomage des jeunes parmi les plus bas d'Europe. Le tourisme et les services "
            "financiers emploient beaucoup de jeunes. L'anglais courant y est un avantage : "
            "beaucoup d'entreprises internationales s'y installent."
        ),
    },
    "IE": {
        "nom": "Irlande",
        "flag": "IE",
        "texte": (
            "L'Irlande a vecu une transformation remarquable. En 2010, pres de 28 jeunes sur 100 "
            "etaient au chomage — une vraie crise. Aujourd'hui, c'est 12. Ce qui a tout change ? "
            "L'arrivee massive de grandes entreprises technologiques (Google, Meta, Apple...) qui "
            "ont cree des milliers d'emplois pour les jeunes qualifies."
        ),
    },
    "PL": {
        "nom": "Pologne",
        "flag": "PL",
        "texte": (
            "La Pologne a enormement progresse depuis 2010, ou presque 1 jeune sur 4 etait sans "
            "emploi. Aujourd'hui c'est 12 %. L'economie polonaise a beaucoup grandi ces 15 ans. "
            "Seul bémol : beaucoup de jeunes Polonais qualifies partent travailler en Allemagne "
            "ou en France, ce qu'on appelle la 'fuite des cerveaux'."
        ),
    },
    "SI": {
        "nom": "Slovenie",
        "flag": "SI",
        "texte": (
            "La Slovenie est un pays discret mais qui se debrouille bien. Son taux de chomage "
            "des jeunes est modere et le pays est plutot stable. Ce petit pays d'Europe centrale "
            "a une economie diversifiee, ce qui protege les jeunes contre les crises qui touchent "
            "un seul secteur."
        ),
    },
    "DK": {
        "nom": "Danemark",
        "flag": "DK",
        "texte": (
            "Le Danemark affiche 14 % — un chiffre qui peut surprendre pour un pays si riche. "
            "En realite, le marche du travail danois est tres flexible : on embauche vite, mais "
            "on licencie vite aussi. Les jeunes alternent souvent entre petits boulots et periodes "
            "de chomage courtes, ce qui fait monter le chiffre sans que ce soit dramatique."
        ),
    },
    "HU": {
        "nom": "Hongrie",
        "flag": "HU",
        "texte": (
            "La Hongrie a beaucoup ameliore sa situation depuis 2010 (de 26 % a 14 %). "
            "Le gouvernement a mis en place des programmes d'emploi public qui ont absorbe "
            "une partie des jeunes sans travail. Certains economistes nuancent ces chiffres, "
            "mais la tendance a la baisse est reelle."
        ),
    },
    "CY": {
        "nom": "Chypre",
        "flag": "CY",
        "texte": (
            "Chypre est dans une situation moyenne. L'ile a souffert d'une grosse crise bancaire "
            "en 2013 qui a blesse son economie. Elle s'en est bien remise, mais le chomage des "
            "jeunes reste autour de 13-14 %. Paradoxalement, meme les jeunes diplomes ont "
            "du mal a trouver a Chypre : 22 % d'entre eux sont sans emploi."
        ),
    },
    "BG": {
        "nom": "Bulgarie",
        "flag": "BG",
        "texte": (
            "La Bulgarie a fait des progres (de 22 % a 13 %), mais elle reste fragile. "
            "Le vrai probleme ici est la fuite des jeunes vers l'Ouest : des centaines de milliers "
            "de Bulgares qualifies ont quitte le pays pour la France, l'Allemagne ou les Pays-Bas. "
            "Ceux qui restent trouvent souvent du travail, mais les salaires sont tres bas."
        ),
    },
    "LT": {
        "nom": "Lituanie",
        "flag": "LT",
        "texte": (
            "La Lituanie a realise une transformation spectaculaire : de 36 % en 2010 a 14 % "
            "aujourd'hui. C'est l'un des progres les plus importants d'Europe. "
            "Mais attention : le taux NEET (jeunes completement decrochés) reste eleve a 12,5 %. "
            "Ca signifie que les progres beneficient surtout aux jeunes qui cherchent activement, "
            "pas a tous."
        ),
    },
    "LV": {
        "nom": "Lettonie",
        "flag": "LV",
        "texte": (
            "Meme histoire qu'en Lituanie voisine : enorme amelioration depuis 2010 (de 36 % "
            "a 15 %). Les pays baltes ont connu une croissance economique rapide grace a leur "
            "integration dans l'Union Europeenne et leur secteur tech dynamique. "
            "La Lettonie souffre aussi de beaucoup d'emigration de jeunes vers l'Ouest."
        ),
    },
    "LU": {
        "nom": "Luxembourg",
        "flag": "LU",
        "texte": (
            "Le Luxembourg est un cas particulier. C'est l'un des pays les plus riches du monde, "
            "pourtant son taux de chomage des jeunes monte a 22 %. Pourquoi ? Parce que beaucoup "
            "d'emplois qualifies sont occupes par des frontaliers (Belges, Francais, Allemands) "
            "qui font la navette. Les jeunes luxembourgeois doivent donc faire face a une "
            "concurrence internationale tres forte."
        ),
    },
    "SK": {
        "nom": "Slovaquie",
        "flag": "SK",
        "texte": (
            "La Slovaquie a progresse depuis 2010 (de 34 % a 15 %), mais reste inegale. "
            "Le gros probleme ici : sans diplome, c'est presque impossible — 55 % des jeunes "
            "sans diplome sont au chomage. C'est le taux le plus eleve d'Europe pour ce groupe. "
            "Avoir un bac ou plus change radicalement la donne en Slovaquie."
        ),
    },
    "BE": {
        "nom": "Belgique",
        "flag": "BE",
        "texte": (
            "La Belgique affiche 17 % de chomage des jeunes, mais cache de grandes differences "
            "internes. En Flandre (nord), les jeunes trouvent facilement du travail. En Wallonie "
            "et a Bruxelles, c'est beaucoup plus dur. Un jeune bruxellois sans diplome fait partie "
            "des profils les plus en difficulte d'Europe occidentale."
        ),
    },
    "HR": {
        "nom": "Croatie",
        "flag": "HR",
        "texte": (
            "La Croatie a fait un effort remarquable depuis son entree dans l'UE en 2013 "
            "(de 33 % a 18 %). Le tourisme est le grand moteur : Dubrovnik et la cote dalmate "
            "emploient enormement de jeunes l'ete. Mais ce sont souvent des emplois saisonniers : "
            "en hiver, le chomage remonte. La stabilite reste un defi."
        ),
    },
    "EE": {
        "nom": "Estonie",
        "flag": "EE",
        "texte": (
            "L'Estonie est connue comme le pays le plus numerique du monde — vote en ligne, "
            "administration 100 % digitale. Pourtant, le chomage des jeunes monte a 21 %, "
            "en hausse ces deux dernieres annees. La revolution numerique n'a pas protege les "
            "jeunes estoniens de la conjoncture economique difficile de la region baltique."
        ),
    },
    "PT": {
        "nom": "Portugal",
        "flag": "PT",
        "texte": (
            "Le Portugal a vecu une crise tres dure entre 2011 et 2015 (plus d'un jeune sur "
            "trois au chomage). Il s'en est bien sorti depuis, tombant a 19-20 %. Mais meme "
            "les diplomes ont du mal : 25 % des jeunes avec un diplome superieur sont sans emploi, "
            "ce qui pousse beaucoup d'entre eux a partir au Royaume-Uni ou en France."
        ),
    },
    "FR": {
        "nom": "France",
        "flag": "FR",
        "texte": (
            "En France, pres de 20 % des jeunes qui cherchent un emploi n'en trouvent pas. "
            "Concretement : dans une promotion de 20 jeunes diplomes qui postulent, 4 seront "
            "toujours sans emploi six mois plus tard. L'ecart est enorme selon le diplome : "
            "13 % de chomage pour les diplomes du superieur, mais 35 % pour ceux sans bac. "
            "Avoir un diplome en France, c'est multiplier par 2,5 ses chances de trouver un travail."
        ),
    },
    "EL": {
        "nom": "Grece",
        "flag": "EL",
        "texte": (
            "La Grece a vecu la pire crise economique d'Europe apres 2010 : a un moment, "
            "60 % des jeunes etaient au chomage. Aujourd'hui c'est 19 %, ce qui represente "
            "une amelioration reelle mais insuffisante. Le drame grec : meme les jeunes tres "
            "diplomes (40 % de chomage pour les titulaires d'un master ou d'une licence) "
            "n'arrivent pas a trouver de travail en Grece et emigrent en masse."
        ),
    },
    "IT": {
        "nom": "Italie",
        "flag": "IT",
        "texte": (
            "L'Italie est le grand malade de l'Europe du sud pour l'emploi des jeunes. "
            "20 % de chomage, et quasiment aucune amelioration depuis 2010. "
            "Le probleme de fond : les entreprises italiennes sont souvent familiales et "
            "petites, elles n'embauchent pas facilement. Un jeune Italien diplome a plus de "
            "chances de trouver un emploi a Paris ou a Berlin qu'a Rome ou Milan."
        ),
    },
    "FI": {
        "nom": "Finlande",
        "flag": "FI",
        "texte": (
            "La Finlande surprend avec 22 % — beaucoup pour un pays nordique tres riche. "
            "En partie, c'est parce que les Finlandais continuent leurs etudes tres longtemps "
            "et entrent tardivement sur le marche du travail. Les jeunes qui cherchent activement "
            "un emploi le trouvent generalement, mais la periode de recherche est plus longue "
            "qu'en Allemagne ou aux Pays-Bas."
        ),
    },
    "SE": {
        "nom": "Suede",
        "flag": "SE",
        "texte": (
            "La Suede affiche 24 % — un chiffre etonnant pour l'un des pays les plus riches d'Europe. "
            "L'explication : la Suede compte beaucoup d'etudiants qui cherchent un emploi "
            "a temps partiel et sont donc comptabilises dans les chomeurs. "
            "Autre facteur : l'integration des jeunes immigres dans le marche du travail "
            "reste difficile, ce qui tire le chiffre global vers le haut."
        ),
    },
    "ES": {
        "nom": "Espagne",
        "flag": "ES",
        "texte": (
            "L'Espagne est l'un des pays ou c'est le plus difficile pour les jeunes. "
            "Presque 1 jeune sur 4 est au chomage — imaginez une salle de classe "
            "de 24 eleves ou 6 ne trouveraient pas de travail apres leurs etudes. "
            "Bonne nouvelle : c'etait encore pire avant (42 % en 2013, pendant la crise). "
            "Mais 25 %, c'est encore trop. Beaucoup de jeunes Espagnols partent en Allemagne "
            "ou en France, emportant leur formation payee par l'Espagne avec eux."
        ),
    },
    "RO": {
        "nom": "Roumanie",
        "flag": "RO",
        "texte": (
            "La Roumanie est la situation la plus preoccupante d'Europe avec 26 % — "
            "et le taux NEET le plus eleve (16,5 % de jeunes completement decrochés). "
            "Ce qui rend la situation unique : le chomage n'a pas baisse depuis 2010. "
            "La Roumanie a un probleme structurel : les regions rurales sont tres pauvres "
            "et isolees. Un jeune qui grandit dans un village roumain a tres peu d'acces "
            "a une formation ou a un employeur. C'est un probleme de geographie autant "
            "qu'un probleme economique."
        ),
    },
}

# Ordre de tri par taux de chomage croissant
ORDRE = sorted(PAYS_INFO.keys(), key=lambda p: stats.get(p, {}).get("cho") or 99)

def niveau(cho):
    if cho is None: return ("gray", "?")
    if cho < 10:    return (GREEN,  "Favorable")
    if cho < 15:    return (BLUE,   "Correct")
    if cho < 20:    return (ORANGE, "Difficile")
    return          (RED,   "Tres difficile")

def fleche(delta):
    if delta is None or abs(delta) < 0.5: return ("→", SUB,    "Stable")
    if delta < 0:                          return ("↓", GREEN,  f"En baisse de {abs(delta):.1f} pts")
    return                                        ("↑", RED,    f"En hausse de {delta:.1f} pts")

def neet_badge(neet):
    if neet is None: return ""
    color = GREEN if neet < 8 else ORANGE if neet < 13 else RED
    return f'<span class="neet-badge" style="border-color:{color};color:{color}">{neet:.1f} % decrochés</span>'

# ── Generation des cartes pays ─────────────────────────────────────────────
def pays_card(code):
    info  = PAYS_INFO.get(code)
    if not info: return ""
    s     = stats.get(code, {})
    cho   = s.get("cho")
    delta = s.get("delta")
    cho_hi= s.get("cho_hi")
    cho_lo= s.get("cho_lo")
    neet  = s.get("neet")
    yr    = s.get("yr", "")
    color, etiquette = niveau(cho)
    arr, arr_col, arr_txt = fleche(delta)

    if cho is None:
        return ""

    # Barre de progression
    pct = min(cho / 35 * 100, 100)

    ed_html = ""
    if cho_hi and cho_lo:
        ed_html = f"""
        <div class="ed-compare">
          <div class="ed-row">
            <span class="ed-label">Avec un diplome superieur</span>
            <div class="ed-bar-wrap"><div class="ed-bar" style="width:{min(cho_hi/50*100,100):.0f}%;background:{GREEN}"></div></div>
            <span class="ed-val" style="color:{GREEN}">{cho_hi:.0f} %</span>
          </div>
          <div class="ed-row">
            <span class="ed-label">Sans diplome</span>
            <div class="ed-bar-wrap"><div class="ed-bar" style="width:{min(cho_lo/50*100,100):.0f}%;background:{RED}"></div></div>
            <span class="ed-val" style="color:{RED}">{cho_lo:.0f} %</span>
          </div>
        </div>"""

    return f"""
<div class="pays-card" id="{code}">
  <div class="pays-header">
    <div class="pays-title">
      <span class="pays-flag">&#127988;</span>
      <h3>{info['nom']}</h3>
    </div>
    <div class="pays-kpis">
      <div class="kpi-main">
        <span class="kpi-num" style="color:{color}">{cho:.0f} %</span>
        <span class="kpi-sub">de jeunes au chomage ({yr})</span>
      </div>
      <span class="etiquette" style="background:{color}22;color:{color};border:1px solid {color}">{etiquette}</span>
    </div>
  </div>
  <div class="barre-wrap">
    <div class="barre" style="width:{pct:.0f}%;background:linear-gradient(90deg,{color}88,{color})"></div>
  </div>
  <p class="pays-texte">{info['texte']}</p>
  <div class="pays-footer">
    <span class="tendance" style="color:{arr_col}">{arr} {arr_txt} (3 derniers ans)</span>
    {neet_badge(neet)}
    {ed_html}
  </div>
</div>"""


# ── Messages cles ──────────────────────────────────────────────────────────
MESSAGES = [
    {
        "icone": "🎓",
        "titre": "Le diplome, c'est votre meilleur bouclier",
        "texte": (
            "En Europe, un jeune sans diplome a en moyenne <strong>3 fois plus de risques</strong> "
            "d'etre au chomage qu'un jeune avec un diplome superieur. "
            "En Slovaquie, 55 jeunes sans diplome sur 100 n'ont pas d'emploi. "
            "En France, ce ratio est de 1 pour 3 : le diplome multiplie par 2,5 les chances de trouver un travail. "
            "<br><br>Ce n'est pas une question d'intelligence. C'est une question de signal : "
            "les employeurs utilisent le diplome comme un filtre, surtout quand ils reccoivent des dizaines de CV."
        ),
        "couleur": GREEN,
    },
    {
        "icone": "🤖",
        "titre": "L'IA va detruire des emplois. Mais pas tous, et pas de la meme facon",
        "texte": (
            "Les emplois les plus menaces par l'intelligence artificielle ? "
            "La comptabilite, la saisie de donnees, certains metiers de la finance, du droit et du conseil. "
            "Ce sont souvent des metiers qui recrutaient beaucoup de jeunes diplomes. "
            "<br><br>Les emplois les moins menaces ? Les metiers manuels complexes "
            "(plomberie, electricite, aide a la personne), et les metiers tres creatifs. "
            "Un robot peut rediger un rapport comptable. Il ne peut pas reparer une fuite d'eau chez vous. "
            "<br><br>Le paradoxe : les jeunes qui travaillent dans la tech (ceux qui <em>font</em> l'IA) "
            "sont aussi ceux qui risquent le plus d'etre remplaces par elle."
        ),
        "couleur": ORANGE,
    },
    {
        "icone": "🌍",
        "titre": "L'Europe n'est pas un seul pays. Les ecarts sont enormes",
        "texte": (
            "7 % de jeunes au chomage en Allemagne. 26 % en Roumanie. "
            "C'est comme comparer la salle de classe d'une ecole privee parisienne "
            "avec celle d'un lycee en zone difficile. Meme continent, monde different. "
            "<br><br>Ces ecarts ne sont pas pres de disparaitre. Les pays qui fonctionnent bien "
            "(Allemagne, Pays-Bas, Tcheque) ont mis des decennies a construire leurs systemes "
            "de formation professionnelle. On ne copie pas ca en quelques annees. "
            "<br><br>Et le probleme s'aggrave avec l'IA : les pays deja bien equipes "
            "vont adapter leurs travailleurs plus vite. Les autres risquent de prendre encore plus de retard."
        ),
        "couleur": BLUE,
    },
    {
        "icone": "🚪",
        "titre": "1 jeune sur 10 en Europe a ferme la porte. C'est le vrai probleme",
        "texte": (
            f"En Europe, {eu_neet:.0f} % des jeunes de 15-24 ans sont ce qu'on appelle des 'NEET' : "
            "ni au travail, ni en etudes, ni en formation. Ils ne cherchent meme plus. "
            "<br><br>En Roumanie, c'est 1 jeune sur 6. Imaginez : dans chaque classe de lycee, "
            "2 ou 3 eleves vont completement decrocher apres l'ecole, sans filet de securite. "
            "<br><br>Ce groupe est le plus vulnerable face a l'IA. Ils n'ont pas de diplome, "
            "pas d'experience, pas de reseau. Quand des emplois peu qualifies disparaissent "
            "a cause de l'automatisation, ce sont eux qui le sentent en premier."
        ),
        "couleur": PURPLE,
    },
    {
        "icone": "📈",
        "titre": "La bonne nouvelle : ca s'ameliore. Mais pas partout",
        "texte": (
            "En 2010, la moyenne europeenne du chomage des jeunes etait bien au-dessus de 20 %. "
            "Aujourd'hui, elle est autour de "
            f"<strong>{eu_cho:.0f} %</strong>. "
            "Des pays comme l'Irlande, la Lituanie, la Lettonie et la Pologne ont fait des progres enormes. "
            "<br><br>Mais la Roumanie stagne. L'Italie n'avance pas. Et les crises (COVID en 2020, "
            "inflation en 2022) ont regulierement efface des annees de progres. "
            "<br><br>L'objectif de l'Union Europeenne est de reduire le taux NEET sous les 9 %. "
            "On n'y est pas encore. Et avec l'arrivee de l'IA, l'objectif risque "
            "de devenir plus difficile a atteindre, pas plus facile."
        ),
        "couleur": GREEN,
    },
]

def message_card(m):
    return f"""
<div class="message-card" style="border-left:4px solid {m['couleur']}">
  <div class="message-header">
    <span class="message-icone">{m['icone']}</span>
    <h3 style="color:{m['couleur']}">{m['titre']}</h3>
  </div>
  <p class="message-texte">{m['texte']}</p>
</div>"""

# ── HTML final ─────────────────────────────────────────────────────────────
print("Generation HTML...")

pays_cards_html = "\n".join(pays_card(c) for c in ORDRE)
messages_html   = "\n".join(message_card(m) for m in MESSAGES)

nav_pays = "".join(
    f'<a href="#{c}">{PAYS_INFO[c]["nom"]}</a>'
    for c in ORDRE if c in PAYS_INFO
)

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Conclusions -- Emploi des jeunes en Europe</title>
<style>
*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:{BG}; color:{TEXT}; font-family:"Segoe UI",Arial,sans-serif;
       font-size:15px; line-height:1.75; max-width:1100px; margin:0 auto; padding:0 24px 60px; }}

/* ── Header ── */
.site-header {{ padding:36px 0 24px; border-bottom:3px solid {BLUE}; margin-bottom:36px; }}
.site-header h1 {{ font-size:26px; color:#fff; margin-bottom:8px; }}
.site-header p  {{ color:{SUB}; font-size:14px; }}

/* ── Sections ── */
.section-title {{ font-size:22px; color:#fff; margin:48px 0 8px; padding-bottom:12px;
                  border-bottom:2px solid {GRID}; }}
.section-intro {{ color:{SUB}; font-size:14px; margin-bottom:28px; }}

/* ── Navigation pays ── */
.nav-pays {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:32px; }}
.nav-pays a {{ background:{CARD}; color:{BLUE}; border:1px solid {GRID}; border-radius:20px;
               padding:5px 14px; font-size:12px; text-decoration:none; }}
.nav-pays a:hover {{ background:{BLUE}; color:#fff; }}

/* ── Grille pays ── */
.pays-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(480px, 1fr)); gap:20px; }}

/* ── Carte pays ── */
.pays-card {{ background:{CARD}; border-radius:12px; padding:22px 24px; }}
.pays-header {{ display:flex; justify-content:space-between; align-items:flex-start;
                margin-bottom:10px; flex-wrap:wrap; gap:10px; }}
.pays-title {{ display:flex; align-items:center; gap:10px; }}
.pays-flag  {{ font-size:24px; }}
.pays-title h3 {{ font-size:17px; color:#fff; font-weight:600; }}
.pays-kpis  {{ display:flex; align-items:center; gap:12px; }}
.kpi-main   {{ text-align:right; }}
.kpi-num    {{ font-size:28px; font-weight:700; display:block; line-height:1; }}
.kpi-sub    {{ font-size:11px; color:{SUB}; }}
.etiquette  {{ font-size:11px; font-weight:600; padding:4px 10px; border-radius:20px; white-space:nowrap; }}

.barre-wrap {{ background:{DARK}; border-radius:4px; height:5px; margin:12px 0 16px; overflow:hidden; }}
.barre      {{ height:100%; border-radius:4px; transition:width 1s; }}

.pays-texte {{ font-size:13.5px; color:{TEXT}; line-height:1.7; margin-bottom:14px; }}

.pays-footer {{ display:flex; flex-direction:column; gap:10px; }}
.tendance   {{ font-size:12px; font-weight:600; }}
.neet-badge {{ font-size:11px; font-weight:600; border:1px solid; border-radius:20px;
               padding:3px 10px; display:inline-block; width:fit-content; }}

/* ── Comparaison diplome ── */
.ed-compare {{ margin-top:4px; }}
.ed-row     {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
.ed-label   {{ font-size:11px; color:{SUB}; width:170px; flex-shrink:0; }}
.ed-bar-wrap{{ flex:1; background:{DARK}; border-radius:3px; height:8px; overflow:hidden; }}
.ed-bar     {{ height:100%; border-radius:3px; }}
.ed-val     {{ font-size:12px; font-weight:700; width:36px; text-align:right; flex-shrink:0; }}

/* ── Messages cles ── */
.messages {{ display:flex; flex-direction:column; gap:24px; }}
.message-card {{ background:{CARD}; border-radius:12px; padding:28px 32px; }}
.message-header {{ display:flex; align-items:center; gap:14px; margin-bottom:16px; }}
.message-icone  {{ font-size:28px; flex-shrink:0; }}
.message-card h3 {{ font-size:17px; font-weight:600; line-height:1.4; }}
.message-texte  {{ font-size:14px; color:{TEXT}; line-height:1.8; }}
.message-texte strong {{ color:#fff; }}
.message-texte em {{ color:{BLUE}; font-style:normal; }}

footer {{ text-align:center; padding:32px 0 0; color:{SUB}; font-size:12px;
          border-top:1px solid {GRID}; margin-top:48px; }}
</style>
</head>
<body>

<div class="site-header">
  <h1>Ce qu'on retient sur l'emploi des jeunes en Europe</h1>
  <p>Source : Eurostat &nbsp;|&nbsp; Jeunes de 15 a 24 ans &nbsp;|&nbsp; Donnees 2010-2025 &nbsp;|&nbsp; 27 pays de l'UE</p>
</div>

<!-- ══ SECTION 1 : PAYS ══ -->
<h2 class="section-title">La situation dans chaque pays</h2>
<p class="section-intro">
  Du plus facile au plus difficile pour un jeune de trouver un emploi.
  Le chiffre indique combien de jeunes sur 100, qui cherchent activement un emploi, ne le trouvent pas.
  Les barres de couleur en dessous du nom de chaque pays montrent la difference de chomage
  entre ceux qui ont un diplome superieur et ceux qui n'ont pas le baccalaureat.
</p>

<nav class="nav-pays">{nav_pays}</nav>

<div class="pays-grid">
{pays_cards_html}
</div>

<!-- ══ SECTION 2 : MESSAGES CLES ══ -->
<h2 class="section-title" style="margin-top:64px">Ce qu'on retient pour l'Europe</h2>
<p class="section-intro">
  Cinq idees simples, issues des donnees, sur l'emploi des jeunes et l'impact de l'intelligence artificielle.
</p>

<div class="messages">
{messages_html}
</div>

<footer>
  Analyse basee sur les donnees Eurostat (lfsa_urgaed, edat_lfse_22) &bull;
  Jeunes de 15 a 24 ans &bull; Derniere mise a jour des donnees : 2025
</footer>

</body>
</html>"""

OUT_FILE.write_text(html, encoding="utf-8")
print(f"Genere : {OUT_FILE}  ({OUT_FILE.stat().st_size // 1024} Ko)")
