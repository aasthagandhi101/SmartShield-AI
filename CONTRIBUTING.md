# 🤝 Contributing to SmartShield AI

The model improves with more data. If you find a message that was wrongly detected — either spam that was missed or a legitimate message flagged as spam — you can help fix it.

---

## What kind of data helps

- New spam/phishing types (fake job offers, fake KYC alerts, fake delivery failed)
- Spam in Hindi, Marathi, Tamil or other Indian languages
- Legitimate emails that got wrongly flagged as spam
- WhatsApp forwards that are scams

---

## How to contribute

**Option A — On your own machine:**
```bash
cd backend
python feedback.py --retrain
```
Paste the message, enter `1` for spam or `0` for legit. Model retrains automatically.

**Option B — Bulk add from a CSV:**

Create a CSV with two columns `text` and `label`:
```csv
text,label
"Your SBI KYC is expired. Update within 24 hours or account will be blocked.",1
"Your Flipkart order has been shipped. Expected delivery tomorrow.",0
```
Then run:
```bash
python feedback.py --bulk ../data/my_samples.csv --retrain
```

**Option C — GitHub Pull Request:**

Fork the repo, add your samples CSV to `data/`, run `feedback.py --bulk`, commit the updated `final_dataset.csv` and `.pkl` files, and open a Pull Request.

---

## Rules

- Real messages only — don't make up examples
- Label accurately — if unsure, don't add it
- Remove personal info before adding (names, phone numbers, account numbers)
- One message per row

---

Every sample you add makes SmartShield AI more accurate for everyone. Thank you!