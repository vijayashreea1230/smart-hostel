def generate_alerts(predictions, issues, health_score):
    alerts = []

    if predictions["burnout_risk_prob"] > 70:
        alerts.append({
            "type": "burnout",
            "msg": "🚨 BURNOUT RISK DETECTED — Immediate rest recommended.",
            "severity": "critical"
        })

    if predictions["stress_overload_prob"] > 65:
        alerts.append({
            "type": "stress",
            "msg": "⚠️ Stress Overload — Consider mindfulness or a break.",
            "severity": "high"
        })

    if predictions["sleep_deprived_prob"] > 60:
        alerts.append({
            "type": "sleep",
            "msg": "😴 Sleep Deprivation Detected — Target 7–8 hours tonight.",
            "severity": "high"
        })

    if health_score["score"] < 40:
        alerts.append({
            "type": "emergency",
            "msg": "🆘 EMERGENCY: Health score critically low. Please consult a doctor.",
            "severity": "emergency"
        })

    return alerts