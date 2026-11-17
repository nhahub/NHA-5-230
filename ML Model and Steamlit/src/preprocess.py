"""
Preprocessing utilities for the productivity dataset.

Handles missing values, encoding, scaling, and feature construction
inside sklearn pipelines so that the same steps are applied at train
and at inference time.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "actual_productivity_score"
TARGET_DISPLAY = "Expected Productivity"

NUMERIC_FEATURES = [
    "age",
    "daily_social_media_time",
    "number_of_notifications",
    "work_hours_per_day",
    "perceived_productivity_score",
    "stress_level",
    "sleep_hours",
    "screen_time_before_sleep",
    "breaks_during_work",
    "coffee_consumption_per_day",
    "days_feeling_burnout_per_month",
    "weekly_offline_hours",
    "job_satisfaction_score",
]

BOOLEAN_FEATURES = [
    "uses_focus_apps",
    "has_digital_wellbeing_enabled",
]

CATEGORICAL_FEATURES = [
    "gender",
    "job_type",
    "social_platform_preference",
]

ALL_FEATURES = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Light cleaning before the sklearn pipeline:
    - drop rows where the target is missing
    - coerce boolean columns
    - strip categorical strings
    - fill missing categoricals with "Other"
      (survey form: blank often means an option not listed)
    """
    out = df.copy()
    out = out.dropna(subset=[TARGET])

    for col in BOOLEAN_FEATURES:
        if col in out.columns:
            out[col] = out[col].astype(bool).astype(int)

    for col in CATEGORICAL_FEATURES:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()
            out[col] = out[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})
            out[col] = out[col].fillna("Other")

    return out


def build_preprocessor() -> ColumnTransformer:
    """
    Numeric     → median impute + standard scale
    Boolean     → most-frequent impute (already 0/1)
    Categorical → constant "Other" impute + one-hot
                  (missing answers treated as an unlisted option)
    """
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    boolean_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Other")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("bool", boolean_pipe, BOOLEAN_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def split_xy(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    X = df[ALL_FEATURES].copy()
    y = df[TARGET].copy()
    return X, y
