import os

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    train_test_split,
    KFold,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# =========================================================
# Configuration
# =========================================================

DATA_PATH = "data/raw/factory_production_data.csv"

TARGET = "production_qty"

FEATURES = [
    "machine_id",
    "product_id",
    "load_percent",
    "speed_percent",
    "ambient_temperature_c",
    "machine_temperature_c",
    "maintenance_age_days",
    "cycle_time_sec",
    "shift",
]

MODEL_PATH = "trained_models/production_prediction_model.joblib"

REPORT_PATH = "data/production_validation_report.csv"


# =========================================================
# Load dataset
# =========================================================

print("=" * 70)
print("ENNERSENSE — PRODUCTION MODEL VALIDATION")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# =========================================================
# Select features and target
# =========================================================

X = df[FEATURES].copy()
y = df[TARGET].copy()


# =========================================================
# Feature types
# =========================================================

categorical_features = [
    "machine_id",
    "product_id",
    "shift",
]

numerical_features = [
    "load_percent",
    "speed_percent",
    "ambient_temperature_c",
    "machine_temperature_c",
    "maintenance_age_days",
    "cycle_time_sec",
]


# =========================================================
# Preprocessing
# =========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median"),
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "encoder",
            OneHotEncoder(handle_unknown="ignore"),
        ),
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numerical_features,
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features,
        ),
    ]
)


# =========================================================
# Model
# =========================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)


# =========================================================
# Complete pipeline
# =========================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# =========================================================
# Train / test split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)

print("\nData split:")
print(f"Training samples: {len(X_train):,}")
print(f"Testing samples : {len(X_test):,}")


# =========================================================
# Train model
# =========================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# =========================================================
# Test predictions
# =========================================================

predictions = pipeline.predict(X_test)


# =========================================================
# Test evaluation
# =========================================================

test_mae = mean_absolute_error(
    y_test,
    predictions,
)

test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions,
    )
)

test_r2 = r2_score(
    y_test,
    predictions,
)


# =========================================================
# 5-Fold Cross Validation
# =========================================================

print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION")
print("=" * 70)

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


cv_mae_scores = -cross_val_score(
    pipeline,
    X,
    y,
    cv=kf,
    scoring="neg_mean_absolute_error",
    n_jobs=1,
)


cv_rmse_scores = np.sqrt(
    -cross_val_score(
        pipeline,
        X,
        y,
        cv=kf,
        scoring="neg_mean_squared_error",
        n_jobs=1,
    )
)


cv_r2_scores = cross_val_score(
    pipeline,
    X,
    y,
    cv=kf,
    scoring="r2",
    n_jobs=1,
)


print(
    f"\nCV MAE  : "
    f"{cv_mae_scores.mean():.4f} "
    f"+/- {cv_mae_scores.std():.4f} units"
)

print(
    f"CV RMSE : "
    f"{cv_rmse_scores.mean():.4f} "
    f"+/- {cv_rmse_scores.std():.4f} units"
)

print(
    f"CV R²   : "
    f"{cv_r2_scores.mean():.4f} "
    f"+/- {cv_r2_scores.std():.4f}"
)


# =========================================================
# Prediction uncertainty
# =========================================================

print("\nCalculating prediction uncertainty...")


# Get transformed test data
X_test_transformed = pipeline.named_steps[
    "preprocessor"
].transform(X_test)


rf_model = pipeline.named_steps["model"]


# Individual tree predictions
tree_predictions = np.array(
    [
        tree.predict(X_test_transformed)
        for tree in rf_model.estimators_
    ]
)


# Mean prediction
ensemble_mean = tree_predictions.mean(axis=0)

# Standard deviation between trees
ensemble_std = tree_predictions.std(axis=0)


# Avoid division by zero
safe_prediction = np.maximum(
    np.abs(ensemble_mean),
    1e-6,
)


uncertainty_percent = (
    ensemble_std
    / safe_prediction
    * 100
)


average_uncertainty = (
    uncertainty_percent.mean()
)

maximum_uncertainty = (
    uncertainty_percent.max()
)


print("\n" + "=" * 70)
print("UNCERTAINTY SUMMARY")
print("=" * 70)

print(
    f"Average uncertainty : "
    f"{average_uncertainty:.4f}%"
)

print(
    f"Maximum uncertainty : "
    f"{maximum_uncertainty:.4f}%"
)


# =========================================================
# Validation summary
# =========================================================

print("\n" + "=" * 70)
print("PRODUCTION VALIDATION COMPLETE")
print("=" * 70)

print(
    f"\nTest MAE  : "
    f"{test_mae:.4f} units"
)

print(
    f"Test RMSE : "
    f"{test_rmse:.4f} units"
)

print(
    f"Test R²   : "
    f"{test_r2:.4f}"
)

print(
    f"CV MAE    : "
    f"{cv_mae_scores.mean():.4f} units"
)

print(
    f"CV RMSE   : "
    f"{cv_rmse_scores.mean():.4f} units"
)

print(
    f"CV R²     : "
    f"{cv_r2_scores.mean():.4f}"
)

print(
    f"Avg uncertainty : "
    f"{average_uncertainty:.4f}%"
)


# =========================================================
# Save validation report
# =========================================================

os.makedirs(
    "data",
    exist_ok=True,
)


report = pd.DataFrame(
    {
        "metric": [
            "test_mae",
            "test_rmse",
            "test_r2",
            "cv_mae_mean",
            "cv_mae_std",
            "cv_rmse_mean",
            "cv_rmse_std",
            "cv_r2_mean",
            "cv_r2_std",
            "average_uncertainty_percent",
            "maximum_uncertainty_percent",
        ],
        "value": [
            test_mae,
            test_rmse,
            test_r2,
            cv_mae_scores.mean(),
            cv_mae_scores.std(),
            cv_rmse_scores.mean(),
            cv_rmse_scores.std(),
            cv_r2_scores.mean(),
            cv_r2_scores.std(),
            average_uncertainty,
            maximum_uncertainty,
        ],
    }
)


report.to_csv(
    REPORT_PATH,
    index=False,
)


print("\nReport saved to:")
print(REPORT_PATH)

print("\n" + "=" * 70)
print("PRODUCTION MODEL VALIDATION FINISHED")
print("=" * 70)