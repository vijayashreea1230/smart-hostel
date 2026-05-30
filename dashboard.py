"""
AI FOCUS & PRODUCTIVITY ASSISTANT
"""

import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import random
import calendar
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="AI Focus Assistant",
#     page_icon=None,
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
def render_focus_assistant():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #0f1c2e !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 15% 25%, rgba(6,182,212,0.08) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 75%, rgba(99,102,241,0.08) 0%, transparent 55%),
            #0f1c2e !important;
    }
    [data-testid="stHeader"],
    [data-testid="stToolbar"]    { background: transparent !important; }
    section[data-testid="stSidebar"] { background: #0c1625 !important; }
    
    h1,h2,h3,h4 { font-family:'Orbitron',monospace !important; color:#e2e8f0 !important; }
    p,label,.stMarkdown { font-family:'Rajdhani',sans-serif !important; }
    
    ::-webkit-scrollbar            { width:5px; }
    ::-webkit-scrollbar-track      { background:#1e2d42; }
    ::-webkit-scrollbar-thumb      { background:#06b6d4; border-radius:3px; }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg,#1a2d44 0%,#162438 100%) !important;
        border: 1.5px solid rgba(6,182,212,0.45) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 4px 18px rgba(6,182,212,0.15) !important;
    }
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] p,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] span {
        color: #38bdf8 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        opacity: 1 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="stMetricValue"] *  {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.55rem !important;
        color: #ffffff !important;
        opacity: 1 !important;
    }
    [data-testid="metric-container"] div,
    [data-testid="metric-container"] p,
    [data-testid="metric-container"] span {
        opacity: 1 !important;
    }
    
    .stButton > button {
        font-family:'Orbitron',monospace !important;
        font-weight:700 !important;
        letter-spacing:2px !important;
        border-radius:10px !important;
        transition:all 0.25s ease !important;
        border:none !important;
    }
    .stButton > button:hover {
        transform:translateY(-2px) !important;
        box-shadow:0 8px 28px rgba(6,182,212,0.40) !important;
    }
    
    div[role="progressbar"] {
        background-color:#1e3a5f !important;
        border-radius:6px !important;
    }
    div[role="progressbar"] > div {
        background:linear-gradient(90deg,#06b6d4,#6366f1) !important;
        border-radius:6px !important;
    }
    
    [data-testid="stDataFrame"] {
        border:1.5px solid rgba(6,182,212,0.22) !important;
        border-radius:12px !important;
    }
    
    hr { border-color:rgba(6,182,212,0.16) !important; }
    
    [data-testid="stSlider"] > div > div > div {
        background: linear-gradient(90deg,#06b6d4,#6366f1) !important;
    }
    [data-testid="stSlider"] label {
        font-family: 'Share Tech Mono', monospace !important;
        color: #38bdf8 !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    
    /* Tab styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: linear-gradient(135deg,#1a2d44,#162438) !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(6,182,212,0.22) !important;
        gap: 4px !important;
        padding: 4px !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.68rem !important;
        letter-spacing: 2px !important;
        color: #475569 !important;
        border-radius: 8px !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(135deg,#06b6d4,#6366f1) !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────
    # SESSION STATE
    # ─────────────────────────────────────────────────────────────
    def init_state():
        defaults = {
            "study_mode_active":     False,
            "timer_running":         False,
            "timer_seconds":         25 * 60,
            "timer_elapsed":         0,
            "sessions_completed":    0,
            "total_study_time":      0,
            "focus_score":           72,
            "streak":                0,
            "session_history":       [],
            "quote_index":           0,
            "rec_indices":           random.sample(range(10), 4),
            "badges_earned":         [],
            "session_duration":      25,
            "play_quote_audio":      False,
            "audio_quote_text":      "",
            # ── live tracking ──
            "live_focus_samples":    [],   # focus samples taken every 10s during active session
            "session_focus_scores":  [],   # final avg focus score per completed session
            "session_durations":     [],   # duration (min) per completed session
            # ── report log: {"YYYY-MM-DD": {"minutes":int, "sessions":int, "avg_focus":int}} ──
            "daily_log":             {},
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v
    
    init_state()
    
    # ─────────────────────────────────────────────────────────────
    # DATA
    # ─────────────────────────────────────────────────────────────
    QUOTES = [
        "Discipline beats motivation every single time.",
        "Consistency is the bridge between goals and achievement.",
        "Focus on progress, not perfection.",
        "Your future self is watching you right now.",
        "Small steps compound into extraordinary results.",
        "The secret of getting ahead is getting started.",
        "Success is the sum of small efforts repeated daily.",
        "Deep work is the superpower of the 21st century.",
        "Energy flows where attention goes.",
        "Win the morning, win the day.",
    ]
    
    AI_RECOMMENDATIONS = [
        ("", "Best focus hours detected between 7 PM and 9 PM"),
        ("", "Productivity improved by 15% this week"),
        ("", "Deep focus sessions increase retention by 40%"),
        ("⚡", "Your focus consistency is improving daily"),
        ("🧠", "Pomodoro rhythm detected — keep it up!"),
        ("", "Evening sessions show highest efficiency"),
        ("", "You study best in 25-minute bursts"),
        ("", "Drink water every 30 min for peak performance"),
        ("", "Set a clear goal before each session"),
        ("", "3 completed sessions boost retention by 60%"),
    ]
    
    BADGE_RULES = {
        "Goal Crusher":        lambda s: s >= 1,
        "Deep Thinker":        lambda s: s >= 2,
        "Study Warrior":       lambda s: s >= 3,
        "Focus Champion":      lambda s: s >= 5,
        "Productivity Master": lambda s: s >= 7,
        "Consistency King":    lambda s: s >= 10,
    }
    
    FOCUS_STATUSES = [
        ("Deep Focus",       "", "#10b981"),
        ("Moderate Focus",   "", "#f59e0b"),
        ("Productive State", "", "#3b82f6"),
    ]
    
    # ─────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────
    def card(html: str, accent: str = "#06b6d4"):
        st.markdown(
            "<div style='"
            "background:linear-gradient(135deg,#1a2d44 0%,#162438 100%);"
            f"border:1.5px solid {accent}44;"
            "border-radius:14px;padding:20px 24px;margin:6px 0;"
            f"box-shadow:0 4px 22px {accent}14,inset 0 1px 0 rgba(255,255,255,0.04);"
            "position:relative;overflow:hidden;'>"
            "<div style='position:absolute;top:0;left:0;right:0;height:3px;"
            f"background:linear-gradient(90deg,transparent,{accent},transparent);'></div>"
            + html +
            "</div>",
            unsafe_allow_html=True,
        )
    
    def section_header(text: str, icon: str = ""):
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;margin:26px 0 12px;'>"
            f"<span style='font-size:1.25rem;'>{icon}</span>"
            f"<h3 style='font-family:Orbitron,monospace;color:#38bdf8;"
            f"font-size:0.80rem;letter-spacing:3px;text-transform:uppercase;margin:0;'>{text}</h3>"
            f"<div style='flex:1;height:1.5px;"
            f"background:linear-gradient(90deg,#06b6d455,transparent);'></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    
    def metric_card(label, value, accent="#06b6d4"):
        return (
            f"<div style='"
            f"background:linear-gradient(135deg,#1a2d44 0%,#162438 100%);"
            f"border:1.5px solid {accent}77;"
            f"border-radius:14px;padding:20px 18px;text-align:center;"
            f"box-shadow:0 4px 18px {accent}22;position:relative;overflow:hidden;'>"
            f"<div style='position:absolute;top:0;left:0;right:0;height:3px;"
            f"background:linear-gradient(90deg,transparent,{accent},transparent);'></div>"
            f"<div style='font-family:Share Tech Mono,monospace;color:{accent};"
            f"font-size:0.68rem;letter-spacing:2.5px;text-transform:uppercase;"
            f"margin-bottom:10px;font-weight:600;'>{label}</div>"
            f"<div style='font-family:Orbitron,monospace;font-size:1.6rem;"
            f"font-weight:900;color:#ffffff;letter-spacing:1px;line-height:1.1;'>{value}</div>"
            f"</div>"
        )
    
    def no_data_card(msg="NO DATA YET · COMPLETE YOUR FIRST SESSION TO SEE THIS REPORT"):
        card(
            f"<div style='text-align:center;padding:18px 0;'>"
            f"<div style='font-size:1.8rem;margin-bottom:10px;'></div>"
            f"<div style='font-family:Share Tech Mono,monospace;color:#334155;"
            f"font-size:0.72rem;letter-spacing:3px;'>{msg}</div>"
            f"</div>",
            accent="#1e3a5f",
        )
    
    def update_badges():
        s = st.session_state.sessions_completed
        for badge, rule in BADGE_RULES.items():
            if rule(s) and badge not in st.session_state.badges_earned:
                st.session_state.badges_earned.append(badge)
    
    def focus_color(score):
        if score >= 80: return "#10b981"
        if score >= 60: return "#f59e0b"
        return "#ef4444"
    
    def speak_quote(quote_text: str):
        safe = quote_text.replace("'", "\\'").replace('"', '\\"')
        components.html(f"""
    <!DOCTYPE html><html><body>
    <script>
    (function(){{
      if (!window.speechSynthesis) return;
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance('{safe}');
      u.rate=0.92; u.pitch=1.18; u.volume=1.0;
      var voices = window.speechSynthesis.getVoices();
      var preferred = voices.find(v => v.lang.startsWith('en') && /female|zira|susan|samantha|karen/i.test(v.name))
                    || voices.find(v => v.lang.startsWith('en'));
      if (preferred) u.voice = preferred;
      window.speechSynthesis.speak(u);
    }})();
    window.speechSynthesis.onvoiceschanged = function(){{
      if (window.speechSynthesis.speaking) return;
      var u2 = new SpeechSynthesisUtterance('{safe}');
      u2.rate=0.92; u2.pitch=1.18; u2.volume=1.0;
      var v2 = window.speechSynthesis.getVoices();
      var p2 = v2.find(v => v.lang.startsWith('en') && /female|zira|susan|samantha|karen/i.test(v.name))
              || v2.find(v => v.lang.startsWith('en'));
      if (p2) u2.voice = p2;
      window.speechSynthesis.speak(u2);
    }};
    </script></body></html>""", height=0)
    
    def complete_session():
        dur = st.session_state.session_duration
        samples = st.session_state.live_focus_samples
        if samples:
            final_focus = min(100, int(sum(samples) / len(samples)))
        else:
            final_focus = min(100, st.session_state.focus_score + random.randint(1, 4))
    
        st.session_state.sessions_completed += 1
        st.session_state.total_study_time   += dur
        st.session_state.focus_score         = final_focus
        st.session_state.streak             += 1
    
        # per-session live records
        st.session_state.session_focus_scores.append(final_focus)
        st.session_state.session_durations.append(dur)
        st.session_state.live_focus_samples = []
    
        new_qi = (st.session_state.quote_index + 1) % len(QUOTES)
        st.session_state.quote_index  = new_qi
        st.session_state.rec_indices  = random.sample(range(len(AI_RECOMMENDATIONS)), 4)
    
        st.session_state.session_history.append({
            "Session":     st.session_state.sessions_completed,
            "Date":        datetime.now().strftime("%Y-%m-%d"),
            "Time":        datetime.now().strftime("%H:%M"),
            "Duration":    f"{dur} min",
            "Focus Score": f"{final_focus}%",
            "Status":      "Completed",
        })
    
        # update daily log for reports
        today_key = datetime.now().strftime("%Y-%m-%d")
        log = st.session_state.daily_log
        if today_key not in log:
            log[today_key] = {"minutes": 0, "sessions": 0, "focus_sum": 0}
        log[today_key]["minutes"]   += dur
        log[today_key]["sessions"]  += 1
        log[today_key]["focus_sum"] += final_focus
        st.session_state.daily_log = log
    
        update_badges()
        st.session_state.play_quote_audio = True
        st.session_state.audio_quote_text = QUOTES[new_qi]
        st.session_state.study_mode_active = False
        st.session_state.timer_running     = False
        st.session_state.timer_seconds     = dur * 60
        st.session_state.timer_elapsed     = 0
        st.balloons()
    
    # matplotlib dark theme
    plt.rcParams.update({
        "figure.facecolor": "#1a2d44",
        "axes.facecolor":   "#162438",
        "axes.edgecolor":   "#1e3a5f",
        "axes.labelcolor":  "#94a3b8",
        "xtick.color":      "#64748b",
        "ytick.color":      "#64748b",
        "grid.color":       "#1e3a5f",
        "text.color":       "#94a3b8",
        "font.family":      "monospace",
    })
    
    # ═════════════════════════════════════════════════════════════
    # HEADER
    # ═════════════════════════════════════════════════════════════
    st.markdown(
        "<div style='text-align:center;padding:32px 0 8px;'>"
        "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
        "font-size:0.68rem;letter-spacing:6px;text-transform:uppercase;"
        "margin-bottom:8px;opacity:0.80;'>AI-POWERED FOCUS SYSTEM · v2.0</div>"
        "<h1 style='font-family:Orbitron,monospace;font-weight:900;font-size:2.2rem;"
        "background:linear-gradient(135deg,#06b6d4 0%,#6366f1 60%,#06b6d4 100%);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
        "background-clip:text;margin:0;letter-spacing:2px;'>"
        "AI FOCUS &amp; PRODUCTIVITY ASSISTANT</h1>"
        "<p style='color:#475569;font-family:Rajdhani,sans-serif;font-size:0.95rem;"
        "letter-spacing:3px;text-transform:uppercase;margin-top:8px;'>"
        "Intelligent Study Environment · Real-time Analytics · Deep Focus Tracking</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:0 0 8px;'>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # LIVE CLOCK
    # ═════════════════════════════════════════════════════════════
    _c1, _c2, _c3 = st.columns([1, 2, 1])
    with _c2:
        components.html("""
    <!DOCTYPE html><html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background: transparent; }
    .clock-wrap {
      background: linear-gradient(135deg,#1a2d44 0%,#162438 100%);
      border: 1.5px solid rgba(99,102,241,0.27);
      border-radius: 14px; padding: 20px 24px; text-align: center;
      box-shadow: 0 4px 22px rgba(99,102,241,0.08), inset 0 1px 0 rgba(255,255,255,0.04);
      position: relative; overflow: hidden;
    }
    .clock-bar { position:absolute;top:0;left:0;right:0;height:3px;
      background:linear-gradient(90deg,transparent,#6366f1,transparent); }
    .clock-label { font-family:'Share Tech Mono',monospace; color:#38bdf8;
      font-size:0.65rem; letter-spacing:4px; opacity:0.90; margin-bottom:6px; }
    .clock-time { font-family:'Orbitron',monospace; font-size:2.2rem;
      color:#e2e8f0; letter-spacing:6px; font-weight:900; }
    .clock-date { font-family:'Share Tech Mono',monospace; color:#6366f1;
      font-size:0.70rem; letter-spacing:3px; margin-top:6px; }
    </style>
    </head>
    <body>
    <div class="clock-wrap">
      <div class="clock-bar"></div>
      <div class="clock-label">LIVE SYSTEM CLOCK</div>
      <div class="clock-time" id="clock">--:--:--</div>
      <div class="clock-date" id="date"></div>
    </div>
    <script>
    var DAYS=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    var MONTHS=['January','February','March','April','May','June',
                'July','August','September','October','November','December'];
    function pad(n){return String(n).padStart(2,'0');}
    function tick(){
      var now=new Date();
      document.getElementById('clock').textContent=pad(now.getHours())+':'+pad(now.getMinutes())+':'+pad(now.getSeconds());
      document.getElementById('date').textContent=DAYS[now.getDay()]+', '+pad(now.getDate())+' '+MONTHS[now.getMonth()]+' '+now.getFullYear();
    }
    tick(); setInterval(tick,1000);
    </script>
    </body></html>
    """, height=130)
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # PRODUCTIVITY METRICS
    # ═════════════════════════════════════════════════════════════
    section_header("PRODUCTIVITY METRICS", "")
    
    prod_level = (
        "Elite " if st.session_state.focus_score >= 85
        else "High " if st.session_state.focus_score >= 70
        else "Medium "
    )
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(metric_card("Total Study Time",   f"{st.session_state.total_study_time} min", "#06b6d4"), unsafe_allow_html=True)
    m2.markdown(metric_card("Sessions Completed", st.session_state.sessions_completed,        "#6366f1"), unsafe_allow_html=True)
    m3.markdown(metric_card("Focus Score",        f"{st.session_state.focus_score}%",         "#10b981"), unsafe_allow_html=True)
    m4.markdown(metric_card("Study Streak",       f"{st.session_state.streak}",            "#f59e0b"), unsafe_allow_html=True)
    m5.markdown(metric_card("Productivity Level", prod_level,                                 "#ec4899"), unsafe_allow_html=True)
    
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # STUDY MODE CONTROL  +  TIMER
    # ═════════════════════════════════════════════════════════════
    section_header("STUDY MODE CONTROL", "")
    ctrl_left, ctrl_right = st.columns([1, 1], gap="large")
    
    with ctrl_left:
        if not st.session_state.study_mode_active:
            section_header("SESSION DURATION", "")
            dur_choice = st.slider(
                "Study session length (minutes)",
                min_value=1,
                max_value=120,
                value=st.session_state.session_duration,
                step=1,
                key="dur_slider",
            )
            st.session_state.session_duration = dur_choice
    
            st.markdown(
                f"<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                f"font-size:0.68rem;letter-spacing:2px;text-align:center;margin-top:4px;'>"
                f"SESSION SET TO {st.session_state.session_duration} MINUTES</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    
            if st.button("1 MIN DEMO", use_container_width=True):
                st.session_state.session_duration = 1
                st.rerun()
    
            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    
            if st.button("START STUDY MODE", use_container_width=True, type="primary"):
                st.session_state.study_mode_active = True
                st.session_state.timer_running     = True
                st.session_state.timer_seconds     = st.session_state.session_duration * 60
                st.session_state.timer_elapsed     = 0
                st.session_state.live_focus_samples = []
                st.rerun()
        else:
            if st.button("STOP SESSION", use_container_width=True):
                st.session_state.study_mode_active  = False
                st.session_state.timer_running      = False
                st.session_state.timer_seconds      = st.session_state.session_duration * 60
                st.session_state.timer_elapsed      = 0
                st.session_state.live_focus_samples = []
                st.rerun()
    
        if st.session_state.study_mode_active:
            card(
                "<div style='text-align:center;'>"
                "<div style='font-size:1.8rem;'>Success</div>"
                "<div style='font-family:Orbitron,monospace;color:#10b981;"
                "font-size:0.85rem;letter-spacing:2px;margin:8px 0;'>FOCUS SESSION ACTIVE</div>"
                "<div style='font-family:Rajdhani,sans-serif;color:#94a3b8;font-size:0.95rem;'>"
                f"Deep Focus Mode — {st.session_state.session_duration} min session</div>"
                "</div>",
                accent="#10b981",
            )
        else:
            card(
                "<div style='text-align:center;'>"
                "<div style='font-family:Orbitron,monospace;color:#475569;"
                "font-size:0.85rem;letter-spacing:2px;margin:8px 0;'>STANDBY MODE</div>"
                "<div style='font-family:Rajdhani,sans-serif;color:#64748b;font-size:0.92rem;'>"
                "Set your session duration above and press START</div>"
                "</div>",
                accent="#334155",
            )
    
        section_header("FOCUS ENERGY", "⚡")
        energy = min(100, st.session_state.focus_score + st.session_state.sessions_completed * 3)
        card(
            "<div>"
            "<div style='display:flex;justify-content:space-between;margin-bottom:8px;'>"
            "<span style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
            "font-size:0.70rem;letter-spacing:2px;'>NEURAL ENERGY</span>"
            f"<span style='font-family:Orbitron,monospace;color:#f0f9ff;font-size:0.85rem;'>{energy}%</span>"
            "</div>"
            "<div style='background:#1e3a5f;border-radius:8px;height:16px;overflow:hidden;'>"
            f"<div style='width:{energy}%;height:100%;"
            "background:linear-gradient(90deg,#06b6d4,#6366f1,#ec4899);"
            "border-radius:8px;box-shadow:0 0 10px #06b6d455;'>"
            "</div></div></div>",
        )
    
    with ctrl_right:
        section_header("FOCUS TIMER", "")
    
        @st.fragment(run_every=1 if st.session_state.timer_running else None)
        def timer_fragment():
            timer_ph = st.empty()
            if st.session_state.study_mode_active and st.session_state.timer_running:
                remaining = max(0, st.session_state.timer_seconds - st.session_state.timer_elapsed)
                mm  = remaining // 60
                ss  = remaining % 60
                total = st.session_state.timer_seconds
                pct = max(0.0, min(1.0, (total - remaining) / total)) if total > 0 else 0
    
                timer_ph.markdown(
                    "<div style='text-align:center;padding:18px 0;'>"
                    "<div style='font-family:Orbitron,monospace;font-size:4.5rem;font-weight:900;"
                    "background:linear-gradient(135deg,#06b6d4,#6366f1);"
                    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
                    f"background-clip:text;letter-spacing:8px;'>{mm:02d}:{ss:02d}</div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.70rem;letter-spacing:4px;margin-top:8px;'>SESSION IN PROGRESS</div>"
                    f"<div style='margin-top:12px;font-family:Rajdhani,sans-serif;color:#64748b;"
                    f"font-size:0.88rem;'>{st.session_state.session_duration} min session · "
                    f"{int(pct*100)}% complete</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.progress(pct)
    
                # ── sample focus every 10s using a realistic curve ──
                elapsed = st.session_state.timer_elapsed
                total_s = st.session_state.timer_seconds
                if elapsed > 0 and elapsed % 10 == 0:
                    phase = elapsed / total_s if total_s > 0 else 0
                    if phase < 0.20:                          # warm-up: climbing
                        base = 55 + int(phase * 5 * 25)
                    elif phase < 0.70:                        # deep focus peak
                        base = 80 + random.randint(-4, 8)
                    else:                                     # cool-down: slight dip
                        base = 76 + random.randint(-6, 4)
                    sample = min(100, max(50, base))
                    st.session_state.live_focus_samples.append(sample)
                    st.session_state.focus_score = sample    # update live metric card too
    
                st.session_state.timer_elapsed += 1
                if st.session_state.timer_elapsed >= st.session_state.timer_seconds:
                    complete_session()
                    st.rerun()
    
            elif not st.session_state.study_mode_active and st.session_state.sessions_completed > 0:
                timer_ph.markdown(
                    "<div style='text-align:center;padding:18px 0;'>"
                    "<div style='font-family:Orbitron,monospace;font-size:1.5rem;font-weight:700;"
                    "color:#f59e0b;letter-spacing:3px;'>BREAK TIME!</div>"
                    "<div style='font-family:Rajdhani,sans-serif;color:#64748b;"
                    "font-size:1rem;margin-top:8px;'>Drink water · Stretch · Rest your eyes</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                dur_disp = st.session_state.session_duration
                timer_ph.markdown(
                    "<div style='text-align:center;padding:18px 0;'>"
                    "<div style='font-family:Orbitron,monospace;font-size:4.5rem;font-weight:900;"
                    f"color:#1e3a5f;letter-spacing:8px;'>{dur_disp:02d}:00</div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#334155;"
                    "font-size:0.70rem;letter-spacing:4px;margin-top:8px;'>READY TO START</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
    
        timer_fragment()
    
        # Focus Status
        if st.session_state.study_mode_active:
            fs_label, fs_dot, fs_color = FOCUS_STATUSES[0]
        elif st.session_state.sessions_completed > 0:
            fs_label, fs_dot, fs_color = FOCUS_STATUSES[2]
        else:
            fs_label, fs_dot, fs_color = FOCUS_STATUSES[1]
    
        card(
            "<div style='text-align:center;'>"
            "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
            "font-size:0.65rem;letter-spacing:3px;margin-bottom:6px;'>FOCUS STATUS</div>"
            f"<div style='font-family:Orbitron,monospace;font-size:1.05rem;"
            f"color:{fs_color};letter-spacing:1px;'>{fs_dot} {fs_label}</div>"
            "</div>",
            accent=fs_color,
        )
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # LIVE ANALYTICS  (replaces old demo charts)
    # ═════════════════════════════════════════════════════════════
    section_header("LIVE SESSION ANALYTICS", "")
    
    scores    = st.session_state.session_focus_scores
    durations = st.session_state.session_durations
    
    # ── uniform 4-column grid — all charts same width & height ──
    CHART_H = 3.4   # identical height for every chart
    ac1, ac2, ac3, ac4 = st.columns(4, gap="medium")
    
    # ── Chart 1: Focus Score per Session line chart ──
    with ac1:
        fig1, ax1 = plt.subplots(figsize=(4, CHART_H))
        if scores:
            xs = list(range(len(scores)))
            ax1.fill_between(xs, scores, alpha=0.15, color="#6366f1")
            ax1.plot(xs, scores, color="#6366f1", linewidth=2.2,
                     marker="o", markersize=6,
                     markerfacecolor="#0f1c2e", markeredgecolor="#6366f1", markeredgewidth=1.8)
            for x, y in zip(xs, scores):
                ax1.text(x, y + 2.8, f"{y}%", ha="center", fontsize=7, color=focus_color(y))
            ax1.set_xticks(xs)
            ax1.set_xticklabels([f"S{i+1}" for i in xs], fontsize=8)
            ax1.axhline(80, color="#10b981", linewidth=0.8, linestyle="--", alpha=0.5)
            ax1.axhline(60, color="#f59e0b", linewidth=0.8, linestyle="--", alpha=0.5)
        else:
            ax1.text(0.5, 0.5, "Complete a session\nto see focus trend",
                     ha="center", va="center", transform=ax1.transAxes,
                     color="#475569", fontsize=9)
        ax1.set_ylim(0, 115)
        ax1.set_title("FOCUS / SESSION", fontsize=8.5, color="#6366f1", pad=10)
        ax1.set_ylabel("Focus %", fontsize=7)
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        fig1.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)
    
    # ── Chart 2: Live focus donut (rolling avg during session) ──
    with ac2:
        fig2, ax2 = plt.subplots(figsize=(4, CHART_H))
        samples = st.session_state.live_focus_samples
        if st.session_state.study_mode_active and samples:
            fs_val       = int(sum(samples) / len(samples))
            ring_color   = focus_color(fs_val)
            title_suffix = "LIVE AVG"
        else:
            fs_val       = st.session_state.focus_score
            ring_color   = focus_color(fs_val)
            title_suffix = "LAST SESSION"
        ax2.pie(
            [fs_val, 100 - fs_val],
            colors=[ring_color, "#1e3a5f"],
            startangle=90,
            wedgeprops=dict(width=0.46, edgecolor="#0f1c2e", linewidth=1.5),
        )
        ax2.text(0,  0.10, f"{fs_val}%",  ha="center", va="center",
                 fontsize=18, color="#f0f9ff", fontweight="bold")
        ax2.text(0, -0.24, title_suffix, ha="center", va="center",
                 fontsize=7, color=ring_color, fontfamily="monospace")
        ax2.set_title("FOCUS (LIVE)", fontsize=8.5, color=ring_color, pad=10)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    
    # ── Chart 3: Session Durations bar chart ──
    with ac3:
        fig3, ax3 = plt.subplots(figsize=(4, CHART_H))
        if durations:
            labels   = [f"S{i+1}" for i in range(len(durations))]
            bar_clrs = ["#06b6d4" if d >= 25 else "#6366f1" if d >= 15 else "#f59e0b"
                        for d in durations]
            bars = ax3.bar(labels, durations, color=bar_clrs, width=0.55,
                           edgecolor="#0f1c2e", linewidth=0.5)
            for b, v in zip(bars, durations):
                ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.4,
                         f"{v}m", ha="center", va="bottom", fontsize=7, color="#94a3b8")
            ax3.set_ylim(0, max(max(durations) * 1.40, 10))
        else:
            ax3.text(0.5, 0.5, "No sessions yet",
                     ha="center", va="center", transform=ax3.transAxes,
                     color="#475569", fontsize=9)
            ax3.set_ylim(0, 10)
        ax3.set_title("DURATIONS", fontsize=8.5, color="#10b981", pad=10)
        ax3.set_ylabel("Minutes", fontsize=7)
        ax3.grid(axis="y", linestyle="--", alpha=0.4)
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
    
    # ── Chart 4: Current focus donut (always current score) ──
    with ac4:
        fig4, ax4 = plt.subplots(figsize=(4, CHART_H))
        fs_now = st.session_state.focus_score
        rc     = focus_color(fs_now)
        ax4.pie(
            [fs_now, 100 - fs_now],
            colors=[rc, "#1e3a5f"],
            startangle=90,
            wedgeprops=dict(width=0.45, edgecolor="#0f1c2e", linewidth=1.5),
        )
        ax4.text(0, 0, f"{fs_now}%", ha="center", va="center",
                 fontsize=18, color="#f0f9ff", fontweight="bold")
        ax4.set_title("CURRENT FOCUS", fontsize=8.5, color=rc, pad=10)
        fig4.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # MOTIVATIONAL QUOTE  +  AI RECOMMENDATIONS
    # ═════════════════════════════════════════════════════════════
    q_col, r_col = st.columns([1, 1], gap="large")
    
    with q_col:
        section_header("MOTIVATIONAL CORE", "")
        quote = QUOTES[st.session_state.quote_index % len(QUOTES)]
    
        # ── Auto-play fires HERE — top of section, before anything else renders ──
        # This guarantees the audio component is injected into the page on the
        # same render cycle that sets play_quote_audio = True.
        _session_just_finished = st.session_state.play_quote_audio
        if _session_just_finished:
            st.session_state.play_quote_audio = False
            speak_quote(st.session_state.audio_quote_text)
    
        card(
            "<div style='text-align:center;padding:10px 0;'>"
            "<div style='font-size:1.8rem;margin-bottom:12px;'></div>"
            f"<div style='font-family:Rajdhani,sans-serif;font-size:1.15rem;"
            f"color:#e2e8f0;font-weight:600;line-height:1.6;font-style:italic;'>"
            f"&ldquo;{quote}&rdquo;</div>"
            "<div style='margin-top:14px;font-family:Share Tech Mono,monospace;"
            "color:#38bdf8;font-size:0.65rem;letter-spacing:3px;opacity:0.7;'>"
            "— AI PRODUCTIVITY ENGINE</div>"
            "</div>",
            accent="#6366f1",
        )
    
        # ── Only STOP AUDIO button remains — no manual speak ──
        if st.button("🔇  STOP AUDIO", use_container_width=True):
            components.html(
                "<script>window.speechSynthesis && window.speechSynthesis.cancel();</script>",
                height=0,
            )
    
        if _session_just_finished:
            card(
                "<div style='text-align:center;'>"
                "<div style='font-size:1.4rem;'>🎉</div>"
                "<div style='font-family:Orbitron,monospace;color:#10b981;"
                "font-size:0.78rem;letter-spacing:2px;margin:6px 0;'>SESSION COMPLETE!</div>"
                "<div style='font-family:Rajdhani,sans-serif;color:#94a3b8;font-size:0.92rem;'>"
                "🔊 Motivational quote playing automatically…</div>"
                "</div>",
                accent="#10b981",
            )
    
    with r_col:
        section_header("AI RECOMMENDATIONS", "")
        for i in st.session_state.rec_indices:
            icon, text = AI_RECOMMENDATIONS[i]
            card(
                "<div style='display:flex;align-items:center;gap:12px;'>"
                f"<span style='font-size:1.3rem;'>{icon}</span>"
                f"<span style='font-family:Rajdhani,sans-serif;color:#cbd5e1;"
                f"font-size:0.98rem;font-weight:600;'>{text}</span>"
                "</div>",
                accent="#10b981",
            )
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # WOW FEATURES
    # ═════════════════════════════════════════════════════════════
    section_header("WOW FEATURES", "")
    w1, w2 = st.columns(2, gap="medium")
    
    with w1:
        card(
            "<div style='text-align:center;'>"
            "<div style='font-size:2rem;'></div>"
            "<div style='font-family:Share Tech Mono,monospace;color:#d97706;"
            "font-size:0.65rem;letter-spacing:3px;margin:6px 0;'>CURRENT STREAK</div>"
            f"<div style='font-family:Orbitron,monospace;font-size:2.8rem;"
            f"color:#f59e0b;font-weight:900;'>{st.session_state.streak}</div>"
            "<div style='font-family:Rajdhani,sans-serif;color:#94a3b8;font-size:0.88rem;'>"
            "consecutive sessions</div>"
            "<div style='margin-top:10px;font-family:Share Tech Mono,monospace;"
            "color:#38bdf8;font-size:0.65rem;letter-spacing:2px;'>DAILY CONSISTENCY</div>"
            "</div>",
            accent="#f59e0b",
        )
        st.progress(min(1.0, st.session_state.streak * 0.1 + 0.4))
    
    with w2:
        update_badges()
        badges = (st.session_state.badges_earned
                  if st.session_state.badges_earned
                  else ["Complete your first session to earn badges!"])
        badge_rows = "".join(
            "<div style='margin:5px 0;padding:7px 12px;"
            "background:rgba(16,185,129,0.10);border-radius:8px;"
            "border-left:3px solid #10b981;"
            f"font-family:Rajdhani,sans-serif;color:#e2e8f0;"
            f"font-size:0.92rem;font-weight:600;'>{b}</div>"
            for b in badges
        )
        card(
            "<div>"
            "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
            "font-size:0.65rem;letter-spacing:3px;margin-bottom:10px;'>ACHIEVEMENT BADGES</div>"
            + badge_rows +
            "</div>",
            accent="#10b981",
        )
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # SESSION HISTORY
    # ═════════════════════════════════════════════════════════════
    section_header("SESSION HISTORY", "")
    if st.session_state.session_history:
        df = pd.DataFrame(st.session_state.session_history)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        card(
            "<div style='text-align:center;padding:14px 0;'>"
            "<div style='font-family:Share Tech Mono,monospace;color:#334155;"
            "font-size:0.75rem;letter-spacing:3px;'>"
            "NO SESSIONS RECORDED YET · START YOUR FIRST FOCUS SESSION</div>"
            "</div>",
            accent="#1e3a5f",
        )
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # PRODUCTIVITY REPORTS  —  Daily / Weekly / Monthly
    # ═════════════════════════════════════════════════════════════
    section_header("PRODUCTIVITY REPORTS", "")
    
    log = st.session_state.daily_log   # {"YYYY-MM-DD": {"minutes":int,"sessions":int,"focus_sum":int}}
    
    def avg_focus(entry):
        """Return average focus % for a log entry."""
        s = entry.get("sessions", 0)
        return int(entry["focus_sum"] / s) if s > 0 else 0
    
    tab_d, tab_w, tab_m = st.tabs(["DAILY REPORT", "WEEKLY REPORT", "MONTHLY REPORT"])
    
    # ── DAILY ──────────────────────────────────────────────────
    with tab_d:
        today_key  = datetime.now().strftime("%Y-%m-%d")
        today_data = log.get(today_key)
    
        if today_data:
            af = avg_focus(today_data)
            d1, d2, d3, d4 = st.columns(4)
            d1.markdown(metric_card("Study Time Today",  f"{today_data['minutes']} min", "#06b6d4"), unsafe_allow_html=True)
            d2.markdown(metric_card("Sessions Today",     today_data['sessions'],         "#6366f1"), unsafe_allow_html=True)
            d3.markdown(metric_card("Avg Focus Score",   f"{af}%",                        "#10b981"), unsafe_allow_html=True)
            level = "Elite " if af >= 85 else "High " if af >= 70 else "Medium "
            d4.markdown(metric_card("Focus Level",        level,                          "#ec4899"), unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    
            # Bar: last 7 days
            days_7   = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            labels_7 = [(datetime.now() - timedelta(days=i)).strftime("%a\n%d %b")  for i in range(6, -1, -1)]
            mins_7   = [log.get(d, {}).get("minutes", 0) for d in days_7]
            focus_7  = [avg_focus(log[d]) if d in log else 0 for d in days_7]
            clrs_7   = ["#06b6d4" if d == today_key else "#1e3a5f" for d in days_7]
    
            fig_d, (axd1, axd2) = plt.subplots(1, 2, figsize=(12, 3.2))
    
            bars = axd1.bar(labels_7, mins_7, color=clrs_7, width=0.55, edgecolor="#0f1c2e", linewidth=0.5)
            for b, v in zip(bars, mins_7):
                if v > 0:
                    axd1.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                              f"{v}m", ha="center", va="bottom", fontsize=8, color="#94a3b8")
            axd1.set_ylim(0, max(max(mins_7)*1.35, 10))
            axd1.set_title("LAST 7 DAYS — STUDY MINUTES  (today = cyan)", fontsize=8.5, color="#06b6d4", pad=10)
            axd1.set_ylabel("Minutes", fontsize=8)
            axd1.grid(axis="y", linestyle="--", alpha=0.4)
    
            focus_clrs = [focus_color(v) if v > 0 else "#1e3a5f" for v in focus_7]
            bars2 = axd2.bar(labels_7, focus_7, color=focus_clrs, width=0.55, edgecolor="#0f1c2e", linewidth=0.5)
            for b, v in zip(bars2, focus_7):
                if v > 0:
                    axd2.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                              f"{v}%", ha="center", va="bottom", fontsize=8, color="#94a3b8")
            axd2.set_ylim(0, 115)
            axd2.axhline(80, color="#10b981", linewidth=0.8, linestyle="--", alpha=0.5)
            axd2.axhline(60, color="#f59e0b", linewidth=0.8, linestyle="--", alpha=0.5)
            axd2.set_title("LAST 7 DAYS — AVG FOCUS SCORE", fontsize=8.5, color="#6366f1", pad=10)
            axd2.set_ylabel("Focus %", fontsize=8)
            axd2.grid(axis="y", linestyle="--", alpha=0.4)
    
            fig_d.tight_layout()
            st.pyplot(fig_d)
            plt.close(fig_d)
    
            # Insight cards
            best_day_idx = mins_7.index(max(mins_7)) if max(mins_7) > 0 else None
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>MOST ACTIVE DAY (7D)</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.0rem;'>{labels_7[best_day_idx].replace(chr(10),' ') if best_day_idx is not None else 'N/A'}</div>"
                    "</div>", accent="#06b6d4")
            with ic2:
                total_7 = sum(mins_7)
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>TOTAL (LAST 7 DAYS)</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.0rem;'>{total_7} min</div>"
                    "</div>", accent="#6366f1")
            with ic3:
                nz = [v for v in focus_7 if v > 0]
                avg7 = int(sum(nz)/len(nz)) if nz else 0
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>AVG FOCUS (7D)</div>"
                    f"<div style='font-family:Orbitron,monospace;color:{focus_color(avg7)};"
                    f"font-size:1.0rem;'>{avg7}%</div>"
                    "</div>", accent="#10b981")
        else:
            no_data_card()
    
    # ── WEEKLY ─────────────────────────────────────────────────
    with tab_w:
        today      = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_days  = [week_start + timedelta(days=i) for i in range(7)]
        week_keys  = [d.strftime("%Y-%m-%d") for d in week_days]
        week_mins  = [log.get(k, {}).get("minutes", 0) for k in week_keys]
        week_sess  = [log.get(k, {}).get("sessions", 0) for k in week_keys]
        week_focus = [avg_focus(log[k]) if k in log else 0 for k in week_keys]
    
        week_total_min  = sum(week_mins)
        week_total_sess = sum(week_sess)
        nz_wf = [v for v in week_focus if v > 0]
        week_avg_focus  = int(sum(nz_wf)/len(nz_wf)) if nz_wf else 0
    
        if week_total_min > 0:
            w1c, w2c, w3c, w4c = st.columns(4)
            w1c.markdown(metric_card("This Week Study",    f"{week_total_min} min", "#06b6d4"), unsafe_allow_html=True)
            w2c.markdown(metric_card("Sessions This Week",  week_total_sess,        "#6366f1"), unsafe_allow_html=True)
            w3c.markdown(metric_card("Avg Focus Score",    f"{week_avg_focus}%",    "#10b981"), unsafe_allow_html=True)
            best_day_w = week_days[week_mins.index(max(week_mins))].strftime("%A") if max(week_mins) > 0 else "—"
            w4c.markdown(metric_card("Best Day",            best_day_w,             "#f59e0b"), unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    
            day_labels = [d.strftime("%A\n%d %b") for d in week_days]
            today_str  = today.strftime("%Y-%m-%d")
            bar_clrs_w = ["#06b6d4" if k == today_str else "#6366f1" for k in week_keys]
            fc_clrs_w  = [focus_color(v) if v > 0 else "#1e3a5f" for v in week_focus]
    
            fig_w, (axw1, axw2) = plt.subplots(1, 2, figsize=(14, 3.2))
    
            bars_w = axw1.bar(day_labels, week_mins, color=bar_clrs_w, width=0.55,
                              edgecolor="#0f1c2e", linewidth=0.5)
            for b, v, s in zip(bars_w, week_mins, week_sess):
                if v > 0:
                    axw1.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                              f"{v}m\n{s}s", ha="center", va="bottom", fontsize=7, color="#94a3b8")
            axw1.set_ylim(0, max(max(week_mins)*1.35, 10))
            axw1.set_title("THIS WEEK — STUDY MINUTES  (today = cyan)", fontsize=8.5, color="#6366f1", pad=10)
            axw1.set_ylabel("Minutes", fontsize=8)
            axw1.grid(axis="y", linestyle="--", alpha=0.4)
    
            bars_wf = axw2.bar(day_labels, week_focus, color=fc_clrs_w, width=0.55,
                               edgecolor="#0f1c2e", linewidth=0.5)
            for b, v in zip(bars_wf, week_focus):
                if v > 0:
                    axw2.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                              f"{v}%", ha="center", va="bottom", fontsize=7.5, color="#94a3b8")
            axw2.set_ylim(0, 115)
            axw2.axhline(80, color="#10b981", linewidth=0.8, linestyle="--", alpha=0.5)
            axw2.axhline(60, color="#f59e0b", linewidth=0.8, linestyle="--", alpha=0.5)
            axw2.set_title("THIS WEEK — AVG FOCUS SCORE PER DAY", fontsize=8.5, color="#10b981", pad=10)
            axw2.set_ylabel("Focus %", fontsize=8)
            axw2.grid(axis="y", linestyle="--", alpha=0.4)
    
            fig_w.tight_layout()
            st.pyplot(fig_w)
            plt.close(fig_w)
    
            # Weekly insight cards
            days_studied = sum(1 for v in week_mins if v > 0)
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>DAYS STUDIED</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.1rem;'>{days_studied} / 7</div>"
                    "</div>", accent="#06b6d4")
            with ic2:
                avg_daily = int(week_total_min / max(days_studied,1))
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>AVG DAILY STUDY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.1rem;'>{avg_daily} min</div>"
                    "</div>", accent="#6366f1")
            with ic3:
                consistency_pct = int(days_studied / 7 * 100)
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.62rem;letter-spacing:2px;margin:6px 0;'>WEEK CONSISTENCY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:{focus_color(consistency_pct)};"
                    f"font-size:1.1rem;'>{consistency_pct}%</div>"
                    "</div>", accent="#f59e0b")
        else:
            no_data_card()
    
    # ── MONTHLY ────────────────────────────────────────────────
    with tab_m:
        this_month   = datetime.now().strftime("%Y-%m")
        today_dt     = datetime.now()
        days_in_month = calendar.monthrange(today_dt.year, today_dt.month)[1]
        month_keys   = [f"{this_month}-{str(d).zfill(2)}" for d in range(1, days_in_month+1)]
        month_mins   = [log.get(k, {}).get("minutes", 0)  for k in month_keys]
        month_sess   = [log.get(k, {}).get("sessions", 0) for k in month_keys]
        month_focus  = [avg_focus(log[k]) if k in log else 0 for k in month_keys]
    
        month_total_min  = sum(month_mins)
        month_total_sess = sum(month_sess)
        nz_mf = [v for v in month_focus if v > 0]
        month_avg_focus  = int(sum(nz_mf)/len(nz_mf)) if nz_mf else 0
        days_studied_m   = sum(1 for v in month_mins if v > 0)
    
        if month_total_min > 0:
            mo1, mo2, mo3, mo4 = st.columns(4)
            mo1.markdown(metric_card("This Month Study",    f"{month_total_min} min",  "#06b6d4"), unsafe_allow_html=True)
            mo2.markdown(metric_card("Sessions This Month",  month_total_sess,          "#6366f1"), unsafe_allow_html=True)
            mo3.markdown(metric_card("Avg Focus Score",     f"{month_avg_focus}%",      "#10b981"), unsafe_allow_html=True)
            mo4.markdown(metric_card("Days Studied",        f"{days_studied_m}/{days_in_month}", "#f59e0b"), unsafe_allow_html=True)
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    
            day_nums   = list(range(1, days_in_month + 1))
            today_d_str = today_dt.strftime("%Y-%m-%d")
            bar_clrs_m  = ["#ec4899" if k == today_d_str else "#06b6d4" for k in month_keys]
            fc_clrs_m   = [focus_color(v) if v > 0 else "#1e3a5f" for v in month_focus]
    
            fig_m, (axm1, axm2) = plt.subplots(2, 1, figsize=(14, 6.0))
    
            bars_m = axm1.bar(day_nums, month_mins, color=bar_clrs_m, width=0.75,
                              edgecolor="#0f1c2e", linewidth=0.3)
            axm1.set_xticks(day_nums)
            axm1.set_xticklabels([str(d) for d in day_nums], fontsize=6.5)
            axm1.set_xlim(0.3, days_in_month + 0.7)
            axm1.set_ylim(0, max(max(month_mins)*1.35, 10))
            axm1.set_title(
                f"THIS MONTH ({today_dt.strftime('%B %Y')}) — DAILY STUDY MINUTES  (today = pink)",
                fontsize=9, color="#ec4899", pad=10,
            )
            axm1.set_ylabel("Minutes", fontsize=8)
            axm1.grid(axis="y", linestyle="--", alpha=0.4)
    
            bars_mf = axm2.bar(day_nums, month_focus, color=fc_clrs_m, width=0.75,
                                edgecolor="#0f1c2e", linewidth=0.3)
            axm2.set_xticks(day_nums)
            axm2.set_xticklabels([str(d) for d in day_nums], fontsize=6.5)
            axm2.set_xlim(0.3, days_in_month + 0.7)
            axm2.set_ylim(0, 115)
            axm2.axhline(80, color="#10b981", linewidth=0.8, linestyle="--", alpha=0.5)
            axm2.axhline(60, color="#f59e0b", linewidth=0.8, linestyle="--", alpha=0.5)
            axm2.set_title(
                f"THIS MONTH ({today_dt.strftime('%B %Y')}) — DAILY AVG FOCUS SCORE",
                fontsize=9, color="#6366f1", pad=10,
            )
            axm2.set_ylabel("Focus %", fontsize=8)
            axm2.grid(axis="y", linestyle="--", alpha=0.4)
    
            fig_m.tight_layout()
            st.pyplot(fig_m)
            plt.close(fig_m)
    
            # Monthly insight cards
            best_day_m_idx = month_mins.index(max(month_mins))
            consistency_m  = int(days_studied_m / days_in_month * 100)
            ic1, ic2, ic3, ic4 = st.columns(4)
            with ic1:
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.60rem;letter-spacing:2px;margin:6px 0;'>BEST STUDY DAY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.0rem;'>Day {best_day_m_idx+1}  ({month_mins[best_day_m_idx]}m)</div>"
                    "</div>", accent="#06b6d4")
            with ic2:
                avg_active = int(month_total_min / max(days_studied_m,1))
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'>⚡</div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.60rem;letter-spacing:2px;margin:6px 0;'>AVG / ACTIVE DAY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:#ffffff;"
                    f"font-size:1.0rem;'>{avg_active} min</div>"
                    "</div>", accent="#6366f1")
            with ic3:
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.60rem;letter-spacing:2px;margin:6px 0;'>MONTH CONSISTENCY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:{focus_color(consistency_m)};"
                    f"font-size:1.0rem;'>{consistency_m}%</div>"
                    "</div>", accent="#f59e0b")
            with ic4:
                best_focus_m = max(month_focus) if month_focus else 0
                card(
                    "<div style='text-align:center;'>"
                    "<div style='font-size:1.4rem;'></div>"
                    "<div style='font-family:Share Tech Mono,monospace;color:#38bdf8;"
                    "font-size:0.60rem;letter-spacing:2px;margin:6px 0;'>PEAK FOCUS DAY</div>"
                    f"<div style='font-family:Orbitron,monospace;color:{focus_color(best_focus_m)};"
                    f"font-size:1.0rem;'>{best_focus_m}%</div>"
                    "</div>", accent="#10b981")
        else:
            no_data_card()
    
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    
    # ═════════════════════════════════════════════════════════════
    # FOOTER
    # ═════════════════════════════════════════════════════════════
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;border-top:1.5px solid rgba(6,182,212,0.14);"
        "padding-top:18px;'>"
        "<div style='font-family:Share Tech Mono,monospace;color:#334155;"
        "font-size:0.63rem;letter-spacing:4px;'>"
        "AI FOCUS &amp; PRODUCTIVITY ASSISTANT</div>"
        "<div style='font-family:Share Tech Mono,monospace;color:#06b6d4;"
        "font-size:0.58rem;letter-spacing:3px;margin-top:4px;opacity:0.45;'>"
        "POWERED BY STREAMLIT · PYTHON · MATPLOTLIB · PANDAS</div>"
        "</div>",
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(
        page_title="AI Focus Assistant",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render_focus_assistant()
