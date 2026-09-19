Voici une version beaucoup plus professionnelle, moderne et GitHub premium, entièrement en anglais, avec un ton orienté portfolio, data analytics et recrutement.

🚢 Passenger Manifest Analytics
Advanced Data Exploration, Quality Assessment & Interactive Executive Dashboard

https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white https://img.shields.io/badge/NumPy-Scientific%20Computing-013243?style=for-the-badge&logo=numpy&logoColor=white https://img.shields.io/badge/Plotly-Interactive%20Dashboard-3F4F75?style=for-the-badge&logo=plotly&logoColor=white https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=for-the-badge&logo=python&logoColor=white

A complete end-to-end data analytics project combining data quality assessment, statistical exploration, interactive visualization, and executive reporting.

👨‍💻 About the Author
KOUAME Koffi Fidèle

Energy Systems Engineer | Data Analyst | Python Developer

📧 Email:
 koffifidelek59@gmail.com

💼 LinkedIn:
 https://www.linkedin.com/in/koffi-fidele-kouame/

💻 GitHub:
 https://github.com/koffifidelek59-collab

📖 Project Overview

This project delivers a comprehensive analytical workflow applied to a passenger manifest dataset containing 418 passenger records and 24 attributes.

From raw-data auditing to dashboard deployment, every stage of the project was developed using a fully reproducible Python ecosystem.

The analysis follows professional data analytics practices including:

Data auditing
Data quality assessment
Missing-value treatment
Feature validation
Exploratory Data Analysis (EDA)
Statistical interpretation
Interactive dashboard development
Executive insight generation

The final output is a fully standalone HTML dashboard that runs directly in any web browser without requiring:

Python
Flask
Streamlit
Database connections
Cloud services
External APIs
🎯 Project Objectives

The project was designed to address the following goals:

✅ Assess dataset quality and reliability

✅ Identify missing and inconsistent information

✅ Develop a transparent data-cleaning pipeline

✅ Explore passenger demographics and ticket information

✅ Produce meaningful visual analytics

✅ Detect structural issues and analytical risks

✅ Generate actionable business insights

✅ Create an executive-level interactive dashboard

✅ Ensure full reproducibility and transparency

🔍 Executive Finding
Survived = Sex (Perfect Information Duplication)

The most significant discovery made during the analysis is the existence of a perfect deterministic relationship between the variables:

Survived ↔ Sex


Every observation encodes exactly the same information in both variables.

The contingency table reveals that only two possible combinations exist, while the remaining combinations never occur.

This indicates a classical case of:

⚠️ Target Leakage

A machine-learning model predicting Survived from Sex would appear to achieve:

100% Accuracy


However, this performance would be entirely misleading because the target variable is simply reproducing information already contained in the predictor.

Why This Matters

One of the most important responsibilities of a data analyst is not building impressive models.

It is ensuring that conclusions remain statistically valid.

A perfect prediction achieved through duplicated information provides no genuine predictive value.

Therefore, this project prioritizes data integrity and analytical transparency over artificially high performance metrics.

A perfect model is not necessarily a useful model.

🧹 Data Cleaning Strategy

The cleaning process was carefully designed to preserve information while ensuring consistency and analytical reliability.

Missing-Value Treatment
Variable	Missing Rate	MethodAge	20.6%	Median by Title × Passenger Class
Fare	0.2%	Median by Passenger Class × Port
Cabin	78.2%	Preserved as Missing
Zero Fare	2 Records	Retained
Data Governance Principles

✔ No passenger records removed

✔ No arbitrary value replacement

✔ Fully traceable transformations

✔ Reproducible methodology

✔ Transparent documentation

Additional audit flags were introduced:

Age_imputed
Fare_imputed


allowing every generated value to be explicitly tracked.

🏗 Dataset Evolution
Dataset Version	Records	VariablesRaw Dataset	418	Original Schema
Cleaned Dataset	418	24

No observations were deleted during processing.

Cleaned dataset:

data/manifest_clean.csv

📊 Interactive Executive Dashboard

A fully interactive web dashboard was developed to transform analytical findings into an intuitive decision-support interface.

dashboard.html

Dashboard Features
Interactive Analytics
KPI Cards
Passenger Distribution Analysis
Passenger Class Breakdown
Gender Distribution
Port Analysis
Fare Distribution
Age Distribution
Missing-Value Diagnostics
Global Filters
Passenger Class
Sex
Embarkation Port
Visualization Engine
Plotly Interactive Charts
Dynamic KPI Updates
Executive Dark Theme
Cross-Filtering Logic
Instant Data Refresh
Self-Contained Architecture

The dashboard operates entirely within the browser.

To eliminate dependency on backend technologies, the dashboard generation process:

Precomputes analytical states in Python
Embeds processed data directly into HTML
Uses JavaScript filtering logic
Updates visualizations through Plotly React rendering

As a result, users can interact with the dashboard without:

❌ Flask
❌ Streamlit
❌ SQL Database
❌ Cloud Services
❌ Python Runtime
❌ API Calls

📈 Analytical Deliverables

The project generates:

Data Quality Assessment
Missing-Value Analysis
Passenger Demographic Study
Age Analysis
Fare Analysis
Class Distribution Analysis
Port Distribution Analysis
Data Integrity Diagnostics
Executive Recommendations
Interactive Dashboard

Key findings are documented in:

INSIGHTS.md

🗂 Repository Structure
passenger-manifest-analysis/
│
├── assets/
├── data/
│   ├── File_3_original.csv
│   └── manifest_clean.csv
│
├── figures/
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

📦 Project Deliverables
Deliverable	StatusJupyter Notebook Analysis	✅
Python Analysis Pipeline	✅
Dashboard Generator	✅
Cleaned Dataset	✅
Interactive Dashboard	✅
Insight Documentation	✅
Technical Report (PDF)	✅
LaTeX Source Files	✅
⚙️ Technology Stack
Data Analytics
Python
Pandas
NumPy
Visualization
Matplotlib
Plotly
Dashboard Layer
HTML
CSS
JavaScript
Reporting
LaTeX
Tools Intentionally Excluded

To demonstrate a fully programmable analytical workflow, the project was completed without using:

❌ Excel
❌ Power BI
❌ Tableau
❌ Low-Code Platforms

Everything was produced through code.

🚀 Quick Start
Clone the Repository
git clone https://github.com/koffifidelek59-collab/passenger-manifest-analysis.git

cd passenger-manifest-analysis

Install Dependencies
pip install pandas numpy matplotlib plotly

Run the Analysis
python analysis.py

Build the Dashboard
python dashboard.py

Launch the Dashboard

Open:

dashboard.html


in any modern browser.

No installation, backend server, or environment configuration is required.

🔬 Analytical Workflow
Raw Dataset
      │
      ▼
Data Audit
      │
      ▼
Missing-Value Assessment
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
Data Quality Diagnostics
      │
      ▼
Visualization
      │
      ▼
Insight Extraction
      │
      ▼
Interactive Dashboard

✅ Data Integrity First

Many analytical projects jump directly into predictive modeling.

This project deliberately adopts a different philosophy:

Validate before you model.

The discovery of the perfect duplication between Survived and Sex demonstrates how easily misleading conclusions can emerge when data-quality validation is ignored.

The objective of analytics is not merely prediction.

The objective is trustworthy decision-making.

📑 Technical Documentation

The project includes a complete technical report available in both:

report.pdf
report.tex


The report covers:

Dataset Structure
Cleaning Methodology
Imputation Strategy
Statistical Analysis
Visualizations
Dashboard Architecture
Key Findings
Limitations
Recommendations
🔄 Reproducibility & Transparency

The entire repository is structured around modern analytics best practices:

Raw Data
     ↓
Cleaning
     ↓
Analysis
     ↓
Visualization
     ↓
Dashboard


This separation ensures:

Reproducibility
Maintainability
Auditability
Scalability
Transparency
🌍 Professional Relevance

This project showcases competencies across multiple disciplines:

Data Engineering

Data quality control, cleaning, validation, and transformation.

Data Analytics

Statistical exploration, KPI development, and insight generation.

Data Visualization

Professional communication through static and interactive visualizations.

Decision Support

Converting analytical findings into actionable recommendations.

The methodology presented here can be applied to sectors including:

Energy Systems
Renewable Energy
Green Hydrogen
Utilities
Industrial Analytics
Asset Management
Engineering Operations
⭐ Project Philosophy

Clean the data. Challenge the assumptions. Validate the evidence. Communicate the insight.

KOUAME Koffi Fidèle

Energy Systems Engineer • Data Analyst • Python Developer

"Transforming data into trustworthy decisions."
