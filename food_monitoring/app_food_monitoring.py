import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import base64
import csv
import io
import os
import pandas as pd
from datetime import datetime, timedelta
from database import *
from PIL import Image

init_db()

# st.set_page_config(page_title="NutriCam", page_icon=None, layout="wide")

for key, val in [
    ('user', None), ('ai_data', {}), ('ai_name', ''),
    ('water_count', 0), ('messages', []),
    ('hostel_admin', False),
    ('admin_scan_data', {}), ('admin_scan_name', ''),
]:
    if key not in st.session_state:
        st.session_state[key] = val

def init_hostel_db():
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mess_menu (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_type   TEXT NOT NULL,
        items       TEXT NOT NULL,
        calories    INTEGER DEFAULT 0,
        protein     REAL    DEFAULT 0,
        carbs       REAL    DEFAULT 0,
        fats        REAL    DEFAULT 0,
        date        TEXT    DEFAULT (DATE('now')),
        posted_by   TEXT    DEFAULT 'Mess Admin',
        image_path  TEXT    DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS student_queries (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER,
        student_name TEXT,
        category    TEXT,
        query_text  TEXT NOT NULL,
        upvotes     INTEGER DEFAULT 0,
        status      TEXT    DEFAULT 'pending',
        admin_reply TEXT    DEFAULT '',
        created_at  TEXT    DEFAULT (DATETIME('now'))
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS query_upvotes (
        query_id INTEGER,
        user_id  INTEGER,
        PRIMARY KEY (query_id, user_id)
    )''')
    # Add image_path column if it doesn't exist (migration)
    try:
        c.execute("ALTER TABLE mess_menu ADD COLUMN image_path TEXT DEFAULT ''")
    except Exception:
        pass
    conn.commit()
    conn.close()

init_hostel_db()

# ─── Mess Menu CRUD ──────────────────────────────────────────────────────────

def add_mess_menu(meal_type, items, calories, protein, carbs, fats, date_str, posted_by, image_path=""):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("DELETE FROM mess_menu WHERE meal_type=? AND date=?", (meal_type, date_str))
    c.execute(
        "INSERT INTO mess_menu (meal_type, items, calories, protein, carbs, fats, date, posted_by, image_path) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (meal_type, items, calories, protein, carbs, fats, date_str, posted_by, image_path)
    )
    conn.commit()
    conn.close()

def get_mess_menu(date_str):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM mess_menu WHERE date=? ORDER BY "
        "CASE meal_type WHEN 'breakfast' THEN 1 WHEN 'lunch' THEN 2 "
        "WHEN 'snacks' THEN 3 WHEN 'dinner' THEN 4 ELSE 5 END",
        (date_str,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def get_mess_menu_range(days=7):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute(
        "SELECT date, meal_type, items, calories FROM mess_menu "
        "WHERE date >= DATE('now', ?) ORDER BY date DESC, "
        "CASE meal_type WHEN 'breakfast' THEN 1 WHEN 'lunch' THEN 2 "
        "WHEN 'snacks' THEN 3 WHEN 'dinner' THEN 4 ELSE 5 END",
        (f'-{days} days',)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def delete_mess_menu(menu_id):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("DELETE FROM mess_menu WHERE id=?", (menu_id,))
    conn.commit()
    conn.close()

# ─── Student Queries CRUD ────────────────────────────────────────────────────

def add_query(user_id, student_name, category, query_text):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO student_queries (user_id, student_name, category, query_text) VALUES (?,?,?,?)",
        (user_id, student_name, category, query_text)
    )
    conn.commit()
    conn.close()

def get_all_queries(status_filter=None):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    if status_filter:
        c.execute(
            "SELECT * FROM student_queries WHERE status=? ORDER BY upvotes DESC, created_at DESC",
            (status_filter,)
        )
    else:
        c.execute("SELECT * FROM student_queries ORDER BY upvotes DESC, created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_student_queries(user_id):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM student_queries WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def upvote_query(query_id, user_id):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO query_upvotes (query_id, user_id) VALUES (?,?)", (query_id, user_id))
        c.execute("UPDATE student_queries SET upvotes = upvotes + 1 WHERE id=?", (query_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def reply_to_query(query_id, reply_text):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute(
        "UPDATE student_queries SET admin_reply=?, status='resolved' WHERE id=?",
        (reply_text, query_id)
    )
    conn.commit()
    conn.close()

def update_query_status(query_id, status):
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("UPDATE student_queries SET status=? WHERE id=?", (status, query_id))
    conn.commit()
    conn.close()

def get_query_stats():
    import sqlite3
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) as cnt FROM student_queries GROUP BY category ORDER BY cnt DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ─── AI Functions ─────────────────────────────────────────────────────────────

def analyze_food_text(food_name):
    """Estimate nutrition for a single food item by name."""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": (
                    f"Nutrition for {food_name} 1 serving. "
                    "ONLY JSON, no extra text: "
                    "{\"name\": \"food name\", \"calories\": number, \"protein\": number, \"carbs\": number, \"fats\": number}"
                )
            }],
            max_tokens=150
        )
        text = response.choices[0].message.content.strip()
        json_str = text[text.find('{'):text.rfind('}') + 1]
        result = json.loads(json_str)
        for key in ["calories", "protein", "carbs", "fats"]:
            result[key] = float(result.get(key, 0))
        result.setdefault("name", food_name)
        return result
    except Exception as e:
        st.error(f"AI Error: {e}")
        return {"name": food_name, "calories": 200.0, "protein": 10.0, "carbs": 25.0, "fats": 8.0}

def analyze_food_image(image_bytes):
    """Identify food and estimate nutrition from an image."""
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        b64 = base64.b64encode(image_bytes).decode()
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    {
                        "type": "text",
                        "text": (
                            "You are a nutrition expert. Carefully look at this food image. "
                            "Identify the food item(s) and estimate the nutritional content for the visible portion. "
                            "Return ONLY a valid JSON object with no extra text, no markdown, no explanation:\n"
                            "{\"name\": \"food name\", \"calories\": number, \"protein\": number, "
                            "\"carbs\": number, \"fats\": number}"
                        )
                    }
                ]
            }],
            max_tokens=200
        )
        text = response.choices[0].message.content.strip()
        json_str = text[text.find('{'):text.rfind('}') + 1]
        result = json.loads(json_str)
        for key in ["calories", "protein", "carbs", "fats"]:
            result[key] = float(result.get(key, 0))
        result.setdefault("name", "Unknown Food")
        return result
    except Exception as e:
        st.error(f"AI Image Error: {e}")
        return {"name": "Unknown", "calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}

def get_meal_recommendation(remaining_cal, goal):
    try:
        from groq import Groq
        client = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": (
                    f"I have {remaining_cal} calories remaining today. My goal is to {goal}. "
                    "Suggest 3 healthy meals or snacks. Keep it brief and practical."
                )
            }],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception:
        return "Enable AI features with a Groq API key for personalized recommendations!"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def save_uploaded_image(image_bytes, filename):
    """Save image bytes to disk and return the path."""
    os.makedirs("mess_images", exist_ok=True)
    path = os.path.join("mess_images", filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path

def calculate_health_score(total_cal, target, total_protein, water_count, exercises):
    score = 0
    cal_ratio = total_cal / target if target > 0 else 0
    if 0.8 <= cal_ratio <= 1.0:
        score += 30
    elif 0.6 <= cal_ratio <= 1.2:
        score += 20
    else:
        score += 10
    if total_protein >= 50:
        score += 20
    elif total_protein >= 30:
        score += 15
    else:
        score += 5
    score += min(water_count / 8 * 25, 25)
    if exercises:
        score += min(len(exercises) * 10, 25)
    return min(int(score), 100)

def export_to_csv(meals, exercises):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["=== MEALS ==="])
    writer.writerow(["Date", "Food", "Calories", "Protein(g)", "Carbs(g)", "Fats(g)", "Meal Type"])
    for meal in meals:
        writer.writerow([meal[8], meal[2], meal[3], meal[4], meal[5], meal[6], meal[7]])
    writer.writerow([])
    writer.writerow(["=== EXERCISES ==="])
    writer.writerow(["Date", "Exercise", "Duration(min)", "Calories Burned"])
    for ex in exercises:
        writer.writerow([ex[5], ex[2], ex[3], ex[4]])
    return output.getvalue()

# ─── Credentials ─────────────────────────────────────────────────────────────

HOSTEL_ADMIN_EMAIL    = st.secrets.get("HOSTEL_ADMIN_EMAIL",    "admin@hostel.com")
HOSTEL_ADMIN_PASSWORD = st.secrets.get("HOSTEL_ADMIN_PASSWORD", "hostel123")

# ═════════════════════════════════════════════════════════════════════════════
# HOSTEL ADMIN PORTAL
# ═════════════════════════════════════════════════════════════════════════════

def render_hostel_admin():
    st.title("Hostel Admin Portal")
    st.caption("Manage mess menu and student queries from here.")

    with st.sidebar:
        st.title("Admin Panel")
        st.success(" Logged in as Hostel Admin")
        if st.button(" Logout Admin", type="primary", use_container_width=True):
            st.session_state.hostel_admin = False
            st.rerun()

    admin_tab1, admin_tab2, admin_tab3 = st.tabs([
        "AI Food Scanner", "View & Manage Menu", "Student Queries"
    ])
# ── Tab 1 : AI Food Scanner ───────────────────────────────────────────────
    with admin_tab1:
        st.subheader("AI Food Scanner — Add to Mess Menu")
        st.info(
            "Choose an input method below. AI will automatically detect the food name and "
            "fill in nutritional values. Review, adjust if needed, then click **Save To Mess Menu**."
        )

        scan_method = st.radio(
            "Input Method",
            [" Type Food Name", " Upload Image From Gallery", "📷 Capture Image Using Webcam"],
            horizontal=True,
            key="admin_scan_method"
        )

        captured_image_bytes = None

        # ── Image input section ──────────────────────────────────────────────
        if scan_method == " Upload Image From Gallery":
            uploaded = st.file_uploader(
                "Upload a photo of the mess food",
                type=["jpg", "jpeg", "png"],
                key="admin_gallery_upload"
            )
            if uploaded:
                st.image(uploaded, caption="📷 Uploaded Food Image", use_container_width=True)
                captured_image_bytes = uploaded.getvalue()
                if st.button(" Detect Food from Image", type="primary", key="admin_analyse_gallery"):
                    with st.spinner("AI is identifying the food…"):
                        result = analyze_food_image(captured_image_bytes)
                        # Store directly with explicit keys
                        st.session_state["_scan_name"]     = result.get("name", "")
                        st.session_state["_scan_calories"] = float(result.get("calories", 0))
                        st.session_state["_scan_protein"]  = float(result.get("protein",  0))
                        st.session_state["_scan_carbs"]    = float(result.get("carbs",    0))
                        st.session_state["_scan_fats"]     = float(result.get("fats",     0))
                        st.session_state["admin_scan_data"] = result
                        st.success(
                            f" Detected: **{result.get('name', 'Unknown')}** — "
                            f"Cal: **{result.get('calories',0)} kcal** | "
                            f"Protein: **{result.get('protein',0)}g** | "
                            f"Carbs: **{result.get('carbs',0)}g** | "
                            f"Fats: **{result.get('fats',0)}g**"
                        )

        elif scan_method == "📷 Capture Image Using Webcam":
            camera_img = st.camera_input("Take a photo of the mess food", key="admin_camera")
            if camera_img:
                st.image(camera_img, caption="📷 Captured Food Image", use_container_width=True)
                captured_image_bytes = camera_img.getvalue()
                if st.button(" Detect Food from Image", type="primary", key="admin_analyse_camera"):
                    with st.spinner("AI is identifying the food…"):
                        result = analyze_food_image(captured_image_bytes)
                        st.session_state["_scan_name"]     = result.get("name", "")
                        st.session_state["_scan_calories"] = float(result.get("calories", 0))
                        st.session_state["_scan_protein"]  = float(result.get("protein",  0))
                        st.session_state["_scan_carbs"]    = float(result.get("carbs",    0))
                        st.session_state["_scan_fats"]     = float(result.get("fats",     0))
                        st.session_state["admin_scan_data"] = result
                        st.success(
                            f" Detected: **{result.get('name', 'Unknown')}** — "
                            f"Cal: **{result.get('calories',0)} kcal** | "
                            f"Protein: **{result.get('protein',0)}g** | "
                            f"Carbs: **{result.get('carbs',0)}g** | "
                            f"Fats: **{result.get('fats',0)}g**"
                        )

        st.divider()
        
        st.markdown("###  Mess Menu Details")

        # ── Read current AI values ────────────────────────────────────────────
        cur_name     = st.session_state.get("_scan_name",     "")
        cur_calories = st.session_state.get("_scan_calories", 0.0)
        cur_protein  = st.session_state.get("_scan_protein",  0.0)
        cur_carbs    = st.session_state.get("_scan_carbs",    0.0)
        cur_fats     = st.session_state.get("_scan_fats",     0.0)

        form_col1, form_col2 = st.columns(2)

        with form_col1:
            # NO key= on text_input so value= is always respected
            scan_food_name = st.text_input(
                "Food Name",
                value=cur_name,
                placeholder="e.g. Paneer Butter Masala"
            )

            # Text-name AI trigger
            if scan_method == " Type Food Name":
                if st.button(" Auto-detect Nutrition from Name",
                             key="admin_text_detect", use_container_width=True):
                    if scan_food_name.strip():
                        with st.spinner("Analysing…"):
                            result = analyze_food_text(scan_food_name.strip())
                            st.session_state["_scan_name"]      = result.get("name", scan_food_name.strip())
                            st.session_state["_scan_calories"]  = float(result.get("calories", 0))
                            st.session_state["_scan_protein"]   = float(result.get("protein",  0))
                            st.session_state["_scan_carbs"]     = float(result.get("carbs",    0))
                            st.session_state["_scan_fats"]      = float(result.get("fats",     0))
                            st.session_state["admin_scan_data"] = result
                        st.success(
                            f" Estimated — Cal: **{result['calories']}** kcal | "
                            f"Protein: **{result['protein']}g** | "
                            f"Carbs: **{result['carbs']}g** | "
                            f"Fats: **{result['fats']}g**"
                        )
                        st.rerun()
                    else:
                        st.warning("Enter a food name first.")

            scan_meal_type = st.selectbox(
                "Meal Type",
                ["breakfast", "lunch", "snacks", "dinner"],
                key="admin_scan_meal_type"
            )
            scan_date = st.date_input(
                "Date", value=datetime.today(), key="admin_scan_date"
            )

        with form_col2:
            # NO key= on number_inputs — this forces Streamlit to use value= every render
            scan_cal = st.number_input(
                "Calories (kcal)",
                min_value=0, max_value=3000,
                value=int(cur_calories),
                step=1
            )
            scan_prot = st.number_input(
                "Protein (g)",
                min_value=0.0, max_value=200.0,
                value=round(cur_protein, 1),
                step=0.1
            )
            scan_carb = st.number_input(
                "Carbs (g)",
                min_value=0.0, max_value=400.0,
                value=round(cur_carbs, 1),
                step=0.1
            )
            scan_fat = st.number_input(
                "Fats (g)",
                min_value=0.0, max_value=200.0,
                value=round(cur_fats, 1),
                step=0.1
            )

        st.markdown("")

        # ── Save button — no validation warning, just disable until ready ─────
        all_filled = bool(scan_food_name.strip()) and scan_cal > 0

        if st.button(
            "Save To Mess Menu",
            type="primary",
            use_container_width=True,
            key="admin_scan_save",
            disabled=not all_filled
        ):
            image_path = ""
            if captured_image_bytes:
                ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = scan_food_name.strip().replace(" ", "_")
                image_path = save_uploaded_image(
                    captured_image_bytes,
                    f"{safe_name}_{ts}.jpg"
                )

            add_mess_menu(
                meal_type  = scan_meal_type,
                items      = scan_food_name.strip(),
                calories   = int(scan_cal),
                protein    = float(scan_prot),
                carbs      = float(scan_carb),
                fats       = float(scan_fat),
                date_str   = scan_date.strftime("%Y-%m-%d"),
                posted_by  = "Mess Admin (AI Scanner)",
                image_path = image_path
            )
            st.success(
                f" **{scan_food_name.strip()}** saved to "
                f"**{scan_meal_type.capitalize()}** for "
                f"{scan_date.strftime('%d %b %Y')}!"
            )
            for k in ["_scan_name", "_scan_calories", "_scan_protein",
                      "_scan_carbs", "_scan_fats", "admin_scan_data", "admin_scan_name"]:
                st.session_state.pop(k, None)
            st.rerun()
    # ── Tab 2 : View & Manage Menu ────────────────────────────────────────────
    with admin_tab2:
        st.subheader(" View & Edit Mess Menu")
        view_date = st.date_input("Select date to view", value=datetime.today(), key="view_date_admin")
        menus     = get_mess_menu(view_date.strftime("%Y-%m-%d"))

        if menus:
            for row in menus:
                mid, mtype, mitems, mcal, mprot, mcarb, mfat, mdate, mby, *extra = row
                mimg = extra[0] if extra else ""
                icon = {"breakfast": "🌅", "lunch": "☀️", "snacks": "🍎", "dinner": "🌙"}.get(mtype, "🍴")
                with st.expander(f"{icon} {mtype.capitalize()} — {mitems} — {mcal} kcal", expanded=False):
                    if mimg and os.path.exists(mimg):
                        st.image(mimg, caption="Mess Food Image", width=300)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Protein", f"{mprot}g")
                    c2.metric("Carbs",   f"{mcarb}g")
                    c3.metric("Fats",    f"{mfat}g")
                    st.caption(f"Posted by: {mby}")
                    if st.button(f"Delete {mtype.capitalize()}", key=f"del_menu_{mid}"):
                        delete_mess_menu(mid)
                        st.success("Deleted!")
                        st.rerun()

            st.subheader(" Last 7 Days — Mess Calorie Summary")
            hist = get_mess_menu_range(7)
            if hist:
                df_hist = pd.DataFrame(hist, columns=["Date", "Meal", "Items", "Calories"])
                fig = px.bar(
                    df_hist, x="Date", y="Calories", color="Meal",
                    barmode="group",
                    title="Mess Calories Uploaded per Day",
                    color_discrete_map={
                        "breakfast": "#f39c12", "lunch": "#27ae60",
                        "snacks":    "#3498db", "dinner": "#8e44ad"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No menu uploaded for {view_date.strftime('%d %b %Y')} yet.")

    # ── Tab 3 : Student Queries ───────────────────────────────────────────────
    with admin_tab3:
        st.subheader("Student Queries Dashboard")
        stats = get_query_stats()
        if stats:
            col_s = st.columns(len(stats))
            for i, (cat, cnt) in enumerate(stats):
                col_s[i].metric(f"🏷️ {cat.capitalize()}", cnt)

        filter_opt = st.selectbox("Filter by status", ["All", "Pending", "Resolved"], key="qfilter")
        status_map = {"All": None, "Pending": "pending", "Resolved": "resolved"}
        queries    = get_all_queries(status_map[filter_opt])

        if not queries:
            st.info("No queries found.")
        else:
            st.markdown(f"**{len(queries)} queries** — sorted by upvotes")
            for q in queries:
                qid, uid, sname, cat, qtxt, ups, qstat, areply, cat_at = q
                status_badge = " Resolved" if qstat == "resolved" else " Pending"
                with st.expander(
                    f"{ups}  |  [{cat.upper()}]  {qtxt[:70]}{'…' if len(qtxt) > 70 else ''}  —  {status_badge}",
                    expanded=(qstat == "pending")
                ):
                    st.markdown(f"**Student:** {sname or 'Anonymous'}")
                    st.markdown(f"**Category:** {cat.capitalize()}")
                    st.markdown(f"**Query:** {qtxt}")
                    st.caption(f"Submitted: {cat_at}")
                    if areply:
                        st.success(f"**Admin Reply:** {areply}")
                    reply_text = st.text_area(
                        "✍️ Reply to this query", value=areply or "",
                        key=f"reply_{qid}", height=80
                    )
                    bc1, bc2 = st.columns(2)
                    if bc1.button(" Send Reply & Mark Resolved", key=f"resolve_{qid}", type="primary"):
                        if reply_text.strip():
                            reply_to_query(qid, reply_text.strip())
                            st.success("Reply sent!")
                            st.rerun()
                        else:
                            st.warning("Please type a reply first.")
                    if bc2.button("🔄 Mark Pending", key=f"pending_{qid}"):
                        update_query_status(qid, "pending")
                        st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER
# ═════════════════════════════════════════════════════════════════════════════

def render_login():
    # Use columns to constrain width and center the login container on wide screen
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; margin-top: 30px; margin-bottom: 20px;'>"
            "<h1 style='font-family: Orbitron, monospace; font-weight: 900; font-size: 2.2rem; "
            "background: linear-gradient(135deg, #06b6d4, #6366f1); -webkit-background-clip: text; "
            "-webkit-text-fill-color: transparent; letter-spacing: 2px; margin-bottom: 10px;'>"
            "🏠 SMART HOSTEL</h1>"
            "<p style='color: #38bdf8; font-family: Rajdhani, sans-serif; font-size: 0.95rem; "
            "letter-spacing: 3px; text-transform: uppercase;'>AI Nutrition &amp; Student Wellness Portal</p>"
            "</div>",
            unsafe_allow_html=True
        )

        with st.container(border=True):
            tab1, tab2, tab3 = st.tabs(["Student Login", "Register", "Hostel Admin Login"])

            with tab1:
                email    = st.text_input("Email",    key="login_email")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.button("Login", type="primary", use_container_width=True, key="login_submit_btn"):
                    user = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")

            with tab2:
                name     = st.text_input("Full Name", key="reg_name")
                email    = st.text_input("Email",    key="reg_email")
                password = st.text_input("Password", type="password", key="reg_pass")
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    age    = st.number_input("Age",           10,   100,   25, key="reg_age")
                    weight = st.number_input("Weight (kg)",   30.0, 200.0, 65.0, key="reg_weight")
                    height = st.number_input("Height (cm)",  100.0, 250.0, 165.0, key="reg_height")
                with reg_col2:
                    goal   = st.selectbox("Goal", ["lose weight", "maintain", "gain weight"], key="reg_goal")
                    target = st.number_input("Daily Calorie Target", 1000, 5000, 2000, key="reg_target")
                if st.button("Register", type="primary", use_container_width=True, key="register_submit_btn"):
                    if register_user(name, email, password, age, weight, height, goal, target):
                        st.success("Registered! Please login.")
                    else:
                        st.error("Email already exists!")

            with tab3:
                st.info("🔒 This portal is restricted to hostel mess administrators only.")
                a_email = st.text_input("Admin Email",    key="admin_email")
                a_pass  = st.text_input("Admin Password", type="password", key="admin_pass")
                if st.button(" Admin Login", type="primary", use_container_width=True, key="admin_submit_btn"):
                    if a_email == HOSTEL_ADMIN_EMAIL and a_pass == HOSTEL_ADMIN_PASSWORD:
                        st.session_state.hostel_admin = True
                        st.success("Welcome, Admin!")
                        st.rerun()
                    else:
                        st.error("Invalid admin credentials!")

# ═════════════════════════════════════════════════════════════════════════════
# STUDENT APP
# ═════════════════════════════════════════════════════════════════════════════

def render_student_app():
    # Initialize food monitoring state keys (safeguard against caching/rerun)
    for key, val in [
        ('user', None), ('ai_data', {}), ('ai_name', ''),
        ('water_count', 0), ('messages', []),
        ('hostel_admin', False),
        ('admin_scan_data', {}), ('admin_scan_name', ''),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    user      = st.session_state.user
    meals     = get_today_meals(user[0])
    exercises = get_today_exercises(user[0])

    total_cal    = sum(m[3] for m in meals)
    total_protein= sum(m[4] for m in meals)
    total_carbs  = sum(m[5] for m in meals)
    total_fats   = sum(m[6] for m in meals)
    total_burned = sum(e[4] for e in exercises)
    net_calories = total_cal - total_burned
    target       = user[8]
    remaining    = target - net_calories

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("NutriCam")
        st.write(f" **{user[1]}**")
        st.write(f" Goal: {user[7]}")
        st.write(f" Target: {target} kcal/day")
        if user[5] and user[6]:
            bmi = user[5] / ((user[6] / 100) ** 2)
            bmi_color  = "" if 18.5 <= bmi <= 24.9 else "" if bmi < 30 else ""
            bmi_status = (
                "Normal"      if 18.5 <= bmi <= 24.9 else
                "Underweight" if bmi < 18.5 else
                "Overweight"  if bmi < 30   else "Obese"
            )
            st.write(f"📏 BMI: {bmi_color} {bmi:.1f} ({bmi_status})")
        st.divider()

        health_score = calculate_health_score(
            total_cal, target, total_protein, st.session_state.water_count, exercises
        )
        score_color = "" if health_score >= 70 else "" if health_score >= 40 else ""
        st.subheader(f" Health Score: {score_color} {health_score}/100")
        st.progress(health_score / 100)
        st.divider()

        st.subheader(" Water Tracker")
        water_goal = 8
        st.write(f"**{st.session_state.water_count}/{water_goal} glasses**")
        st.progress(min(st.session_state.water_count / water_goal, 1.0))
        wc1, wc2 = st.columns(2)
        with wc1:
            if st.button(" Glass", key="add_water_glass"):
                if st.session_state.water_count < water_goal:
                    st.session_state.water_count += 1
                    st.rerun()
        with wc2:
            if st.button(" Glass", key="remove_water_glass"):
                if st.session_state.water_count > 0:
                    st.session_state.water_count -= 1
                    st.rerun()
        if st.session_state.water_count >= water_goal:
            st.success(" Water goal done!")
        else:
            st.warning(f" {water_goal - st.session_state.water_count} more glasses needed!")
        st.divider()

        if st.button(" Logout", type="primary", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ── Top metrics ───────────────────────────────────────────────────────────
    st.title(f" Welcome, {user[1]}!")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Eaten",   f"{total_cal} kcal")
    col2.metric("Burned",  f"{total_burned} kcal")
    col3.metric("Net",     f"{net_calories} kcal", f"{remaining} remaining")
    col4.metric("Protein", f"{total_protein:.1f}g")
    col5.metric(" Water",   f"{st.session_state.water_count}/8")

    if net_calories > target:
        st.error(f" You exceeded your calorie goal by {net_calories - target} kcal!")
    elif net_calories > target * 0.9:
        st.warning(" You are close to your daily calorie limit!")
    else:
        st.success(f" Great job! {remaining} kcal remaining today.")
    st.progress(min(net_calories / target, 1.0), text=f"Net Progress: {net_calories}/{target} kcal")

    # ── Main Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Dashboard", "Add Meal", "Exercise",
        "Weight", "AI Chatbot", "Export",
        "Mess Menu", "My Queries"
    ])

    # ── Tab 1 : Dashboard ─────────────────────────────────────────────────────
    with tab1:
        if meals:
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=net_calories,
                    title={"text": "Net Calories"},
                    gauge={"axis": {"range": [0, target]},
                           "bar":  {"color": "green" if net_calories <= target else "red"}}
                ))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.pie(
                    values=[total_protein, total_carbs, total_fats],
                    names=["Protein", "Carbs", "Fats"],
                    title="Macronutrient Breakdown",
                    color_discrete_sequence=["#2ecc71", "#3498db", "#e74c3c"]
                )
                st.plotly_chart(fig2, use_container_width=True)

            week_data = get_week_meals(user[0])
            if week_data:
                st.subheader(" Last 7 Days")
                df_week = pd.DataFrame(week_data, columns=["Date", "Calories"])
                fig3 = px.bar(
                    df_week, x="Date", y="Calories",
                    title="Weekly Calorie Intake",
                    color="Calories",
                    color_continuous_scale=["green", "yellow", "red"]
                )
                fig3.add_hline(y=target, line_dash="dash", line_color="white", annotation_text="Target")
                st.plotly_chart(fig3, use_container_width=True)

            st.subheader(" Today's Meals")
            for meal in meals:
                with st.expander(f" {meal[2]} — {meal[3]} kcal ({meal[7]})"):
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.write(f"Protein: {meal[4]}g")
                    mc2.write(f" Carbs:   {meal[5]}g")
                    mc3.write(f" Fats:    {meal[6]}g")
                    if st.button(f"Delete", key=f"del_{meal[0]}"):
                        delete_meal(meal[0])
                        st.rerun()

            st.subheader(" AI Meal Recommendations")
            if st.button("Get Personalized Recommendations"):
                with st.spinner("AI is thinking…"):
                    rec = get_meal_recommendation(remaining, user[7])
                    st.info(rec)
        else:
            st.info("No meals logged today. Add your first meal!")
            if st.button("Get AI Recommendations"):
                with st.spinner("Getting recommendations…"):
                    rec = get_meal_recommendation(target, user[7])
                    st.info(rec)

    # ── Tab 2 : Add Meal ──────────────────────────────────────────────────────
    with tab2:
        st.subheader(" Add a Meal")

        input_method = st.radio(
            "How would you like to add your meal?",
            [" Type Food Name", " Upload From Gallery", "📷 Take Photo Using Camera"],
            horizontal=True
        )

        if input_method == " Upload From Gallery":
            uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Food Image", use_container_width=True)
                if st.button(" Analyze Uploaded Image", type="primary"):
                    with st.spinner("AI is analyzing your food…"):
                        data = analyze_food_image(uploaded_file.getvalue())
                        st.session_state.ai_data = data
                        st.session_state.ai_name = data.get("name", "")
                        st.success(f" Detected: **{data.get('name', 'Unknown Food')}**")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric(" Calories", f"{data.get('calories', 0)} kcal")
                        col2.metric("Protein",  f"{data.get('protein',  0)}g")
                        col3.metric(" Carbs",    f"{data.get('carbs',    0)}g")
                        col4.metric(" Fats",     f"{data.get('fats',     0)}g")
                        st.rerun()

        elif input_method == "📷 Take Photo Using Camera":
            camera_photo = st.camera_input("Take a photo of your food")
            if camera_photo is not None:
                st.image(camera_photo, caption="Captured Food Image", use_container_width=True)
                if st.button(" Analyze Camera Image", type="primary"):
                    with st.spinner("AI is analyzing your food…"):
                        data = analyze_food_image(camera_photo.getvalue())
                        st.session_state.ai_data = data
                        st.session_state.ai_name = data.get("name", "")
                        st.success(f" Detected: **{data.get('name', 'Unknown Food')}**")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric(" Calories", f"{data.get('calories', 0)} kcal")
                        col2.metric("Protein",  f"{data.get('protein',  0)}g")
                        col3.metric(" Carbs",    f"{data.get('carbs',    0)}g")
                        col4.metric(" Fats",     f"{data.get('fats',     0)}g")
                        st.rerun()

        st.divider()
        am_c1, am_c2 = st.columns(2)

        with am_c1:
            food_name = st.text_input("Food Name", value=st.session_state.get("ai_name", ""))
            meal_type = st.selectbox("Meal Type", ["breakfast", "lunch", "snacks", "dinner"])
            if input_method == " Type Food Name":
                if st.button(" Auto-detect Nutrition"):
                    if food_name:
                        with st.spinner("Analyzing food…"):
                            data = analyze_food_text(food_name)
                            st.session_state.ai_data = data
                            st.session_state.ai_name = data.get("name", food_name)
                            st.success(f" Estimated Calories: {data['calories']} kcal")
                            st.rerun()

        with am_c2:
            ai = st.session_state.get("ai_data", {})
            calories = st.number_input("Calories",    0,   5000,  int(ai.get("calories", 0)))
            protein  = st.number_input("Protein (g)", 0.0, 500.0, float(ai.get("protein", 0)))
            carbs    = st.number_input("Carbs (g)",   0.0, 500.0, float(ai.get("carbs",   0)))
            fats     = st.number_input("Fats (g)",    0.0, 500.0, float(ai.get("fats",    0)))

        if st.button(" Add Meal", type="primary", use_container_width=True):
            if food_name and calories > 0:
                add_meal(user[0], food_name, calories, protein, carbs, fats, meal_type)
                st.success(f" {food_name} added successfully!")
                st.session_state.ai_data = {}
                st.session_state.ai_name = ""
                st.rerun()
            else:
                st.warning("Please enter valid food details.")

    # ── Tab 3 : Exercise ──────────────────────────────────────────────────────
    with tab3:
        st.subheader("Exercise Tracker")
        ex_c1, ex_c2 = st.columns(2)
        with ex_c1:
            exercise_list = {
                "Walking": 4, "Running": 10, "Cycling": 8,
                "Swimming": 9, "Yoga": 3, "Gym/Weights": 6,
                "Dancing": 5, "Skipping": 10, "Other": 5
            }
            exercise_name  = st.selectbox("Exercise Type", list(exercise_list.keys()))
            duration       = st.number_input("Duration (minutes)", 1, 300, 30)
            estimated_burn = duration * exercise_list.get(exercise_name, 5)
            st.info(f" Estimated calories burned: **{estimated_burn} kcal**")
        with ex_c2:
            st.subheader("Today's Exercises")
            if exercises:
                for ex in exercises:
                    st.write(f" **{ex[2]}** — {ex[3]} min —  {ex[4]} kcal")
                st.metric("Total Burned Today", f"{total_burned} kcal")
            else:
                st.info("No exercises logged today!")
        if st.button(" Log Exercise", type="primary"):
            add_exercise(user[0], exercise_name, duration, estimated_burn)
            st.success(f" {exercise_name} logged! Burned {estimated_burn} kcal")
            st.rerun()

    # ── Tab 4 : Weight ────────────────────────────────────────────────────────
    with tab4:
        st.subheader("Weight Progress Tracker")
        wt_c1, wt_c2 = st.columns(2)
        with wt_c1:
            st.subheader("Log Today's Weight")
            new_weight = st.number_input("Your weight today (kg)", 30.0, 200.0, float(user[5] or 65.0))
            if st.button(" Log Weight", type="primary"):
                log_weight(user[0], new_weight)
                st.success(f" Weight {new_weight}kg logged!")
                st.rerun()
        with wt_c2:
            weight_history = get_weight_history(user[0])
            if weight_history:
                df_weight = pd.DataFrame(weight_history, columns=["Date", "Weight"])
                fig_w = px.line(
                    df_weight, x="Date", y="Weight",
                    title="Weight Progress", markers=True,
                    color_discrete_sequence=["#2ecc71"]
                )
                fig_w.update_layout(yaxis_title="Weight (kg)")
                st.plotly_chart(fig_w, use_container_width=True)
                start_w   = df_weight["Weight"].iloc[-1]
                current_w = df_weight["Weight"].iloc[0]
                diff = current_w - start_w
                if diff < 0:
                    st.success(f"🎉 You lost {abs(diff):.1f}kg!")
                elif diff > 0:
                    st.info(f"📈 You gained {diff:.1f}kg")
                else:
                    st.info("Weight maintained!")
            else:
                st.info("No weight data yet. Log your first weight!")

    # ── Tab 5 : AI Chatbot ────────────────────────────────────────────────────
    with tab5:
        st.subheader(" AI Nutrition Chatbot")
        st.write("Ask me anything about nutrition, diet, and health!")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        if prompt := st.chat_input("Ask about nutrition, recipes, diet tips…"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                from groq import Groq
                client  = Groq(api_key=st.secrets.get("GROQ_API_KEY", ""))
                context = f"User stats: calories today={total_cal}, goal={user[7]}, target={target} kcal"
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"You are a helpful nutrition expert. {context}"},
                        {"role": "user",   "content": prompt}
                    ]
                )
                reply = response.choices[0].message.content
            except Exception:
                reply = "Please add a Groq API key to enable the AI chatbot!"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

    # ── Tab 6 : Export ────────────────────────────────────────────────────────
    with tab6:
        st.subheader("Export Your Nutrition Report")
        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            hs = calculate_health_score(total_cal, target, total_protein, st.session_state.water_count, exercises)
            st.write("###  Today's Summary")
            st.write(f"-  Calories eaten: **{total_cal} kcal**")
            st.write(f"-  Calories burned: **{total_burned} kcal**")
            st.write(f"- Net calories: **{net_calories} kcal**")
            st.write(f"- Protein: **{total_protein:.1f}g**")
            st.write(f"-  Carbs: **{total_carbs:.1f}g**")
            st.write(f"-  Fats: **{total_fats:.1f}g**")
            st.write(f"-  Water: **{st.session_state.water_count}/8 glasses**")
            st.write(f"-  Health Score: **{hs}/100**")
        with exp_c2:
            if meals or exercises:
                csv_data = export_to_csv(meals, exercises)
                st.download_button(
                    label=" Download Report (CSV)",
                    data=csv_data,
                    file_name=f"nutricam_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
                if meals:
                    st.subheader("Meals")
                    df = pd.DataFrame(meals, columns=["ID","UserID","Food","Cal","Protein","Carbs","Fats","Type","Date"])
                    st.dataframe(df[["Food","Cal","Protein","Carbs","Fats","Type"]], use_container_width=True)
                if exercises:
                    st.subheader("Exercises")
                    df_ex = pd.DataFrame(exercises, columns=["ID","UserID","Exercise","Duration","Burned","Date"])
                    st.dataframe(df_ex[["Exercise","Duration","Burned"]], use_container_width=True)
            else:
                st.info("No data to export yet!")

    # ── Tab 7 : Mess Menu ─────────────────────────────────────────────────────
    with tab7:
        st.subheader(" Today's Hostel Mess Menu")
        st.caption("Menu is uploaded daily by the mess admin.")
        view_date_student = st.date_input(" View menu for date", value=datetime.today(), key="mess_date_student")
        today_menu = get_mess_menu(view_date_student.strftime("%Y-%m-%d"))

        icons = {"breakfast": "🌅", "lunch": "☀️", "snacks": "🍎", "dinner": "🌙"}

        if today_menu:
            total_mess_cal = 0
            cols = st.columns(min(len(today_menu), 3))
            for i, row in enumerate(today_menu):
                mid, mtype, mitems, mcal, mprot, mcarb, mfat, mdate, mby, *extra = row
                mimg = extra[0] if extra else ""
                icon = icons.get(mtype, "🍴")
                total_mess_cal += mcal
                with cols[i % 3]:
                    st.markdown(f"### {icon} {mtype.capitalize()}")
                    if mimg and os.path.exists(mimg):
                        st.image(mimg, use_container_width=True)
                    dishes = [d.strip() for d in mitems.split(',') if d.strip()]
                    for dish in dishes:
                        st.markdown(f"- {dish}")
                    st.divider()
                    nc1, nc2, nc3 = st.columns(3)
                    nc1.metric(" kcal",  mcal)
                    nc2.metric(" Prot",  f"{mprot}g")
                    nc3.metric(" Carbs", f"{mcarb}g")

            st.success(f" Total mess calories today: **{total_mess_cal} kcal**")
            st.subheader(" Add Mess Meal to Your Tracker")
            st.info("Click below to instantly log a mess meal into your personal calorie tracker.")
            for row in today_menu:
                mid, mtype, mitems, mcal, mprot, mcarb, mfat, mdate, mby, *_ = row
                icon = icons.get(mtype, "🍴")
                if st.button(
                    f"{icon} Add {mtype.capitalize()} to My Log ({mcal} kcal)",
                    key=f"addmess_{mid}", use_container_width=True
                ):
                    add_meal(user[0], f"Mess {mtype.capitalize()} ({mdate})",
                             mcal, mprot, mcarb, mfat, mtype)
                    st.success(f" Mess {mtype.capitalize()} added to your log!")
                    st.rerun()
        else:
            st.warning("🚫 No menu has been uploaded for this date yet. Please check back later.")
            st.info("💡 Tip: You can still log mess meals manually using the **Add Meal** tab.")

        with st.expander(" View Last 7 Days Menu History", expanded=False):
            hist_menu = get_mess_menu_range(7)
            if hist_menu:
                for date_val, mtype, items, cal in hist_menu:
                    st.markdown(
                        f"**{date_val}  |  {icons.get(mtype,'🍴')} {mtype.capitalize()}** "
                        f"— {cal} kcal  |  {items}"
                    )
            else:
                st.info("No menu history available.")

    # ── Tab 8 : My Queries ────────────────────────────────────────────────────
    with tab8:
        st.subheader(" Hostel Queries")
        st.write("Raise concerns about mess food, facility, or hygiene. Popular queries are prioritised by the admin.")
        sq_tab1, sq_tab2 = st.tabs([" All Queries", "✏️ Submit a Query"])

        with sq_tab1:
            cat_filter = st.selectbox(
                "Filter by category",
                ["All", "food", "facility", "hygiene", "other"],
                key="cat_filter_student"
            )
            all_q = get_all_queries()
            if cat_filter != "All":
                all_q = [q for q in all_q if q[3] == cat_filter]
            if not all_q:
                st.info("No queries yet. Be the first to submit one!")
            else:
                st.markdown(f"**{len(all_q)} queries**")
                for q in all_q:
                    qid, uid, sname, cat, qtxt, ups, qstat, areply, cat_at = q
                    status_badge = "" if qstat == "resolved" else ""
                    with st.expander(
                        f"{status_badge} {ups}  [{cat.upper()}]  {qtxt[:65]}{'…' if len(qtxt)>65 else ''}",
                        expanded=False
                    ):
                        st.markdown(f"**Query:** {qtxt}")
                        st.caption(f"By: {sname or 'Anonymous'}  |  {cat_at}")
                        if areply:
                            st.success(f"**Admin Reply:** {areply}")
                        uv_col, _ = st.columns([1, 3])
                        if uv_col.button(f" Upvote ({ups})", key=f"upvote_{qid}_{user[0]}"):
                            if upvote_query(qid, user[0]):
                                st.success("Upvoted!")
                            else:
                                st.warning("You already upvoted this.")
                            st.rerun()

        with sq_tab2:
            st.subheader("✏️ Submit a New Query")
            st.info("Your query will be visible to all students and the hostel admin.")
            q_category   = st.selectbox("Category", ["food", "facility", "hygiene", "other"])
            q_text       = st.text_area(
                "Describe your query / complaint",
                placeholder="e.g. The dal served on Monday was undercooked and salty.",
                height=120
            )
            show_name    = st.checkbox("Show my name on the query", value=True)
            student_name = user[1] if show_name else "Anonymous"

            if st.button(" Submit Query", type="primary", use_container_width=True):
                if q_text.strip():
                    add_query(user[0], student_name, q_category, q_text.strip())
                    st.success(" Query submitted! Other students can upvote it and the admin will respond soon.")
                    st.rerun()
                else:
                    st.warning("Please describe your query before submitting.")

            st.divider()
            st.subheader("📌 My Submitted Queries")
            my_queries = get_student_queries(user[0])
            if my_queries:
                for q in my_queries:
                    qid, uid, sname, cat, qtxt, ups, qstat, areply, cat_at = q
                    status_label = " Resolved" if qstat == "resolved" else " Pending"
                    with st.expander(f"{status_label}  [{cat.upper()}]  {qtxt[:60]}…"):
                        st.markdown(f"**Query:** {qtxt}")
                        st.markdown(f"**Upvotes:**  {ups}")
                        st.caption(f"Submitted: {cat_at}")
                        if areply:
                            st.success(f"**Admin Reply:** {areply}")
                        else:
                            st.info("Awaiting admin response…")
            else:
                st.info("You haven't submitted any queries yet.")

# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    st.set_page_config(page_title="NutriCam", page_icon=None, layout="wide")
    if st.session_state.hostel_admin:
        render_hostel_admin()
    elif st.session_state.user is not None:
        render_student_app()
    else:
        render_login()