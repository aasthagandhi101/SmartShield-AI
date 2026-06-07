# 🛡️ SmartShield AI — Spam & Phishing Detection

> AI-powered threat detection for emails, SMS, and messages. Works as a Chrome extension and a web app.

---

## 👩‍💻 What I Built

I trained an ML model on 97,000+ spam and phishing messages, wrapped it in a FastAPI REST API, and deployed it as both a Chrome Extension and a Streamlit web app. When the model kept flagging legitimate Indian emails (Nykaa orders, HDFC OTPs, Instagram codes) as spam, I fixed it by adding real-world Indian email samples to the training data and building a rule layer that adjusts predictions based on trusted sender domains and transactional signals. I also built a feedback pipeline so wrong predictions can be added back to the dataset and the model retrained — making it improve over time.

---

## 🌐 Live Demo

- **Web App:** [smartshield-ai.streamlit.app](https://smartshield-ai.streamlit.app)
- **API:** [smartshield-ai-1.onrender.com](https://smartshield-ai-1.onrender.com)

---

## 📌 What It Does

SmartShield AI detects spam, phishing, and scam content in real time across:

- 📧 **Gmail** — analyzes the open email instantly
- 💬 **WhatsApp Web** — scans chat messages
- 🌐 **Any webpage** — generic text analysis
- 📝 **Web App** — paste any message and analyze it

It uses a **two-layer detection system**:
1. A trained ML model (TF-IDF + Logistic Regression) trained on 97,000+ messages
2. A **smart rule-based trust engine** — trusted sender domains + transactional signal detection

---

## 🚀 Features

- ✅ Detects phishing emails, lottery scams, Nigerian fraud, crypto scams
- ✅ Zero false positives on OTPs, order confirmations, bank alerts
- ✅ Trusted sender domain recognition (Amazon, Instagram, HDFC, Nykaa, etc.)
- ✅ Transactional email signal detection (order IDs, UPI refs, delivery status)
- ✅ Risk levels: HIGH / MEDIUM / LOW with confidence score
- ✅ Works on Gmail, Outlook, WhatsApp Web
- ✅ Streamlit web app for manual message analysis
- ✅ Continuous learning via feedback pipeline

---

## 🧠 How It Works

```
User opens email / message
        ↓
Chrome Extension extracts text (content.js)
        ↓
FastAPI backend receives text
        ↓
Step 1: Clean text — strip HTML, normalize URLs, emails, numbers
        ↓
Step 2: ML Model scores spam probability (0–100%)
        ↓
Step 3: Rule-based adjustments
  → Trusted sender? (Instagram, HDFC, Nykaa...) → reduce spam score
  → Transactional signals? (OTP, order ID, UPI ref...) → reduce spam score
        ↓
Returns: prediction, confidence %, risk level
```

---

## 📊 Dataset

Trained on **97,000+ messages** from multiple sources:

| Dataset | Size | Type |
|---|---|---|
| SMS Spam Collection | 5,572 | SMS spam/ham |
| Nigerian Fraud Emails | 3,332 | Email fraud |
| SpamAssassin | 5,809 | Email spam/legit |
| Phishing Email Dataset | 82,486 | Phishing/legit |
| Real-world legit samples | 650+ | OTPs, orders, bank alerts, WhatsApp |

**Model Accuracy: 98%** on test set (20% holdout)

---

## 🗂️ Project Structure

```
SmartShield-AI/
│
├── backend/
│   ├── api.py              
│   ├── train.py            
│   ├── predict.py          
│   ├── app.py              
│   ├── prepare_data.py     
│   ├── feedback.py         
│   └── models/
│       ├── spam_model.pkl  
│       └── vectorizer.pkl  
│
├── extension/
│   ├── manifest.json       
│   ├── content.js          
│   ├── popup.html          
│   └── popup.js            
│
├── data/
│   ├── spam.csv
│   ├── Nigerian_Fraud.csv
│   ├── SpamAssasin.csv
│   ├── phishing_email.csv
│   └── final_dataset.csv
│
├── requirements.txt
├── CONTRIBUTING.md
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/aasthagandhi101/SmartShield-AI.git
cd SmartShield-AI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the model
```bash
cd backend
python prepare_data.py
python train.py
```

### 4. Start the FastAPI server
```bash
cd backend
uvicorn api:app --reload
```

### 5. Run the Streamlit web app
```bash
cd backend
streamlit run app.py
```

---

## 🔌 Chrome Extension Setup

1. Open Chrome → go to `chrome://extensions`
2. Enable **Developer Mode**
3. Click **Load unpacked** → select the `extension/` folder
4. Open Gmail and click the SmartShield AI icon

---

## 🧪 API Usage

```bash
curl -X POST https://smartshield-ai-1.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won a lottery. Send bank details to claim prize."}'
```

**Response:**
```json
{
  "prediction": 1,
  "confidence": 96.3,
  "risk": "HIGH",
  "trusted_sender": false,
  "transactional_signals": 0,
  "sender_domain": ""
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ML Model | scikit-learn (TF-IDF + Logistic Regression) |
| Backend API | FastAPI + Uvicorn |
| Web App | Streamlit |
| Browser Extension | Chrome Extension Manifest V3 |
| Language | Python 3.10+, JavaScript |

---

## 📈 Detection Examples

| Message | Result | Confidence |
|---|---|---|
| "Your Nykaa order #NYK-357 has been confirmed" | ✅ LEGIT | 10% spam |
| "HDFC OTP: 739201. Valid 5 mins. Do not share." | ✅ LEGIT | 9% spam |
| "Someone tried to log into your Instagram account" | ✅ LEGIT | 25% spam |
| "Hey are you coming for dinner tonight at 8pm?" | ✅ LEGIT | 5% spam |
| "URGENT: You won $1M lottery. Send bank details." | 🚨 SPAM | 97% spam |
| "Your PayPal account suspended. Verify now." | 🚨 SPAM | 99% spam |
| "Double your bitcoin in 24hrs. Send crypto now." | 🚨 SPAM | 95% spam |
| "BUSINESS ASSISTANCE — transfer $25M to your account" | 🚨 SPAM | 96% spam |

---

## 🤝 Contributing

The model improves with more data! Found a spam message that wasn't detected? Got a legitimate email that was wrongly flagged? See [CONTRIBUTING.md](CONTRIBUTING.md) to add samples and help improve accuracy.