# MONTIG | مُنتِج
### Social Media Impact Analysis & Digital Wellbeing Ecosystem

DEPI final project, track **Data Analytics / Junior Data Analyst** (NHA-5-230).

MONTIG looks at how social media habits relate to productivity, sleep, stress and burnout in a survey of **29,863 people** (19 columns after cleaning). The main deliverable is a five-page Power BI report. Around it we built a SQL Server layer with 29 business questions, a machine learning model that estimates productivity, and a Streamlit web app that serves that model.

**Live app:** https://appuctivityapp.streamlit.app/

---

## What is in this repository

```
.
├── Dashboards/                       Power BI report and a PNG of every page
│   ├── Social Media Impact Analysis & Digital Wellbeing Ecosystem.pbix
│   ├── Home.png
│   └── Dashboard 01 ... 05 *.png
├── Dataset/
│   └── productivity_dataset.csv      raw survey data (30,000 rows, 19 columns)
├── SQL/
│   └── montig_29_queries.sql         the 29 business questions (SQL Server)
├── ML Model and Steamlit/
│   ├── data/                         raw and cleaned CSV used by the notebooks and the app
│   ├── models/                       best_model.joblib, model_comparison.csv, meta.json
│   ├── notebooks/                    01_cleaning_inspection, 02_eda, 03_modeling
│   ├── src/                          preprocess.py and train.py
│   ├── streamlit_app/app.py          the web app
│   ├── requirements.txt
│   └── README.md
├── Proposal.pdf
├── SQL .pdf                          the dashboard plan with all SQL and findings
├── Infographic.pdf                   one-slide DEPI summary
└── Final Presentation.pptx
```

> If `~$Final Presentation.pptx` is still in the repo, delete it. It is a temporary lock file that PowerPoint creates while the real file is open, and it should never be committed. Upload the actual presentation instead. The `.gitignore` in this folder keeps these files out from now on.

## Team

| Member | Part of the project |
|---|---|
| Ahmed Fathallah | Data collection, data cleaning, project idea, ML model, Streamlit app, maintenance |
| Mohamed Mohamed | Business domain, database schemas, 29 SQL queries, Dashboard 01 |
| Samaa Elsayed | Data cleaning pipelines, Dashboard 02 |
| Sama Hatem | DAX measures, statistical analysis, Dashboard 03 |
| Habiba Alaa | Power Query ETL, data model optimisation, Dashboard 04 |
| Farah Ahmed | Requirements, business questions, documentation, presentations, Dashboard 05 |

---

## The five dashboards

| # | Dashboard | Question it answers |
|---|---|---|
| 01 | Social Media Usage Overview | Which platforms dominate, and who gets the most notifications? |
| 02 | Productivity & Work Performance | How do work hours, coffee and social media time relate to productivity? |
| 03 | Wellbeing, Sleep & Burnout | Who sleeps less, feels more stress and reports more burnout? |
| 04 | Digital Habits & Focus | Do focus apps and digital wellbeing settings go with better routines? |
| 05 | Workforce Segmentation & Insights | How do job types, ages and genders differ, and where is perceived productivity off? |

Every page has four KPI cards (20 in total), slicers, tooltips and a navigation bar. The `Home` page links to all of them.

---

## How to run each part

### 1. Power BI report

You need **Power BI Desktop** (Windows). The report cannot be opened in the browser from the file alone.

1. Open `Dashboards/Social Media Impact Analysis & Digital Wellbeing Ecosystem.pbix`.
2. The report was built with the CSV at `D:\DEPI\Final Project\productivity_dataset.csv`. On another machine Power BI will complain that it cannot find the file. Fix it once:
   **Home → Transform data → select the `Productivity` query → Source (Applied Steps) → change the file path to wherever you saved `Dataset/productivity_dataset.csv` → Close & Apply.**
3. Start on the `Home` page and use the navigation buttons. Ctrl+click follows a button in Desktop.

The Power Query steps (rename columns, "Other" for blank categories, default values for missing numbers, remove duplicates, four derived columns) are all in the Applied Steps list, so nothing is hidden in the data.

### 2. SQL Server queries

You need SQL Server (Express is enough) and SSMS or Azure Data Studio.

1. Create a database, for example `montig`.
2. Load the data into a table named exactly **`social_media_vs_productivity`** (SSMS: right-click the database → Tasks → Import Flat File). The findings in `SQL .pdf` come from the **cleaned table of 29,863 rows**, i.e. the data after the Power Query steps. To reproduce them exactly, export the cleaned table from Power BI (right-click the `Productivity` table → *Export data*) and import that file. You can also import the raw `Dataset/productivity_dataset.csv`; the queries run, but counts and averages will differ slightly because blanks and duplicates are still in it. The Power BI export uses spaces in column names (`job type`), while the queries use underscores (`job_type`, `daily_social_media_time`, ...), so rename the columns during import.
3. Numeric columns are stored as `tinyint`, and the boolean columns (`uses_focus_apps`, `has_digital_wellbeing_enabled`) as `bit` or `'True'/'False'` text. The queries handle both.
4. Open `SQL/montig_29_queries.sql` and run one question at a time. Each question has its suggested visual and the finding we got on the full data in a comment above it.

### 3. Notebooks and the ML model

Python 3.10 or newer is recommended.

```bash
cd "ML Model and Steamlit"
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Run the notebooks in order from the `notebooks/` folder with Jupyter or VS Code:

1. `01_cleaning_inspection.ipynb` checks types, missing values and duplicates and produces the cleaned file.
2. `02_eda.ipynb` has the exploratory charts and correlations.
3. `03_modeling.ipynb` trains and compares the models.

To retrain from the command line instead, run this **from the `ML Model and Steamlit` folder** (the imports expect `src` to be importable from there):

```bash
python -m src.train
```

This reads `data/productivity_dataset.csv`, tries seven models (Linear Regression, Ridge, KNN, Random Forest, Gradient Boosting, XGBoost, LightGBM) with a grid search each, and writes three files into `models/`: `best_model.joblib`, `model_comparison.csv` and `meta.json`. It also writes `data/cleaned.csv`, which the app reads.

The saved model is a full scikit-learn pipeline. It includes the preprocessing (imputation, scaling, one-hot encoding), so you can pass it the raw columns directly.

> A `.joblib` file only loads reliably with the same scikit-learn version that saved it. If you retrain, keep your own `requirements.txt` in sync with the version you trained with.

### 4. Streamlit app

#### Run it on your own machine

```bash
cd "ML Model and Steamlit"
pip install -r requirements.txt          # once
streamlit run streamlit_app/app.py
```

A browser tab opens at `http://localhost:8501`.

Things the app needs, all relative to the `ML Model and Steamlit` folder:

| Needed | Why |
|---|---|
| `src/` (with `__init__.py` and `preprocess.py`) | the app imports the target name from it |
| `data/cleaned.csv` (or `data/productivity_dataset.csv`) | the charts |
| `models/best_model.joblib`, `meta.json`, `model_comparison.csv` | the Predict page and the model summary |

`app.py` finds these through `Path(__file__).parents[1]`, which means **`app.py` must stay inside a subfolder (`streamlit_app/`) that sits next to `src/`, `data/` and `models/`**. Do not move it up or out.

The app has nine pages in the sidebar: Overview, Exploratory Insights, Correlations, Job & Platform, Digital Habits, Wellbeing, Key Insights, Recommendations and Predict. On **Predict**, set the sliders and dropdowns for demographics and work, digital habits and wellbeing, then press *Run prediction* to get the expected productivity score.

The green theme comes from the CSS in `app.py`, plus an optional `.streamlit/config.toml` that colours the built-in widgets. If you want it, keep that folder next to where you run `streamlit run`.

#### Deploy it on Streamlit Community Cloud

1. Push the repository to GitHub (public, or private with access granted to Streamlit).
2. Go to https://share.streamlit.io, choose **New app** and select the repo and the `main` branch.
3. Set **Main file path** to `ML Model and Steamlit/streamlit_app/app.py`.
4. Make sure a `requirements.txt` is available. Streamlit Cloud looks for it next to the main file and in the repository root. If the build fails with `ModuleNotFoundError`, copy the file into `streamlit_app/` or into the repo root.
5. The app only needs these packages, so a short file builds faster than the full training one:
   ```
   streamlit
   pandas
   numpy
   scikit-learn==<the version you trained with>
   plotly
   joblib
   ```
   `xgboost`, `lightgbm`, `statsmodels`, `seaborn` and `matplotlib` are used for training and notebooks, not by the app.
6. Press **Deploy**. After every push, use **Manage app → Reboot** if the page still shows the old version.

Common problems:

| Message | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | `src/` is not next to `streamlit_app/`, or `src/__init__.py` is missing |
| `FileNotFoundError ... cleaned.csv` | run `python -m src.train` once, or commit `data/cleaned.csv` |
| `InconsistentVersionWarning` / model fails to load | install the scikit-learn version that trained the model |
| First load is slow | the free tier sleeps when idle and rebuilds the environment; later pages are fast because data and model are cached |

---

## Method in short

- **Cleaning (Power BI).** Blank job type and platform became "Other"; missing numbers were filled with fixed defaults; duplicates were removed. Four bands were added: Burnout Group, Work Hours Range, Age Group and Social Media Level.
- **Cleaning (Python).** Rows without a target were dropped. Missing numbers use the median, missing categories become "Other". The model learns from a train split and is judged on a held-out test split.
- **Why the two paths differ.** Power BI needs readable, complete values for the visuals; the model should not see values we invented, so it imputes inside the pipeline using training data only.
- **Reading the results.** Everything here describes relationships and group differences in survey data. None of it shows that social media use *causes* a change in productivity, sleep or stress.

## Tech stack

Power BI Desktop and Service, DAX, Power Query (M), SQL Server, Python, pandas, NumPy, scikit-learn, XGBoost, LightGBM, Plotly, Streamlit, GitHub.
