def detect_issues(data: dict) -> list:
    issues = []
    if data["meals_count"] < 2:
        issues.append({"type": "⚠️ Skipping Meals", "severity": "medium",
                       "msg": f"Only {data['meals_count']} meal(s) logged today."})
    h = data["sleep_time_hour"]
    if h >= 0 and h < 6:
        issues.append({"type": "🌙 Late Sleep", "severity": "high",
                       "msg": f"You slept at {h}:00 — late sleep disrupts recovery."})
    if data["junk_food_count"] >= 3:
        issues.append({"type": "🍔 Excess Junk Food", "severity": "medium",
                       "msg": f"{data['junk_food_count']} junk food instances detected."})
    if data["stress_level"] >= 8:
        issues.append({"type": "🔥 High Stress", "severity": "critical",
                       "msg": f"Stress level at {data['stress_level']}/10 — intervention needed."})
    if data["water_intake"] < 1.5:
        issues.append({"type": "💧 Dehydration Risk", "severity": "medium",
                       "msg": f"Only {data['water_intake']}L water today."})
    return issues