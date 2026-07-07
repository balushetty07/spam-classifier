import os
import pickle
import re
import time
# 🛠️ SQL DATABASE INJECTIONS
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Spam SMS Classifier",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 🛠️ SYSTEM FIX: Create a bulletproof absolute path for the database file
DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")


# 🛠️ SQL DATABASE INJECTION: Initialize table structure
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            message TEXT,
            prediction TEXT,
            confidence TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()  # Safely boot up database table

# --- 2. Locked Dark Mode CSS Injection (Cosmic Indigo Theme) ---
st.markdown(
    """
    <style>
    @font-face {
        font-family: 'Google Sans';
        src: url('https://fonts.gstatic.com/s/productsans/v5/HYvgU2fE2nRJvZ5JFAumwegdm0LZdjqr5-oayXSOefg.woff2') format('woff2');
    }
    h1, h2, h3, .stApp { font-family: 'Google Sans', sans-serif !important; }
    
    /* Global Background & Text - NEW COSMIC INDIGO THEME */
    .stApp { background: linear-gradient(135deg, #09090b 0%, #1e1b4b 50%, #312e81 100%) !important; background-attachment: fixed !important; }
    .stMarkdown p, .stText, label, .stMarkdown li { color: #FFFFFF !important; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 0 2px 10px rgba(0,0,0,0.4); }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    
    /* 🚫 NUKE ALL BLUE UNDERLINES FROM LINKS 🚫 */
    a, a:hover, a:visited, a:active {
        text-decoration: none !important;
        color: inherit !important;
    }
    
    /* Hide Top Headers */
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* 🚀 Hijacking the Sidebar Arrow to a Hamburger Menu */
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"]::before {
        content: '☰';
        font-size: 24px;
        color: #FFFFFF;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }
    [data-testid="collapsedControl"] {
        background: rgba(15, 23, 42, 0.4) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Frosted Glass Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 20, 0.5) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Glassmorphism Cards */
    [data-testid="stVerticalBlockBorderWrapper"], .stExpander {
        background: rgba(20, 20, 35, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.2) !important; 
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
    }

    /* 💎 PILL-SHAPED Glassy Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #8B5CF6, #6366F1) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 50px !important; 
        border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 12px 24px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
        backdrop-filter: blur(5px) !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6) !important;
        background: linear-gradient(90deg, #A78BFA, #8B5CF6) !important;
    }
    
    /* Bottom Right Floating GitHub Pill */
    .github-pill {
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        transition: all 0.3s ease;
        z-index: 9999;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .github-pill:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.3);
    }

    /* Sidebar Main Developer Pill */
    .menu-pill {
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .menu-pill:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 20px rgba(255, 255, 255, 0.2);
    }
    
    /* Sidebar Development Support Pills */
    .dev-pill {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.03);
        padding: 8px 16px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    .dev-pill:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Toggle Button Specific Styling */
    button[title="View fullscreen"] { display: none; } 

    /* Input Areas */
    div[data-baseweb="textarea"] > div {
        background-color: rgba(10, 10, 20, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    textarea { color: #FFFFFF !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 2.5 Inject Bottom Right GitHub Pill ---
st.markdown(
    """
    <a href="https://github.com/balushetty07" target="_blank" class="github-pill">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="22" style="margin-right:8px; filter: invert(1);">
        <b style="color:#FFFFFF; font-size: 15px;">Balu S</b>
    </a>
""",
    unsafe_allow_html=True,
)


# --- 3. Text Preprocessing Engine ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+", " suspiciouslink ", text)
    text = re.sub(r"www\.\S+", " suspiciouslink ", text)
    text = re.sub(
        r"\[.*?\]|\b[a-zA-Z0-9.-]+\.(com|org|net|info|biz|co)\b",
        " suspiciouslink ",
        text,
    )
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


# --- 4. Load Models ---
@st.cache_resource
def load_models():
    with open("spam_model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    with open("vectorizer.pkl", "rb") as vec_file:
        vectorizer = pickle.load(vec_file)
    return model, vectorizer


model, vectorizer = load_models()

# --- 5. Memory & Routing ---
if "history" not in st.session_state:
    st.session_state.history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- 6. Sidebar Menu & Navigation ---
with st.sidebar:
    st.title("⚙️ System Menu")
    st.markdown("### 🧭 Navigation")

    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.button("📖 About System", use_container_width=True):
        st.session_state.current_page = "About"
        st.rerun()

    # 🛠️ SQL DATABASE INJECTION: Database sub-panel tab
    if st.button("🗄️ SQL Database Admin", use_container_width=True):
        st.session_state.current_page = "Database"
        st.rerun()

    st.markdown("---")

    st.subheader("📁 Session Management")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        csv = df_history.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Session CSV",
            data=csv,
            file_name="spam_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Run a scan to generate a report.")

    st.markdown("---")
    st.subheader("👨‍💻 Project Team")
    st.markdown("**Main Developer:**")

    st.markdown(
        """
    <a href="https://github.com/balushetty07" target="_blank" class="menu-pill">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="margin-right:10px; filter: invert(1);">
        <b style="color:#FFFFFF; font-size: 15px;">Balu S</b>
    </a>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("**Development Support:**")
    st.markdown(
        """
    <div class="dev-pill">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Vijaya Kumar</b>
    </div>
    <a href="https://github.com/shivaraj57" target="_blank" class="dev-pill" style="text-decoration: none;">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Shivaraj PM</b>
    </a>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.warning(
        "Disclaimer: This AI Spam Shield is an educational engineering project designed to demonstrate Natural Language Processing and Machine Learning classification techniques. It is not a commercial security product. Please do not input sensitive personal information, real passwords, banking details, or corporate data into this system. Use at your own risk."
    )

# --- 7. PAGE ROUTING LOGIC ---
if st.session_state.current_page == "Dashboard":

    st.title("🛡️ Spam SMS Classifier")
    st.markdown(
        "Enter a message below. The NLP engine will calculate the mathematical probability of a phishing or spam attempt."
    )

    user_input = st.text_area(
        "Message Content",
        placeholder="Paste email, SMS, or suspicious link here...",
        height=150,
        label_visibility="collapsed",
    )

    if st.button("🔍 Scan for Threats", use_container_width=True):
        if user_input.strip() == "":
            st.error("⚠️ Please enter a message to analyze!")
        else:
            st.toast("Initiating NLP text vectorization...", icon="⏳")
            time.sleep(0.3)

            with st.spinner("Calculating mathematical probabilities..."):
                cleaned_input = clean_text(user_input)
                input_vector = vectorizer.transform([cleaned_input])

                probabilities = model.predict_proba(input_vector)[0]

                safe_prob = probabilities[0] * 100
                spam_prob = probabilities[1] * 100
                confidence = max(safe_prob, spam_prob)

                st.toast("Scan complete!", icon="✅")

            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric(label="🟢 Clean Probability", value=f"{safe_prob:.2f}%")
            col2.metric(label="🔴 Spam Probability", value=f"{spam_prob:.2f}%")

            if spam_prob >= 35:
                status_label = "SPAM 🚨"
                st.error("🚨 **CRITICAL THREAT DETECTED**")
                st.info(
                    "The system has flagged this content as highly suspicious. Do not click any links or provide personal information."
                )
            else:
                status_label = "CLEAN ✅"
                st.success("✅ **CLEAN MESSAGE**")
                st.info(
                    "No malicious patterns detected in the text structure or vocabulary."
                )

            st.session_state.history.insert(
                0,
                {
                    "Message": user_input,
                    "Status": status_label,
                    "Confidence": f"{confidence:.2f}%",
                    "Timestamp": time.strftime("%H:%M:%S"),
                },
            )

            # 🛠️ SQL DATABASE INJECTION: Insert using the bulletproof DB_PATH
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO message_log (timestamp, message, prediction, confidence) VALUES (?, ?, ?, ?)",
                (
                    current_time,
                    user_input,
                    status_label,
                    f"{confidence:.2f}%",
                ),
            )
            conn.commit()
            conn.close()
            st.success("💾 Row permanently saved inside SQLite Database!")

            with st.expander("⚙️ View Technical Analysis"):
                st.write(f"**Raw Input Length:** {len(user_input)} characters")
                st.write(f"**Cleaned NLP Tokens:** `{cleaned_input}`")
                st.markdown("---")
                st.write("**🧠 Comparative Model Architecture:**")
                st.write("✅ **Active Production Model:** Multinomial Naive Bayes")
                st.write("✅ **Validation Baseline Model:** Logistic Regression")

    if st.session_state.history:
        st.markdown("---")
        st.subheader("🕒 Session History")
        for item in st.session_state.history:
            with st.container(border=True):
                col_type, col_time, col_score = st.columns([2, 1, 1])
                col_type.write(f"**{item['Status']}**")
                col_time.write(f"⏱️ {item['Timestamp']}")
                col_score.write(f"🧠 {item['Confidence']}")
                st.write(f"_{item['Message'][:120]}..._")

elif st.session_state.current_page == "About":
    st.title("📖 System Documentation")
    st.markdown("---")
    st.markdown("### 🌍 The Threat Landscape")
    st.write(
        "This system serves as an educational engineering project showcasing Natural Language Processing."
    )

# 🛠️ SQL DATABASE INJECTION: Render panel using bulletproof DB_PATH query reads
elif st.session_state.current_page == "Database":
    st.title("🗄️ SQL Database Admin Control Panel")
    st.markdown(
        "This panel reads directly from the persistent SQLite instance (**`history.db`**)."
    )

    if st.button("🔄 Refresh Data From SQL", use_container_width=True):
        conn = sqlite3.connect(DB_PATH)
        df_sql = pd.read_sql_query(
            "SELECT * FROM message_log ORDER BY id DESC", conn
        )
        conn.close()

        if not df_sql.empty:
            st.dataframe(df_sql, use_container_width=True)
        else:
            st.info("The SQL Database table is currently empty.")