import pickle
import re
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# models/ folder needs to exist to save the output files
os.makedirs("models", exist_ok=True)


def clean_text(text):

    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)               # strip HTML tags
    text = re.sub(r'http\S+|www\.\S+', ' URL ', text)  # normalize URLs
    text = re.sub(r'\S+@\S+\.\S+', ' EMAIL ', text)    # normalize emails
    text = re.sub(r'\b\d{4,}\b', ' NUMBER ', text)     # normalize numbers
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


print("=" * 50)
print("  SmartShield AI — Model Training")
print("=" * 50)

# ── Load final dataset ────────────────────────────────────────────
print("\nLoading final_dataset.csv...")
df = pd.read_csv("../data/final_dataset.csv")
df = df.dropna()
df["text"] = df["text"].apply(clean_text)
df["label"] = df["label"].astype(int)

print(f"Dataset: {len(df)} rows")
print(f"  Spam  (1): {df['label'].sum()}")
print(f"  Legit (0): {len(df) - df['label'].sum()}")

# ── Train/test split ──────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]   
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")

# ── TF-IDF Vectorizer ─────────────────────────────────────────────
print("\nVectorizing with TF-IDF...")
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=20000,
    ngram_range=(1, 3),    # captures single words AND phrases up to 3 words
    sublinear_tf=True,     # dampens effect of very frequent terms
    min_df=2,              # ignore terms that appear in fewer than 2 documents
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ── Train model ───────────────────────────────────────────────────
print("Training Logistic Regression model...")
model = LogisticRegression(
    class_weight="balanced",  # handles imbalanced spam/legit ratio
    max_iter=1000,
    C=1.0
)
model.fit(X_train_vec, y_train)

# ── Evaluate ──────────────────────────────────────────────────────
preds = model.predict(X_test_vec)
print("\n=== MODEL PERFORMANCE ===")
print(classification_report(y_test, preds, target_names=["Legit", "Spam"]))

# ── Save ──────────────────────────────────────────────────────────
with open("models/spam_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("Model saved:      models/spam_model.pkl")
print("Vectorizer saved: models/vectorizer.pkl")
print("\nTraining complete!")