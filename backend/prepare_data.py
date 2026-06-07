import pandas as pd
import re
 
# ── 1. SMS Spam 
sms_df = pd.read_csv(
    "data/spam.csv",
    sep="\t",
    header=None,
    names=["label", "text"],
    on_bad_lines="skip"
)
sms_df["label"] = sms_df["label"].map({"ham": 0, "spam": 1})
sms_df = sms_df[["text", "label"]].dropna()
print(f"SMS dataset loaded: {len(sms_df)} rows")
 
# ── 2. Phishing Emails
phishing_df = pd.read_csv("data/phishing_email.csv")
phishing_df = phishing_df[["text_combined", "label"]]
phishing_df = phishing_df.rename(columns={"text_combined": "text"})
phishing_df = phishing_df.dropna()
print(f"Phishing dataset loaded: {len(phishing_df)} rows")
 
# ── 3. Nigerian Fraud 
fraud_df = pd.read_csv("data/Nigerian_Fraud.csv")
fraud_df["text"] = (
    fraud_df["subject"].fillna("") + " " + fraud_df["body"].fillna("")
)
fraud_df["label"] = 1
fraud_df = fraud_df[["text", "label"]].dropna()
print(f"Fraud dataset loaded: {len(fraud_df)} rows")
 
# ── 4. SpamAssassin
sa_df = pd.read_csv("data/SpamAssasin.csv")
sa_df["text"] = sa_df["subject"].fillna("") + " " + sa_df["body"].fillna("")
sa_df = sa_df[["text", "label"]].dropna()
print(f"SpamAssassin dataset loaded: {len(sa_df)} rows")
 
# ── 5. Extra legit emails 
emails_df = pd.read_csv("data/emails.csv")
# keep only text and label columns
emails_df = emails_df[["text", "label"]].dropna()
print(f"Emails dataset loaded: {len(emails_df)} rows")
 
# ── Combine all 
combined_df = pd.concat([
    sms_df,
    phishing_df,
    fraud_df,
    sa_df,
    emails_df,
], ignore_index=True)
 
# Clean up
combined_df = combined_df.dropna()
combined_df["text"] = combined_df["text"].astype(str)
combined_df["label"] = combined_df["label"].astype(int)
 
print(f"\nFINAL DATASET SIZE: {combined_df.shape}")
print("\nLABEL COUNTS:")
print(combined_df["label"].value_counts())
 
combined_df.to_csv("data/final_dataset.csv", index=False)
print("\nfinal_dataset.csv created successfully!")