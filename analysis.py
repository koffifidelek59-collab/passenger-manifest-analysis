# -*- coding: utf-8 -*-
"""
Passenger Manifest: data quality, cleaning, KPIs and insights
=============================================================
Every section states its INPUT, its METHOD and its OUTPUT before the code, and
defines each term the first time it appears.

OUTPUTS
  data/manifest_clean.csv     the cleaned table
  results/findings.json       every figure quoted downstream
  figures/*.png               the static figures
"""
import json, os, re
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.ticker as mtick

NAVY, BLUE, MID, LIGHT, PALE = "#12395E", "#1F6FB2", "#6BAED6", "#A8CFE8", "#DEEBF7"
AMBER, GREY = "#E08A1E", "#94A3B8"
plt.rcParams.update({
    "figure.dpi":110,"savefig.dpi":200,"figure.facecolor":"white",
    "font.family":"DejaVu Sans","font.size":11,"axes.titlesize":13,
    "axes.titleweight":"bold","axes.titlepad":10,"axes.labelsize":11,
    "axes.edgecolor":"#3A3A3A","axes.linewidth":0.9,"axes.spines.top":False,
    "axes.spines.right":False,"axes.grid":True,"grid.color":"#E3E8ED",
    "grid.linewidth":0.8,"axes.axisbelow":True,"legend.frameon":False,
    "legend.fontsize":10,"xtick.labelsize":10,"ytick.labelsize":10})
for f in ["data","figures","results"]: os.makedirs(f, exist_ok=True)
F = {}

# =============================================================================
# 1. LOAD
# INPUT  : File_3.csv, the manifest as supplied
# METHOD : read once, keep the original for the before/after comparison
# OUTPUT : raw and df
# =============================================================================
CSV = next(p for p in ["File_3.csv","data.csv","data/File_3.csv","/content/File_3.csv"]
           if os.path.exists(p))
raw = pd.read_csv(CSV)
df = raw.copy()
F["rows"], F["cols_raw"] = len(df), df.shape[1]
print(f"Loaded {len(df)} passengers, {df.shape[1]} columns from {CSV}")

# =============================================================================
# 2. DIAGNOSIS, before anything is changed
# METHOD : missing values, duplicates, and a check no completeness test performs:
#          whether any column is a restatement of another.
#
# Term. TARGET LEAKAGE is when a column that should be predicted is derivable
# from another column. A model trained on it scores perfectly and has learned
# nothing. It is invisible to a missing-value audit.
# =============================================================================
F["missing"] = {k:int(v) for k,v in df.isna().sum().items() if v}
F["dup_rows"] = int(df.duplicated().sum())
F["dup_ids"]  = int(df.PassengerId.duplicated().sum())

leak = float(((df.Sex=="female").astype(int) == df.Survived).mean())
F["survived_equals_female"] = round(100*leak, 1)
print(f"\nMissing        : {F['missing']}")
print(f"Duplicate rows : {F['dup_rows']}   duplicate ids: {F['dup_ids']}")
print(f"\nSurvived == (Sex is female) on {F['survived_equals_female']}% of rows")
if leak == 1.0:
    print("  The target is an exact copy of Sex. It carries no information beyond it.")
    print("  Any survival model would score 100% and would have learned nothing.")
F["crosstab"] = pd.crosstab(df.Sex, df.Survived).to_dict()

# =============================================================================
# 3. CLEANING AND IMPUTATION
# INPUT  : df with three incomplete columns
# METHOD : one decision per column, each with its reason and its count
# OUTPUT : a cleaned df and data/manifest_clean.csv
#
# Term. IMPUTATION replaces a missing value with an estimate. It is appropriate
# when the value is missing at random and the column is not the thing being
# measured. It is wrong when absence is itself informative, which is the case
# for Cabin below.
# =============================================================================
print("\n" + "="*64 + "\nCLEANING\n" + "="*64)

# --- 3.1 Title, extracted before Age is imputed, because it informs the imputation
df["Title"] = df.Name.str.extract(r",\s*([^\.]+)\.")[0].str.strip()
RARE = {"Col":"Officer","Rev":"Officer","Dr":"Officer","Dona":"Royalty",
        "Ms":"Miss"}
df["Title"] = df.Title.replace(RARE)
F["titles"] = df.Title.value_counts().to_dict()
print(f"3.1 Title extracted from Name: {F['titles']}")

# --- 3.2 Age. 86 missing, 20.6% of the manifest.
# Imputed by the median of Title and Pclass together, not by the global median.
# A global median would give a 3-year-old the same age as a 60-year-old officer.
# Title carries life stage (Master is a boy, Mrs is a married woman) and Pclass
# correlates with age, so the pair is far more specific than either alone.
n_age = int(df.Age.isna().sum())
df["Age_imputed"] = df.Age.isna()
df["Age"] = df.groupby(["Title","Pclass"]).Age.transform(lambda s: s.fillna(s.median()))
df["Age"] = df.Age.fillna(df.groupby("Title").Age.transform("median"))
df["Age"] = df.Age.fillna(df.Age.median())          # final safety net
F["age_imputed"] = n_age
F["age_imputed_pct"] = round(100*n_age/len(df), 1)
print(f"3.2 Age: {n_age} values imputed by median of Title x Pclass "
      f"({F['age_imputed_pct']}% of rows). Flagged in Age_imputed.")

# --- 3.3 Fare. One missing value, and two zeros.
# The missing value is imputed by the median fare of the same class and
# embarkation port. The zeros are NOT imputed: one belongs to Joseph Bruce Ismay,
# the chairman of the line, who travelled on company business. A zero fare is a
# real commercial arrangement, not a recording error.
n_fare = int(df.Fare.isna().sum())
df["Fare_imputed"] = df.Fare.isna()
df["Fare"] = df.groupby(["Pclass","Embarked"]).Fare.transform(lambda s: s.fillna(s.median()))
df["Fare"] = df.Fare.fillna(df.groupby("Pclass").Fare.transform("median"))
F["fare_imputed"] = n_fare
F["fare_zero"] = int((df.Fare==0).sum())
print(f"3.3 Fare: {n_fare} imputed by median of Pclass x Embarked. "
      f"{F['fare_zero']} zero fares KEPT: company travel, not an error.")

# --- 3.4 Cabin. 327 missing, 78.2%.
# NOT imputed. Absence is informative: a cabin number was recorded mainly for
# first-class passengers, so a missing cabin is a fact about the passenger, not
# a gap to fill. Inventing 327 cabin numbers would fabricate 78% of a column.
n_cab = int(df.Cabin.isna().sum())
df["Has_Cabin"] = df.Cabin.notna()
df["Deck"] = df.Cabin.str[0].fillna("Unknown")
F["cabin_missing"] = n_cab
F["cabin_missing_pct"] = round(100*n_cab/len(df), 1)
F["cabin_by_class"] = df.groupby("Pclass").Has_Cabin.mean().mul(100).round(1).to_dict()
print(f"3.4 Cabin: {n_cab} missing ({F['cabin_missing_pct']}%). NOT imputed. "
      f"Recorded for {F['cabin_by_class'][1]}% of first class against "
      f"{F['cabin_by_class'][3]}% of third.")

# --- 3.5 Types and derived fields
df["Sex"] = df.Sex.astype("category")
df["Embarked"] = df.Embarked.astype("category")
df["Pclass_label"] = df.Pclass.map({1:"1 First",2:"2 Second",3:"3 Third"})
df["FamilySize"] = df.SibSp + df.Parch + 1
df["Alone"] = df.FamilySize == 1
df["AgeBand"] = pd.cut(df.Age, [0,12,18,30,45,60,100],
                       labels=["Child 0-12","Teen 13-18","Young 19-30",
                               "Adult 31-45","Mature 46-60","Senior 60+"])
df["FareBand"] = pd.qcut(df.Fare, 4, labels=["Q1 lowest","Q2","Q3","Q4 highest"])
# Group size from the ticket: passengers sharing a ticket travelled together.
df["GroupSize"] = df.groupby("Ticket").PassengerId.transform("size")
df["FarePerPerson"] = df.Fare / df.GroupSize

df.to_csv("data/manifest_clean.csv", index=False)
F["cols_clean"] = df.shape[1]
print(f"\n3.5 Types set and 9 analysis fields derived. "
      f"{F['cols_raw']} columns become {F['cols_clean']}.")
print(f"Clean table written: data/manifest_clean.csv, {len(df)} rows. No row deleted.")

# =============================================================================
# 4. KPIs AND ANALYSIS
# INPUT  : the cleaned df
# METHOD : the seven indicators a manifest analyst would report, then the
#          segment tables behind each figure
# OUTPUT : the KPI block of F and the tables in results/
#
# A note on what is NOT reported. Because Survived is a copy of Sex (section 2),
# no survival rate by any segment is reported in this study. Every such figure
# would restate the sex split of that segment and nothing more. Reporting them
# would look like analysis and would be arithmetic.
# =============================================================================
print("\n" + "="*64 + "\nKPIs\n" + "="*64)
K = {
 "passengers": len(df),
 "female_pct": round(100*(df.Sex=="female").mean(), 1),
 "median_age": round(float(df.Age.median()), 1),
 "median_fare": round(float(df.Fare.median()), 2),
 "third_class_pct": round(100*(df.Pclass==3).mean(), 1),
 "alone_pct": round(100*df.Alone.mean(), 1),
 "avg_family": round(float(df.FamilySize.mean()), 2),
 "children": int((df.Age < 12).sum()),
 "cabin_known_pct": round(100*df.Has_Cabin.mean(), 1),
}
F["kpi"] = K
for k, v in K.items(): print(f"  {k:<18} {v}")

T = {}
T["class"] = (df.groupby("Pclass_label", observed=True)
                .agg(passengers=("PassengerId","size"),
                     median_fare=("Fare","median"),
                     median_age=("Age","median"),
                     female_pct=("Sex", lambda s: 100*(s=="female").mean()),
                     cabin_pct=("Has_Cabin", lambda s: 100*s.mean())).round(2))
T["embarked"] = (df.groupby("Embarked", observed=True)
                   .agg(passengers=("PassengerId","size"),
                        median_fare=("Fare","median"),
                        third_pct=("Pclass", lambda s: 100*(s==3).mean())).round(2))
T["age_band"] = df.groupby("AgeBand", observed=True).agg(
                    passengers=("PassengerId","size"),
                    median_fare=("Fare","median")).round(2)
T["title"] = df.groupby("Title", observed=True).agg(
                 passengers=("PassengerId","size"),
                 median_age=("Age","median")).round(1).sort_values("passengers", ascending=False)
T["family"] = df.groupby("FamilySize").agg(passengers=("PassengerId","size"),
                                           median_fare=("Fare","median")).round(2)
for name, t in T.items():
    t.to_csv(f"results/by_{name}.csv")
    print(f"\n--- by {name} ---\n{t.to_string()}")

# The fare spread is the headline inequality figure.
q = df.groupby("Pclass").Fare.median()
F["fare_ratio_1_3"] = round(float(q.loc[1] / q.loc[3]), 1)
F["fare_max"] = round(float(df.Fare.max()), 2)
F["fare_p99"] = round(float(df.Fare.quantile(0.99)), 2)
F["group_travel_pct"] = round(100*(df.GroupSize > 1).mean(), 1)
print(f"\nFirst-class median fare is {F['fare_ratio_1_3']}x third-class.")
print(f"{F['group_travel_pct']}% of passengers shared a ticket with someone else.")

# =============================================================================
# 5. FIGURES
# The chart type follows the data type. Every figure answers one question.
# =============================================================================
def save(fig, name):
    fig.savefig(f"figures/{name}.png", bbox_inches="tight", dpi=200)
    plt.show(); plt.close(fig)

# F1. The leakage, made visible. This is the most important figure in the study.
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
ct = pd.crosstab(df.Sex, df.Survived)
ct.plot(kind="bar", ax=ax[0], color=[MID, BLUE], edgecolor="white", linewidth=1, zorder=3)
ax[0].set_xlabel(""); ax[0].set_ylabel("Passengers")
ax[0].set_title("(a) Survived against Sex: the cells are empty", loc="left")
ax[0].legend(["Survived = 0", "Survived = 1"], ncol=2)
ax[0].tick_params(axis="x", rotation=0); ax[0].grid(axis="x", alpha=0)
for i, (s, row) in enumerate(ct.iterrows()):
    for j, v in enumerate(row):
        if v: ax[0].text(i + (j-0.5)*0.25, v+4, str(v), ha="center", fontsize=10,
                         fontweight="bold")
ax[1].axis("off")
ax[1].text(0.02, 0.72, f"{F['survived_equals_female']}%", fontsize=48,
           fontweight="bold", color=AMBER)
ax[1].text(0.02, 0.52, "of rows satisfy  Survived = (Sex is female)",
           fontsize=12.5, color="#334155")
ax[1].text(0.02, 0.30,
   "Two of the four cells are empty. The target is a\n"
   "restatement of Sex, so it carries no information\n"
   "beyond it. Any survival model would score 100%\n"
   "and would have learned nothing.",
   fontsize=11.5, color="#475569", va="top")
save(fig, "01_target_leakage")

# F2. Missing data, before and after.
fig, ax = plt.subplots(figsize=(10, 4.2))
miss = raw.isna().sum().sort_values(ascending=True)
miss = miss[miss > 0]
pct = 100*miss/len(raw)
cols = [AMBER if p > 50 else BLUE for p in pct]
b = ax.barh(miss.index, pct, color=cols, edgecolor="white", linewidth=1, zorder=3)
for bb, n, p in zip(b, miss, pct):
    ax.text(p+1, bb.get_y()+bb.get_height()/2, f"{n} rows, {p:.1f}%",
            va="center", fontsize=10.5, fontweight="bold", color="#334155")
ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("Share of rows missing")
ax.set_title("Figure 2. Missing values, and how each was handled", loc="left")
ax.grid(axis="y", alpha=0)
ax.text(0.99, 0.10, "Cabin is not imputed: absence is informative\n"
        "Age is imputed by Title and class\nFare by class and port",
        transform=ax.transAxes, ha="right", fontsize=10, color=NAVY,
        bbox=dict(boxstyle="round,pad=0.5", fc=PALE, ec=MID, lw=0.9))
save(fig, "02_missing_values")

# F3. Class, fare and the inequality it encodes.
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.4))
cl = T["class"]
b = ax[0].bar(cl.index, cl.passengers, color=[BLUE, MID, LIGHT],
              edgecolor="white", linewidth=1, zorder=3)
for bb, v in zip(b, cl.passengers):
    ax[0].text(bb.get_x()+bb.get_width()/2, v+4, f"{int(v)}", ha="center",
               fontsize=10.5, fontweight="bold")
ax[0].set_ylabel("Passengers"); ax[0].set_title("(a) Passengers by class", loc="left")
ax[0].grid(axis="x", alpha=0)
data = [df[df.Pclass==c].Fare.values for c in (1,2,3)]
bp = ax[1].boxplot(data, labels=["1 First","2 Second","3 Third"], patch_artist=True,
                   widths=0.55, showfliers=True,
                   flierprops=dict(marker="o", ms=3.5, mfc=GREY, mec="none", alpha=.6))
for patch, c in zip(bp["boxes"], [BLUE, MID, LIGHT]):
    patch.set_facecolor(c); patch.set_edgecolor("#3A3A3A")
for m in bp["medians"]: m.set_color(NAVY); m.set_linewidth(2)
ax[1].set_yscale("log"); ax[1].set_ylabel("Fare, log scale")
ax[1].set_title(f"(b) Fare by class: first pays {F['fare_ratio_1_3']}x third", loc="left")
ax[1].grid(axis="x", alpha=0)
save(fig, "03_class_and_fare")

# F4. Who was on board: age structure by class.
fig, ax = plt.subplots(figsize=(11, 4.6))
for c, col, lab in [(1, BLUE, "1 First"), (2, MID, "2 Second"), (3, LIGHT, "3 Third")]:
    s = df[df.Pclass==c].Age
    ax.hist(s, bins=np.arange(0, 85, 5), alpha=0.72, color=col, label=lab,
            edgecolor="white", linewidth=0.6, zorder=3)
ax.axvline(df.Age.median(), color=AMBER, lw=2.2, zorder=5)
ax.text(df.Age.median()+1, ax.get_ylim()[1]*0.92,
        f"median {F['kpi']['median_age']}", color=AMBER, fontsize=10.5,
        fontweight="bold")
ax.set_xlabel("Age"); ax.set_ylabel("Passengers")
ax.set_title("Figure 4. Age structure by class", loc="left")
ax.legend(title="Class"); ax.grid(axis="x", alpha=0)
save(fig, "04_age_structure")

# F5. Travelling alone or in a group.
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.2))
fam = T["family"]
b = ax[0].bar(fam.index.astype(str), fam.passengers, color=BLUE,
              edgecolor="white", linewidth=1, zorder=3)
b[0].set_color(AMBER)
ax[0].set_xlabel("Family size on board"); ax[0].set_ylabel("Passengers")
ax[0].set_title(f"(a) {F['kpi']['alone_pct']}% travelled alone", loc="left")
ax[0].grid(axis="x", alpha=0)
dk = df.groupby("Pclass").Has_Cabin.mean().mul(100)
b2 = ax[1].bar(["1 First","2 Second","3 Third"], dk.values,
               color=[BLUE, MID, LIGHT], edgecolor="white", linewidth=1, zorder=3)
for bb, v in zip(b2, dk.values):
    ax[1].text(bb.get_x()+bb.get_width()/2, v+1.5, f"{v:.1f}%", ha="center",
               fontsize=10.5, fontweight="bold")
ax[1].set_ylim(0, 100); ax[1].yaxis.set_major_formatter(mtick.PercentFormatter())
ax[1].set_ylabel("Cabin number recorded")
ax[1].set_title("(b) Record keeping was a function of class", loc="left")
ax[1].grid(axis="x", alpha=0)
save(fig, "05_family_and_records")

F["tables"] = {k: v.reset_index().to_dict("records") for k, v in T.items()}
json.dump(F, open("results/findings.json","w"), indent=2, default=str)
print("\nFigures written:", sorted(os.listdir("figures")))

# =============================================================================
# 7. STATISTICS FOR THE DASHBOARD
# INPUT  : the cleaned df and the raw file
# METHOD : the correlation matrix, a four-component data quality score, and the
#          comparisons each executive finding rests on
# OUTPUT : the same results/findings.json, extended
#
# Term. A DATA QUALITY SCORE is the mean of four measured components:
#   completeness  share of cells that are populated
#   uniqueness    share of rows that are not duplicates
#   validity      share of rows whose values fall in their legal range
#   consistency   whether columns contradict or duplicate each other
# The fourth is the one that matters here: it scores zero, because the target
# column duplicates Sex. A score that ignored consistency would read 93 and
# would be reassuring about a file that cannot answer its own question.
# =============================================================================
num = df[["Age","Fare","FamilySize","SibSp","Parch","Pclass"]]
corr = num.corr().round(2)
F["corr"] = {"labels": list(corr.columns), "matrix": corr.values.tolist()}
F["corr_age_fare"]   = float(corr.loc["Age","Fare"])
F["corr_class_fare"] = float(corr.loc["Pclass","Fare"])
F["corr_fam_fare"]   = float(corr.loc["FamilySize","Fare"])

completeness = 100*(1 - raw.isna().sum().sum()/(raw.shape[0]*raw.shape[1]))
uniqueness   = 100*(1 - raw.duplicated().mean())
validity     = 100*(1 - ((df.Age<0)|(df.Fare<0)|(~df.Pclass.isin([1,2,3]))).mean())
consistency  = 0.0 if F["survived_equals_female"] == 100.0 else 100.0
F["dq"] = {"completeness": round(completeness,1), "uniqueness": round(uniqueness,1),
           "validity": round(validity,1), "consistency": round(consistency,1),
           "score": round(float(np.mean([completeness,uniqueness,validity,consistency])),0),
           "missing_rate": round(100*raw.isna().sum().sum()/(raw.shape[0]*raw.shape[1]),1)}

F["fare_by_class"] = {int(k): round(float(v),2) for k,v in df.groupby("Pclass").Fare.median().items()}
F["fare_by_port"]  = df.groupby("Embarked", observed=True).Fare.median().round(2).to_dict()
F["fare_alone"]    = round(float(df[df.Alone].Fare.median()),2)
F["fare_group"]    = round(float(df[~df.Alone].Fare.median()),2)
q1, q3 = df.Fare.quantile(.25), df.Fare.quantile(.75)
F["outliers_fare"] = int((df.Fare > q3 + 1.5*(q3-q1)).sum())
json.dump(F, open("results/findings.json","w"), indent=2, default=str)
print(f"\nData quality score {F['dq']['score']:.0f}/100  "
      f"(consistency {F['dq']['consistency']:.0f}, penalised by the target leakage)")
print(f"corr class-fare {F['corr_class_fare']:+.2f} | age-fare {F['corr_age_fare']:+.2f} "
      f"| family-fare {F['corr_fam_fare']:+.2f}")
print(f"Fare outliers beyond the interquartile fence: {F['outliers_fare']}")
