"""
ml/data/generate_synthetic_data.py

Generates a synthetic transaction dataset matching FinGuard's full schema.
Stands in for a real Kaggle dataset until one is swapped in — same
columns, same downstream code path.

Fraud signal design (mirrors known real-world fraud indicators):
- High amount, especially relative to customer age/profile
- Late-night transactions (12am-4am)
- New/unrecognized device
- Foreign/unknown location
- High-risk merchant categories (crypto, jewelry, gambling)
- Customer has prior fraud history
- High-risk payment methods (wire transfer, crypto)
"""

import numpy as np
import pandas as pd

np.random.seed(42)
N = 30000

merchant_categories = ["Grocery", "Electronics", "Travel", "Online Retail",
                        "Gas Station", "Restaurant", "Jewelry", "Crypto Exchange", "Gambling"]
transaction_types = ["Purchase", "Transfer", "Withdrawal", "Deposit", "Bill Payment"]
device_types = ["Mobile - Known", "Mobile - New", "Desktop - Known", "Desktop - New", "ATM"]
locations = ["New York", "Los Angeles", "Chicago", "Houston", "Miami",
             "Dallas", "Seattle", "Unknown/Foreign"]
payment_methods = ["Debit Card", "Credit Card", "Wire Transfer", "ACH", "Cryptocurrency"]

rows = []
for i in range(N):
    amount = round(np.random.exponential(scale=180), 2)
    merchant = np.random.choice(merchant_categories, p=[0.18, 0.14, 0.1, 0.18, 0.13, 0.11, 0.05, 0.06, 0.05])
    txn_type = np.random.choice(transaction_types, p=[0.4, 0.25, 0.15, 0.1, 0.1])
    device = np.random.choice(device_types, p=[0.35, 0.15, 0.25, 0.15, 0.1])
    location = np.random.choice(locations, p=[0.16, 0.14, 0.13, 0.12, 0.12, 0.1, 0.11, 0.12])
    hour = np.random.randint(0, 24)
    prev_fraud = np.random.choice([0, 1], p=[0.93, 0.07])
    age = int(np.clip(np.random.normal(42, 15), 18, 90))
    payment = np.random.choice(payment_methods, p=[0.35, 0.3, 0.1, 0.15, 0.1])

    risk_score = 0.0
    if amount > 1000:
        risk_score += 0.28
    if hour in [0, 1, 2, 3, 4]:
        risk_score += 0.2
    if device in ["Mobile - New", "Desktop - New"]:
        risk_score += 0.18
    if location == "Unknown/Foreign":
        risk_score += 0.2
    if merchant in ["Crypto Exchange", "Jewelry", "Gambling"]:
        risk_score += 0.15
    if prev_fraud:
        risk_score += 0.3
    if payment in ["Wire Transfer", "Cryptocurrency"]:
        risk_score += 0.15
    if age < 25 and amount > 800:
        risk_score += 0.1

    risk_score += np.random.normal(0, 0.08)
    is_fraud = 1 if risk_score > 0.55 else 0

    rows.append({
        "transaction_id": f"TXN{100000+i}",
        "sender_name": f"User_{np.random.randint(1, 4000)}",
        "receiver_name": f"Merchant_{np.random.randint(1, 800)}",
        "amount": amount,
        "merchant_category": merchant,
        "transaction_type": txn_type,
        "device_type": device,
        "location": location,
        "transaction_hour": hour,
        "previous_fraud_history": prev_fraud,
        "customer_age": age,
        "payment_method": payment,
        "is_fraud": is_fraud,
    })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/FinGuard/ml/data/transactions.csv", index=False)
print(f"Generated {len(df)} transactions. Fraud rate: {df['is_fraud'].mean()*100:.2f}%")
print(df.head())
