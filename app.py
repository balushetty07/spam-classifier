import os
import pickle
import re
import time
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Spam SMS Classifier",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")

# --- 2. Database Initialization ---
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
    try:
        cursor.execute("ALTER TABLE message_log ADD COLUMN is_misclassified INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

# --- 3. MIDNIGHT GLASS CSS THEME (Completely Upgraded) ---
st.markdown("""
    <style>
    @font-face { font-family: 'Google Sans'; src: url('https://fonts.gstatic.com/s/productsans/v5/HYvgU2fE2nRJvZ5JFAumwegdm0LZdjqr5-oayXSOefg.woff2') format('woff2'); }
    h1, h2, h3, h4, h5, h6, .stApp { font-family: 'Google Sans', sans-serif !important; }
    
    /* Sleek Dark Gradient Background */
    .stApp { 
        background: linear-gradient(135deg, #09090b 0%, #17153B 50%, #2E236C 100%) !important; 
        background-attachment: fixed !important; 
    }
    
    .stMarkdown p, .stText, label, .stMarkdown li { color: #E2E8F0 !important; }
    h1, h2, h3 { color: #FFFFFF !important; text-shadow: 0 4px 20px rgba(139, 92, 246, 0.3); }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    a, a:hover, a:visited, a:active { text-decoration: none !important; color: inherit !important; }
    
    /* Hide Top Headers */
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] { 
        background: rgba(10, 10, 15, 0.6) !important; 
        backdrop-filter: blur(20px) !important; 
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important; 
    }
    
    /* 🌟 THE NEW BEAUTIFUL DROPDOWN MENU */
    div[data-baseweb="select"] > div {
        background: rgba(20, 20, 35, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    div[data-baseweb="select"] > div:hover {
        border: 1px solid rgba(139, 92, 246, 0.8) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.4) !important;
        transform: translateY(-2px);
    }
    div[data-baseweb="select"] * { color: #FFFFFF !important; }
    
    /* 🌟 BEAUTIFUL TEXT AREA */
    div[data-baseweb="textarea"] > div { 
        background-color: rgba(15, 15, 25, 0.5) !important; 
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 12px !important; 
        color: #FFFFFF !important;
        transition: all 0.3s ease !important;
    }
    div[data-baseweb="textarea"] > div:focus-within {
        border: 1px solid rgba(139, 92, 246, 0.7) !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.2) !important;
    }
    textarea { color: #FFFFFF !important; }

    /* Interactive Glass Cards */
    [data-testid="stVerticalBlockBorderWrapper"], .stExpander { 
        background: rgba(255, 255, 255, 0.03) !important; 
        backdrop-filter: blur(12px) !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        border-radius: 16px !important; 
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; 
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease !important; 
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { 
        transform: translateY(-5px) !important; 
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25) !important;  
        border: 1px solid rgba(139, 92, 246, 0.4) !important; 
    }

    /* Glowing Pill Buttons */
    .stButton>button { 
        background: linear-gradient(135deg, #8B5CF6 0%, #4F46E5 100%) !important; 
        color: white !important; 
        font-weight: 600 !important; 
        border-radius: 50px !important;  
        border: 1px solid rgba(255,255,255,0.1) !important; 
        padding: 12px 28px !important; 
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important; 
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important; 
    }
    .stButton>button:hover { 
        transform: translateY(-3px) scale(1.03) !important; 
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.7) !important; 
        background: linear-gradient(135deg, #A78BFA 0%, #6366F1 100%) !important; 
    }
    
    /* Custom Pills & Menus */
    .github-pill { position: fixed; bottom: 20px; right: 20px; display: flex; align-items: center; background: rgba(255, 255, 255, 0.05); padding: 10px 20px; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); transition: all 0.3s ease; z-index: 9999; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); }
    .github-pill:hover { transform: translateY(-3px); background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.5); box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4); }
    .menu-pill { display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.05); padding: 10px 20px; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); }
    .menu-pill:hover { transform: translateY(-2px); background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.4); box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3); }
    .dev-pill { display: flex; align-items: center; background: rgba(255, 255, 255, 0.03); padding: 8px 16px; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease; margin-bottom: 10px; }
    .dev-pill:hover { transform: translateY(-2px); background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.3); }
    
    </style>
""", unsafe_allow_html=True)

st.markdown("""<a href="https://github.com/balushetty07" target="_blank" class="github-pill"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="22" style="margin-right:8px; filter: invert(1);"><b style="color:#FFFFFF; font-size: 15px;">Balu S</b></a>""", unsafe_allow_html=True)

# --- 4. Text Preprocessing Engine ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+", " suspiciouslink ", text)
    text = re.sub(r"www\.\S+", " suspiciouslink ", text)
    text = re.sub(r"\[.*?\]|\b[a-zA-Z0-9.-]+\.(com|org|net|info|biz|co)\b", " suspiciouslink ", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text

# --- 5. Load Models (Dual Model Architecture) ---
@st.cache_resource
def load_models():
    with open("spam_model.pkl", "rb") as model_file:
        nb_model = pickle.load(model_file)
    with open("vectorizer.pkl", "rb") as vec_file:
        vectorizer = pickle.load(vec_file)
        
    lr_model = None
    if os.path.exists("lr_model.pkl"):
        with open("lr_model.pkl", "rb") as lr_file:
            lr_model = pickle.load(lr_file)
            
    return nb_model, lr_model, vectorizer

nb_model, lr_model, vectorizer = load_models()

# --- 6. Memory & Routing ---
if "history" not in st.session_state: st.session_state.history = []
if "current_page" not in st.session_state: st.session_state.current_page = "Dashboard"

# --- 7. Sidebar Navigation (RESTORED COMPLETELY) ---
with st.sidebar:
    st.title("⚙️ System Menu")
    
    st.markdown("### 🧭 Navigation")
    if st.button("📊 Dashboard", use_container_width=True): st.session_state.current_page = "Dashboard"; st.rerun()
    if st.button("🗄️ SQL Analytics & Admin", use_container_width=True): st.session_state.current_page = "Database"; st.rerun()
    if st.button("📖 About System", use_container_width=True): st.session_state.current_page = "About"; st.rerun()
    
    st.markdown("---")
    
    st.subheader("📁 Session Management")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        csv = df_history.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 Download Session CSV", data=csv, file_name="spam_report.csv", mime="text/csv", use_container_width=True)
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Run a scan to generate a report.")
        
    st.markdown("---")
    
    st.subheader("👨‍💻 Project Team")
    st.markdown("**Main Developer:**")
    st.markdown("""<a href="https://github.com/balushetty07" target="_blank" class="menu-pill"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="margin-right:10px; filter: invert(1);"><b style="color:#FFFFFF; font-size: 15px;">Balu S</b></a>""", unsafe_allow_html=True)
    
    st.markdown("**Development Support:**")
    st.markdown("""
    <div class="dev-pill">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Vijaya Kumar</b>
    </div>
    <a href="https://github.com/shivaraj57" target="_blank" class="dev-pill" style="text-decoration: none;">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Shivaraj PM</b>
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.warning("Disclaimer: This AI Spam Shield is an educational engineering project designed to demonstrate Natural Language Processing and Machine Learning classification techniques. It is not a commercial security product. Please do not input sensitive personal information, real passwords, banking details, or corporate data into this system. Use at your own risk.")

# --- 8. PAGE ROUTING: DASHBOARD ---
if st.session_state.current_page == "Dashboard":
    st.title("🛡️ Threat Detection Center")
    
    st.markdown("### ⚙️ Engine Configuration")
    selected_engine = st.selectbox(
        "Select AI Classification Engine:",
        ["Multinomial Naive Bayes (Production)", "Logistic Regression (Validation)"]
    )

    st.markdown("Enter a message below. The NLP engine will calculate the mathematical probability of a phishing or spam attempt.")
    user_input = st.text_area("Message Content", placeholder="Paste email, SMS, or suspicious link here...", height=150, label_visibility="collapsed")

    if st.button("🔍 Run Security Scan", use_container_width=True):
        if user_input.strip() == "":
            st.error("⚠️ Please enter a message to analyze!")
        else:
            if "Naive Bayes" in selected_engine:
                active_model = nb_model
            else:
                active_model = lr_model

            if active_model is None:
                st.error("⚠️ Logistic Regression model not found. Please run classifier.py to generate lr_model.pkl first!")
            else:
                with st.spinner(f"Analyzing using {selected_engine}..."):
                    cleaned_input = clean_text(user_input)
                    input_vector = vectorizer.transform([cleaned_input])

                    probs = active_model.predict_proba(input_vector)[0]
                    spam_prob = probs[1] * 100
                    safe_prob = probs[0] * 100
                    confidence = max(spam_prob, safe_prob)
                    
                    if spam_prob >= 35:
                        status_label = "SPAM 🚨"
                        st.error("🚨 **CRITICAL THREAT DETECTED**")
                        st.info("The system has flagged this content as highly suspicious. Do not click any links or provide personal information.")
                    else:
                        status_label = "CLEAN ✅"
                        st.success("✅ **CLEAN MESSAGE**")
                        st.info("No malicious patterns detected in the text structure or vocabulary.")

                    col1, col2 = st.columns(2)
                    col1.metric(label="Active Engine", value="Naive Bayes" if "Naive Bayes" in selected_engine else "Logistic Regression")
                    col2.metric(label="Spam Probability", value=f"{spam_prob:.2f}%")

                st.session_state.history.insert(0, {
                    "Message": user_input,
                    "Status": status_label,
                    "Confidence": f"{confidence:.2f}%",
                    "Timestamp": time.strftime("%H:%M:%S")
                })

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO message_log (timestamp, message, prediction, confidence) VALUES (?, ?, ?, ?)",
                    (current_time, user_input, status_label, f"{confidence:.2f}%")
                )
                conn.commit()
                conn.close()
                st.toast("Saved to SQL Database!", icon="💾")

    # RESTORED: Temporary Session History on the Dashboard
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

# --- 9. PAGE ROUTING: DATABASE & ANALYTICS ---
elif st.session_state.current_page == "Database":
    st.title("🗄️ System Analytics & Database Control")
    st.markdown("This panel reads directly from the persistent SQLite instance (**`history.db`**).")
    
    conn = sqlite3.connect(DB_PATH)
    df_sql = pd.read_sql_query("SELECT * FROM message_log ORDER BY id DESC", conn)
    
    if not df_sql.empty:
        st.subheader("📈 Security Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_scans = len(df_sql)
        spam_blocked = len(df_sql[df_sql['prediction'].str.contains('SPAM')])
        clean_passed = total_scans - spam_blocked
        false_positives = len(df_sql[df_sql['is_misclassified'] == 1])
        
        col1.metric("Total Scans", total_scans)
        col2.metric("Threats Blocked 🚨", spam_blocked)
        col3.metric("Clean Passed ✅", clean_passed)
        col4.metric("Flagged Errors 🔧", false_positives)

        chart_data = pd.DataFrame({
            "Classification": ["Spam Blocked", "Clean Passed"],
            "Count": [spam_blocked, clean_passed]
        })
        st.bar_chart(chart_data, x="Classification", y="Count", color="Classification")

        st.markdown("---")
        st.subheader("🔍 Raw Threat Logs")
        
        with st.expander("🛠️ Admin Tools: Flag Misclassified Row"):
            st.write("If the AI made a mistake, flag the row ID here so the data can be used to retrain future models.")
            flag_id = st.number_input("Enter Row ID to Flag:", min_value=1, step=1)
            if st.button("Flag as Misclassified (False Positive/Negative)"):
                cursor = conn.cursor()
                cursor.execute("UPDATE message_log SET is_misclassified = 1 WHERE id = ?", (flag_id,))
                conn.commit()
                st.success(f"Row {flag_id} successfully flagged! Refreshing...")
                time.sleep(1)
                st.rerun()

        st.dataframe(df_sql, use_container_width=True)
    else:
        st.info("The SQL Database is empty. Run a scan to generate analytics!")
        
    conn.close()

# --- 10. PAGE ROUTING: ABOUT (RESTORED FULLY) ---
elif st.session_state.current_page == "About":
    st.title("📖 System Documentation")
    st.markdown("---")
    
    st.markdown("### 🌍 The Threat Landscape: Why is this system required?")
    st.write("In today's hyper-connected digital economy, communication channels like SMS and email are the primary attack vectors for cybercriminals. We are witnessing an exponential rise in **Social Engineering**, **Spear-Phishing**, and **Smishing (SMS Phishing)** attacks. Malicious actors are no longer just sending obvious junk mail; they use sophisticated, psychologically manipulative text to steal financial credentials, distribute malware, and commit identity fraud.")
    st.write("Traditional security systems rely on static 'blocklists' (blocking known bad numbers or hardcoded links). These legacy systems fail entirely because attackers can generate thousands of new numbers and domains instantly. **This is why an AI-driven, Machine Learning approach is strictly required.** Instead of memorizing bad links, our NLP system mathematically learns the underlying behavioral patterns and vocabulary of a scam, allowing it to intercept brand new, zero-day phishing attacks before they ever reach the user.")
    
    st.markdown("### ⚡ Computational Efficiency & Real-Time Processing")
    st.write("For a cybersecurity firewall to be viable, it must be highly accurate and computationally lightweight. This system was engineered specifically for high-speed, real-time threat detection.")
    st.markdown("""
    * **Algorithmic Speed:** By deploying **Multinomial Naive Bayes** as the production model, the system achieves an incredibly low time-complexity of **O(N)**. It calculates probability distributions using simple mathematical products, allowing it to classify large blocks of text in milliseconds without requiring massive server infrastructure.
    * **Precision-Recall Balance:** The model uses a custom detection threshold tuned for optimal spam recall without excessive false positives — ensuring genuine spam is caught while legitimate messages remain unaffected.
    * **Dynamic Vectorization:** The TF-IDF (Term Frequency-Inverse Document Frequency) engine instantly drops useless English "stop words" and assigns heavy mathematical weights to structural threat indicators including suspicious links, amounts, and spam keywords. This makes the classification highly efficient, even if attackers attempt to bypass filters using typos or masked text.
    """)
    
    st.markdown("### 🧠 Comparative Model Architecture")
    st.markdown("""
    * **Data Preprocessing & Cleansing:** Scrubs raw text data to normalize inputs while preserving numerical spam signals.
    * **URL Detection:** Detects and tags suspicious links as a dedicated spam-signal token before vectorization.
    * **TF-IDF Vectorization:** Evaluates how frequently a word appears relative to the entire dataset.
    * **Probabilistic Classification (Naive Bayes):** The production model calculates the statistical probability of a threat using a calibrated class prior.
    * **Comparative Baseline (Logistic Regression):** Evaluated against a Logistic Regression baseline to ensure boundary accuracy.
    """)
    
    st.markdown("### 📊 Performance Metrics")
    st.info(
        "**Benchmark Accuracy: 96.86%**\n\n"
        "The system was rigorously trained on the globally recognized *SMS Spam Collection Dataset*. "
        "To guarantee maximum reliability, the live Naive Bayes model was cross-validated against a **Logistic Regression** baseline. "
        "While Logistic Regression maps decision boundaries using complex log-odds, Naive Bayes proved vastly superior in handling the high-dimensional, sparse data generated by text vectors, resulting in faster and more accurate real-time classification."
    )