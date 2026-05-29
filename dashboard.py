import streamlit as st
import pyttsx3
import os
import time
import random
import pandas as pd
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Smart Emotion Adaptive Room",
    page_icon="🧠",
    layout="wide"
)

# ---------------- READ EMOTION FIRST ----------------

emotion = "neutral"

if os.path.exists("emotion.txt"):

    with open("emotion.txt", "r") as file:
        emotion = file.read().strip()

# ---------------- DYNAMIC BACKGROUND COLORS ----------------

bg_color = "#243B55"

if emotion == "happy":
    bg_color = "#4E9F3D"

elif emotion == "sad":
    bg_color = "#1B4965"

elif emotion == "angry":
    bg_color = "#8B0000"

elif emotion == "fear":
    bg_color = "#5D3FD3"

elif emotion == "neutral":
    bg_color = "#243B55"

elif emotion == "surprise":
    bg_color = "#6A0572"

elif emotion == "disgust":
    bg_color = "#2E7D32"

# ---------------- CUSTOM CSS ----------------

st.markdown(f"""
<style>

.stApp {{
    background: linear-gradient(to right, #141E30, {bg_color});
    color: white;
}}

.main-title {{
    font-size: 55px;
    font-weight: bold;
    text-align: center;
    color: #00E5FF;
    text-shadow: 0px 0px 20px #00E5FF;
    animation: glow 2s infinite alternate;
}}

@keyframes glow {{
    from {{
        text-shadow: 0px 0px 10px #00E5FF;
    }}

    to {{
        text-shadow: 0px 0px 25px #00E5FF;
    }}
}}

.sub-text {{
    text-align: center;
    font-size: 20px;
    color: #E0E0E0;
}}

.card {{
    background-color: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0px 0px 20px rgba(0,229,255,0.5);
    margin-bottom: 20px;
}}

.big-text {{
    font-size: 30px;
    font-weight: bold;
    color: #00E5FF;
}}

.small-text {{
    font-size: 18px;
    color: white;
}}

.status-box {{
    background-color: rgba(0,255,0,0.15);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    font-size: 18px;
}}

</style>
""", unsafe_allow_html=True)

# ---------------- VOICE ENGINE ----------------

engine = pyttsx3.init()

# ---------------- TITLE ----------------

st.markdown(
    "<div class='main-title'>🧠 Smart Emotion Adaptive Room</div>",
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
<div class='big-text'>⏰ Live Monitoring Time</div>
<div class='small-text'>{current_time}</div>
</div>
""", unsafe_allow_html=True)

# ---------------- SYSTEM STATUS ----------------

st.markdown("""
<div class='status-box'>
🟢 Camera Active <br>
🟢 AI Emotion Monitoring Running <br>
🟢 Smart Wellness Support Active
</div>
""", unsafe_allow_html=True)

# ---------------- LOGIC ----------------

room_status = ""
light = ""
voice_message = ""
wellness = 50
emoji = "😐"
songs = []

# HAPPY
if emotion == "happy":

    room_status = "🎉 Positive Mood Environment Activated"
    light = "🟡 Warm Yellow Lighting"
    wellness = 95
    emoji = "😊"

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

    room_status = "💡 Calming Environment Activated"
    light = "🔵 Soft Blue Lighting"
    wellness = 45
    emoji = "😔"

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

    room_status = "🎵 Relaxation Mode Activated"
    light = "🟠 Stress Reduction Lighting"
    wellness = 35
    emoji = "😠"

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

    room_status = "🚨 Emergency Wellness Support Activated"
    light = "🔴 Alert Lighting"
    wellness = 20
    emoji = "😨"

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

    room_status = "✨ Excitement Mode Activated"
    light = "🟣 Purple Ambient Lighting"
    wellness = 80
    emoji = "😲"

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

    room_status = "📚 Focus Study Environment Activated"
    light = "⚪ Balanced White Lighting"
    wellness = 75
    emoji = "😌"

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

    room_status = "🌿 Refresh Environment Activated"
    light = "🟢 Fresh Green Lighting"
    wellness = 50
    emoji = "🤢"

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

    engine.say(voice_message)
    engine.runAndWait()

    st.session_state.last_emotion = emotion

# ---------------- DASHBOARD ----------------

col1, col2 = st.columns(2)

with col1:

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>📷 Current Emotion</div>
    <div class='small-text'>{emotion.upper()} {emoji}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>💡 Adaptive Room Response</div>
    <div class='small-text'>{room_status}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>🌈 Smart Lighting</div>
    <div class='small-text'>{light}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card'>
    <div class='big-text'>🧠 Wellness Score</div>
    <div class='small-text'>{wellness}%</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- WELLNESS BAR ----------------

st.subheader("📊 Student Wellness Monitoring")
st.progress(wellness)

# ---------------- MOTIVATIONAL ASSISTANT ----------------

st.markdown(f"""
<div class='card'>
<div class='big-text'>🎤 AI Motivational Assistant</div>
<div class='small-text'>{voice_message}</div>
</div>
""", unsafe_allow_html=True)

# ---------------- AI WELLNESS ASSISTANT ----------------

st.markdown("""
<div class='card'>
<div class='big-text'>🤖 AI Voice Wellness Assistant</div>
<div class='small-text'>
Talk with the AI assistant whenever you feel stressed or overwhelmed.
</div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:

    if st.button("😓 I Feel Stressed"):

        response = (
            "It is okay to feel stressed sometimes. "
            "Please relax and take a short break."
        )

        st.success(response)

        engine.say(response)
        engine.runAndWait()

with col4:

    if st.button("🔥 Motivate Me"):

        response = (
            "Believe in yourself. "
            "Every small effort creates a stronger future."
        )

        st.success(response)

        engine.say(response)
        engine.runAndWait()

# ---------------- MUSIC THERAPY ----------------

st.subheader("🎵 AI Mood-Based Music Therapy")

for song, link in songs:
    st.markdown(f"- [{song}]({link})")

music_search = st.text_input("🔍 Search your favorite music")

if music_search:

    search_url = (
        "https://www.youtube.com/results?search_query="
        + music_search.replace(" ", "+")
    )

    st.markdown(
        f"[🎧 Click here to search '{music_search}' on YouTube]({search_url})"
    )

# ---------------- EMOTION ANALYTICS ----------------

st.subheader("📈 Emotion Analytics")

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

st.subheader("✨ Smart Features")

feature1, feature2, feature3 = st.columns(3)

with feature1:
    st.success("✅ Real-time Emotion Detection")

with feature2:
    st.success("✅ Adaptive Smart Environment")

with feature3:
    st.success("✅ AI Wellness Assistance")

# ---------------- AUTO REFRESH ----------------

time.sleep(2)
st.rerun()