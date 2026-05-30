import streamlit as st
# import pyttsx3
import os
import time
import random
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

# st.set_page_config(
#     page_title="Smart Emotion Adaptive Room",
#     page_icon="",
#     layout="wide"
# )

@st.fragment(run_every=2)
def render_emotion_room():
# ---------------- READ EMOTION FIRST ----------------

    emotion = st.session_state.get("detected_emotion")
    if emotion is None:
        emotion = "neutral"
        if os.path.exists("emotion.txt"):
            with open("emotion.txt", "r") as file:
                emotion = file.read().strip()

    # ---------------- DYNAMIC GLOW COLORS ----------------
    glow_colors = {
        "happy": "rgba(78, 159, 61, 0.25)",
        "sad": "rgba(27, 73, 101, 0.3)",
        "angry": "rgba(139, 0, 0, 0.3)",
        "fear": "rgba(93, 63, 211, 0.3)",
        "neutral": "rgba(99, 102, 241, 0.08)",  # standard indigo glow
        "surprise": "rgba(106, 5, 114, 0.3)",
        "disgust": "rgba(46, 125, 50, 0.3)"
    }
    glow_color = glow_colors.get(emotion, "rgba(99, 102, 241, 0.08)")

    # ---------------- CUSTOM CSS ----------------

    st.markdown(f"""
    <style>

    .stApp, [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(ellipse at 15% 25%, rgba(6,182,212,0.08) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 75%, {glow_color} 0%, transparent 55%),
            #0f1c2e !important;
        color: #e2e8f0 !important;
    }}

    .main-title {{
        font-family: 'Orbitron', monospace !important;
        font-weight: 900;
        font-size: 2.2rem;
        text-align: center;
        background: linear-gradient(135deg, #06b6d4 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 5px;
    }}

    .sub-text {{
        text-align: center;
        font-family: 'Rajdhani', sans-serif !important;
        color: #475569;
        font-size: 0.95rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 8px;
        margin-bottom: 20px;
    }}

    .card {{
        background: linear-gradient(135deg, #1a2d44 0%, #162438 100%);
        border: 1.5px solid rgba(6, 182, 212, 0.22);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0px 4px 22px rgba(6, 182, 212, 0.08);
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }}
    .card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, transparent, #06b6d4, transparent);
    }}

    .big-text {{
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        color: #38bdf8 !important;
        margin-bottom: 8px;
    }}

    .small-text {{
        font-family: 'Orbitron', monospace !important;
        font-size: 1.55rem !important;
        color: #ffffff !important;
        font-weight: 900;
    }}

    .status-box {{
        background-color: rgba(6, 182, 212, 0.06);
        border: 1.5px solid rgba(6, 182, 212, 0.22);
        color: #38bdf8;
        padding: 15px;
        border-radius: 14px;
        margin-bottom: 20px;
        font-size: 18px;
        font-family: 'Rajdhani', sans-serif !important;
    }}

    </style>
    """, unsafe_allow_html=True)

    # ---------------- VOICE ENGINE ----------------

# engine = pyttsx3.init()

    def speak_message(text: str):
        import streamlit.components.v1 as components
        safe = text.replace("'", "\\'").replace('"', '\\"')
        components.html(f"""
<!DOCTYPE html><html><body>
<script>
(function(){{
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance('{safe}');
  u.rate=0.95; u.pitch=1.0; u.volume=1.0;
  window.speechSynthesis.speak(u);
}})();
</script></body></html>""", height=0)


    # ---------------- TITLE ----------------

    st.markdown(
        "<div class='main-title'>Smart Emotion Adaptive Room</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sub-text'>AI-powered student wellness and smart hostel monitoring system</div>",
        unsafe_allow_html=True
    )

    st.write("")

    # ---------------- LIVE TIME ----------------

    current_time = datetime.now().strftime("%d %B %Y | %I:%M:%S %p")

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>Live Monitoring Time</div>
    <div class='small-text'>{current_time}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- SYSTEM STATUS ----------------

    st.success("Camera: Active | AI Emotion Monitoring: Running | Wellness Support: Active")

    # ---------------- LOGIC ----------------

    room_status = ""
    light = ""
    voice_message = ""
    wellness = 50
    emoji = ""
    songs = []

    # HAPPY
    if emotion == "happy":

        room_status = "Positive Mood Environment Activated"
        light = "Warm Yellow Lighting"
        wellness = 95
        emoji = ""

        voice_message = (
            "You look happy and energetic today. "
            "Keep smiling and continue spreading positivity around you."
        )

        songs = [
            ("Happy - Pharrell Williams",
             "https://www.youtube.com/results?search_query=Happy+Pharrell+Williams"),

            ("On Top Of The World",
             "https://www.youtube.com/results?search_query=On+Top+Of+The+World")
        ]

    # SAD
    elif emotion == "sad":

        room_status = "Calming Environment Activated"
        light = "Soft Blue Lighting"
        wellness = 45
        emoji = ""

        voice_message = (
            "Hey, you seem sad today. "
            "Do not worry because difficult moments never last forever."
        )

        songs = [
            ("Fight Song",
             "https://www.youtube.com/results?search_query=Fight+Song"),

            ("Stronger",
             "https://www.youtube.com/results?search_query=Stronger+Kelly+Clarkson")
        ]

    # ANGRY
    elif emotion == "angry":

        room_status = "Relaxation Mode Activated"
        light = "Stress Reduction Lighting"
        wellness = 35
        emoji = ""

        voice_message = (
            "You seem stressed or angry right now. "
            "Please relax and take a deep breath."
        )

        songs = [
            ("Relaxing Piano Music",
             "https://www.youtube.com/results?search_query=Relaxing+Piano+Music"),

            ("Calm Music",
             "https://www.youtube.com/results?search_query=Calm+Music")
        ]

    # FEAR
    elif emotion == "fear":

        room_status = "Emergency Wellness Support Activated"
        light = "Alert Lighting"
        wellness = 20
        emoji = ""

        voice_message = (
            "You look anxious right now. "
            "Stay calm because you are stronger than your worries."
        )

        songs = [
            ("Peaceful Instrumental Music",
             "https://www.youtube.com/results?search_query=Peaceful+Instrumental+Music"),

            ("Calm Relaxing Music",
             "https://www.youtube.com/results?search_query=Calm+Relaxing+Music")
        ]

    # SURPRISE
    elif emotion == "surprise":

        room_status = "Excitement Mode Activated"
        light = "Purple Ambient Lighting"
        wellness = 80
        emoji = ""

        voice_message = (
            "You look surprised today. "
            "Hope something exciting happened."
        )

        songs = [
            ("Best Day Of My Life",
             "https://www.youtube.com/results?search_query=Best+Day+Of+My+Life")
        ]

    # NEUTRAL
    elif emotion == "neutral":

        room_status = "Focus Study Environment Activated"
        light = "Balanced White Lighting"
        wellness = 75
        emoji = ""

        voice_message = (
            "You seem calm and focused right now."
        )

        songs = [
            ("LoFi Study Music",
             "https://www.youtube.com/results?search_query=LoFi+Study+Music"),

            ("Deep Focus Music",
             "https://www.youtube.com/results?search_query=Deep+Focus+Music")
        ]

    # DISGUST
    elif emotion == "disgust":

        room_status = "Refresh Environment Activated"
        light = "Fresh Green Lighting"
        wellness = 50
        emoji = ""

        voice_message = (
            "You seem uncomfortable right now. "
            "Please take some rest and refresh yourself."
        )

        songs = [
            ("Nature Relaxation Music",
             "https://www.youtube.com/results?search_query=Nature+Relaxation+Music")
        ]

    # ---------------- SPEAK VOICE ----------------

    if "last_emotion" not in st.session_state:
        st.session_state.last_emotion = ""

    if st.session_state.last_emotion != emotion:
        speak_message(voice_message)
        st.session_state.last_emotion = emotion

    # ---------------- DASHBOARD ----------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div class='card'>
        <div class='big-text'>Current Emotion</div>
        <div class='small-text'>{emotion.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card'>
        <div class='big-text'>Adaptive Room Response</div>
        <div class='small-text'>{room_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class='card'>
        <div class='big-text'>Smart Lighting</div>
        <div class='small-text'>{light}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card'>
        <div class='big-text'>Wellness Score</div>
        <div class='small-text'>{wellness}%</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- WELLNESS BAR ----------------

    st.subheader("Student Wellness Monitoring")
    st.progress(wellness)

    # ---------------- MOTIVATIONAL ASSISTANT ----------------

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>AI Motivational Assistant</div>
    <div class='small-text'>{voice_message}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- AI WELLNESS ASSISTANT ----------------

    st.markdown("""
    <div class='card'>
    <div class='big-text'>AI Voice Wellness Assistant</div>
    <div class='small-text'>
    Talk with the AI assistant whenever you feel stressed or overwhelmed.
    </div>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:

        if st.button("I Feel Stressed"):

            response = (
                "It is okay to feel stressed sometimes. "
                "Please relax and take a short break."
            )

            st.success(response)
            speak_message(response)

    with col4:

        if st.button("Motivate Me"):

            response = (
                "Believe in yourself. "
                "Every small effort creates a stronger future."
            )

            st.success(response)
            speak_message(response)

    # ---------------- MUSIC THERAPY ----------------

    st.subheader("AI Mood-Based Music Therapy")

    for song, link in songs:
        st.markdown(f"- [{song}]({link})")

    music_search = st.text_input("Search your favorite music")

    if music_search:

        search_url = (
            "https://www.youtube.com/results?search_query="
            + music_search.replace(" ", "+")
        )

        st.markdown(
            f"[Click here to search '{music_search}' on YouTube]({search_url})"
        )

    # ---------------- EMOTION ANALYTICS ----------------

    st.subheader("Emotion Analytics")

    emotion_data = pd.DataFrame({
        "Emotion": [
            "Happy",
            "Sad",
            "Angry",
            "Fear",
            "Neutral"
        ],
        "Percentage": [
            random.randint(40, 90),
            random.randint(10, 50),
            random.randint(5, 40),
            random.randint(5, 35),
            random.randint(30, 80)
        ]
    })

    st.bar_chart(
        emotion_data.set_index("Emotion")
    )

    # ---------------- FEATURES ----------------

    st.subheader("Smart Features")

    feature1, feature2, feature3 = st.columns(3)

    with feature1:
        st.success("Real-time Emotion Detection")

    with feature2:
        st.success("Adaptive Smart Environment")

    with feature3:
        st.success("AI Wellness Assistance")


if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(
        page_title="Smart Emotion Adaptive Room",
        page_icon="",
        layout="wide"
    )
    render_emotion_room()
