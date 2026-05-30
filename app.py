import streamlit as st
import sys
import os

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG (Must be the very first Streamlit command)
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Hostel Student Wellness Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Append sub-directories to sys.path to resolve module imports
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root_dir, "food_monitoring"))
sys.path.append(os.path.join(root_dir, "emotion"))
sys.path.append(os.path.join(root_dir, "preventive_health"))

# ─────────────────────────────────────────────────────────────
# FORCE STREAMLIT SECRETS PATCH
# ─────────────────────────────────────────────────────────────
def patched_parse(self):
    if self._secrets is not None:
        return self._secrets
    
    secrets = {}
    # Try using tomllib or standard open
    root_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(root_dir, ".streamlit", "secrets.toml"),
        r"D:\V\smart-hostel\.streamlit\secrets.toml",
        os.path.expanduser("~/.streamlit/secrets.toml"),
    ]
    
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            try:
                import tomllib
                with open(path, "rb") as f:
                    secrets.update(tomllib.load(f))
                found = True
            except Exception:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and "=" in line and not line.startswith("#"):
                                k, v = line.split("=", 1)
                                secrets[k.strip()] = v.strip().strip('"').strip("'")
                    found = True
                except Exception:
                    pass
                
    if not found:
        # Ultimate fallback to default keys
        secrets = {
            "GROQ_API_KEY": "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",
            "HOSTEL_ADMIN_EMAIL": "admin@hostel.com",
            "HOSTEL_ADMIN_PASSWORD": "hostel123"
        }
        
    for k, v in secrets.items():
        self._maybe_set_environment_variable(k, v)
        
    self._secrets = secrets
    return self._secrets

import streamlit.runtime.secrets as st_secrets
st_secrets.Secrets._parse = patched_parse
st.secrets._secrets = None

# Now import the modules safely
from database import *
from app_food_monitoring import render_login, render_student_app, render_hostel_admin
from dashboard import render_focus_assistant
from dashboard_emotion import render_emotion_room
import preventive_health.app as preventive_health_app

# ─────────────────────────────────────────────────────────────
# STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Focus Assistant"

if "detected_emotion" not in st.session_state:
    st.session_state.detected_emotion = "neutral"

# Initialize food monitoring state keys (safeguard against module caching)
for key, val in [
    ('user', None), ('ai_data', {}), ('ai_name', ''),
    ('water_count', 0), ('messages', []),
    ('hostel_admin', False),
    ('admin_scan_data', {}), ('admin_scan_name', ''),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────────────────────
# REAL-TIME EMOTION PARSING
# ─────────────────────────────────────────────────────────────
emotion_file = os.path.join(root_dir, "emotion.txt")
if os.path.exists(emotion_file):
    try:
        with open(emotion_file, "r") as f:
            current_emotion = f.read().strip().lower()
            if current_emotion in ["happy", "sad", "angry", "fear", "neutral", "surprise", "disgust"]:
                st.session_state.detected_emotion = current_emotion
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION ROUTING
# ─────────────────────────────────────────────────────────────
is_logged_in = (
    st.session_state.get("user") is not None or 
    st.session_state.get("hostel_admin", False)
)

if not is_logged_in:
    # Render the login/registration screen from NutriCam (food_monitoring)
    render_login()
else:
    # ─────────────────────────────────────────────────────────────
    # GLOBAL SLEEK CSS (Unified Cyber-Dark Theme)
    # ─────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
    
    /* Global Background and Fonts */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0f1c2e;
        color: #e2e8f0;
        font-family: 'Rajdhani', sans-serif !important;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 15% 25%, rgba(6,182,212,0.08) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 75%, rgba(99,102,241,0.08) 0%, transparent 55%),
            #0f1c2e;
    }
    
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', monospace !important;
        color: #e2e8f0 !important;
    }
    
    /* Set font family on text elements, avoiding broad div/span overrides that break icons */
    p, label, .stMarkdown {
        font-family: 'Rajdhani', sans-serif !important;
    }

    /* Global sidebar background */
    [data-testid="stSidebar"] {
        background-color: #0b111e !important;
        border-right: 1.5px solid rgba(6, 182, 212, 0.15) !important;
    }
    
    /* Top banner logo or text */
    .banner-text {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 1.25rem;
        background: linear-gradient(135deg, #06b6d4, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Navigation link styles */
    .stRadio [data-testid="stWidgetLabel"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #38bdf8 !important;
    }

    /* Uniform Metric Cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a2d44 0%, #162438 100%) !important;
        border: 1.5px solid rgba(6, 182, 212, 0.3) !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 4px 18px rgba(6, 182, 212, 0.1) !important;
    }
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] p {
        color: #38bdf8 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.6rem !important;
        color: #ffffff !important;
    }

    /* Uniform Container Borders (st.container(border=True)) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, #1a2d44 0%, #162438 100%) !important;
        border: 1.5px solid rgba(6, 182, 212, 0.22) !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 22px rgba(6, 182, 212, 0.08) !important;
    }

    /* Uniform Tabs styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1a2d44, #162438) !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(6, 182, 212, 0.22) !important;
        gap: 4px !important;
        padding: 4px !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        color: #94a3b8 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4, #6366f1) !important;
        color: #ffffff !important;
    }

    /* Uniform Buttons styling */
    .stButton > button {
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        border-radius: 10px !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(6, 182, 212, 0.40) !important;
    }

    /* Uniform Sliders */
    [data-testid="stSlider"] > div > div > div {
        background: linear-gradient(90deg, #06b6d4, #6366f1) !important;
    }
    [data-testid="stSlider"] label {
        font-family: 'Share Tech Mono', monospace !important;
        color: #38bdf8 !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }

    /* Uniform Progress Bars */
    div[role="progressbar"] {
        background-color: #1e3a5f !important;
        border-radius: 6px !important;
    }
    div[role="progressbar"] > div {
        background: linear-gradient(90deg, #06b6d4, #6366f1) !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # SIDEBAR NAVIGATION
    # ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("<div class='banner-text'>SMART HOSTEL</div>", unsafe_allow_html=True)
        
        # Display current user info
        if st.session_state.get("hostel_admin"):
            st.success("Logged in: **ADMIN**")
        else:
            st.info(f"Student: **{st.session_state.user[1]}**")
            
        st.write("")
        st.subheader("SYSTEM NAVIGATOR")
        
        # Define menu items
        nav_options = [
            "AI Focus Assistant",
            "NutriCam (Diet & Gym)",
            "Smart Adaptive Room",
            "Health Monitor Engine"
        ]
        
        choice = st.radio(
            "Select Dashboard Module",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Live emotion widget in the sidebar
        active_emo = st.session_state.detected_emotion
        
        st.markdown(
            f"<div style='background:rgba(6,182,212,0.06); border:1px solid rgba(6,182,212,0.15); "
            f"border-radius:10px; padding:12px; text-align:center; font-family:Rajdhani,sans-serif;'>"
            f"<div style='font-size:0.75rem; letter-spacing:1px; color:#94a3b8; text-transform:uppercase;'>Webcam Emotion Reader</div>"
            f"<div style='font-size:1.4rem; font-weight:700; color:#06b6d4; margin-top:6px;'>{active_emo.upper()}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.write("")
        st.write("")
        if st.button("Logout Account", type="primary", use_container_width=True):
            st.session_state.user = None
            st.session_state.hostel_admin = False
            st.rerun()

    # ─────────────────────────────────────────────────────────────
    # MODULE ROUTING
    # ─────────────────────────────────────────────────────────────
    if choice == "AI Focus Assistant":
        render_focus_assistant()
    elif choice == "NutriCam (Diet & Gym)":
        if st.session_state.get("hostel_admin"):
            render_hostel_admin()
        else:
            render_student_app()
    elif choice == "Smart Adaptive Room":
        render_emotion_room()
    elif choice == "Health Monitor Engine":
        preventive_health_app.render_health_monitor()
