import re
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ================================================================
#  SPAM CLASSIFIER — FIXED VERSION
#  Fixes applied:
#   1. clean_text now KEEPS numbers (huge spam signals like 1000, 50%)
#   2. URL detection added during training (synced with app.py)
#   3. MultinomialNB class_prior adjusted (stops favoring ham)
#   4. LogisticRegression uses class_weight='balanced'
# ================================================================

# === STEP 1: LOAD DATASET ===
file_path = r"D:\Users\acer\Documents\VS Code\Spam_Classifier_Project\spam.csv"

df = pd.read_csv(file_path, encoding='latin-1')
df = df[['v1', 'v2']]
df.columns = ['label', 'message']

print("✅ Data loaded successfully!")
print(f"   Total messages: {len(df)}")
print(f"   Ham:  {len(df[df['label']=='ham'])} ({len(df[df['label']=='ham'])/len(df)*100:.1f}%)")
print(f"   Spam: {len(df[df['label']=='spam'])} ({len(df[df['label']=='spam'])/len(df)*100:.1f}%)")
print("\nFirst 5 rows:")
print(df.head())


# === STEP 2: CLEAN TEXT ===
# ----------------------------------------------------------------
# FIX 1: Keep numbers — "WIN 1000", "FREE 50%", "Call 0800" etc.
#         are MASSIVE spam signals. Old code was deleting all of them!
#
# FIX 2: Detect URLs BEFORE cleaning — replace them with
#         'suspiciouslink' token so model LEARNS from links.
#         This is now SYNCED with app.py's clean_text function.
# ----------------------------------------------------------------
def clean_text(text):
    text = str(text).lower()

    # Detect and tag URLs as a strong spam signal token
    text = re.sub(r'https?://\S+', ' suspiciouslink ', text)
    text = re.sub(r'www\.\S+', ' suspiciouslink ', text)
    text = re.sub(r'\b[a-zA-Z0-9.-]+\.(com|org|net|info|biz|co)\b', ' suspiciouslink ', text)

    # FIX: Keep letters AND numbers, remove only symbols/punctuation
    # OLD (broken): r'[^a-z\s]'   <- was deleting numbers!
    # NEW (fixed):  r'[^a-z0-9\s]' <- numbers stay!
    text = re.sub(r'[^a-z0-9\s]', '', text)

    return text

df['clean_message'] = df['message'].apply(clean_text)

print("\n✅ Text cleaned! Before vs After comparison:")
print(df[['message', 'clean_message']].head(10))


# === STEP 3: TF-IDF VECTORIZATION ===
df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})

# max_features=5000 keeps only the top 5000 most useful words
tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
X = tfidf.fit_transform(df['clean_message'])
y = df['label_num']

print("\n✅ TF-IDF Vectorization complete!")
print(f"   Shape of X (Messages x Words): {X.shape}")
print(f"   Shape of y (Labels):           {y.shape}")


# === STEP 4: TRAIN/TEST SPLIT ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\n✅ Data split complete!")
print(f"   Training messages: {X_train.shape[0]}")
print(f"   Testing messages:  {X_test.shape[0]}")


# === STEP 5: TRAIN MODELS ===
# ----------------------------------------------------------------
# FIX 3: class_prior=[0.45, 0.55]
#
# By default, Naive Bayes uses the training data distribution as
# class probabilities. Since the dataset is ~87% ham / ~13% spam,
# the model was heavily biased toward always predicting "ham".
#
# Setting class_prior=[0.45, 0.55] (ham=45%, spam=55%) tells the
# model to take spam much more seriously during prediction.
#
# Think of it like this:
# Default prior -> "Assume it's probably ham unless VERY sure"
# Fixed prior   -> "Be more suspicious, flag borderline cases as spam"
# ----------------------------------------------------------------
nb_model = MultinomialNB(class_prior=[0.45, 0.55])

# class_weight='balanced' auto-adjusts for the same imbalance issue
# max_iter=1000 prevents convergence warnings on larger datasets
lr_model = LogisticRegression(class_weight='balanced', max_iter=1000)

print("\n🚀 Training Naive Bayes (with fixed class prior)...")
nb_model.fit(X_train, y_train)
print("   Done!")

print("🚀 Training Logistic Regression (with balanced class weight)...")
lr_model.fit(X_train, y_train)
print("   Done!")


# === STEP 6: PREDICT & EVALUATE ===
nb_predictions  = nb_model.predict(X_test)
lr_predictions  = lr_model.predict(X_test)

print("\n" + "="*55)
print("         FINAL ACCURACY RESULTS")
print("="*55)
print(f"  Naive Bayes Accuracy:         {accuracy_score(y_test, nb_predictions)*100:.2f}%")
print(f"  Logistic Regression Accuracy: {accuracy_score(y_test, lr_predictions)*100:.2f}%")


# --- Naive Bayes Full Report ---
print("\n" + "-"*55)
print("  NAIVE BAYES — Full Performance Report")
print("-"*55)
print("\nConfusion Matrix:")
print("(Rows = Actual, Columns = Predicted)")
print("         Ham   Spam")
cm_nb = confusion_matrix(y_test, nb_predictions)
print(f"  Ham    {cm_nb[0][0]:4d}  {cm_nb[0][1]:4d}")
print(f"  Spam   {cm_nb[1][0]:4d}  {cm_nb[1][1]:4d}")
print("\nClassification Report:")
print(classification_report(y_test, nb_predictions, target_names=['Ham', 'Spam']))

# --- Logistic Regression Full Report ---
print("-"*55)
print("  LOGISTIC REGRESSION — Full Performance Report")
print("-"*55)
print("\nConfusion Matrix:")
print("         Ham   Spam")
cm_lr = confusion_matrix(y_test, lr_predictions)
print(f"  Ham    {cm_lr[0][0]:4d}  {cm_lr[0][1]:4d}")
print(f"  Spam   {cm_lr[1][0]:4d}  {cm_lr[1][1]:4d}")
print("\nClassification Report:")
print(classification_report(y_test, lr_predictions, target_names=['Ham', 'Spam']))


# === STEP 7: SAVE MODELS ===
# Save the Naive Bayes model (used by app.py)
with open('spam_model.pkl', 'wb') as model_file:
    pickle.dump(nb_model, model_file)

# Save the TF-IDF Vectorizer (MUST be saved — app.py needs this!)
with open('vectorizer.pkl', 'wb') as vec_file:
    pickle.dump(tfidf, vec_file)

print("\n" + "="*55)
print("  ✅ EXPORT COMPLETE!")
print("  spam_model.pkl  — Naive Bayes model saved")
print("  vectorizer.pkl  — TF-IDF vectorizer saved")
print("  Both files ready for app.py!")
print("="*55)
