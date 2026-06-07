import os
"""
api.py — SmartShield AI
========================
FastAPI backend that serves the spam/phishing detection model.

Two-layer detection:
  Layer 1: ML model (TF-IDF + Logistic Regression) gives a raw spam probability
  Layer 2: Rule-based adjustments for trusted senders and transactional signals
           to eliminate false positives on legitimate Indian emails

Run with:
  uvicorn api:app --reload
"""

import pickle
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="SmartShield AI",
    description="Spam and phishing detection API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "models", "spam_model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "models", "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

TRUSTED_DOMAINS = [
    "gmail.com", "google.com", "googlemail.com",
    "instagram.com", "facebook.com", "meta.com",
    "amazon.com", "amazon.in", "flipkart.com",
    "nykaa.com", "zomato.com", "swiggy.com",
    "paytm.com", "phonepe.com", "razorpay.com",
    "linkedin.com", "twitter.com", "x.com", "microsoft.com",
    "apple.com", "netflix.com", "spotify.com",
    "myntra.com", "ajio.com", "meesho.com",
    "hdfcbank.com", "icicibank.com", "sbi.co.in",
    "axisbank.com", "kotak.com", "yesbank.in",
    "irctc.co.in", "makemytrip.com", "goibibo.com",
    "ola.com", "uber.com", "rapido.bike",
    "airtel.in", "jio.com", "vi.in", "bsnl.co.in",
    "bookmyshow.com", "hotstar.com",
    "indigo.in", "airindia.in", "spicejet.com",
    "zepto.com", "blinkit.com",
    "youtube.com", "whatsapp.com", "telegram.org",
]

TRANSACTIONAL_PATTERNS = [
    r"order\s*(#|number|id|no\.?)\s*[\w\-]+",       # order ID
    r"invoice\s*(#|number|id)?",                      # invoice
    r"tracking\s*(number|id)?",                       # tracking number
    r"booking\s*(id|number|reference|confirmed)",     # booking confirmed
    r"your\s+order\s+has\s+been",                     # order status
    r"has\s+been\s+(shipped|delivered|dispatched|confirmed|placed)",
    r"estimated\s+delivery",                          # delivery date
    r"out\s+for\s+delivery",                          # delivery update
    r"otp\s*(is|:)?\s*\d{4,8}",                      # OTP message
    r"verification\s+code\s*(is|:)?\s*\d{4,8}",      # verification code
    r"your\s+(security\s+)?code\s+is\s+\d{4,8}",     # security code
    r"two.factor|2fa",                                # 2FA
    r"order\s+total",                                 # order total amount
    r"amount\s+(debited|credited|paid|received)",     # bank transaction
    r"rs\.?\s*\d+\s*(debited|credited|paid|received|deducted)",
    r"upi\s+(ref|transaction|id)",                    # UPI reference
    r"unsubscribe",                                   # legit marketing emails have this
    r"privacy\s+policy",                              # legit emails link to privacy policy
    r"refund\s+will\s+be",                            # refund notice
    r"payment\s+(successful|received|confirmed)",     # payment confirmation
    r"flight\s+(confirmed|booking|pnr)",              # flight booking
    r"pnr\s*:\s*[a-z0-9]+",                          # PNR number
    r"recharge\s+of\s+rs",                            # mobile recharge
    r"validity\s*:\s*\d+\s*days",                     # recharge validity
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

def count_spam_keywords(text: str) -> int:
    text_lower = text.lower()
    return sum(1 for kw in SPAM_KEYWORDS if kw in text_lower)

def clean_text(text: str) -> str:
    """
    Normalize text before sending to the ML model.

    IMPORTANT: This function must be identical in both train.py and api.py.
    Using different preprocessing at training vs serving time causes
    train-serve skew — a common production ML bug where the model performs
    well on test data but poorly in real use.

    Steps:
    - Strip HTML tags (emails often contain HTML)
    - Normalize URLs to the token 'URL' (the actual URL is not meaningful)
    - Normalize email addresses to 'EMAIL'
    - Normalize long numbers to 'NUMBER' (order IDs, phone numbers etc.)
    - Collapse whitespace
    """
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)               # remove HTML tags
    text = re.sub(r'http\S+|www\.\S+', ' URL ', text)  # normalize URLs
    text = re.sub(r'\S+@\S+\.\S+', ' EMAIL ', text)    # normalize emails
    text = re.sub(r'\b\d{4,}\b', ' NUMBER ', text)     # normalize numbers
    text = re.sub(r'\s+', ' ', text)                   # collapse whitespace
    return text.strip().lower()

def extract_sender_domain(text: str) -> str | None:
    """
    Try to extract the sender's email domain from the message text.
    Looks for 'From: name@domain.com' pattern first,
    then falls back to any email address in the text.
    """
    match = re.search(r'[Ff]rom:\s*.*?@([\w.\-]+)', text)
    if match:
        return match.group(1).lower()

    match2 = re.search(r'@([\w.\-]+\.[a-z]{2,})', text)
    if match2:
        return match2.group(1).lower()

    return None

def is_trusted_sender(domain: str | None) -> bool:
    """
    Check if the sender domain is a known legitimate brand.
    Uses endswith() to handle subdomains (e.g. security@mail.instagram.com).
    """
    if not domain:
        return False
    return any(domain == d or domain.endswith('.' + d) for d in TRUSTED_DOMAINS)

def count_transactional_signals(text: str) -> int:
    """
    Count how many transactional signal patterns are found in the text.
    More signals = more likely to be a legitimate email.
    Used to reduce false positives on order confirmations, OTPs, bank alerts.
    """
    text_lower = text.lower()
    return sum(1 for p in TRANSACTIONAL_PATTERNS if re.search(p, text_lower))

class Message(BaseModel):
    """Request body schema for the /predict endpoint."""
    text: str

@app.get("/")
def home():
    """Health check endpoint."""
    return {"message": "SmartShield AI API Running"}

@app.post("/predict")
def predict(message: Message):
    """
    Main prediction endpoint.

    Accepts a message (email body, SMS, WhatsApp text etc.)
    and returns spam prediction with confidence score.

    Flow:
    1. Clean the text (strip HTML, normalize URLs/emails/numbers)
    2. Vectorize with TF-IDF
    3. Get raw spam probability from ML model
    4. Apply rule-based adjustments:
       - Trusted sender domain → reduce probability by 55%
       - Transactional signals → reduce further based on signal count
    5. Apply threshold (75%) to get final prediction
    """
    raw_text = message.text
    cleaned = clean_text(raw_text)

    vec = vectorizer.transform([cleaned])
    raw_prob = model.predict_proba(vec)[0][1]  # probability of spam (class 1)
    prob = raw_prob

    sender_domain = extract_sender_domain(raw_text)
    trusted = is_trusted_sender(sender_domain)
    transactional = count_transactional_signals(raw_text)

    if trusted:
        prob = prob * 0.45  # reduce spam probability by 55%

    if transactional >= 3:
        prob = prob * 0.40
    elif transactional >= 2:
        prob = prob * 0.55
    elif transactional == 1:
        prob = prob * 0.75

    confidence = round(prob * 100, 2)

    prediction = 1 if prob >= 0.75 else 0

    if confidence >= 75:
        risk = "HIGH"
    elif confidence >= 45:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    print(f"[predict] raw={raw_prob:.3f} adj={prob:.3f} "
          f"pred={prediction} conf={confidence}% risk={risk} "
          f"trusted={trusted} transactional={transactional}")

    return {
        "prediction": prediction,          # 1 = spam, 0 = legit
        "confidence": confidence,          # adjusted spam probability %
        "risk": risk,                      # HIGH / MEDIUM / LOW
        "trusted_sender": trusted,         # was sender domain recognised?
        "transactional_signals": transactional,  # how many legit signals found
        "sender_domain": sender_domain or "",    # extracted domain
    }