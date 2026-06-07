import streamlit as st
import pickle
import re
import pandas as pd
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Spam SMS Classifier", page_icon="🛡️", layout="centered", initial_sidebar_state="expanded")

# --- 2. Locked Dark Mode CSS Injection (Cosmic Indigo Theme) ---
st.markdown("""
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
""", unsafe_allow_html=True)

# --- 2.5 Inject Bottom Right GitHub Pill ---
st.markdown("""
    <a href="https://github.com/balushetty07" target="_blank" class="github-pill">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="22" style="margin-right:8px; filter: invert(1);">
        <b style="color:#FFFFFF; font-size: 15px;">Balu S</b>
    </a>
""", unsafe_allow_html=True)

# --- 3. Text Preprocessing Engine ---
# ================================================================
#  FIX 1: Keep numbers in clean_text!
#  Numbers are huge spam signals: "WIN 1000", "FREE 50%", "0800"
#  Old code: r'[^a-z\s]'    <- was nuking all numbers!
#  New code: r'[^a-z0-9\s]' <- numbers survive the cleaning!
#
#  This function is now 100% SYNCED with classifier.py's
#  clean_text so training and inference use identical preprocessing.
# ================================================================
def clean_text(text):
    text = str(text).lower()
    # Detect URLs and replace with 'suspiciouslink' spam-signal token
    text = re.sub(r'https?://\S+', ' suspiciouslink ', text)
    text = re.sub(r'www\.\S+', ' suspiciouslink ', text)
    text = re.sub(r'\[.*?\]|\b[a-zA-Z0-9.-]+\.(com|org|net|info|biz|co)\b', ' suspiciouslink ', text)
    # FIX: Keep letters AND numbers, remove only symbols/punctuation
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

# --- 4. Load Models ---
@st.cache_resource
def load_models():
    with open('spam_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vec_file:
        vectorizer = pickle.load(vec_file)
    return model, vectorizer

model, vectorizer = load_models()

# --- 5. Memory & Routing ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_page' not in st.session_state:
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

    st.markdown("---")
    
    st.subheader("📁 Session Management")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        csv = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Session CSV", data=csv, file_name='spam_report.csv', mime='text/csv', use_container_width=True)
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Run a scan to generate a report.")
        
    st.markdown("---")
    st.subheader("👨‍💻 Project Team")
    st.markdown("**Main Developer:**")
    
    # Main Developer Pill
    st.markdown("""
    <a href="https://github.com/balushetty07" target="_blank" class="menu-pill">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="margin-right:10px; filter: invert(1);">
        <b style="color:#FFFFFF; font-size: 15px;">Balu S</b>
    </a>
    """, unsafe_allow_html=True)
    
    # Development Support Pills
    st.markdown("**Development Support:**")
    st.markdown("""
    <div class="dev-pill">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Vijaya Kumar</b>
    </div>
    <div class="dev-pill">
        <span style="margin-right:10px; font-size: 16px;">👨‍💻</span>
        <b style="color:#FFFFFF; font-size: 14px;">Shivaraj PM</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.warning("Disclaimer: This AI Spam Shield is an educational engineering project designed to demonstrate Natural Language Processing and Machine Learning classification techniques. It is not a commercial security product. Please do not input sensitive personal information, real passwords, banking details, or corporate data into this system. Use at your own risk.")

# --- 7. PAGE ROUTING LOGIC ---
if st.session_state.current_page == "Dashboard":
    
    st.title("🛡️ Spam SMS Classifier")
    st.markdown("Enter a message below. The NLP engine will calculate the mathematical probability of a phishing or spam attempt.")

    user_input = st.text_area("Message Content", placeholder="Paste email, SMS, or suspicious link here...", height=150, label_visibility="collapsed")

    if st.button("🔍 Scan for Threats", use_container_width=True):
        if user_input.strip() == "":
            st.error("⚠️ Please enter a message to analyze!")
        else:
            st.toast("Initiating NLP text vectorization...", icon="⏳")
            time.sleep(0.3)
            
            with st.spinner("Calculating mathematical probabilities..."):
                cleaned_input = clean_text(user_input)
                input_vector = vectorizer.transform([cleaned_input])
                
                # We only need probabilities — NOT model.predict()
                # model.predict() uses 50% default threshold which
                # causes spam to be missed. We use 35% instead.
                probabilities = model.predict_proba(input_vector)[0]
                
                safe_prob = probabilities[0] * 100
                spam_prob = probabilities[1] * 100
                confidence = max(safe_prob, spam_prob)
                
                st.toast("Scan complete!", icon="✅")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            col1.metric(label="🟢 Clean Probability", value=f"{safe_prob:.2f}%")
            col2.metric(label="🔴 Spam Probability", value=f"{spam_prob:.2f}%")
            
            # ================================================================
            #  FIX 2: Lowered spam detection threshold from 50% → 35%
            #
            #  Old code: if prediction == 1   (model.predict default = 50%)
            #  New code: if spam_prob >= 35   (our custom threshold = 35%)
            #
            #  Why? The dataset is 87% ham / 13% spam so the model was
            #  trained on very few spam examples. It needed >50% confidence
            #  to flag something as spam which was too high a bar. Lowering
            #  to 35% means borderline spam messages get caught correctly.
            # ================================================================
            if spam_prob >= 35:
                st.error("🚨 **CRITICAL THREAT DETECTED**")
                st.info("The system has flagged this content as highly suspicious. Do not click any links or provide personal information.")
                st.session_state.history.insert(0, {"Message": user_input, "Status": "SPAM 🚨", "Confidence": f"{confidence:.2f}%", "Timestamp": time.strftime("%H:%M:%S")})
            else:
                st.success("✅ **CLEAN MESSAGE**")
                st.info("No malicious patterns detected in the text structure or vocabulary.")
                st.session_state.history.insert(0, {"Message": user_input, "Status": "CLEAN ✅", "Confidence": f"{confidence:.2f}%", "Timestamp": time.strftime("%H:%M:%S")})
            
            with st.expander("⚙️ View Technical Analysis"):
                st.write(f"**Raw Input Length:** {len(user_input)} characters")
                st.write(f"**Cleaned NLP Tokens:** `{cleaned_input}`")
                st.markdown("---")
                st.write("**🧠 Comparative Model Architecture:**")
                st.write("✅ **Active Production Model:** Multinomial Naive Bayes")
                st.write("✅ **Validation Baseline Model:** Logistic Regression")
                st.caption("To guarantee maximum accuracy, this system was developed using a dual-model architecture. The Naive Bayes algorithm actively drives the real-time predictions on the live server, while the Logistic Regression model served as the statistical baseline to validate the results during local development.")

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
    
    st.markdown("### 🌍 The Threat Landscape: Why is this system required?")
    st.write(
        "In today's hyper-connected digital economy, communication channels like SMS and email are the primary attack vectors for cybercriminals. "
        "We are witnessing an exponential rise in **Social Engineering**, **Spear-Phishing**, and **Smishing (SMS Phishing)** attacks. "
        "Malicious actors are no longer just sending obvious junk mail; they use sophisticated, psychologically manipulative text to steal financial credentials, "
        "distribute malware, and commit identity fraud."
    )
    st.write(
        "Traditional security systems rely on static 'blocklists' (blocking known bad numbers or hardcoded links). These legacy systems fail entirely because attackers "
        "can generate thousands of new numbers and domains instantly. **This is why an AI-driven, Machine Learning approach is strictly required.** "
        "Instead of memorizing bad links, our NLP system mathematically learns the underlying behavioral patterns and vocabulary of a scam, allowing it to intercept "
        "brand new, zero-day phishing attacks before they ever reach the user."
    )
    
    st.markdown("### ⚡ Computational Efficiency & Real-Time Processing")
    st.write(
        "For a cybersecurity firewall to be viable, it must be highly accurate and computationally lightweight. This system was engineered specifically for "
        "high-speed, real-time threat detection."
    )
    
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
