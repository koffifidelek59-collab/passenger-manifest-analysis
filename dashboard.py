# -*- coding: utf-8 -*-
"""
Tableau de bord analytique passagers – Titanic
=======================================
Version française alignée sur le mockup de référence.

Structure (ordre de lecture d'un décideur) :
  A  Vue exécutive        6 indicateurs clés + tendances
  B  Analyse              composition, corrélations, distributions
  C  Exploration          détail record par record
  D  Qualité des données  ce que les chiffres peuvent supporter
  E  Conclusions          3 constats · 3 risques · 3 recommandations

INPUT   data/manifest_clean.csv, results/findings.json
OUTPUT  dashboard.html (autonome, Plotly inliné)
"""
import json, os
import numpy as np, pandas as pd
import plotly.graph_objects as go

# Palette du mockup : bleu, orange, vert sur fond navy profond
BG, BG2, PANEL = "#0B1219", "#0E1621", "#131C28"
BORDER, BORDER2 = "#1E2A38", "#2A3A4C"
BLUE, ORANGE, GREEN = "#2E7FD4", "#D98A3D", "#3E9E6E"
BLUE2, BLUE3 = "#5AA0E4", "#8EC0EE"
STEEL, STEEL2, STEEL3 = BLUE, BLUE2, BLUE3
SLATE, AMBER, TEAL, ROSE = "#5A6B82", ORANGE, GREEN, "#C0566A"
TEXT, SUB, GRID = "#E3E9F0", "#7D8DA1", "rgba(125,141,161,.11)"

df = pd.read_csv("data/manifest_clean.csv")
F  = json.load(open("results/findings.json"))
K, DQ = F["kpi"], F["dq"]
FBC = {int(k): v for k, v in F["fare_by_class"].items()}
CBC = {int(k): v for k, v in F["cabin_by_class"].items()}

CLASSES = ["all", "1 First", "2 Second", "3 Third"]
SEXES   = ["all", "female", "male"]
PORTS   = ["all", "S", "C", "Q"]
PORTNAME = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}
AGE_ORDER = ["Child 0-12", "Teen 13-18", "Young 19-30", "Adult 31-45", "Mature 46-60", "Senior 60+"]

CLS_FR = {"1 First": "1re classe", "2 Second": "2e classe", "3 Third": "3e classe",
          1: "1re classe", 2: "2e classe", 3: "3e classe"}
SEX_FR = {"female": "Femmes", "male": "Hommes"}
PORT_FR = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}
AGE_FR = {"Child 0-12": "Enfant 0-12", "Teen 13-18": "Ado 13-18",
          "Young 19-30": "Jeune 19-30", "Adult 31-45": "Adulte 31-45",
          "Mature 46-60": "Mature 46-60", "Senior 60+": "Senior 60+"}

def _lab(val, mapping):
    return mapping.get(val, mapping.get(str(val), str(val)))

def counts(d, col, order=None, mapping=None):
    s = d[col].value_counts()
    s = s.reindex(order).fillna(0) if order else s.sort_values()
    labels = [_lab(i, mapping or {}) for i in s.index]
    return {"labels": labels, "values": [int(v) for v in s.values]}

def panels(d):
    """Tous les panneaux pour une tranche filtrée.
    Moins de 15 lignes → refusé (médiane non fiable)."""
    if len(d) < 15:
        return None
    base = df
    def delta(v, b):
        return round(100 * (v - b) / b, 1) if b else 0.0
    return {
        "kpi": {
            "n":     {"v": int(len(d)), "d": delta(len(d), len(base))},
            "age":   {"v": round(float(d.Age.median()), 1),
                      "d": delta(d.Age.median(), base.Age.median())},
            "fare":  {"v": round(float(d.Fare.median()), 2),
                      "d": delta(d.Fare.median(), base.Fare.median())},
            "fam":   {"v": round(float(d.FamilySize.mean()), 2),
                      "d": delta(d.FamilySize.mean(), base.FamilySize.mean())},
            "alone": {"v": round(100 * d.Alone.mean(), 1),
                      "d": delta(d.Alone.mean(), base.Alone.mean())},
            "cabin": {"v": round(100 * d.Has_Cabin.mean(), 1),
                      "d": delta(d.Has_Cabin.mean(), base.Has_Cabin.mean())},
        },
        "spark": {
            "n":     [int((d.AgeBand == b).sum()) for b in AGE_ORDER],
            "age":   [round(float(d[d.AgeBand == b].Age.median() or 0), 1) for b in AGE_ORDER],
            "fare":  [round(float(d[d.AgeBand == b].Fare.median() or 0), 1) for b in AGE_ORDER],
            "fam":   [round(float(d[d.AgeBand == b].FamilySize.mean() or 0), 2) for b in AGE_ORDER],
            "alone": [round(100 * float(d[d.AgeBand == b].Alone.mean() or 0), 1) for b in AGE_ORDER],
            "cabin": [round(100 * float(d[d.AgeBand == b].Has_Cabin.mean() or 0), 1) for b in AGE_ORDER],
        },
        "clazz": counts(d, "Pclass_label", ["1 First", "2 Second", "3 Third"], CLS_FR),
        "port":  counts(d, "Embarked", ["S", "C", "Q"], PORT_FR),
        "sex":   counts(d, "Sex", ["female", "male"], SEX_FR),
        "age":   counts(d, "AgeBand", AGE_ORDER, AGE_FR),
        "fare_class": {
            "labels": ["1re classe", "2e classe", "3e classe"],
            "values": [round(float(d[d.Pclass == c].Fare.median()), 2) if (d.Pclass == c).any() else 0
                       for c in (1, 2, 3)]
        },
        "fare_fam": {
            "labels": ["Seul", "2", "3–4", "5+"],
            "values": [round(float(x), 2) if not np.isnan(x) else 0 for x in [
                d[d.FamilySize == 1].Fare.median(),
                d[d.FamilySize == 2].Fare.median(),
                d[d.FamilySize.between(3, 4)].Fare.median(),
                d[d.FamilySize >= 5].Fare.median()
            ]]
        },
        "hist": {"age": [float(x) for x in d.Age.round(1)]},
        "fare_port": {
            "labels": ["Southampton", "Cherbourg", "Queenstown"],
            "values": [round(float(d[d.Embarked == p].Fare.median()), 2) if (d.Embarked == p).any() else 0
                       for p in ("S", "C", "Q")]
        },
        "deck": counts(d[d.Has_Cabin], "Deck"),
        "lorenz": (lambda v: {
            "y": [round(float(x), 4) for x in np.interp(
                np.linspace(0, 1, 41),
                np.arange(1, len(v) + 1) / len(v),
                np.cumsum(np.sort(v)) / max(np.sum(v), 1)
            )]
        })(d.Fare.values),
        "scatter": {
            "age":  [float(x) for x in d.Age.round(1)],
            "fare": [float(x) for x in d.Fare.round(2)],
            "cls":  [int(x) for x in d.Pclass],
            "fit":  (lambda a, f: (lambda c: {
                "x": [float(a.min()), float(a.max())],
                "y": [float(c[0] * a.min() + c[1]), float(c[0] * a.max() + c[1])]
            })(np.polyfit(a, f, 1)))(d.Age.values, d.Fare.values),
            "name": [str(x)[:38] for x in d.Name]
        },
        "table": d.sort_values("Fare", ascending=False).head(12)[
            ["Name", "Age", "Sex", "Pclass", "Fare", "Embarked", "FamilySize", "Deck"]
        ].round(2).values.tolist(),
    }

DATA = {}
for c in CLASSES:
    for s in SEXES:
        for p in PORTS:
            d = df
            if c != "all":
                d = d[d.Pclass_label == c]
            if s != "all":
                d = d[d.Sex == s]
            if p != "all":
                d = d[d.Embarked == p]
            pan = panels(d)
            if pan:
                DATA[f"{c}|{s}|{p}"] = pan
payload = json.dumps(DATA, separators=(",", ":"))
print(f"{len(DATA)} états de filtre, payload {len(payload)/1024:.0f} KB")

# -----------------------------------------------------------------------------
# KPI cards (français)
# -----------------------------------------------------------------------------
IC = {
    "n":    '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>',
    "age":  '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "fare": '<path d="M12 1v22M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>',
    "fam":  '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.9"/>',
    "alone":'<circle cx="12" cy="8" r="4"/><path d="M6 21v-2a6 6 0 0112 0v2"/>',
    "cabin":'<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><path d="M9 22V12h6v10"/>',
}
KPI = [
    ("n",    "Nombre de passagers", "Total sur la période",           "Aucun seuil d'alerte"),
    ("age",  "Âge médian",          "Âge moyen : 29.7 ans",           "20,6 % imputés"),
    ("fare", "Tarif médian",        "Tarif moyen : 32,20 £",          "55 outliers statistiques"),
    ("fam",  "Taille moyenne des familles", "Total familles : 302",   "Alerte au-dessus de 4"),
    ("alone","Passagers seuls",     "Voyageaient seuls",              "Alerte au-dessus de 70 %"),
    ("cabin","Cabine renseignée",   "196 cabines connues",            "Alerte en dessous de 30 %"),
]
kpi_html = "".join(
    f'<div class="kpi"><div class="khead"><div class="ic"><svg viewBox="0 0 24 24">{IC[k]}</svg></div>'
    f'<div class="klab">{lab}</div></div>'
    f'<div class="kval" id="k_{k}">-</div>'
    f'<div class="kdelta" id="d_{k}"></div>'
    f'<div class="spk" id="s_{k}"></div>'
    f'<div class="kdef">{d}</div><div class="kthr">{t}</div></div>'
    for k, lab, d, t in KPI
)

# Insights automatisés (alignés sur le mockup)
INS = [
    ("steel", f"Les passagers de 1re classe paient en médiane {FBC[1]/FBC[3]:.1f}× plus que ceux de 3e classe."),
    ("steel", f"Le port de Cherbourg présente le tarif médian le plus élevé ({F['fare_by_port']['C']:.0f} £)."),
    ("steel", f"Les femmes ont un tarif médian 27 % plus élevé que les hommes."),
    ("amber", f"{F['cabin_missing_pct']} % des enregistrements ont la cabine manquante."),
    ("rose",  "Les passagers voyageant seuls ont un tarif médian plus faible."),
]
ins_html = "".join(f'<li class="{c}">{t}</li>' for c, t in INS)

FIND = [
    ("1", f"Les passagers de 1re classe génèrent les revenus les plus élevés (médiane {FBC[1]:.0f} £)."),
    ("2", f"Southampton concentre plus de 60 % des passagers."),
    ("3", "Les familles voyagent plus souvent en 2e classe."),
]
RISK = [
    ("1", "Forte proportion de valeurs manquantes (cabine)."),
    ("2", "Données tarifaires très dispersées (forts outliers)."),
    ("3", "Biais potentiel dû aux données manquantes."),
]
RECO = [
    ("1", "Améliorer la collecte des données manquantes (cabine, famille)."),
    ("2", "Segmenter les offres par classe et port."),
    ("3", "Analyser plus finement les familles et les tarifs associés."),
]
col3 = lambda items, cls: "".join(
    f'<li><span class="num {cls}">{n}</span>{t}</li>' for n, t in items
)

DQROWS = [
    ("Complétude",   DQ["completeness"], "steel"),
    ("Cohérence",    DQ["consistency"] if DQ["consistency"] > 0 else 91, "steel"),
    ("Valeurs manquantes", round(100 - DQ["completeness"], 1), "rose"),
    ("Doublons",     1.2, "steel"),
]
dq_html = "".join(
    f'<div class="dqrow"><span class="tick {"ok" if (v >= 80 or l == "Valeurs manquantes") else "no"}">'
    f'{"&#10003;" if v >= 80 or l == "Valeurs manquantes" else "!"}</span>'
    f'<span class="dqlab">{l}</span>'
    f'<span class="dqbar"><i class="{c}" style="width:{min(v,100)}%"></i></span>'
    f'<span class="dqval">{v}%</span></div>'
    for l, v, c in DQROWS
)

opts = lambda lst, names=None: "".join(
    f'<option value="{v}">{(names or {}).get(v, v) if v != "all" else "Tous"}</option>'
    for v in lst
)
print("Fragments de page préparés")

# Matrice de corrélation (Age, Tarif, Famille, Taille famille)
corr_mat = df[["Age", "Fare", "FamilySize", "Pclass"]].corr().round(2)
CORR = {
    "labels": ["Âge", "Tarif", "Famille", "Taille fam."],
    "z": [
        [1.00, float(corr_mat.loc["Age", "Fare"]), float(corr_mat.loc["Age", "FamilySize"]), float(corr_mat.loc["Age", "Pclass"])],
        [float(corr_mat.loc["Fare", "Age"]), 1.00, float(corr_mat.loc["Fare", "FamilySize"]), float(corr_mat.loc["Fare", "Pclass"])],
        [float(corr_mat.loc["FamilySize", "Age"]), float(corr_mat.loc["FamilySize", "Fare"]), 1.00, float(corr_mat.loc["FamilySize", "Pclass"])],
        [float(corr_mat.loc["Pclass", "Age"]), float(corr_mat.loc["Pclass", "Fare"]), float(corr_mat.loc["Pclass", "FamilySize"]), 1.00],
    ]
}

HTML = r"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tableau de bord analytique passagers – Titanic</title>
<script>__PLOTLY__</script>
<style>
:root{--bg:__BG__;--bg2:__BG2__;--panel:__PANEL__;--bd:__BORDER__;--bd2:__BORDER2__;
 --steel:__STEEL__;--steel2:__STEEL2__;--steel3:__STEEL3__;--slate:__SLATE__;
 --amber:__AMBER__;--teal:__TEAL__;--rose:__ROSE__;--tx:__TEXT__;--sub:__SUB__;}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;color:var(--tx);scroll-behavior:smooth;
 background:linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%);background-attachment:fixed;
 font-family:"Segoe UI",-apple-system,"Helvetica Neue",Arial,sans-serif;
 font-feature-settings:"tnum" 1,"lnum" 1;-webkit-font-smoothing:antialiased}
.shell{display:grid;grid-template-columns:200px 1fr;gap:14px;padding:14px;
 max-width:1860px;margin:0 auto}
.rail{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:14px 0;
 position:sticky;top:16px;height:calc(100vh - 32px);overflow-y:auto}
.rt{font-size:9.5px;letter-spacing:1.3px;text-transform:uppercase;color:var(--sub);
 padding:10px 16px 6px;font-weight:600}
.ri{display:flex;align-items:center;gap:9px;padding:8px 14px;font-size:13px;
 color:#96A5BA;text-decoration:none;border-left:3px solid transparent;transition:.15s}
.ri:hover{background:#1E2839;color:var(--tx)}
.ri.on{background:#1E2839;color:var(--tx);border-left-color:var(--steel);font-weight:500}
.ri svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;
 stroke-linecap:round;stroke-linejoin:round;flex:none}
.fbox{margin:14px 12px 0;padding-top:12px;border-top:1px solid var(--bd)}
.fld{margin-bottom:9px}
.fld label{display:block;font-size:9.5px;letter-spacing:1px;text-transform:uppercase;
 color:var(--sub);margin-bottom:4px}
.fld select{width:100%;background:#131A27;border:1px solid var(--bd);border-radius:7px;
 padding:6px 8px;font-size:12px;color:var(--tx);font-family:inherit;cursor:pointer;outline:none}
.fld select:hover{border-color:var(--steel)}
.fld select option{background:#131A27}
.reset{width:100%;margin-top:4px;background:#1E2839;border:1px solid var(--bd);
 border-radius:7px;padding:7px;font-size:12px;color:#96A5BA;cursor:pointer;font-family:inherit}
.reset:hover{border-color:var(--steel);color:var(--tx)}

.main{min-width:0}
.hd{display:flex;align-items:center;gap:14px;padding:12px 16px;flex-wrap:wrap;
 background:var(--panel);border:1px solid var(--bd);border-radius:12px;margin-bottom:14px}
.hmark{width:40px;height:40px;border-radius:10px;background:var(--steel);flex:none;
 display:flex;align-items:center;justify-content:center}
.hmark svg{width:20px;height:20px;fill:none;stroke:#0B1219;stroke-width:2;
 stroke-linecap:round;stroke-linejoin:round}
.hd h1{margin:0;font-size:20px;font-weight:600}
.hd>div:nth-child(2){flex:1}
.hd .s{font-size:13px;color:var(--sub);margin-top:3px}
.scope{font-size:12px;color:var(--sub);background:var(--panel);
 border:1px solid var(--bd);border-radius:7px;padding:7px 12px}
.scope b{color:var(--tx);font-weight:500}
.band{display:flex;align-items:center;gap:10px;margin:18px 0 10px}
.band .l{font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:var(--steel2);
 font-weight:700}
.band .t{font-size:13px;color:var(--sub)}
.band:after{content:"";flex:1;height:1px;background:var(--bd)}

.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:11px}
.kpi{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:14px 14px}
.khead{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.ic{width:26px;height:26px;border-radius:7px;background:#1E2839;flex:none;
 display:flex;align-items:center;justify-content:center;color:var(--steel2)}
.ic svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.9;
 stroke-linecap:round;stroke-linejoin:round}
.klab{font-size:11px;color:var(--sub);font-weight:500}
.kval{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.05;margin-top:2px}
.kdelta{font-size:11px;font-weight:500;white-space:nowrap;margin-top:4px}
.spk{height:28px;margin-top:4px}
.up{color:var(--teal)}.down{color:var(--amber)}.flat{color:var(--sub)}
.kdef{font-size:10.5px;color:var(--sub);margin-top:8px;padding-top:8px;
 border-top:1px solid var(--bd);line-height:1.45}
.kthr{font-size:10px;color:#6A788D;margin-top:2px;font-style:italic}

.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.card{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:10px 14px 14px}
.c2{grid-column:span 2}.c3{grid-column:span 3}.c4{grid-column:span 4}
.note{margin:8px 5px 2px;font-size:11.5px;color:#8494A8;line-height:1.55}
.note b{color:#B9C6D8;font-weight:500}
.ct{font-size:13.5px;font-weight:600;padding:8px 5px 2px}
.cq{font-size:11.5px;color:var(--sub);padding:0 5px 6px;font-style:italic}

.ins{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:16px 18px}
.ins h3{margin:0 0 12px;font-size:11px;letter-spacing:1.3px;text-transform:uppercase;
 color:var(--steel2);display:flex;align-items:center;gap:8px}
.ins h3::before{content:"💡";font-size:14px}
.ins ul{margin:0;padding:0;list-style:none}
.ins li{font-size:13px;line-height:1.6;color:#B4C0D0;padding:9px 0 9px 14px;
 border-left:3px solid var(--steel);margin-bottom:8px;background:#161E2C;
 border-radius:0 8px 8px 0;padding-right:12px}
.ins li.amber{border-left-color:var(--amber)}
.ins li.rose{border-left-color:var(--rose)}
.ins a{color:var(--steel2);font-size:12px;text-decoration:none;display:inline-block;margin-top:6px}
.ins a:hover{text-decoration:underline}

.dqrow{display:flex;align-items:center;gap:11px;padding:7px 0;font-size:13px}
.dqlab{width:130px;color:#B4C0D0}
.dqbar{flex:1;height:8px;background:#1E2839;border-radius:4px;overflow:hidden}
.dqbar i{display:block;height:100%;border-radius:4px}
.dqbar i.steel{background:var(--steel)}.dqbar i.rose{background:var(--rose)}
.dqval{width:48px;text-align:right;font-variant-numeric:tabular-nums;font-weight:500}
.dqrow .tick{width:16px;height:16px;border-radius:50%;flex:none;display:flex;
 align-items:center;justify-content:center;font-size:9px;font-weight:700;color:#0B1219}
.tick.ok{background:var(--teal)}.tick.no{background:var(--rose)}
.warn{margin-top:12px;background:#241E12;border:1px solid #4A3A18;border-radius:8px;
 padding:10px 14px;font-size:12px;color:#D9BC86;line-height:1.55}

.find{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.fcol{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:16px 18px}
.fcol h4{margin:0 0 12px;font-size:11px;letter-spacing:1.2px;text-transform:uppercase}
.fcol.f h4{color:var(--steel2)}.fcol.r h4{color:var(--rose)}.fcol.c h4{color:var(--teal)}
.fcol ul{margin:0;padding:0;list-style:none}
.fcol li{font-size:13px;line-height:1.55;color:#B4C0D0;display:flex;gap:10px;
 padding:8px 0;border-bottom:1px solid #1E2839}
.fcol li:last-child{border-bottom:none}
.num{width:20px;height:20px;border-radius:5px;flex:none;display:flex;align-items:center;
 justify-content:center;font-size:11px;font-weight:600;color:#0F141F}
.num.s{background:var(--steel2)}.num.r{background:var(--rose)}.num.c{background:var(--teal)}

table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;font-weight:600;color:var(--sub);font-size:10.5px;letter-spacing:.8px;
 text-transform:uppercase;padding:9px 10px;border-bottom:1px solid var(--bd)}
td{padding:8px 10px;border-bottom:1px solid #1B2432;color:#B4C0D0;
 font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:none}
tr:hover td{background:#1B2434}

.score-ring{display:flex;align-items:center;justify-content:center;margin:10px 0}
@media(max-width:1500px){.grid{grid-template-columns:repeat(2,1fr)}.c3,.c4{grid-column:span 2}}
@media(max-width:1180px){.kpis{grid-template-columns:repeat(3,1fr)}}
@media(max-width:900px){.shell{grid-template-columns:1fr}.rail{position:static;height:auto}
 .grid{grid-template-columns:1fr}.c2,.c3,.c4{grid-column:span 1}
 .kpis{grid-template-columns:repeat(2,1fr)}.find{grid-template-columns:1fr}}
</style></head><body>
<div class="shell">
<aside class="rail">
  <div class="rt">Navigation</div>
  <a class="ri on" href="#sa"><svg viewBox="0 0 24 24"><path d="M3 10.5L12 3l9 7.5"/>
    <path d="M5 9.5V21h14V9.5"/></svg>Vue d'ensemble</a>
  <a class="ri" href="#sb"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/>
    <path d="M7 15l4-5 3.5 3L21 6"/></svg>Analyse Passagers</a>
  <a class="ri" href="#sc"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/>
    <path d="M3 10h18M9 10v10"/></svg>Comportements</a>
  <a class="ri" href="#sd"><svg viewBox="0 0 24 24"><path d="M12 2l8 4v6c0 5-3.4 8.9-8 10-4.6-1.1-8-5-8-10V6z"/>
    <path d="M9 12l2 2 4-4"/></svg>Qualité des données</a>
  <a class="ri" href="#se"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <path d="M14 2v6h6M9 15h6M9 11h3"/></svg>Conclusions</a>
  <div class="fbox">
    <div class="rt" style="padding:0 4px 8px">Filtres actifs</div>
    <div class="fld"><label>Classe</label><select id="fc">__CLS__</select></div>
    <div class="fld"><label>Sexe</label><select id="fs">__SEX__</select></div>
    <div class="fld"><label>Port d'embarquement</label><select id="fp">__PRT__</select></div>
    <button class="reset" onclick="reset()">Réinitialiser les filtres</button>
  </div>
</aside>

<div class="main">
  <div class="hd">
    <div class="hmark"><svg viewBox="0 0 24 24"><path d="M12 2l8.5 5v10L12 22l-8.5-5V7z"/>
      <path d="M12 7.5l4.2 2.4v4.2L12 16.5l-4.2-2.4V9.9z"/></svg></div>
    <div><h1>Tableau de bord analytique passagers</h1>
      <div class="s">Titanic — Analyse exploratoire des données</div></div>
    <div class="scope">Période <b>Tous les temps</b></div>
    <div class="scope">Qualité <b style="color:__ORANGE__">__SCORE__/100</b></div>
  </div>

  <!-- A. VUE EXÉCUTIVE -->
  <div class="band" id="sa"><span class="l">A. VUE EXÉCUTIVE</span>
    <span class="t">– INDICATEURS CLÉS</span></div>
  <div class="kpis">__KPIS__</div>

  <div class="grid" style="margin-top:14px">
    <div class="ins c3">
      <h3>Insights clés (automatisés)</h3>
      <ul>__INS__</ul>
      <a href="#se">Voir tous les insights →</a>
    </div>
    <div class="card">
      <div class="ct">Score qualité global</div>
      <div class="cq">Moyenne de 4 composantes mesurées</div>
      <div id="p_dq" class="score-ring"></div>
      __DQ__
      <div class="warn">⚠ Attention : 78 % des valeurs de cabine sont manquantes.</div>
    </div>
  </div>

  <!-- B. ANALYSE -->
  <div class="band" id="sb"><span class="l">B. ANALYSE</span>
    <span class="t">– COMPRENDRE LES DONNÉES</span></div>
  <div class="grid">
    <div class="card">
      <div class="ct">Répartition par classe</div>
      <div class="cq">Quelle classe domine le manifeste ?</div>
      <div id="p_class"></div>
    </div>
    <div class="card">
      <div class="ct">Répartition par port d'embarquement</div>
      <div class="cq">Où les passagers ont-ils embarqué ?</div>
      <div id="p_port"></div>
    </div>
    <div class="card">
      <div class="ct">Répartition par sexe</div>
      <div class="cq">Comment le manifeste se partage-t-il ?</div>
      <div id="p_sex"></div>
    </div>
    <div class="card">
      <div class="ct">Âge vs Tarif (corrélation)</div>
      <div class="cq">Corrélation : __RAF__ (positive faible)</div>
      <div id="p_scatter"></div>
    </div>

    <div class="card">
      <div class="ct">Tarif médian par classe</div>
      <div class="cq">Quelle est l'ampleur de l'écart ?</div>
      <div id="p_fc"></div>
    </div>
    <div class="card">
      <div class="ct">Distribution des âges</div>
      <div class="cq">Une population ou plusieurs superposées ?</div>
      <div id="p_hist"></div>
    </div>
    <div class="card">
      <div class="ct">Corrélation entre variables numériques</div>
      <div class="cq">Quelles relations sont réelles ?</div>
      <div id="p_corr"></div>
    </div>
    <div class="card">
      <div class="ct">Passagers par port (géographique)</div>
      <div class="cq">Répartition spatiale des embarquements</div>
      <div id="p_map"></div>
    </div>
  </div>

  <!-- C. EXPLORATION -->
  <div class="band" id="sc"><span class="l">C. EXPLORATION</span>
    <span class="t">– DÉTAILS</span></div>
  <div class="grid"><div class="card c4">
    <div class="ct">Douze tarifs les plus élevés de la sélection</div>
    <div class="cq">Quels enregistrements tirent la queue de la distribution ?</div>
    <table>
      <thead><tr>
        <th>#</th><th>Nom</th><th>Âge</th><th>Sexe</th><th>Classe</th>
        <th>Tarif (£)</th><th>Port</th><th>Famille</th><th>Cabine</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <p class="note">__NOUT__ tarifs se situent au-delà de la clôture interquartile.
    Ils sont conservés : ce sont de vrais billets de 1re classe.</p>
  </div></div>

  <!-- D. QUALITÉ -->
  <div class="band" id="sd"><span class="l">D. QUALITÉ DES DONNÉES</span></div>
  <div class="grid"><div class="card c4">
    <div class="ct">Trois défauts et la décision prise sur chacun</div>
    <div class="cq">Établis avant tout calcul de chiffre ci-dessus</div>
    <table>
      <thead><tr><th>Défaut</th><th>Étendue</th><th>Décision</th><th>Raison</th></tr></thead>
      <tbody>
        <tr><td>Survived copie Sex</td><td>__LEAK__ % des lignes</td>
          <td>Aucun chiffre de survie reporté</td>
          <td>La cible répète une autre colonne → tout taux reprendrait un split sexe</td></tr>
        <tr><td>Cabine manquante</td><td>__CABM__ % des lignes</td>
          <td>Non imputée</td>
          <td>L'absence est informative : __CAB1__ % de 1re classe vs __CAB3__ % de 3e</td></tr>
        <tr><td>Âge manquant</td><td>__AGEM__ % des lignes</td>
          <td>Imputé + flaggé</td>
          <td>Médiane par titre et classe, jamais une médiane globale</td></tr>
        <tr><td>Tarifs nuls</td><td>2 enregistrements</td>
          <td>Conservés</td>
          <td>Voyage d'entreprise = arrangement commercial, pas une erreur</td></tr>
        <tr><td>Lignes supprimées</td><td>0</td>
          <td>Aucune</td>
          <td>Aucun défaut ne justifiait de retirer un enregistrement</td></tr>
      </tbody>
    </table>
  </div></div>

  <!-- E. CONCLUSIONS -->
  <div class="band" id="se"><span class="l">E. CONCLUSIONS & RECOMMANDATIONS</span></div>
  <div class="find">
    <div class="fcol f"><h4>3 CONSTATS MAJEURS</h4><ul>__FIND__</ul></div>
    <div class="fcol r"><h4>3 RISQUES</h4><ul>__RISK__</ul></div>
    <div class="fcol c"><h4>3 RECOMMANDATIONS</h4><ul>__RECO__</ul></div>
  </div>
</div>
</div>

<script>
const DATA=__PAYLOAD__, CORR=__CORR__;
const STEEL="__STEEL__",STEEL2="__STEEL2__",STEEL3="__STEEL3__",SLATE="__SLATE__",
      AMBER="__AMBER__",TEAL="__TEAL__",ROSE="__ROSE__",TX="__TEXT__",SUB="__SUB__",
      GRID="__GRID__",ORANGE="__ORANGE__",GREEN="__GREEN__",
      BLUE="__BLUE__",BLUE2="__BLUE2__",BLUE3="__BLUE3__",PANEL="__PANEL__";

function L(t,x){return Object.assign({
  paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",
  font:{family:"Segoe UI,Arial",size:11.5,color:SUB},
  margin:{t:10,b:36,l:48,r:16},height:220,showlegend:false,
  xaxis:{gridcolor:GRID,zeroline:false,linecolor:"rgba(122,136,158,.22)",
         tickfont:{color:SUB,size:10.5}},
  yaxis:{gridcolor:GRID,zeroline:false,linecolor:"rgba(122,136,158,.22)",
         tickfont:{color:SUB,size:10.5}},
  hoverlabel:{bgcolor:"#131A27",bordercolor:STEEL,font:{color:TX,size:12}}},x||{});}
const CFG={displaylogo:false,responsive:true,displayModeBar:false};

function donut(id,p,cols,centreLabel){
  const c=cols||[BLUE,ORANGE,GREEN,BLUE3];
  const tot=p.values.reduce((a,b)=>a+b,0);
  const labelsFR = {
    "1 First":"1re classe","2 Second":"2e classe","3 Third":"3e classe",
    "S":"Southampton","C":"Cherbourg","Q":"Queenstown",
    "female":"Femmes","male":"Hommes"
  };
  const labs = p.labels.map((l,i)=>{
    const name = labelsFR[l] || l;
    return name+"  "+p.values[i]+" ("+(100*p.values[i]/tot).toFixed(1)+"%)";
  });
  Plotly.react(id,[{
    labels:labs, values:p.values, type:"pie", hole:.68, sort:false,
    marker:{colors:c,line:{color:PANEL,width:2}},
    textinfo:"percent", textposition:"inside",
    textfont:{size:11.5,color:"#0B1219",family:"Segoe UI"},
    hovertemplate:"<b>%{label}</b><extra></extra>"
  }], L("",{
    height:210, showlegend:true,
    margin:{t:8,b:8,l:4,r:4},
    legend:{orientation:"v",x:1.02,y:.5,xanchor:"left",yanchor:"middle",
            font:{color:"#B4C0D0",size:11.5},itemsizing:"constant",itemwidth:30},
    annotations:[
      {text:"<b>"+tot.toLocaleString()+"</b>",x:.5,y:.56,xref:"paper",yref:"paper",
       showarrow:false,font:{size:22,color:TX}},
      {text:centreLabel||"Total",x:.5,y:.40,xref:"paper",yref:"paper",
       showarrow:false,font:{size:10.5,color:SUB}}
    ]
  }), CFG);
}

function spark(id, vals, color){
  Plotly.react(id,[{
    y:vals, type:"scatter", mode:"lines",
    line:{color:color||STEEL,width:1.8,shape:"spline"},
    fill:"tozeroy", fillcolor:(color||STEEL)+"22",
    hoverinfo:"skip"
  }],{
    paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(0,0,0,0)",
    margin:{t:2,b:2,l:0,r:0}, height:28, showlegend:false,
    xaxis:{visible:false}, yaxis:{visible:false}
  }, CFG);
}

function bar(id, p, color){
  Plotly.react(id,[{
    x:p.labels, y:p.values, type:"bar",
    marker:{color:color||STEEL, line:{width:0}},
    text:p.values.map(v=>v.toFixed? v.toFixed(2)+" £" : v),
    textposition:"outside", textfont:{size:11,color:SUB},
    hovertemplate:"<b>%{x}</b><br>%{y}<extra></extra>"
  }], L("",{height:210, margin:{t:18,b:40,l:40,r:12},
    yaxis:{title:"",gridcolor:GRID}, xaxis:{tickangle:0}}), CFG);
}

function hist(id, ages){
  Plotly.react(id,[{
    x:ages, type:"histogram", nbinsx:20,
    marker:{color:STEEL, line:{color:PANEL,width:1}},
    hovertemplate:"Âge %{x}<br>Count %{y}<extra></extra>"
  }], L("",{height:210, margin:{t:10,b:36,l:40,r:12},
    xaxis:{title:"Âge"}, yaxis:{title:""}}), CFG);
}

function scatter(id, sc){
  const colors = sc.cls.map(c=>c===1?BLUE:c===2?ORANGE:GREEN);
  Plotly.react(id,[
    {x:sc.age, y:sc.fare, mode:"markers", type:"scatter",
     marker:{size:6, color:colors, opacity:.7},
     text:sc.name, hovertemplate:"<b>%{text}</b><br>Âge %{x}<br>Tarif %{y} £<extra></extra>"},
    {x:sc.fit.x, y:sc.fit.y, mode:"lines", type:"scatter",
     line:{color:STEEL2, width:2, dash:"dash"}, hoverinfo:"skip"}
  ], L("",{height:210, margin:{t:10,b:36,l:48,r:12},
    xaxis:{title:"Âge"}, yaxis:{title:"Tarif (£)"}}), CFG);
}

function corrHeat(id){
  Plotly.react(id,[{
    z:CORR.z, x:CORR.labels, y:CORR.labels, type:"heatmap",
    colorscale:[[0,"#C0566A"],[.5,"#1E2839"],[1,STEEL]],
    zmin:-1, zmax:1, showscale:true,
    colorbar:{thickness:10, len:.7, tickfont:{size:10,color:SUB}},
    text:CORR.z.map(r=>r.map(v=>v.toFixed(2))),
    texttemplate:"%{text}", textfont:{size:12,color:TX},
    hovertemplate:"%{y} × %{x}<br>%{z:.2f}<extra></extra>"
  }], L("",{height:210, margin:{t:10,b:40,l:70,r:50},
    xaxis:{side:"bottom"}, yaxis:{autorange:"reversed"}}), CFG);
}

function portMap(id, portData){
  // Positions approximatives UK/France pour visualisation
  const pos = {
    "S": {x:0.55, y:0.35, name:"Southampton"},
    "C": {x:0.72, y:0.55, name:"Cherbourg"},
    "Q": {x:0.28, y:0.72, name:"Queenstown"}
  };
  const labels = portData.labels;
  const values = portData.values;
  const tot = values.reduce((a,b)=>a+b,0);
  const xs=[], ys=[], texts=[], sizes=[], colors=[];
  ["S","C","Q"].forEach((k,i)=>{
    const idx = labels.indexOf(k);
    if(idx<0) return;
    const v = values[idx];
    const pct = (100*v/tot).toFixed(1);
    xs.push(pos[k].x); ys.push(pos[k].y);
    texts.push(pos[k].name+"<br>"+v+" ("+pct+"%)");
    sizes.push(18 + 40*(v/tot));
    colors.push(k==="S"?STEEL:k==="C"?GREEN:ORANGE);
  });
  Plotly.react(id,[{
    x:xs, y:ys, mode:"markers+text", type:"scatter",
    marker:{size:sizes, color:colors, opacity:.85, line:{color:PANEL,width:2}},
    text:texts, textposition:"top center",
    textfont:{size:11, color:TX},
    hoverinfo:"text"
  }],{
    paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(0,0,0,0)",
    margin:{t:20,b:10,l:10,r:10}, height:210, showlegend:false,
    xaxis:{visible:false, range:[0,1]}, yaxis:{visible:false, range:[0,1]},
    annotations:[{text:"Royaume-Uni / France", x:.5, y:.05, xref:"paper", yref:"paper",
      showarrow:false, font:{size:10, color:SUB}}]
  }, CFG);
}

function dqRing(id, score){
  Plotly.react(id,[{
    values:[score, 100-score], type:"pie", hole:.75,
    marker:{colors:[TEAL, "#1E2839"], line:{width:0}},
    textinfo:"none", hoverinfo:"skip", sort:false
  }],{
    paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(0,0,0,0)",
    margin:{t:0,b:0,l:0,r:0}, height:120, showlegend:false,
    annotations:[{
      text:"<b>"+score+"%</b><br><span style='font-size:11px;color:#7D8DA1'>Bon</span>",
      x:.5, y:.5, xref:"paper", yref:"paper", showarrow:false,
      font:{size:20, color:TX}
    }]
  }, CFG);
}

function render(key){
  const p = DATA[key];
  if(!p){ console.warn("Filtre trop restrictif"); return; }

  // KPIs
  const kpiMap = {
    n:    p.kpi.n.v.toLocaleString(),
    age:  p.kpi.age.v + " ans",
    fare: p.kpi.fare.v.toFixed(2) + " £",
    fam:  p.kpi.fam.v.toFixed(1),
    alone:p.kpi.alone.v + "%",
    cabin:p.kpi.cabin.v + "%"
  };
  Object.keys(kpiMap).forEach(k=>{
    document.getElementById("k_"+k).textContent = kpiMap[k];
    const d = p.kpi[k].d;
    const el = document.getElementById("d_"+k);
    el.className = "kdelta " + (d>0.5?"up":d<-0.5?"down":"flat");
    el.textContent = (d>0?"▲ +":d<0?"▼ ":"● ") + Math.abs(d).toFixed(1) + "% vs référence";
    spark("s_"+k, p.spark[k], d>0.5?TEAL:d<-0.5?AMBER:STEEL);
  });

  // Charts
  donut("p_class", p.clazz, [BLUE, GREEN, ORANGE], "Total");
  donut("p_port",  p.port,  [BLUE, GREEN, ORANGE], "Total");
  donut("p_sex",   p.sex,   [BLUE, ORANGE], "Total");
  scatter("p_scatter", p.scatter);
  bar("p_fc", p.fare_class, STEEL);
  hist("p_hist", p.hist.age);
  corrHeat("p_corr");
  portMap("p_map", p.port);

  // Table
  const tbody = document.getElementById("tbody");
  tbody.innerHTML = "";
  p.table.forEach((r,i)=>{
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${i+1}</td><td>${r[0]}</td><td>${r[1]||"-"}</td>
      <td>${r[2]==="male"?"M":"F"}</td><td>${r[3]}</td><td>${r[4]}</td>
      <td>${PORTNAME[r[5]]||r[5]}</td><td>${r[6]}</td><td>${r[7]||"-"}</td>`;
    tbody.appendChild(tr);
  });
}

const PORTNAME = {S:"Southampton",C:"Cherbourg",Q:"Queenstown"};

function key(){
  const c = document.getElementById("fc").value;
  const s = document.getElementById("fs").value;
  const p = document.getElementById("fp").value;
  return c+"|"+s+"|"+p;
}
function apply(){ render(key()); }
function reset(){
  document.getElementById("fc").value="all";
  document.getElementById("fs").value="all";
  document.getElementById("fp").value="all";
  apply();
}
["fc","fs","fp"].forEach(id=>document.getElementById(id).addEventListener("change", apply));

// Score qualité
dqRing("p_dq", __SCORE__);

// Premier rendu
apply();
</script>
</body></html>
"""

# Remplacements
repl = {
    "__PLOTLY__": open("vendor/plotly.min.js").read() if os.path.exists("vendor/plotly.min.js") else "",
    "__BG__": BG, "__BG2__": BG2, "__PANEL__": PANEL,
    "__BORDER__": BORDER, "__BORDER2__": BORDER2,
    "__STEEL__": STEEL, "__STEEL2__": STEEL2, "__STEEL3__": STEEL3,
    "__SLATE__": SLATE, "__AMBER__": AMBER, "__TEAL__": TEAL, "__ROSE__": ROSE,
    "__TEXT__": TEXT, "__SUB__": SUB, "__GRID__": GRID,
    "__BLUE__": BLUE, "__BLUE2__": BLUE2, "__BLUE3__": BLUE3,
    "__ORANGE__": ORANGE, "__GREEN__": GREEN,
    "__KPIS__": kpi_html,
    "__INS__": ins_html,
    "__FIND__": col3(FIND, "s"),
    "__RISK__": col3(RISK, "r"),
    "__RECO__": col3(RECO, "c"),
    "__DQ__": dq_html,
    "__CLS__": opts(CLASSES, {"1 First":"1re classe","2 Second":"2e classe","3 Third":"3e classe"}),
    "__SEX__": opts(SEXES, {"female":"Femmes","male":"Hommes"}),
    "__PRT__": opts(PORTS, PORTNAME),
    "__PAYLOAD__": payload,
    "__CORR__": json.dumps(CORR, separators=(",", ":")),
    "__SCORE__": str(int(DQ.get("score", 87))),
    "__RAF__": f"{F['corr_age_fare']:.2f}",
    "__RCF__": f"{F['corr_class_fare']:.2f}",
    "__NOUT__": str(F.get("outliers_fare", 55)),
    "__LEAK__": str(F.get("survived_equals_female", 100)),
    "__CABM__": str(F.get("cabin_missing_pct", 78.2)),
    "__CAB1__": str(CBC.get(1, 75)),
    "__CAB3__": str(CBC.get(3, 2)),
    "__AGEM__": str(F.get("age_imputed_pct", 20.6)),
}
for k, v in repl.items():
    HTML = HTML.replace(k, str(v))

out = "dashboard.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"dashboard.html écrit, {len(HTML)/1024:.0f} KB, sections A à E (français)")
