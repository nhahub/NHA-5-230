# Workpulse

Estimate expected productivity from survey signals: workload, digital habits and wellbeing.

---

## Layout

```
workpulse/
├── data/
├── notebooks/
│   ├── 01_cleaning_inspection.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modeling.ipynb
├── src/
│   ├── preprocess.py
│   └── train.py
├── models/
├── streamlit_app/
│   └── app.py
└── requirements.txt
```

## Run

```bash
pip install -r requirements.txt
cd streamlit_app
streamlit run app.py
```

Dashboard pages: Overview, Exploratory Insights, Correlations, Job & Platform, Digital Habits, Wellbeing, Key Insights, Recommendations, Predict.

## Data handling

- Target rows only when a productivity label exists.
- Categorical blanks from the form are set to **Other** (`SimpleImputer(strategy="constant", fill_value="Other")`).
- Numeric blanks use median inside the sklearn pipeline.
- Scaling and one-hot encoding are fit on the training split only.
