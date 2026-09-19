# 🚢 Passenger Manifest — Data Analysis & Interactive Dashboard

<p align="center">

**A rigorous Python-based data analysis of 418 passenger records, with an interactive executive dashboard**

<br>

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python\&logoColor=white)](#)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas\&logoColor=white)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Computation-013243?logo=numpy\&logoColor=white)](#)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Visualization-3F4F75?logo=plotly\&logoColor=white)](#)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?logo=matplotlib\&logoColor=white)](#)

</p>

---

## 👤 Author

**KOUAME Koffi Fidèle**
*Energy Systems Engineer · Data Analyst*

📧 **Email:** [koffifidelek59@gmail.com](mailto:koffifidelek59@gmail.com)
💼 **LinkedIn:** [Koffi Fidèle Kouamé](https://www.linkedin.com/in/koffi-fidele-kouame/)
💻 **GitHub:** [koffifidelek59-collab](https://github.com/koffifidelek59-collab)

---

## 📌 Project Overview

This project presents a complete **data cleaning, exploratory analysis, visualization and dashboard development workflow** based on a passenger manifest containing **418 records and 24 variables**.

The project was developed entirely in **Python**, from raw-data inspection and cleaning to statistical analysis and interactive visualization.

The final deliverable is a **self-contained HTML dashboard** that can be opened directly in any modern web browser without requiring a server, Python environment or additional installation.

> **Dashboard language:** French 🇫🇷
> **Analysis & documentation:** English 🇬🇧

---

## 🎯 Objectives

The analysis was designed to:

* 🔎 Audit the quality and structure of the original dataset
* 🧹 Clean and prepare the passenger manifest
* 📊 Explore passenger characteristics and distributions
* 📈 Produce statistically meaningful visualizations
* 🧠 Identify important patterns and data-quality issues
* ⚠️ Detect potential target leakage
* 📋 Translate analytical results into actionable insights
* 🖥️ Build an interactive executive-style dashboard
* ♻️ Provide a fully reproducible Python workflow

---

# 🚨 Key Analytical Finding

## `Survived` is an exact copy of `Sex`

The most important discovery in the dataset is a **perfect deterministic relationship between `Survived` and `Sex`**.

In other words:

> **Every observation has the same information encoded twice.**

The contingency table contains only two populated cells, while the other two possible combinations are empty.

This constitutes **target leakage**.

### Why does this matter?

A model trained on `Sex` to predict `Survived` could achieve an apparently perfect performance.

However, such a result would not represent meaningful predictive power. The target variable is effectively reproducing the predictor.

Therefore, the project deliberately **does not report survival rates by segment as substantive findings**, because these would simply reproduce the underlying sex distribution rather than reveal an independent survival pattern.

### Analytical principle

> **A perfect model is not necessarily a valid model.**

Detecting and documenting the data defect is more valuable than producing an artificially impressive predictive score.

---

# 🧹 Data Cleaning & Preparation

The cleaning process was designed to preserve the original observations while handling missing and inconsistent values transparently.

### Cleaning decisions

| Variable   | Missing values | Treatment                                  | Rationale                                                 |
| :--------- | -------------: | :----------------------------------------- | :-------------------------------------------------------- |
| `Age`      |     86 · 20.6% | Median imputation by `Title` × `Pclass`    | Captures both life stage and passenger class              |
| `Fare`     |              1 | Median imputation by `Pclass` × `Embarked` | Fare depends strongly on class and route                  |
| `Cabin`    |    327 · 78.2% | **Not imputed**                            | Missingness itself contains useful structural information |
| Zero fares |              2 | **Retained**                               | Treated as legitimate commercial/company arrangements     |

### Preservation principle

**No passenger record was deleted.**

Every imputed value is explicitly flagged through:

* `Age_imputed`
* `Fare_imputed`

This makes the transformation process auditable and reproducible.

---

## 🏗️ Dataset Transformation

The original dataset is transformed without deleting observations.

| Stage            | Records |       Variables |
| :--------------- | ------: | --------------: |
| Original dataset |     418 | Original schema |
| Cleaned dataset  | **418** |          **24** |

The final cleaned dataset is available at:

```text
data/manifest_clean.csv
```

---

# 📊 Interactive Dashboard

The project includes a browser-based interactive dashboard:

```text
dashboard.html
```

### Dashboard characteristics

* **8 analytical panels**
* **3 global filters**
* Passenger-class filtering
* Sex filtering
* Port filtering
* Synchronized KPI updates
* Interactive Plotly visualizations
* Executive-style dark theme
* No external server required

### Cross-filtering architecture

A standard browser cannot directly execute pandas operations.

To preserve interactivity while keeping the dashboard completely self-contained, the Python dashboard generator:

1. Computes the relevant filter combinations in advance
2. Stores the resulting analytical states inside the HTML
3. Uses JavaScript to retrieve the appropriate state
4. Updates the visualizations through `Plotly.react`

This provides instantaneous filtering without requiring:

* a Python backend
* Flask
* Streamlit
* a database
* an external API
* a running server

For analytical stability, combinations involving fewer than **five passengers** are suppressed rather than presented as statistically meaningful rates.

---

# 📈 Analytical Outputs

The project produces:

* Passenger distribution analysis
* Class-level analysis
* Sex distribution
* Port analysis
* Missing-value assessment
* Fare analysis
* Age analysis
* Data-quality diagnostics
* Five key analytical insights
* Executive recommendations

The principal conclusions are documented separately in:

```text
INSIGHTS.md
```

---

# 🗂️ Project Structure

```text
passenger-manifest-analysis/
│
├── assets/
│
├── data/
│   ├── File_3_original.csv
│   └── manifest_clean.csv
│
├── figures/
│
├── results/
│
├── vendor/
│   └── plotly.min.js
│
├── Passenger_Manifest_Analysis.ipynb
├── analysis.py
├── dashboard.py
├── dashboard.html
├── INSIGHTS.md
├── report.pdf
├── report.tex
├── README.md
└── .gitignore
```

---

# 📦 Deliverables

| Requirement                 | Status | Deliverable                         |
| :-------------------------- | :----: | :---------------------------------- |
| Python analysis             |    ✅   | `Passenger_Manifest_Analysis.ipynb` |
| Reusable analysis script    |    ✅   | `analysis.py`                       |
| Dashboard generation script |    ✅   | `dashboard.py`                      |
| Cleaned dataset             |    ✅   | `data/manifest_clean.csv`           |
| Interactive dashboard       |    ✅   | `dashboard.html`                    |
| Key insights                |    ✅   | `INSIGHTS.md`                       |
| Technical report            |    ✅   | `report.pdf`                        |
| LaTeX source                |    ✅   | `report.tex`                        |

---

# 🛠️ Technology Stack

The project was developed using a **Python-only analytical workflow**.

| Technology     | Purpose                          |
| :------------- | :------------------------------- |
| **Python**     | Core programming language        |
| **Pandas**     | Data cleaning and manipulation   |
| **NumPy**      | Numerical computation            |
| **Matplotlib** | Static visualization             |
| **Plotly**     | Interactive visualization        |
| **JavaScript** | Browser-side dashboard filtering |
| **LaTeX**      | Technical report production      |

### Deliberately excluded

No use was made of:

* ❌ Microsoft Excel
* ❌ Power BI
* ❌ Tableau

The complete analytical workflow remains reproducible from Python.

---

# 🚀 Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/koffifidelek59-collab/passenger-manifest-analysis.git
cd passenger-manifest-analysis
```

## 2. Install dependencies

```bash
pip install pandas numpy matplotlib plotly
```

## 3. Run the analysis

```bash
python analysis.py
```

This performs the main cleaning, KPI computation and figure generation.

## 4. Generate the dashboard

```bash
python dashboard.py
```

The resulting dashboard is:

```text
dashboard.html
```

## 5. Open the dashboard

Simply open:

```text
dashboard.html
```

in any modern browser.

**No server is required.**

---

# 📓 Reproduce the Notebook Analysis

The complete analytical workflow is also available in:

```text
Passenger_Manifest_Analysis.ipynb
```

The notebook can be opened with:

* Jupyter Notebook
* JupyterLab
* Google Colab
* VS Code

Run the cells sequentially to reproduce the analysis.

---

# 🔬 Analytical Methodology

The project follows a structured data-analysis pipeline:

```text
Raw Dataset
     │
     ▼
Data Audit
     │
     ▼
Missing-Value Analysis
     │
     ▼
Data Cleaning
     │
     ▼
Feature Validation
     │
     ▼
Exploratory Data Analysis
     │
     ▼
Data-Quality Diagnostics
     │
     ▼
Visualization
     │
     ▼
Insight Extraction
     │
     ▼
Interactive Dashboard
```

This workflow emphasizes **data validity before visualization or modeling**.

---

# ⚠️ Data Quality & Analytical Integrity

A central principle of this project is:

> **Do not allow a visually convincing result to hide a structurally invalid dataset.**

The discovery of the `Survived`–`Sex` duplication demonstrates why data validation must precede predictive modeling.

Rather than optimizing for an impressive metric, the analysis documents the limitation and adjusts the interpretation accordingly.

This approach prioritizes:

**Data quality → Valid analysis → Reliable interpretation → Actionable insight**

---

# 📋 Key Insights

Five principal insights and corresponding recommendations are documented in:

```text
INSIGHTS.md
```

The insights are derived from the cleaned dataset and the analytical workflow rather than from unsupported assumptions.

---

# 📄 Technical Report

A complete technical report is provided in both PDF and LaTeX formats:

```text
report.pdf
report.tex
```

The report documents:

* Dataset preparation
* Cleaning methodology
* Analytical decisions
* Visualizations
* Findings
* Data-quality limitations
* Recommendations

---

# 🔐 Reproducibility

The project is structured so that another analyst can reproduce the principal outputs from the repository.

The workflow separates:

**Raw data → Cleaning → Analysis → Visualization → Dashboard**

This separation improves:

* reproducibility
* auditability
* maintainability
* transparency
* future extension

---

# 🌍 Professional Profile

This project reflects an analytical workflow combining:

**Data Engineering**
→ data quality, cleaning and transformation

**Data Analytics**
→ exploratory analysis, KPIs and statistical interpretation

**Data Visualization**
→ static and interactive visual communication

**Decision Support**
→ translating analytical findings into recommendations

The same methodology can be transferred to domains such as **energy systems, renewable energy, green hydrogen and engineering analytics**.

---

## ⭐ Project Philosophy

> **Clean the data. Question the structure. Validate the evidence. Then communicate the insight.**

---

<p align="center">

**KOUAME Koffi Fidèle**
*Energy Systems Engineer · Data Analyst*

</p>
