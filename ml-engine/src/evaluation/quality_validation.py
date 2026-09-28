import os

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import KFold, train_test_split


# =========================================================
# Configuration
# =========================================================

DATA_PATH = "data/raw/factory_production_data.csv"

MODEL_PATH = "trained_models/quality_prediction_model.joblib"

REPORT_PATH = "data/quality_validation_report.csv"

TARGET = "defect_rate"

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

TEST_SIZE = 0.20

RANDOM_STATE = 42

N_SPLITS = 5


# =========================================================
# Header
# =========================================================

print("=" * 70)
print("ENNERSENSE — QUALITY / DEFECT MODEL VALIDATION")
print("=" * 70)


# =========================================================
# Load dataset
# =========================================================

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# =========================================================
# Select features and target
# =========================================================

X = df[FEATURES]

y = df[TARGET]


# =========================================================
# Train / test split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
)


print("\nData split:")
print(f"Training samples: {len(X_train):,}")
print(f"Testing samples : {len(X_test):,}")


# =========================================================
# Load trained model
# =========================================================

print("\nLoading trained quality model...")

pipeline = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# =========================================================
# Test-set prediction
# =========================================================

print("\nGenerating test-set predictions...")

predictions = pipeline.predict(X_test)


# =========================================================
# Test-set metrics
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


print("\n" + "=" * 70)
print("TEST SET PERFORMANCE")
print("=" * 70)

print(f"MAE  : {test_mae:.6f}")
print(f"RMSE : {test_rmse:.6f}")
print(f"R²   : {test_r2:.4f}")


# =========================================================
# 5-Fold Cross-Validation
# =========================================================

print("\nRunning 5-fold cross-validation...")

kf = KFold(
    n_splits=N_SPLITS,
    shuffle=True,
    random_state=RANDOM_STATE,
)

cv_mae_scores = []
cv_rmse_scores = []
cv_r2_scores = []


for fold, (train_idx, val_idx) in enumerate(
    kf.split(X),
    start=1,
):

    X_fold_train = X.iloc[train_idx]
    X_fold_val = X.iloc[val_idx]

    y_fold_train = y.iloc[train_idx]
    y_fold_val = y.iloc[val_idx]

    fold_model = joblib.load(MODEL_PATH)

    fold_model.fit(
        X_fold_train,
        y_fold_train,
    )

    fold_predictions = fold_model.predict(
        X_fold_val
    )

    fold_mae = mean_absolute_error(
        y_fold_val,
        fold_predictions,
    )

    fold_rmse = np.sqrt(
        mean_squared_error(
            y_fold_val,
            fold_predictions,
        )
    )

    fold_r2 = r2_score(
        y_fold_val,
        fold_predictions,
    )

    cv_mae_scores.append(fold_mae)
    cv_rmse_scores.append(fold_rmse)
    cv_r2_scores.append(fold_r2)


cv_mae_mean = np.mean(cv_mae_scores)
cv_mae_std = np.std(cv_mae_scores)

cv_rmse_mean = np.mean(cv_rmse_scores)
cv_rmse_std = np.std(cv_rmse_scores)

cv_r2_mean = np.mean(cv_r2_scores)
cv_r2_std = np.std(cv_r2_scores)


print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION")
print("=" * 70)

print(
    f"CV MAE  : {cv_mae_mean:.6f} +/- "
    f"{cv_mae_std:.6f}"
)

print(
    f"CV RMSE : {cv_rmse_mean:.6f} +/- "
    f"{cv_rmse_std:.6f}"
)

print(
    f"CV R²   : {cv_r2_mean:.4f} +/- "
    f"{cv_r2_std:.4f}"
)


# =========================================================
# Prediction uncertainty
# =========================================================

print("\nCalculating prediction uncertainty...")


# Absolute percentage error.
# Small epsilon prevents division by zero.

# =========================================================
# Prediction error / uncertainty
# =========================================================

absolute_errors = np.abs(
    predictions - y_test
)

average_error = np.mean(
    absolute_errors
)

maximum_error = np.max(
    absolute_errors
)

error_std = np.std(
    absolute_errors
)


print("\n" + "=" * 70)
print("PREDICTION ERROR SUMMARY")
print("=" * 70)

print(
    f"Average absolute error : "
    f"{average_error:.6f}"
)

print(
    f"Maximum absolute error : "
    f"{maximum_error:.6f}"
)

print(
    f"Error standard deviation : "
    f"{error_std:.6f}"
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
# Validation report
# =========================================================

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
            "average_absolute_error",
            "maximum_absolute_error",
            "error_std",
        ],
        "value": [
            test_mae,
            test_rmse,
            test_r2,
            cv_mae_mean,
            cv_mae_std,
            cv_rmse_mean,
            cv_rmse_std,
            cv_r2_mean,
            cv_r2_std,
            average_error,
            maximum_error,
            error_std,
        ],
    }
)


# =========================================================
# Save report
# =========================================================

os.makedirs(
    os.path.dirname(REPORT_PATH),
    exist_ok=True,
)

report.to_csv(
    REPORT_PATH,
    index=False,
)


# =========================================================
# Final summary
# =========================================================

print("\n" + "=" * 70)
print("QUALITY VALIDATION COMPLETE")
print("=" * 70)

print(
    f"\nTest MAE       : {test_mae:.6f}"
)

print(
    f"Test RMSE      : {test_rmse:.6f}"
)

print(
    f"Test R²        : {test_r2:.4f}"
)

print(
    f"CV MAE         : {cv_mae_mean:.6f}"
)

print(
    f"CV RMSE        : {cv_rmse_mean:.6f}"
)

print(
    f"CV R²          : {cv_r2_mean:.4f}"
)

print(
    f"Avg absolute error: "
    f"{average_error:.6f}"
)

print("\nReport saved to:")
print(REPORT_PATH)

print("\n" + "=" * 70)
print("QUALITY MODEL VALIDATION FINISHED")
print("=" * 70)
