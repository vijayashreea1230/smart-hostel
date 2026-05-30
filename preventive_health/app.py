import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from engine.predictor import HealthPredictor

# ─────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="Health Monitor Engine",
#     page_icon=None,
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

def render_health_monitor():
    st.markdown("""
    <style>
    h1, h2, h3 { font-family: 'Orbitron', monospace !important; }
    
    .card {
        background: linear-gradient(145deg, #0f1520, #151d2e);
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-2px); }
    
    .val-crit { color: #ff3b3b; font-size: 2.6rem; font-weight: 800; font-family:'Syne',sans-serif; }
    .val-warn { color: #ff9f1c; font-size: 2.6rem; font-weight: 800; font-family:'Syne',sans-serif; }
    .val-ok   { color: #2ecc71; font-size: 2.6rem; font-weight: 800; font-family:'Syne',sans-serif; }
    .val-blue { color: #4db8ff; font-size: 2.6rem; font-weight: 800; font-family:'Syne',sans-serif; }
    
    .lbl { font-size: 0.78rem; color: #5a7090; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 6px; }
    
    .alert-box {
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.02em;
    }
    .alert-emergency { background:#1a0000; border:1.5px solid #ff0000; color:#ff6b6b; }
    .alert-critical  { background:#1a0800; border:1.5px solid #ff4500; color:#ff8c42; }
    .alert-high      { background:#1a1200; border:1.5px solid #ffd600; color:#ffe566; }
    .alert-ok        { background:#001a08; border:1.5px solid #00cc44; color:#33ff88; }
    
    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        border-bottom: 1px solid #1e2d45;
        padding-bottom: 8px;
        margin: 28px 0 16px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────
    @st.cache_resource
    def load_predictor():
        return HealthPredictor()
    
    @st.cache_data
    def load_dataset():
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return pd.read_csv(os.path.join(base_dir, "data", "health_dataset.csv"))
    
    predictor = load_predictor()
    df_full   = load_dataset()
    
    FEATURES = [
        "sleep_hours","sleep_time_hour","meals_count","junk_food_count",
        "stress_level","work_hours","exercise_minutes","water_intake",
        "mood_score","screen_time_hrs","caffeine_cups"
    ]
    
    # ─────────────────────────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Health Monitor")
        st.markdown("---")
        mode = st.radio("Mode", ["Predict Single Record", "Analyze Full Dataset"], index=0)
        st.markdown("---")
    
        if "Single" in mode:
            st.markdown("### Enter Today's Data")
            sleep_hours      = st.slider("Sleep Hours",        0.0, 12.0, 6.5, 0.5)
            sleep_time_hour  = st.slider("Sleep Time (24h)",   20,  4,    23)
            meals_count      = st.slider("Meals Today",        0,   5,    2)
            junk_food_count  = st.slider("Junk Food",          0,   8,    2)
            # Read mapped emotion from state
        detected_emotion = st.session_state.get("detected_emotion", "neutral")
        emotion_map = {
            "happy": (3, 9), "surprise": (4, 8), "neutral": (5, 7),
            "disgust": (6, 5), "sad": (7, 3), "angry": (8, 2), "fear": (9, 2)
        }
        default_stress, default_mood = emotion_map.get(detected_emotion, (6, 5))
        st.sidebar.info(f"🎭 Live Emotion: **{detected_emotion.upper()}** (Stress: {default_stress}, Mood: {default_mood})")
        stress_level     = st.slider("Stress Level",       1,   10,   default_stress)
        work_hours       = st.slider("Work Hours",         0.0, 18.0, 9.0, 0.5)
        exercise_minutes = st.slider("Exercise (min)",     0,   120,  20)
        water_intake     = st.slider("Water (liters)",     0.0, 5.0,  1.5, 0.25)
        mood_score       = st.slider("Mood Score",         1,   10,   default_mood)
        screen_time_hrs  = st.slider("Screen Time (hrs)",  0.0, 14.0, 7.0, 0.5)
        caffeine_cups    = st.slider("Caffeine Cups",      0,   6,    2)
        predict_btn = st.button("Run Prediction", type="primary", use_container_width=True)
    
    # ─────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────
    st.markdown("""
    <h1 style='font-family:Syne,sans-serif; font-size:2.4rem; font-weight:800;
               letter-spacing:0.03em; margin-bottom:4px;'>
       Preventive Health Monitoring Engine
    </h1>
    <p style='color:#4a6080; font-size:0.9rem; letter-spacing:0.08em;'>
      ML-POWERED · BURNOUT · STRESS · SLEEP · HABITS · HEALTH SCORE
    </p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # MODE 1 — SINGLE PREDICTION
    # ─────────────────────────────────────────────────────────────
    if "Single" in mode:
        if predict_btn:
            row = {
                "sleep_hours":      sleep_hours,
                "sleep_time_hour":  sleep_time_hour,
                "meals_count":      meals_count,
                "junk_food_count":  junk_food_count,
                "stress_level":     stress_level,
                "work_hours":       work_hours,
                "exercise_minutes": exercise_minutes,
                "water_intake":     water_intake,
                "mood_score":       mood_score,
                "screen_time_hrs":  screen_time_hrs,
                "caffeine_cups":    caffeine_cups,
            }
    
            res = predictor.predict(row)
            hs  = res["health_score"]
    
            # ── ALERTS ──────────────────────────────────────────
            st.markdown('<div class="section-title">ALERT STATUS</div>', unsafe_allow_html=True)
            alerts = []
    
            if res["burnout_risk_prob"] > 70:
                alerts.append(("emergency", f'BURNOUT RISK DETECTED — {res["burnout_risk_prob"]}% probability. Immediate rest required.'))
            elif res["burnout_risk_prob"] > 45:
                alerts.append(("critical", f'Elevated Burnout Risk — {res["burnout_risk_prob"]}%. Reduce workload.'))
    
            if res["stress_overload_prob"] > 65:
                alerts.append(("critical", f'STRESS OVERLOAD — {res["stress_overload_prob"]}% probability. Intervention recommended.'))
    
            if res["sleep_deprived_prob"] > 60:
                alerts.append(("high", f'Sleep Deprivation Detected — {res["sleep_deprived_prob"]}% risk. Target 7–8 hrs tonight.'))
    
            if res["poor_habits_prob"] > 55:
                alerts.append(("high", f'Poor Health Habits — {res["poor_habits_prob"]}% score. Review diet & hydration.'))
    
            if hs < 35:
                alerts.append(("emergency", f'CRITICAL HEALTH SCORE: {hs}/100. Please consult a doctor.'))
    
            if not alerts:
                st.markdown('<div class="alert-box alert-ok">All systems normal. Health looks good today!</div>',
                            unsafe_allow_html=True)
            else:
                for sev, msg in alerts:
                    st.markdown(f'<div class="alert-box alert-{sev}">{msg}</div>', unsafe_allow_html=True)
    
            # ── METRIC CARDS ────────────────────────────────────
            st.markdown('<div class="section-title"> PREDICTION RESULTS</div>', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns(5)
    
            def score_color(v, invert=False):
                thresholds = (40, 65) if not invert else (60, 75)
                if invert:
                    return "val-ok" if v > 75 else "val-warn" if v > 50 else "val-crit"
                return "val-crit" if v > thresholds[1] else "val-warn" if v > thresholds[0] else "val-ok"
    
            with c1:
                hc = "val-crit" if hs < 40 else "val-warn" if hs < 65 else "val-ok"
                st.markdown(f'<div class="card"><div class="{hc}">{hs}</div>'
                            f'<div class="lbl">Health Score</div></div>', unsafe_allow_html=True)
            with c2:
                cls = score_color(res["burnout_risk_prob"])
                st.markdown(f'<div class="card"><div class="{cls}">{res["burnout_risk_prob"]}%</div>'
                            f'<div class="lbl">Burnout Risk</div></div>', unsafe_allow_html=True)
            with c3:
                cls = score_color(res["stress_overload_prob"])
                st.markdown(f'<div class="card"><div class="{cls}">{res["stress_overload_prob"]}%</div>'
                            f'<div class="lbl">Stress Overload</div></div>', unsafe_allow_html=True)
            with c4:
                cls = score_color(res["sleep_deprived_prob"])
                st.markdown(f'<div class="card"><div class="{cls}">{res["sleep_deprived_prob"]}%</div>'
                            f'<div class="lbl">Sleep Deprived</div></div>', unsafe_allow_html=True)
            with c5:
                cls = score_color(res["poor_habits_prob"])
                st.markdown(f'<div class="card"><div class="{cls}">{res["poor_habits_prob"]}%</div>'
                            f'<div class="lbl">Poor Habits</div></div>', unsafe_allow_html=True)
    
            # ── RADAR CHART ─────────────────────────────────────
            st.markdown('<div class="section-title">RISK PROFILE</div>', unsafe_allow_html=True)
            categories = ["Burnout Risk", "Stress Overload", "Sleep Deprived",
                          "Poor Habits", "Burnout Risk"]
            values = [
                res["burnout_risk_prob"], res["stress_overload_prob"],
                res["sleep_deprived_prob"], res["poor_habits_prob"],
                res["burnout_risk_prob"]
            ]
            fig_radar = go.Figure(go.Scatterpolar(
                r=values, theta=categories,
                fill="toself",
                line=dict(color="#ff3b3b", width=2),
                fillcolor="rgba(255,59,59,0.15)"
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#0f1520",
                    radialaxis=dict(visible=True, range=[0, 100],
                                    gridcolor="#1e2d45", tickcolor="#4a6080",
                                    tickfont=dict(color="#4a6080")),
                    angularaxis=dict(gridcolor="#1e2d45",
                                     tickfont=dict(color="#8ab0d0"))
                ),
                paper_bgcolor="#080c12",
                font=dict(color="#8ab0d0"),
                height=380,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
        else:
            st.info("👈 Fill in today's health data in the sidebar and click **Run Prediction**")
    
    # ─────────────────────────────────────────────────────────────
    # MODE 2 — FULL DATASET ANALYSIS
    # ─────────────────────────────────────────────────────────────
    else:
        st.markdown('<div class="section-title">DATASET OVERVIEW</div>', unsafe_allow_html=True)
    
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records",   len(df_full))
        col2.metric("Burnout Cases",   f"{df_full['burnout_risk'].sum()} ({df_full['burnout_risk'].mean()*100:.1f}%)")
        col3.metric("Stress Overload", f"{df_full['stress_overload'].sum()} ({df_full['stress_overload'].mean()*100:.1f}%)")
        col4.metric("Sleep Deprived",  f"{df_full['sleep_deprived'].sum()} ({df_full['sleep_deprived'].mean()*100:.1f}%)")
    
        # Run batch predictions
        with st.spinner("Running ML predictions on full dataset..."):
            df_pred = predictor.predict_batch(df_full.copy())
    
        # ── DISTRIBUTION CHARTS ──────────────────────────────────
        st.markdown('<div class="section-title">FEATURE DISTRIBUTIONS</div>', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["Sleep & Work", "Stress & Mood", "Diet & Habits"])
    
        with t1:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.histogram(df_full, x="sleep_hours", nbins=30,
                                   color_discrete_sequence=["#4db8ff"],
                                   title="Sleep Hours Distribution")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.histogram(df_full, x="work_hours", nbins=30,
                                   color_discrete_sequence=["#ff6b42"],
                                   title="Work Hours Distribution")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
    
        with t2:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.histogram(df_full, x="stress_level", nbins=10,
                                   color_discrete_sequence=["#ff3b3b"],
                                   title="Stress Level Distribution")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.histogram(df_full, x="mood_score", nbins=10,
                                   color_discrete_sequence=["#2ecc71"],
                                   title="Mood Score Distribution")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
    
        with t3:
            col_a, col_b = st.columns(2)
            with col_a:
                fig = px.histogram(df_full, x="junk_food_count", nbins=8,
                                   color_discrete_sequence=["#ffd600"],
                                   title="Junk Food Count")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.histogram(df_full, x="water_intake", nbins=20,
                                   color_discrete_sequence=["#00bcd4"],
                                   title="Water Intake (L)")
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                  plot_bgcolor="#0f1520", height=300)
                st.plotly_chart(fig, use_container_width=True)
    
        # ── PREDICTION PROBABILITIES SCATTER ────────────────────
        st.markdown('<div class="section-title">ML PREDICTIONS ON DATASET</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df_pred, x="burnout_risk_prob", y="stress_overload_prob",
            color="health_score_pred",
            color_continuous_scale="RdYlGn",
            size="work_hours",
            hover_data=["sleep_hours","stress_level","mood_score"],
            title="Burnout vs Stress Risk (size = work hours, color = health score)",
            labels={"burnout_risk_prob": "Burnout Risk %",
                    "stress_overload_prob": "Stress Overload %"}
        )
        fig_scatter.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                   plot_bgcolor="#0f1520", height=450)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
        # ── CORRELATION HEATMAP ──────────────────────────────────
        st.markdown('<div class="section-title">FEATURE CORRELATION</div>', unsafe_allow_html=True)
        corr = df_full[FEATURES + ["health_score"]].corr()
        fig_heat = px.imshow(
            corr, text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Feature Correlation Matrix"
        )
        fig_heat.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                                height=500)
        st.plotly_chart(fig_heat, use_container_width=True)
    
        # ── LABEL BREAKDOWN BAR ──────────────────────────────────
        st.markdown('<div class="section-title">LABEL BREAKDOWN</div>', unsafe_allow_html=True)
        label_counts = {
            "Burnout Risk":    int(df_full["burnout_risk"].sum()),
            "Stress Overload": int(df_full["stress_overload"].sum()),
            "Sleep Deprived":  int(df_full["sleep_deprived"].sum()),
            "Poor Habits":     int(df_full["poor_habits"].sum()),
            "Skipping Meals":  int(df_full["skipping_meals"].sum()),
            "Late Sleep":      int(df_full["late_sleep"].sum()),
        }
        fig_bar = px.bar(
            x=list(label_counts.keys()),
            y=list(label_counts.values()),
            color=list(label_counts.values()),
            color_continuous_scale="Reds",
            title="Positive Case Count per Label"
        )
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor="#0f1520",
                               plot_bgcolor="#0f1520", showlegend=False, height=380)
        st.plotly_chart(fig_bar, use_container_width=True)
    
        # ── RAW DATA TABLE ───────────────────────────────────────
        st.markdown('<div class="section-title">RAW DATASET</div>', unsafe_allow_html=True)
        st.dataframe(df_full.head(50), use_container_width=True)
    
    st.markdown("---")
    st.caption(" Preventive Health Monitoring Engine · CSV + ML + Streamlit")

if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(
        page_title="Health Monitor Engine",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    render_health_monitor()
