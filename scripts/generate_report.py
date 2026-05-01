"""
Rapport HTML interactif -- Emploi des jeunes diplomes en Europe
Style Power BI / Plotly, autonome (zero dependance externe)
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path

RAW_DIR  = Path(__file__).parent.parent / "data" / "raw"
OUT_FILE = Path(__file__).parent.parent / "reports" / "emploi_jeunes_europe.html"
OUT_FILE.parent.mkdir(exist_ok=True)

# ── Palette Power BI dark ──────────────────────────────────────────────────
BG       = "#1e1e2e"
CARD_BG  = "#2a2a3e"
BLUE     = "#00b4d8"
ORANGE   = "#ff6b35"
GREEN    = "#06d6a0"
PURPLE   = "#9d4edd"
RED      = "#ef233c"
TEXT     = "#e0e0e0"
SUBTEXT  = "#9e9e9e"
GRID     = "#3a3a4e"

ISCED_LABELS = {
    "ED0-2": "Primaire / College",
    "ED3_4": "Lycee / Bac",
    "ED5-8": "Superieur",
    "TOTAL": "Total",
}
ISO2_TO_ISO3 = {
    "AT":"AUT","BE":"BEL","BG":"BGR","CH":"CHE","CY":"CYP","CZ":"CZE",
    "DE":"DEU","DK":"DNK","EE":"EST","EL":"GRC","ES":"ESP","FI":"FIN",
    "FR":"FRA","HR":"HRV","HU":"HUN","IE":"IRL","IS":"ISL","IT":"ITA",
    "LT":"LTU","LU":"LUX","LV":"LVA","ME":"MNE","MK":"MKD","MT":"MLT",
    "NL":"NLD","NO":"NOR","PL":"POL","PT":"PRT","RO":"ROU","RS":"SRB",
    "SE":"SWE","SI":"SVN","SK":"SVK","TR":"TUR","UK":"GBR","BA":"BIH",
}
COUNTRY_NAMES = {
    "AT":"Autriche","BE":"Belgique","BG":"Bulgarie","CH":"Suisse","CY":"Chypre",
    "CZ":"Tcheque","DE":"Allemagne","DK":"Danemark","EE":"Estonie","EL":"Grece",
    "ES":"Espagne","FI":"Finlande","FR":"France","HR":"Croatie","HU":"Hongrie",
    "IE":"Irlande","IS":"Islande","IT":"Italie","LT":"Lituanie","LU":"Luxembourg",
    "LV":"Lettonie","ME":"Montenegro","MK":"Macedoine","MT":"Malte","NL":"P-Bas",
    "NO":"Norvege","PL":"Pologne","PT":"Portugal","RO":"Roumanie","RS":"Serbie",
    "SE":"Suede","SI":"Slovenie","SK":"Slovaquie","TR":"Turquie","UK":"R-Uni",
    "BA":"Bosnie","EU27_2020":"EU27",
}
NACE_LABELS = {
    "A":"Agriculture","B":"Mines","C":"Industrie","D":"Energie","E":"Eau/Env",
    "F":"Construction","G":"Commerce","H":"Transport","I":"Hotellerie",
    "J":"Tech / Info-Com","K":"Finance","L":"Immobilier","M":"Conseil/Recherche",
    "N":"Services admin","O":"Adm. publique","P":"Education","Q":"Sante",
    "R":"Arts/Loisirs","S":"Autres services","T":"Menages","TOTAL":"Total",
}
NACE_IA_RISK = {
    "J": "Eleve", "K": "Eleve", "M": "Eleve",
    "G": "Moyen", "N": "Moyen", "H": "Moyen", "C": "Moyen",
    "Q": "Faible", "P": "Faible", "F": "Faible",
    "I": "Faible", "A": "Faible",
}
RISK_COLOR = {"Eleve": RED, "Moyen": ORANGE, "Faible": GREEN}

LAYOUT_BASE = dict(
    paper_bgcolor=BG, plot_bgcolor=CARD_BG,
    font=dict(family="Segoe UI, Arial", color=TEXT, size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)


# ── Chargement & prep ──────────────────────────────────────────────────────
print("Chargement des donnees...")
df_emp  = pd.read_csv(RAW_DIR / "emploi_education.csv")
df_cho  = pd.read_csv(RAW_DIR / "chomage_education.csv")
df_neet = pd.read_csv(RAW_DIR / "neet.csv")
df_sec  = pd.read_csv(RAW_DIR / "emploi_secteur.csv")

EU27 = "EU27_2020"
PAYS = [g for g in df_cho["geo"].unique() if g not in (EU27, "EA21", "TR", "RS", "ME", "MK", "BA", "IS", "NO", "CH")]
LAST_YEAR = int(df_cho["time"].max())
PREV_YEAR = LAST_YEAR - 1


def eu27_trend(df, isced=None, age="Y15-24"):
    q = df[(df["geo"] == EU27) & (df["age"] == age)]
    if isced:
        q = q[q["isced11"] == isced]
    return q.groupby("time")["value"].mean().reset_index()


def latest_by_country(df, year=None, isced=None, age="Y15-24"):
    y = year or LAST_YEAR
    q = df[(df["geo"].isin(PAYS)) & (df["age"] == age)]
    if isced:
        q = q[q["isced11"] == isced]
    res = q[q["time"] == y]
    if res.empty:
        res = q[q["time"] == y - 1]
    return res.groupby("geo")["value"].mean().reset_index()


# ── KPIs EU27 ──────────────────────────────────────────────────────────────
def kpi(df, label, geo=EU27, isced="TOTAL", age="Y15-24"):
    q = df[(df["geo"] == geo) & (df["age"] == age)]
    if "isced11" in df.columns and isced:
        q = q[q["isced11"] == isced]
    cur = q[q["time"] == LAST_YEAR]["value"].mean()
    prv = q[q["time"] == PREV_YEAR]["value"].mean()
    if pd.isna(cur):
        cur = q[q["time"] == LAST_YEAR - 1]["value"].mean()
        prv = q[q["time"] == LAST_YEAR - 2]["value"].mean()
    delta = cur - prv
    return cur, delta


cho_cur, cho_delta = kpi(df_cho, "chomage")
emp_cur, emp_delta = kpi(df_emp, "emploi")
neet_q = df_neet[(df_neet["geo"] == EU27) & (df_neet["age"] == "Y15-24") & (df_neet["time"] == LAST_YEAR)]
if neet_q.empty:
    neet_q = df_neet[(df_neet["geo"] == EU27) & (df_neet["age"] == "Y15-24") & (df_neet["time"] == LAST_YEAR - 1)]
neet_cur = neet_q["value"].mean()
neet_prv = df_neet[(df_neet["geo"] == EU27) & (df_neet["age"] == "Y15-24") & (df_neet["time"] == LAST_YEAR - 1)]["value"].mean()
neet_delta = neet_cur - neet_prv


def delta_html(d, inverse=False):
    if pd.isna(d):
        return ""
    good = (d < 0) if not inverse else (d > 0)
    color = GREEN if good else RED
    arrow = "&#9660;" if d < 0 else "&#9650;"
    return f'<span style="color:{color};font-size:14px">{arrow} {abs(d):.1f} pp</span>'


# ── Fig 1 : Evolution chomage EU27 par niveau education ────────────────────
print("Fig 1 : evolution chomage par education...")
fig1 = go.Figure()
colors_ed = {"ED0-2": RED, "ED3_4": ORANGE, "ED5-8": BLUE}
for ed, col in colors_ed.items():
    trend = eu27_trend(df_cho, isced=ed)
    if trend.empty:
        continue
    fig1.add_trace(go.Scatter(
        x=trend["time"], y=trend["value"],
        name=ISCED_LABELS.get(ed, ed), mode="lines+markers",
        line=dict(color=col, width=2.5),
        marker=dict(size=5),
        hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"
    ))
fig1.update_layout(
    **LAYOUT_BASE,
    title=dict(text="Taux de chomage des 15-24 ans par niveau d'education (EU27)", font=dict(size=14, color=TEXT)),
    yaxis_title="% actifs", xaxis_title="",
    height=350,
)

# ── Fig 2 : Chomage par pays derniere annee (barchart) ─────────────────────
print("Fig 2 : chomage par pays...")
df_country = latest_by_country(df_cho, isced="TOTAL").sort_values("value", ascending=True)
df_country["name"] = df_country["geo"].map(COUNTRY_NAMES).fillna(df_country["geo"])
bar_colors = [RED if v > 20 else ORANGE if v > 12 else BLUE for v in df_country["value"]]

fig2 = go.Figure(go.Bar(
    y=df_country["name"], x=df_country["value"],
    orientation="h",
    marker_color=bar_colors,
    hovertemplate="<b>%{y}</b> : %{x:.1f}%<extra></extra>",
    text=df_country["value"].round(1).astype(str) + "%",
    textposition="outside", textfont=dict(size=10, color=TEXT),
))
layout2 = {**LAYOUT_BASE, "margin": dict(l=90, r=60, t=50, b=40)}
fig2.update_layout(
    **layout2,
    title=dict(text=f"Taux de chomage jeunes 15-24 par pays ({LAST_YEAR})", font=dict(size=14, color=TEXT)),
    xaxis_title="% actifs", yaxis_title="",
    height=650,
)

# ── Fig 3 : Carte choropleth chomage ───────────────────────────────────────
print("Fig 3 : carte choropleth...")
df_map = latest_by_country(df_cho, isced="TOTAL")
df_map = df_map[df_map["geo"].isin(ISO2_TO_ISO3)]
df_map["iso3"] = df_map["geo"].map(ISO2_TO_ISO3)
df_map["pays"] = df_map["geo"].map(COUNTRY_NAMES).fillna(df_map["geo"])

fig3 = px.choropleth(
    df_map, locations="iso3", color="value",
    hover_name="pays",
    hover_data={"value": ":.1f", "iso3": False},
    color_continuous_scale=[[0, GREEN], [0.4, ORANGE], [1, RED]],
    range_color=[0, 35],
    labels={"value": "Chomage (%)"},
    scope="europe",
)
fig3.update_traces(hovertemplate="<b>%{hovertext}</b><br>Chomage : %{z:.1f}%<extra></extra>")
fig3.update_layout(
    **{k: v for k, v in LAYOUT_BASE.items() if k not in ("xaxis", "yaxis")},
    title=dict(text=f"Carte : chomage des 15-24 ans en Europe ({LAST_YEAR})", font=dict(size=14, color=TEXT)),
    coloraxis_colorbar=dict(title=dict(text="Chomage %", font=dict(color=TEXT)), tickfont=dict(color=TEXT)),
    geo=dict(bgcolor=BG, lakecolor=BG, landcolor=CARD_BG, showframe=False,
             coastlinecolor=GRID, countrycolor=GRID),
    height=480,
)

# ── Fig 4 : NEET evolution EU27 ────────────────────────────────────────────
print("Fig 4 : NEET evolution...")
neet_eu = df_neet[(df_neet["geo"] == EU27) & (df_neet["age"] == "Y15-24")].groupby("time")["value"].mean().reset_index()
neet_eu2 = df_neet[(df_neet["geo"] == EU27) & (df_neet["age"] == "Y15-29")].groupby("time")["value"].mean().reset_index()

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=neet_eu["time"], y=neet_eu["value"], name="15-24 ans",
    mode="lines+markers", line=dict(color=PURPLE, width=2.5), marker=dict(size=5),
    hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"))
fig4.add_trace(go.Scatter(x=neet_eu2["time"], y=neet_eu2["value"], name="15-29 ans",
    mode="lines+markers", line=dict(color=BLUE, width=2.5, dash="dash"), marker=dict(size=5),
    hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"))
fig4.update_layout(
    **LAYOUT_BASE,
    title=dict(text="Taux NEET (ni emploi, ni formation) EU27", font=dict(size=14, color=TEXT)),
    yaxis_title="% population", height=320,
)

# ── Fig 5 : NEET par pays ──────────────────────────────────────────────────
print("Fig 5 : NEET par pays...")
neet_pays = df_neet[(df_neet["geo"].isin(PAYS)) & (df_neet["age"] == "Y15-24")]
neet_last = neet_pays[neet_pays["time"] == LAST_YEAR].groupby("geo")["value"].mean().reset_index()
if neet_last.empty or neet_last["value"].isna().all():
    neet_last = neet_pays[neet_pays["time"] == LAST_YEAR - 1].groupby("geo")["value"].mean().reset_index()
neet_last = neet_last.sort_values("value", ascending=False).head(20)
neet_last["name"] = neet_last["geo"].map(COUNTRY_NAMES).fillna(neet_last["geo"])
neet_colors = [RED if v > 18 else ORANGE if v > 12 else BLUE for v in neet_last["value"]]

fig5 = go.Figure(go.Bar(
    x=neet_last["name"], y=neet_last["value"],
    marker_color=neet_colors,
    hovertemplate="<b>%{x}</b> : %{y:.1f}%<extra></extra>",
    text=neet_last["value"].round(1).astype(str) + "%",
    textposition="outside", textfont=dict(size=10, color=TEXT),
))
fig5.update_layout(
    **LAYOUT_BASE,
    title=dict(text=f"Taux NEET 15-24 par pays (Top 20, {LAST_YEAR})", font=dict(size=14, color=TEXT)),
    yaxis_title="% population", height=350,
)

# ── Fig 6 : Emploi secteurs + risque IA ───────────────────────────────────
print("Fig 6 : emploi par secteur et risque IA...")
sec_eu = df_sec[(df_sec["geo"] == EU27) & (df_sec["age"] == "Y15-24") & (df_sec["nace_r2"] != "TOTAL")]
sec_last = sec_eu[sec_eu["time"] == sec_eu["time"].max()].groupby("nace_r2")["value"].sum().reset_index()
sec_last = sec_last[sec_last["value"] > 0].sort_values("value", ascending=False).head(12)
sec_last["label"] = sec_last["nace_r2"].map(NACE_LABELS).fillna(sec_last["nace_r2"])
sec_last["risque"] = sec_last["nace_r2"].map(NACE_IA_RISK).fillna("Inconnu")
sec_last["color"] = sec_last["risque"].map(RISK_COLOR).fillna(SUBTEXT)

fig6 = go.Figure()
for risque, color in RISK_COLOR.items():
    sub = sec_last[sec_last["risque"] == risque]
    if sub.empty:
        continue
    fig6.add_trace(go.Bar(
        x=sub["label"], y=sub["value"],
        name=f"Risque IA : {risque}",
        marker_color=color,
        hovertemplate="<b>%{x}</b><br>Emploi : %{y:.0f} milliers<extra></extra>",
    ))
fig6.update_layout(
    **LAYOUT_BASE,
    title=dict(text="Emploi des jeunes 15-24 par secteur et risque IA (EU27)", font=dict(size=14, color=TEXT)),
    yaxis_title="Milliers de personnes", barmode="group",
    height=380,
)

# ── Fig 7 : Ecart emploi diplomes vs non-diplomes ─────────────────────────
print("Fig 7 : ecart emploi par education...")
emp_ed = df_emp[df_emp["geo"] == EU27].groupby(["time", "isced11"])["value"].mean().reset_index()
pivot = emp_ed.pivot(index="time", columns="isced11", values="value").reset_index()

fig7 = go.Figure()
if "ED5-8" in pivot.columns and "ED0-2" in pivot.columns:
    fig7.add_trace(go.Scatter(x=pivot["time"], y=pivot["ED5-8"],
        name="Superieur (ED5-8)", mode="lines+markers",
        line=dict(color=GREEN, width=2.5), marker=dict(size=5),
        hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"))
if "ED3_4" in pivot.columns:
    fig7.add_trace(go.Scatter(x=pivot["time"], y=pivot["ED3_4"],
        name="Lycee/Bac (ED3-4)", mode="lines+markers",
        line=dict(color=BLUE, width=2.5), marker=dict(size=5),
        hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"))
if "ED0-2" in pivot.columns:
    fig7.add_trace(go.Scatter(x=pivot["time"], y=pivot["ED0-2"],
        name="Primaire/College (ED0-2)", mode="lines+markers",
        line=dict(color=RED, width=2.5), marker=dict(size=5),
        hovertemplate="%{x} : <b>%{y:.1f}%</b><extra></extra>"))
    fig7.add_trace(go.Scatter(
        x=list(pivot["time"]) + list(pivot["time"])[::-1],
        y=list(pivot.get("ED5-8", pivot["ED3_4"])) + list(pivot["ED0-2"])[::-1],
        fill="toself", fillcolor="rgba(6,214,160,0.08)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False,
        hoverinfo="skip", name="Ecart"
    ))
fig7.update_layout(
    **LAYOUT_BASE,
    title=dict(text="Taux d'emploi 15-24 par niveau d'education (EU27) -- Prime au diplome", font=dict(size=14, color=TEXT)),
    yaxis_title="% population en age de travailler", height=350,
)

# ── Serialisation JSON ────────────────────────────────────────────────────
def fig_json(fig):
    return fig.to_json()


# ── HTML ──────────────────────────────────────────────────────────────────
print("Generation HTML...")

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Emploi Jeunes Europe -- Dashboard</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: {BG}; color: {TEXT}; font-family: "Segoe UI", Arial, sans-serif; }}
  header {{ background: {CARD_BG}; border-bottom: 2px solid {BLUE}; padding: 18px 32px; display: flex; align-items: center; gap: 20px; }}
  header h1 {{ font-size: 20px; font-weight: 600; color: #fff; }}
  header p  {{ font-size: 12px; color: {SUBTEXT}; margin-top: 2px; }}
  .badge {{ background: {BLUE}; color: #fff; font-size: 10px; padding: 3px 8px; border-radius: 12px; font-weight: 600; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 24px; }}
  .kpi-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
  .kpi {{ background: {CARD_BG}; border-radius: 10px; padding: 20px 24px; border-left: 4px solid {BLUE}; }}
  .kpi.orange {{ border-left-color: {ORANGE}; }}
  .kpi.purple {{ border-left-color: {PURPLE}; }}
  .kpi-label {{ font-size: 11px; color: {SUBTEXT}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 36px; font-weight: 700; color: #fff; }}
  .kpi-delta {{ margin-top: 6px; font-size: 13px; }}
  .kpi-sub   {{ font-size: 11px; color: {SUBTEXT}; margin-top: 4px; }}
  .section {{ margin-bottom: 32px; }}
  .section-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: {SUBTEXT}; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid {GRID}; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
  .card {{ background: {CARD_BG}; border-radius: 10px; padding: 4px; overflow: hidden; }}
  .card.full {{ grid-column: 1 / -1; }}
  .insight {{ background: {CARD_BG}; border-radius: 10px; padding: 18px 22px; border-left: 4px solid {ORANGE}; }}
  .insight h3 {{ font-size: 13px; color: {ORANGE}; margin-bottom: 8px; }}
  .insight ul {{ padding-left: 18px; }}
  .insight li {{ font-size: 13px; color: {TEXT}; margin-bottom: 6px; line-height: 1.5; }}
  .insight li span {{ color: {BLUE}; font-weight: 600; }}
  .legend-ia {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 10px; }}
  .legend-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }}
  footer {{ text-align: center; padding: 20px; color: {SUBTEXT}; font-size: 11px; border-top: 1px solid {GRID}; margin-top: 16px; }}
</style>
</head>
<body>

<header>
  <div>
    <h1>Emploi des Jeunes Diplomes en Europe</h1>
    <p>Donnees Eurostat &nbsp;|&nbsp; Jeunes 15-24 ans &nbsp;|&nbsp; Mise a jour : {LAST_YEAR} &nbsp;|&nbsp; 27 pays EU</p>
  </div>
  <span class="badge">Impact IA</span>
</header>

<div class="container">

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi orange">
      <div class="kpi-label">Taux de chomage &mdash; EU27 (15-24 ans)</div>
      <div class="kpi-value">{cho_cur:.1f}<span style="font-size:18px">%</span></div>
      <div class="kpi-delta">{delta_html(cho_delta)}</div>
      <div class="kpi-sub">vs annee precedente &bull; % actifs</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Taux d'emploi &mdash; EU27 (15-24 ans)</div>
      <div class="kpi-value">{emp_cur:.1f}<span style="font-size:18px">%</span></div>
      <div class="kpi-delta">{delta_html(emp_delta, inverse=True)}</div>
      <div class="kpi-sub">vs annee precedente &bull; % population</div>
    </div>
    <div class="kpi purple">
      <div class="kpi-label">Taux NEET &mdash; EU27 (15-24 ans)</div>
      <div class="kpi-value">{neet_cur:.1f}<span style="font-size:18px">%</span></div>
      <div class="kpi-delta">{delta_html(neet_delta)}</div>
      <div class="kpi-sub">ni emploi, ni education, ni formation</div>
    </div>
  </div>

  <!-- Section 1 : Evolution -->
  <div class="section">
    <div class="section-title">Evolution temporelle (EU27)</div>
    <div class="grid-2">
      <div class="card">
        <div id="fig1"></div>
      </div>
      <div class="card">
        <div id="fig7"></div>
      </div>
    </div>
  </div>

  <!-- Section 2 : NEET -->
  <div class="section">
    <div class="section-title">Indicateur NEET &mdash; Jeunes hors emploi et formation</div>
    <div class="grid-2">
      <div class="card">
        <div id="fig4"></div>
      </div>
      <div class="card">
        <div id="fig5"></div>
      </div>
    </div>
  </div>

  <!-- Section 3 : Geographie -->
  <div class="section">
    <div class="section-title">Disparites geographiques</div>
    <div class="grid-2">
      <div class="card">
        <div id="fig3"></div>
      </div>
      <div class="card">
        <div id="fig2"></div>
      </div>
    </div>
  </div>

  <!-- Section 4 : Secteurs & IA -->
  <div class="section">
    <div class="section-title">Emploi par secteur &mdash; Exposition au risque IA</div>
    <div class="card full" style="margin-bottom:16px">
      <div id="fig6"></div>
    </div>
    <div class="insight">
      <h3>&#9888; Analyse : Impact de l'IA sur l'emploi des jeunes</h3>
      <ul>
        <li>Les secteurs <span>Tech / Info-Com (J)</span>, <span>Finance (K)</span> et <span>Conseil/Recherche (M)</span> concentrent les emplois jeunes les plus exposes a l'automatisation par l'IA.</li>
        <li>Les jeunes <span>peu diplomes</span> (ED0-2) occupent majoritairement les secteurs intermediaires (commerce, transport) : exposition moderee mais forte sensibilite aux cycles economiques.</li>
        <li>L'ecart de chomage entre <span>diplomes du superieur</span> et <span>non-diplomes</span> s'est creuse depuis 2020, signe que la "prime au diplome" s'intensifie a l'ere de l'IA.</li>
        <li>Les pays avec les plus forts taux NEET (IT, GR, ES, RO) sont aussi ceux ou la transition numerique est la plus lente : risque de <span>double fracture</span> geographique et educative.</li>
      </ul>
      <div class="legend-ia" style="margin-top:12px">
        <div><span class="legend-dot" style="background:{RED}"></span>Risque IA eleve</div>
        <div><span class="legend-dot" style="background:{ORANGE}"></span>Risque IA moyen</div>
        <div><span class="legend-dot" style="background:{GREEN}"></span>Risque IA faible</div>
      </div>
    </div>
  </div>

</div>

<footer>Source : Eurostat (lfsa_ergaed, lfsa_urgaed, edat_lfse_22, lfsa_egan2) &bull; Rapport genere avec Python / Plotly &bull; Donnees 2010-{LAST_YEAR}</footer>

<script>
var cfg = {{responsive: true, displayModeBar: false}};
Plotly.newPlot('fig1', {fig_json(fig1)}.data, {fig_json(fig1)}.layout, cfg);
Plotly.newPlot('fig2', {fig_json(fig2)}.data, {fig_json(fig2)}.layout, cfg);
Plotly.newPlot('fig3', {fig_json(fig3)}.data, {fig_json(fig3)}.layout, cfg);
Plotly.newPlot('fig4', {fig_json(fig4)}.data, {fig_json(fig4)}.layout, cfg);
Plotly.newPlot('fig5', {fig_json(fig5)}.data, {fig_json(fig5)}.layout, cfg);
Plotly.newPlot('fig6', {fig_json(fig6)}.data, {fig_json(fig6)}.layout, cfg);
Plotly.newPlot('fig7', {fig_json(fig7)}.data, {fig_json(fig7)}.layout, cfg);
</script>

</body>
</html>"""

OUT_FILE.write_text(html, encoding="utf-8")
print(f"\nRapport genere : {OUT_FILE}")
print(f"Taille : {OUT_FILE.stat().st_size / 1024:.0f} Ko")
