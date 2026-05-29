def generate_health_score(data: dict, predictions: dict) -> dict:
    score = 100

    score -= max(0, (7 - data["sleep_hours"]) * 5)
    score -= data["junk_food_count"] * 4
    score -= max(0, (3 - data["meals_count"]) * 6)
    score -= max(0, data["stress_level"] - 5) * 3
    score -= max(0, (30 - data["exercise_minutes"]) * 0.3)
    score -= max(0, (2 - data["water_intake"]) * 5)
    score -= predictions["burnout_risk_prob"] * 0.2
    score -= predictions["stress_overload_prob"] * 0.1

    score = max(0, min(100, round(score)))

    if score >= 80:   grade, color = "Excellent 🟢", "#00C853"
    elif score >= 60: grade, color = "Fair 🟡",      "#FFD600"
    elif score >= 40: grade, color = "At Risk 🟠",   "#FF6D00"
    else:             grade, color = "Critical 🔴",  "#D50000"

    return {"score": score, "grade": grade, "color": color}