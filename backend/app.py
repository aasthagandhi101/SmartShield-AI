import os
import streamlit as st
import pickle
import re

TRUSTED_DOMAINS = [
    "gmail.com", "google.com", "instagram.com", "facebook.com",
    "amazon.com", "amazon.in", "flipkart.com", "nykaa.com",
    "zomato.com", "swiggy.com", "paytm.com", "phonepe.com",
    "razorpay.com", "linkedin.com", "twitter.com", "microsoft.com",
    "apple.com", "myntra.com", "hdfcbank.com", "icicibank.com",
    "sbi.co.in", "axisbank.com", "irctc.co.in", "makemytrip.com",
    "airtel.in", "jio.com", "bookmyshow.com", "uber.com", "ola.com",
]

TRANSACTIONAL_PATTERNS = [
    r"order\s*(number|id|no\.?)\s*[\w\-]+",
    r"has\s+been\s+(shipped|delivered|dispatched|confirmed|placed)",
    r"otp\s*(is|:)?\s*\d{4,8}",
    r"verification\s+code\s*(is|:)?\s*\d{4,8}",
    r"your\s+(security\s+)?code\s+is\s+\d{4,8}",
    r"amount\s+(debited|credited|paid|received)",
    r"rs\.?\s*\d+\s*(debited|credited|paid|received|deducted)",
    r"upi\s+(ref|transaction|id)",
    r"unsubscribe",
    r"refund\s+will\s+be",
    r"payment\s+(successful|received|confirmed)",
    r"pnr\s*:\s*[a-z0-9]+",
    r"recharge\s+of\s+rs",
    r"out\s+for\s+delivery",
    r"estimated\s+delivery",
]

SPAM_KEYWORDS = [
    "lottery", "prize", "winner", "won", "claim",
    "free", "urgent", "congratulations", "selected",
    "bitcoin", "crypto", "investment", "double",
    "nigerian", "transfer", "million", "dollars",
    "verify account", "suspended", "blocked",
    "bank details", "account number", "send money",
    "wire transfer", "western union", "processing fee",
    "limited offer", "act now", "expires today",
]

def count_spam_keywords(text):
    text_lower = text.lower()
    return sum(1 for kw in SPAM_KEYWORDS if kw in text_lower)

def clean_text(text):
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'http\S+|www\.\S+', ' URL ', text)
    text = re.sub(r'\S+@\S+\.\S+', ' EMAIL ', text)
    text = re.sub(r'\b\d{4,}\b', ' NUMBER ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

def extract_sender_domain(text):
    match = re.search(r'[Ff]rom:\s*.*?@([\w.\-]+)', text)
    if match:
        return match.group(1).lower()
    match2 = re.search(r'@([\w.\-]+\.[a-z]{2,})', text)
    if match2:
        return match2.group(1).lower()
    return None

def is_trusted(domain):
    if not domain:
        return False
    return any(domain == d or domain.endswith('.' + d) for d in TRUSTED_DOMAINS)

def count_transactional(text):
    tl = text.lower()
    return sum(1 for p in TRANSACTIONAL_PATTERNS if re.search(p, tl))

@st.cache_resource
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_model():
    with open(os.path.join(BASE_DIR, "models", "spam_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(BASE_DIR, "models", "vectorizer.pkl"), "rb") as f:
        vec = pickle.load(f)
    return model, vec

model, vectorizer = load_model()

st.set_page_config(page_title="SmartShield AI", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stSidebar"] { background-color: #0d0d1a; border-right: 1px solid #2d1b4e; }
    .stTextArea textarea { background-color: #111111 !important; color: white !important; border: 1px solid #7c3aed !important; border-radius: 10px !important; }
    .stButton > button { background: linear-gradient(90deg, #7c3aed, #db2777) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: bold !important; width: 100% !important; padding: 12px !important; }
    .stButton > button:hover { opacity: 0.85 !important; }
    [data-testid="stMetric"] { background-color: #111111; border: 1px solid #2d1b4e; border-radius: 10px; padding: 10px; }
    h1 { background: linear-gradient(90deg, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    hr { border-color: #2d1b4e !important; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🛡️ SmartShield AI")
st.sidebar.info("""
AI-Powered Phishing & Scam Detection

Datasets:
• SMS Spam
• Phishing Emails
• Fraud Emails
• SpamAssassin
• Real-world Legit Emails

Messages Trained:
97,000+
""")
st.sidebar.markdown("---")
st.sidebar.caption("Trained on 97,000+ messages across 5 datasets")

st.title("🛡️ SmartShield AI")
st.subheader("Spam, Phishing & Scam Detection")

message = st.text_area(
    "Paste any message, email, or SMS:",
    height=160,
    placeholder="Paste a suspicious email, WhatsApp message, or SMS here..."
)

if st.button("🔍 Analyze Threat"):
    if not message.strip():
        st.warning("Please enter a message.")
    else:
        raw = message
        cleaned = clean_text(raw)

        vec = vectorizer.transform([cleaned])
        raw_prob = model.predict_proba(vec)[0][1]
        prob = raw_prob

        sender_domain = extract_sender_domain(raw)
        trusted = is_trusted(sender_domain)
        transactional = count_transactional(raw)

        if trusted:
            prob = prob * 0.45
        if transactional >= 3:
            prob = prob * 0.40
        elif transactional >= 2:
            prob = prob * 0.55
        elif transactional == 1:
            prob = prob * 0.75

        spam_kw_count = count_spam_keywords(raw)
        if spam_kw_count >= 2:
            prob = max(prob, 0.80)
        elif spam_kw_count == 1:
            prob = max(prob, 0.60)

        confidence = round(prob * 100, 2)
        prediction = 1 if prob >= 0.75 else 0

        if confidence >= 75:
            risk = "HIGH"
        elif confidence >= 45:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        st.markdown("---")

        if prediction == 1:
            st.error("🚨 SPAM / PHISHING DETECTED")
        else:
            st.success("✅ MESSAGE APPEARS SAFE")

        m1, m2, m3 = st.columns(3)
        m1.metric("Spam Confidence", f"{confidence}%")
        m2.metric("Risk Level", risk)
        m3.metric("Raw ML Score", f"{round(raw_prob*100, 1)}%")

        st.progress(int(min(confidence, 100)))

        st.markdown("#### 🔍 Signal Breakdown")
        s1, s2 = st.columns(2)
        s1.info(f"**Trusted Sender:** {'✅ Yes — ' + sender_domain if trusted else '❌ No'}")
        s2.info(f"**Transactional Signals:** {'✅ ' if transactional > 0 else '❌ '}{transactional} found")

        st.markdown("#### 💡 Recommendation")
        if prediction == 1:
            st.warning("""
- ⛔ Do **not** click any links
- ⛔ Do **not** share passwords, OTPs, or bank details
- ✅ Verify the sender by contacting the organization directly
- ✅ Report and delete the message
            """)
        else:
            st.success("""
- ✅ Message appears safe
- ✅ Never share OTPs or passwords even with trusted contacts
            """)

        with st.expander("🛠️ Debug Info"):
            st.json({
                "raw_ml_probability": round(raw_prob, 4),
                "adjusted_probability": round(prob, 4),
                "confidence_percent": confidence,
                "prediction": prediction,
                "risk": risk,
                "trusted_sender": trusted,
                "sender_domain": sender_domain or "not detected",
                "transactional_signals": transactional,
            })