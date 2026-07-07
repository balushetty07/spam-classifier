# 🛡️ Spam Email & SMS Classifier
 
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-TF--IDF-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
 
> An AI-powered web app that detects spam SMS/email in real-time, with a dual-engine ML dashboard, SQL-backed analytics, and a glassmorphism dark UI. Built as part of the AI/ML open elective project at **SJCE, Mysore (2024 Batch)**.
 
---
 
## 🌐 Live Demo
👉 **[Try it live here](https://spam-classifier-balushetty07.streamlit.app/)**
 
---
 
## 📌 What This Project Does
 
Spam filters based on keyword blocklists fail because attackers keep changing wording. This project instead uses ML to **learn the pattern** of spam from thousands of real messages.
 
**Key features:**
- 🧠 **Dual engine** — switch between Naive Bayes and Logistic Regression at runtime
- 📊 Instant spam probability score (not just yes/no)
- 🔗 Automatic suspicious-link detection
- 🗄️ Every scan logged to a persistent **SQLite** database (`history.db`)
- 📈 Built-in **Analytics Dashboard** — total scans, threats blocked, clean passed, bar chart
- 🚩 Admin tool to flag misclassified rows (for future retraining)
- 🕒 Live session history on the main page
- 🎨 Fully responsive glassmorphism dark-mode UI
---
 
## 🧠 How It Works
 
### 1. Data Collection
- Dataset: [SMS Spam Collection Dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) (UCI/Kaggle) — 5,574 messages, ~87% ham / ~13% spam
### 2. Text Preprocessing
```python
def clean_text(text):
    text = text.lower()
    text = re.sub(r'https?://\S+', ' suspiciouslink ', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)  # numbers kept — strong spam signal
    return text
```
- Lowercases text, tags URLs as `suspiciouslink`, strips punctuation, **keeps digits** (amounts/codes are strong spam signals)
### 3. TF-IDF Vectorization
Converts cleaned text to numeric features — rare, spam-heavy words (e.g. "free", "win", "prize") get high weights.
 
### 4. Model Training — Two Engines, One App
 
| Model | Accuracy | Role |
|---|---|---|
| **Multinomial Naive Bayes** ✅ | ~97% | Default production engine — fast & lightweight |
| **Logistic Regression** | ~96% | Selectable alternate engine, `class_weight='balanced'` |
 
**Key fix:** dataset is 87% ham, so Naive Bayes was biased toward "safe" by default. Fixed with `class_prior=[0.45, 0.55]`.
 
### 5. Decision Threshold
Default 50% threshold missed borderline spam → lowered to **35%** `spam_prob` cutoff in the app.
 
### 6. Streamlit Dashboard (3 pages)
- **Classifier** — paste a message, pick an engine, get an instant verdict + probability, auto-saved to SQLite
- **Database** — analytics on all historical scans (totals, chart, raw log, misclassification flagging)
- **About** — project rationale, architecture, and benchmark write-up
---
 
## 🗂️ Project Structure
```
spam-classifier/
│
├── app.py               # Streamlit app — UI, dual-engine prediction, SQLite logging, analytics
├── classifier.py        # ML pipeline — data loading, training, model export
├── requirements.txt     # Python dependencies
├── spam_model.pkl       # Trained Naive Bayes model
├── lr_model.pkl         # Trained Logistic Regression model
├── vectorizer.pkl       # Fitted TF-IDF vectorizer
├── history.db           # SQLite database (auto-created on first run)
└── .gitignore
```
> `spam.csv` is not included (too large) — download from [Kaggle](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset) to retrain.
 
---
 
## ⚙️ Tech Stack
| Tool | Purpose |
|---|---|
| Python 3.8+ | Core language |
| Pandas | Data loading/manipulation |
| Scikit-learn | TF-IDF, Naive Bayes, Logistic Regression, metrics |
| Streamlit | Web app framework & multi-page dashboard |
| SQLite3 | Persistent scan history & analytics |
| Pickle | Model serialization |
| Regex (re) | Text cleaning & URL detection |
 
---
 
## 🚀 Run Locally
 
```bash
git clone https://github.com/balushetty07/spam-classifier.git
cd spam-classifier
pip install -r requirements.txt
```
 
Optional — retrain from scratch (needs `spam.csv` from Kaggle):
```bash
python classifier.py
```
 
Run the app:
```bash
streamlit run app.py
```
Open `http://localhost:8501` 🎉
 
---
 
## 💡 Key Problems Solved
| Problem | Cause | Fix |
|---|---|---|
| Spam flagged as safe | Numbers deleted during cleaning | Regex changed to `[^a-z0-9\s]` |
| Model biased toward "safe" | 87% ham in dataset | `class_prior=[0.45, 0.55]` |
| Borderline spam missed | 50% threshold too high | Lowered to 35% |
| URLs ignored | Not tagged during training | `suspiciouslink` token |
| No visibility into past scans | No persistence layer | Added SQLite logging + analytics dashboard |
 
---
 
## 🔮 Future Scope
- Deep learning models (LSTM, BERT)
- Multilingual spam detection
- Real phishing-URL verification (not just detection)
- Live email/SMS API integration
- Lightweight model variant for IoT/embedded devices
---
 
## 👨‍💻 Team
| Name | Role |
|---|---|
| **Balu S** | Main Developer — ML pipeline, dashboard, deployment |
| **Vijaya Kumar** | Development Support |
| **Shivaraj PM** | Development Support |
 
**Institution:** SJCE, Mysore | **Dept:** ECE | **Semester:** 4th, 2024 Batch | **Subject:** AI/ML Open Elective
 
---
 
## 📚 References
1. Almeida et al., *Contributions to the Study of SMS Spam Filtering*, ACM 2011
2. Joachims T., *Text Categorization with Support Vector Machines*, ECML 1998
3. Pedregosa et al., *Scikit-learn: Machine Learning in Python*, JMLR 2011
4. [SMS Spam Collection Dataset — UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/sms+spam+collection)
5. Jurafsky & Martin, *Speech and Language Processing*, Pearson 2021
---
<p align="center">Made with ❤️ by Balu S | SJCE Mysore</p>