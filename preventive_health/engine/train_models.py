import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, mean_absolute_error, r2_score)
from sklearn.pipeline import Pipeline

# ── Load CSV ───────────────────────────────────────────────
df = pd.read_csv("data/health_dataset.csv")
print(f"✅ Loaded dataset: {df.shape}")

FEATURES = [
    "sleep_hours", "sleep_time_hour", "meals_count",
    "junk_food_count", "stress_level", "work_hours",
    "exercise_minutes", "water_intake", "mood_score",
    "screen_time_hrs", "caffeine_cups"
]

CLASSIFICATION_TARGETS = [
    "burnout_risk",
    "stress_overload",
    "sleep_deprived",
    "poor_habits",
]

REGRESSION_TARGET = "health_score"

X = df[FEATURES]
os.makedirs("models", exist_ok=True)

# ── Train Classification Models ────────────────────────────
trained_models = {}

for target in CLASSIFICATION_TARGETS:
    print(f"\n🔧 Training model for: {target}")
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", GradientBoostingClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")

    print(f"  AUC: {auc:.3f} | CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save model
    path = f"models/{target}_model.pkl"
    joblib.dump(pipeline, path)
    trained_models[target] = pipeline
    print(f"  ✅ Saved → {path}")

# ── Train Regression Model (Health Score) ─────────────────
print(f"\n🔧 Training regression model for: {REGRESSION_TARGET}")
y_reg = df[REGRESSION_TARGET]
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X, y_reg, test_size=0.2, random_state=42
)

reg_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    ))
])

reg_pipeline.fit(X_train_r, y_train_r)
y_pred_r = reg_pipeline.predict(X_test_r)

print(f"  MAE: {mean_absolute_error(y_test_r, y_pred_r):.2f}")
print(f"  R²:  {r2_score(y_test_r, y_pred_r):.3f}")

joblib.dump(reg_pipeline, "models/health_score_model.pkl")
print("  ✅ Saved → models/health_score_model.pkl")

# ── Save Feature List ──────────────────────────────────────
joblib.dump(FEATURES, "models/features.pkl")
print("\n✅ All models trained and saved to /models/")
