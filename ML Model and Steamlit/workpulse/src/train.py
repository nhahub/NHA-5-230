"""
Model training, hyper-parameter search and evaluation.

Models:
  - Linear Regression (baseline)
  - Ridge
  - K-Nearest Neighbors
  - Random Forest
  - Gradient Boosting
  - XGBoost
  - LightGBM

Each model is wrapped in a Pipeline with the shared preprocessor.
GridSearchCV selects hyper-parameters by R² on a 5-fold CV.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline

from src.preprocess import (
    TARGET,
    build_preprocessor,
    clean_frame,
    load_raw,
    split_xy,
)

logger = logging.getLogger(__name__)

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMRegressor
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


def get_model_grids() -> Dict[str, Tuple[Any, Dict[str, List]]]:
    grids = {
        "LinearRegression": (
            LinearRegression(),
            {},
        ),
        "Ridge": (
            Ridge(random_state=42),
            {"model__alpha": [0.1, 1.0, 10.0, 50.0]},
        ),
        "KNN": (
            KNeighborsRegressor(),
            {
                "model__n_neighbors": [5, 11, 21],
                "model__weights": ["uniform", "distance"],
            },
        ),
        "RandomForest": (
            RandomForestRegressor(random_state=42, n_jobs=-1),
            {
                "model__n_estimators": [100, 200],
                "model__max_depth": [8, 14, None],
                "model__min_samples_leaf": [2, 5],
            },
        ),
        "GradientBoosting": (
            GradientBoostingRegressor(random_state=42),
            {
                "model__n_estimators": [100, 200],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [3, 5],
            },
        ),
    }

    if HAS_XGB:
        grids["XGBoost"] = (
            XGBRegressor(
                random_state=42,
                n_jobs=-1,
                objective="reg:squarederror",
                verbosity=0,
            ),
            {
                "model__n_estimators": [150, 300],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [4, 6],
                "model__subsample": [0.8, 1.0],
            },
        )

    if HAS_LGBM:
        grids["LightGBM"] = (
            LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
            {
                "model__n_estimators": [150, 300],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [4, 8],
                "model__num_leaves": [31, 63],
            },
        )

    return grids


def build_pipeline(estimator) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", estimator),
        ]
    )


def evaluate(y_true, y_pred) -> Dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def run_training(
    data_path: str | Path,
    models_dir: str | Path,
    test_size: float = 0.2,
    random_state: int = 42,
    cv: int = 3,
) -> Dict[str, Any]:
    """
    Full training loop.
    Returns a summary dict and writes artefacts to models_dir.
    """
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    raw = load_raw(data_path)
    df = clean_frame(raw)
    X, y = split_xy(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    results = []
    best_name = None
    best_score = -np.inf
    best_pipe = None

    grids = get_model_grids()
    for name, (estimator, param_grid) in grids.items():
        logger.info("Training %s …", name)
        pipe = build_pipeline(estimator)

        if param_grid:
            search = GridSearchCV(
                pipe,
                param_grid=param_grid,
                scoring="r2",
                cv=cv,
                n_jobs=-1,
                refit=True,
                verbose=0,
            )
            search.fit(X_train, y_train)
            fitted = search.best_estimator_
            best_params = search.best_params_
            cv_r2 = float(search.best_score_)
        else:
            pipe.fit(X_train, y_train)
            fitted = pipe
            best_params = {}
            cv_r2 = None

        y_pred = fitted.predict(X_test)
        metrics = evaluate(y_test, y_pred)
        metrics["cv_r2"] = cv_r2
        metrics["best_params"] = best_params
        metrics["model"] = name
        results.append(metrics)

        logger.info(
            "%s  test R²=%.4f  RMSE=%.3f  MAE=%.3f",
            name, metrics["r2"], metrics["rmse"], metrics["mae"],
        )

        if metrics["r2"] > best_score:
            best_score = metrics["r2"]
            best_name = name
            best_pipe = fitted

    # Persist best model and full results table
    joblib.dump(best_pipe, models_dir / "best_model.joblib")
    results_df = pd.DataFrame(results).sort_values("r2", ascending=False)
    results_df.to_csv(models_dir / "model_comparison.csv", index=False)

    meta = {
        "best_model": best_name,
        "best_test_r2": best_score,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": list(X.columns),
    }
    with open(models_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Also keep a cleaned training snapshot for the dashboard
    df.to_csv(Path(data_path).parent / "cleaned.csv", index=False)

    logger.info("Best model: %s (R²=%.4f)", best_name, best_score)
    return {
        "results": results_df,
        "best_name": best_name,
        "best_pipe": best_pipe,
        "meta": meta,
        "X_test": X_test,
        "y_test": y_test,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    summary = run_training(
        data_path="data/productivity_dataset.csv",
        models_dir="models",
    )
    print(summary["results"][["model", "r2", "rmse", "mae", "cv_r2"]].to_string(index=False))
