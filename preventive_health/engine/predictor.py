import joblib
import numpy as np

class HealthPredictor:
    def __init__(self):
        self.models = {
            "burnout_risk":    joblib.load("models/burnout_risk_model.pkl"),
            "stress_overload": joblib.load("models/stress_overload_model.pkl"),
            "sleep_deprived":  joblib.load("models/sleep_deprived_model.pkl"),
            "poor_habits":     joblib.load("models/poor_habits_model.pkl"),
        }
        self.score_model = joblib.load("models/health_score_model.pkl")
        self.features    = joblib.load("models/features.pkl")

    def predict(self, row: dict) -> dict:
        X = [[row[f] for f in self.features]]

        results = {}
        for name, model in self.models.items():
            prob = model.predict_proba(X)[0][1]
            results[f"{name}_prob"] = round(prob * 100, 1)
            results[name] = int(prob > 0.5)

        results["health_score"] = round(
            float(self.score_model.predict(X)[0]), 1
        )
        return results

    def predict_batch(self, df):
        """Run predictions on entire CSV DataFrame."""
        import pandas as pd
        X = df[self.features]
        out = pd.DataFrame()
        for name, model in self.models.items():
            out[f"{name}_prob"] = (model.predict_proba(X)[:, 1] * 100).round(1)
            out[name + "_pred"] = model.predict(X)
        out["health_score_pred"] = self.score_model.predict(X).round(1)
        return pd.concat([df, out], axis=1)