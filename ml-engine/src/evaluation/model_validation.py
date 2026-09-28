import os

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
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# =========================================================
# Configuration
# =========================================================

DATA_PATH = "data/raw/factory_production_data.csv"
OUTPUT_DIR = "data"

TARGET = "energy_kwh"

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

CATEGORICAL_FEATURES = [
    "machine_id",
    "product_id",
    "shift",
]

NUMERICAL_FEATURES = [
    "load_percent",
    "speed_percent",
    "ambient_temperature_c",
    "machine_temperature_c",
    "maintenance_age_days",
    "cycle_time_sec",
]


# =========================================================
# Load dataset
# =========================================================

print("=" * 70)
print("ENNERSENSE — ENERGY MODEL VALIDATION")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

X = df[FEATURES]
y = df[TARGET]

print(f"\nDataset shape: {df.shape}")


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
            NUMERICAL_FEATURES,
        ),
        (
            "categorical",
            categorical_pipeline,
            CATEGORICAL_FEATURES,
        ),
    ]
)


# =========================================================
# Random Forest
# =========================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)


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
# Train / Test Split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)


print("\nTraining validation model...")

pipeline.fit(
    X_train,
    y_train,
)


# =========================================================
# Test Set Evaluation
# =========================================================

predictions = pipeline.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions,
)

rmse = mean_squared_error(
    y_test,
    predictions,
) ** 0.5

r2 = r2_score(
    y_test,
    predictions,
)


print("\n" + "=" * 70)
print("TEST SET PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.4f} kWh")
print(f"RMSE : {rmse:.4f} kWh")
print(f"R²   : {r2:.4f}")


# =========================================================
# 5-Fold Cross Validation
# =========================================================

print("\nRunning 5-fold cross-validation...")

kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

scoring = {
    "mae": "neg_mean_absolute_error",
    "rmse": "neg_root_mean_squared_error",
    "r2": "r2",
}

cv_results = cross_validate(
    pipeline,
    X,
    y,
    cv=kf,
    scoring=scoring,
    n_jobs=1,
)


cv_mae = -cv_results["test_mae"]
cv_rmse = -cv_results["test_rmse"]
cv_r2 = cv_results["test_r2"]


print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION")
print("=" * 70)

print(
    f"CV MAE  : {cv_mae.mean():.4f} ± {cv_mae.std():.4f} kWh"
)

print(
    f"CV RMSE : {cv_rmse.mean():.4f} ± {cv_rmse.std():.4f} kWh"
)

print(
    f"CV R²   : {cv_r2.mean():.4f} ± {cv_r2.std():.4f}"
)


# =========================================================
# Prediction Uncertainty
# =========================================================

print("\nCalculating prediction uncertainty...")


# Transform test data
X_test_transformed = pipeline.named_steps[
    "preprocessor"
].transform(X_test)


rf_model = pipeline.named_steps["model"]


# Get prediction from every tree
tree_predictions = np.array(
    [
        tree.predict(X_test_transformed)
        for tree in rf_model.estimators_
    ]
)


# Mean prediction
mean_predictions = tree_predictions.mean(
    axis=0
)


# Standard deviation between trees
prediction_std = tree_predictions.std(
    axis=0
)


# 10th and 90th percentile prediction range
lower_prediction = np.percentile(
    tree_predictions,
    10,
    axis=0,
)

upper_prediction = np.percentile(
    tree_predictions,
    90,
    axis=0,
)


# Relative uncertainty
uncertainty_percent = (
    prediction_std
    / np.maximum(np.abs(mean_predictions), 1e-6)
) * 100


print("\n" + "=" * 70)
print("UNCERTAINTY SUMMARY")
print("=" * 70)

print(
    f"Average uncertainty : "
    f"{uncertainty_percent.mean():.4f}%"
)

print(
    f"Maximum uncertainty : "
    f"{uncertainty_percent.max():.4f}%"
)


# =========================================================
# Validation Report
# =========================================================

validation_report = pd.DataFrame(
    {
        "actual_energy_kwh": y_test.values,
        "predicted_energy_kwh": mean_predictions,
        "prediction_error_kwh":
            y_test.values - mean_predictions,
        "uncertainty_kwh":
            prediction_std,
        "uncertainty_percent":
            uncertainty_percent,
        "lower_prediction_kwh":
            lower_prediction,
        "upper_prediction_kwh":
            upper_prediction,
    }
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)


output_path = os.path.join(
    OUTPUT_DIR,
    "energy_validation_report.csv",
)


validation_report.to_csv(
    output_path,
    index=False,
)


# =========================================================
# Final Summary
# =========================================================

print("\n" + "=" * 70)
print("ENERGY VALIDATION COMPLETE")
print("=" * 70)

print(
    f"\nTest MAE       : {mae:.4f} kWh"
)

print(
    f"Test RMSE      : {rmse:.4f} kWh"
)

print(
    f"Test R²        : {r2:.4f}"
)

print(
    f"CV MAE         : {cv_mae.mean():.4f} kWh"
)

print(
    f"CV RMSE        : {cv_rmse.mean():.4f} kWh"
)

print(
    f"CV R²          : {cv_r2.mean():.4f}"
)

print(
    f"Avg uncertainty: "
    f"{uncertainty_percent.mean():.4f}%"
)

print(
    f"\nReport saved to:"
)

print(output_path)

print("\n" + "=" * 70)