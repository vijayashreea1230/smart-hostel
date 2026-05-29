import pandas as pd
import numpy as np
import random

np.random.seed(42)
n = 1000  # rows (patients/days)

# ── Raw Features ───────────────────────────────────────────
sleep_hours      = np.random.normal(6.2, 1.5, n).clip(2, 10).round(1)
sleep_time_hour  = np.random.choice([21,22,23,0,1,2,3], n,
                     p=[0.05,0.15,0.25,0.20,0.15,0.12,0.08])
meals_count      = np.random.choice([1,2,3,4], n, p=[0.15,0.30,0.40,0.15])
junk_food_count  = np.random.choice([0,1,2,3,4,5], n,
                     p=[0.20,0.25,0.25,0.15,0.10,0.05])
                     
stress_level     = np.random.randint(1, 11, n)
work_hours       = np.random.normal(8.5, 2.5, n).clip(2, 18).round(1)
exercise_minutes = np.random.normal(28, 22, n).clip(0, 120).round(0)
water_intake     = np.random.normal(1.8, 0.7, n).clip(0.3, 4.0).round(1)
mood_score       = np.random.randint(1, 11, n)
screen_time_hrs  = np.random.normal(6, 2, n).clip(1, 14).round(1)
caffeine_cups    = np.random.choice([0,1,2,3,4,5], n,
                     p=[0.10,0.25,0.30,0.20,0.10,0.05])

# ── Labels (Rule-Based Ground Truth) ──────────────────────
burnout_risk = (
    (work_hours > 10) &
    (sleep_hours < 6) &
    (stress_level >= 7) &
    (exercise_minutes < 20)
).astype(int)

stress_overload = (
    (stress_level >= 8) &
    (mood_score <= 4) &
    (sleep_hours < 6.5)
).astype(int)

sleep_deprived = (sleep_hours < 6).astype(int)

poor_habits = (
    (junk_food_count >= 3) |
    (meals_count <= 1) |
    (water_intake < 1.2)
).astype(int)

# ── Health Score (0–100) ───────────────────────────────────
health_score = 100
health_score -= np.maximum(0, (7 - sleep_hours) * 6)
health_score -= junk_food_count * 4
health_score -= np.maximum(0, (3 - meals_count) * 5)
health_score -= np.maximum(0, (stress_level - 5) * 3)
health_score -= np.maximum(0, (30 - exercise_minutes) * 0.25)
health_score -= np.maximum(0, (2 - water_intake) * 4)
health_score -= burnout_risk * 12
health_score -= stress_overload * 8
health_score = np.clip(health_score, 0, 100).round(1)

# ── Skipping Meals (binary detection label) ───────────────
skipping_meals = (meals_count <= 1).astype(int)

# ── Late Sleep (binary) ───────────────────────────────────
late_sleep = np.isin(sleep_time_hour, [0, 1, 2, 3]).astype(int)

# ── Assemble DataFrame ────────────────────────────────────
df = pd.DataFrame({
    "sleep_hours":       sleep_hours,
    "sleep_time_hour":   sleep_time_hour,
    "meals_count":       meals_count,
    "junk_food_count":   junk_food_count,
    "stress_level":      stress_level,
    "work_hours":        work_hours,
    "exercise_minutes":  exercise_minutes,
    "water_intake":      water_intake,
    "mood_score":        mood_score,
    "screen_time_hrs":   screen_time_hrs,
    "caffeine_cups":     caffeine_cups,
    "burnout_risk":      burnout_risk,
    "stress_overload":   stress_overload,
    "sleep_deprived":    sleep_deprived,
    "poor_habits":       poor_habits,
    "skipping_meals":    skipping_meals,
    "late_sleep":        late_sleep,
    "health_score":      health_score,
})

df.to_csv("data/health_dataset.csv", index=False)
print(f"✅ Dataset saved: {n} rows, {df.shape[1]} columns")
print(df.head())
print("\nLabel distribution:")
for col in ["burnout_risk","stress_overload","sleep_deprived","poor_habits"]:
    print(f"  {col}: {df[col].sum()} positive ({df[col].mean()*100:.1f}%)")