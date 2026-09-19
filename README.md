# Manifeste passagers : analyse de données et tableau de bord

**KOUAME Koffi Fidele** · Stage d'analyse de données · koffifidelek59@gmail.com

418 enregistrements · **Python uniquement**

> Le tableau de bord interactif (`dashboard.html`) est **entièrement en français**.

---

# Passenger Manifest: Data Analysis and Dashboard

**KOUAME Koffi Fidele** · Data Analysis Internship · koffifidelek59@gmail.com

418 passenger records · **Python only**

---

## Deliverables

| Required | Delivered | File |
| :--- | :--- | :--- |
| Python code | Commented notebook, executed, plus two scripts | `Passenger_Manifest_Analysis.ipynb`, `analysis.py`, `dashboard.py` |
| Cleaned dataset | 418 rows, 24 columns, no row deleted | `data/manifest_clean.csv` |
| Interactive dashboard | 8 panels, 3 cross-filters, opens in any browser | `dashboard.html` |
| Key insights | Five insights with recommendations | `INSIGHTS.md` |

**Tools.** pandas, NumPy, Matplotlib, Plotly. No Excel, no Power BI, no Tableau at
any stage, as the brief requires.

## Start here

Double-click `dashboard.html`. Self-contained: no server, no Python, no install.
Three filters, class, sex and port, update **every KPI and every chart at once**.

For the analysis, open `Passenger_Manifest_Analysis.ipynb` with the Colab badge at
the top and run every cell.

## The finding that shapes the whole study

**`Survived` is an exact copy of `Sex`.** 100% of rows. Two of the four cells of the
contingency table are empty.

This is target leakage, and it is invisible to a missing-value audit. The consequence
runs through everything: **no survival rate by any segment is reported**, because
every such figure would restate the sex split of that segment and nothing more.

Producing a model with a perfect score would have been the easy path. Reporting the
defect is the correct one.

## Cleaning decisions

| Column | Missing | Decision | Why |
| :--- | ---: | :--- | :--- |
| `Age` | 86, 20.6% | Imputed by median of Title and Pclass | Title carries life stage, class correlates with age. A global median would give a three-year-old the age of an officer |
| `Fare` | 1 | Imputed by median of Pclass and Embarked | Fare is set by class and route |
| `Cabin` | 327, 78.2% | **Not imputed** | Absence is informative: recorded for 74.8% of first class against 1.8% of third |
| Zero fares | 2 rows | **Kept** | One is the chairman of the line on company business. A commercial arrangement, not an error |

Every imputed value is flagged in `Age_imputed` and `Fare_imputed`. **No row was
deleted.** 12 columns become 24.

## The dashboard

Dark executive theme, one hue plus a single accent. Colour that encodes nothing is
decoration, and decoration on an analytical page costs credibility.

**Cross-filtering.** A browser cannot run pandas, so the script precomputes all 41
reachable filter states and embeds them; the JavaScript looks up a key and calls
`Plotly.react`, which is instant. Combinations below five passengers are suppressed,
because a rate on four people is not a finding.

## Reproducing

```bash
pip install pandas numpy matplotlib plotly
python analysis.py     # cleaning, KPIs, five figures
python dashboard.py    # builds dashboard.html
```

`analysis.py` must run first: it writes the cleaned table and the findings the
dashboard reads.
