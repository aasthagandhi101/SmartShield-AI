import pickle

suspicious_keywords = [
    "urgent",
    "verify",
    "bank",
    "account",
    "password",
    "login",
    "click",
    "winner",
    "lottery",
    "prize",
    "free",
    "claim",
    "limited",
    "offer",
    "crypto",
    "bitcoin"
]


def analyze_threat(message):

    message = message.lower()

    detected = []

    for word in suspicious_keywords:
        if word in message:
            detected.append(word)

    return detected


def get_threat_level(confidence):

    if confidence >= 85:
        return "HIGH"

    elif confidence >= 60:
        return "MEDIUM"

    else:
        return "LOW"


# Load trained model
with open("models/spam_model.pkl", "rb") as file:
    model = pickle.load(file)

# Load vectorizer
with open("models/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)


# User input
message = input("Enter a message: ")

# Convert text into vectors
message_vector = vectorizer.transform([message])

# Predict spam/safe
prediction = model.predict(message_vector)[0]

# Get probabilities
probabilities = model.predict_proba(message_vector)[0]

# Spam confidence
spam_probability = probabilities[1] * 100

# Threat analysis
threats = analyze_threat(message)

# Threat level
threat_level = get_threat_level(spam_probability)


# Final Output
print("\n==============================")
print("      THREAT ANALYSIS")
print("==============================\n")

# Old prediction logic
if prediction == 1:
    print("Spam detected!")
else:
    print("Not spam.")

# Confidence
print(f"Spam confidence: {spam_probability:.2f}%")

# New threat intelligence
print(f"Threat Level: {threat_level}")

# Threat indicators
if threats:

    print("\nThreat Indicators:")

    for threat in threats:
        print(f"- {threat}")

else:
    print("\nNo suspicious indicators detected.")