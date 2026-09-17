import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from xgboost import XGBRegressor


# =========================================================
# Configuration
# =========================================================

DATA_PATH = "data/raw/factory_production_data.csv"

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

TARGET = "energy_kwh"


# =========================================================
# Load data
# =========================================================

print("=" * 70)
print("ENNERSENSE — ENERGY MODEL COMPARISON")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

X = df[FEATURES]
y = df[TARGET]


# =========================================================
# Train / test split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)


# =========================================================
# Feature groups
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
# Preprocessor
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            SimpleImputer(strategy="median"),
            numerical_features,
        ),
        (
            "categorical",
            Pipeline(
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
            ),
            categorical_features,
        ),
    ]
)


# =========================================================
# Models
# =========================================================

random_forest = RandomForestRegressor(
    n_estimators=200,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)


xgboost_model = XGBRegressor(
    n_estimators=500,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1,
)


# =========================================================
# Pipelines
# =========================================================

rf_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", random_forest),
    ]
)


xgb_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", xgboost_model),
    ]
)


# =========================================================
# Evaluation helper
# =========================================================

def evaluate_model(name, model):

    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

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

    print(f"{name} complete.")

    print(f"MAE  : {mae:.4f} kWh")
    print(f"RMSE : {rmse:.4f} kWh")
    print(f"R²   : {r2:.4f}")

    return {
        "model": name,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


# =========================================================
# Train models
# =========================================================

rf_results = evaluate_model(
    "Random Forest",
    rf_pipeline,
)

xgb_results = evaluate_model(
    "XGBoost",
    xgb_pipeline,
)


# =========================================================
# Compare
# =========================================================

results = pd.DataFrame(
    [
        rf_results,
        xgb_results,
    ]
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)


# =========================================================
# Feature importance — XGBoost
# =========================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

fitted_preprocessor = xgb_pipeline.named_steps[
    "preprocessor"
]

fitted_model = xgb_pipeline.named_steps[
    "model"
]

feature_names = (
    fitted_preprocessor
    .get_feature_names_out()
)

importance = fitted_model.feature_importances_

feature_importance = (
    pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance,
        }
    )
    .sort_values(
        "importance",
        ascending=False,
    )
)

print(
    feature_importance.head(15).to_string(
        index=False
    )
)


# =========================================================
# Save comparison
# =========================================================

os.makedirs(
    "trained_models",
    exist_ok=True,
)

results.to_csv(
    "trained_models/energy_model_comparison.csv",
    index=False,
)


# =========================================================
# Save XGBoost model
# =========================================================

joblib.dump(
    xgb_pipeline,
    "trained_models/energy_xgboost_model.joblib",
)


print("\nXGBoost model saved to:")

print(
    "trained_models/energy_xgboost_model.joblib"
)

print("\nComparison saved to:")

print(
    "trained_models/energy_model_comparison.csv"
)


print("\n" + "=" * 70)
print("ENERGY MODEL COMPARISON COMPLETE")
print("=" * 70)