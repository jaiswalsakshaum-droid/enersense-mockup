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


# =========================================================
# Configuration
# =========================================================

DATA_PATH = "data/raw/factory_production_data.csv"

MODEL_DIR = "trained_models"

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


# =========================================================
# Load dataset
# =========================================================

print("=" * 70)
print("ENNERSENSE — PRODUCTION PREDICTION MODEL")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")


# =========================================================
# Features / target
# =========================================================

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


print("\nData split:")
print(f"Training samples: {len(X_train):,}")
print(f"Testing samples : {len(X_test):,}")


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
# Pipeline
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
# Train
# =========================================================

print("\nTraining Random Forest...")

pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# =========================================================
# Predict
# =========================================================

predictions = pipeline.predict(X_test)


# =========================================================
# Evaluate
# =========================================================

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
print("MODEL PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.4f} units")
print(f"RMSE : {rmse:.4f} units")
print(f"R²   : {r2:.4f}")


# =========================================================
# Save model
# =========================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True,
)

model_path = os.path.join(
    MODEL_DIR,
    "production_prediction_model.joblib",
)

joblib.dump(
    pipeline,
    model_path,
)


print("\nModel saved to:")
print(model_path)

print("\n" + "=" * 70)
print("PRODUCTION MODEL COMPLETE")
print("=" * 70)