"""
  python feedback.py --retrain
  Then enter the message, then 0 (legit) or 1 (spam)
"""

import argparse
import subprocess
import pandas as pd
import os

DATASET_PATH = "data/final_dataset.csv"


def add_sample(text: str, label: int):
    """Add a single labelled sample to the dataset."""
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}")
        return False

    df = pd.read_csv(DATASET_PATH)
    new_row = pd.DataFrame({"text": [text], "label": [label]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATASET_PATH, index=False)

    label_name = "SPAM" if label == 1 else "LEGIT"
    print(f"✅ Added as {label_name}. Dataset now has {len(df)} samples.")
    return True


def add_bulk_from_file(filepath: str):
    """
    Add multiple samples from a CSV file.
    CSV must have columns: text, label (0 or 1)
    """
    new_data = pd.read_csv(filepath)
    assert "text" in new_data.columns and "label" in new_data.columns, \
        "CSV must have 'text' and 'label' columns"

    df = pd.read_csv(DATASET_PATH)
    combined = pd.concat([df, new_data], ignore_index=True)
    combined.to_csv(DATASET_PATH, index=False)
    print(f"✅ Added {len(new_data)} samples. Dataset now has {len(combined)} rows.")


def retrain():
    """Retrain the model with updated dataset."""
    print("\n🔄 Retraining model...")
    result = subprocess.run(["python", "train.py"], capture_output=False)
    if result.returncode == 0:
        print("✅ Model retrained and saved successfully!")
    else:
        print("❌ Retraining failed. Check train.py for errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add feedback samples and optionally retrain.")
    parser.add_argument("--retrain", action="store_true", help="Retrain model after adding sample")
    parser.add_argument("--bulk", type=str, help="Path to CSV file with bulk samples (text, label)")
    args = parser.parse_args()

    if args.bulk:
        add_bulk_from_file(args.bulk)
    else:
        print("=== SmartShield AI — Add Feedback Sample ===\n")
        text = input("Paste the message:\n> ").strip()
        if not text:
            print("No message entered.")
            exit()
        label_input = input("\nIs this SPAM or LEGIT? Enter 1 for spam, 0 for legit: ").strip()
        if label_input not in ["0", "1"]:
            print("Invalid input. Enter 0 or 1.")
            exit()
        label = int(label_input)
        add_sample(text, label)

    if args.retrain:
        retrain()
    else:
        print("\nRun with --retrain to retrain the model now, or retrain later with: python train.py")
