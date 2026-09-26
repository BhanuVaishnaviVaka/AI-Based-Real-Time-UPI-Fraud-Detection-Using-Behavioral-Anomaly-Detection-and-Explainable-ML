"""
Realistic Balanced UPI Behavioral Dataset Generator
Ensures natural feature distributions and subtle multi-attribute interactions.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

COMMON_USERS = [
    {"user_id": "usr_anil", "upi_id": "anil.k@okhdfcbank", "name": "Anil Kumar", "avg_amt": 850, "std_amt": 350, "home_loc": "Hyderabad", "reg_device": "dev_oneplus_11"},
    {"user_id": "usr_sunita", "upi_id": "sunita.r@oksbi", "name": "Sunita Roy", "avg_amt": 650, "std_amt": 250, "home_loc": "Hyderabad", "reg_device": "dev_pixel_8"},
    {"user_id": "usr_vikram", "upi_id": "vikram.s@icici", "name": "Vikram Singh", "avg_amt": 1200, "std_amt": 500, "home_loc": "Secunderabad", "reg_device": "dev_samsung_s23"},
    {"user_id": "usr_rahul", "upi_id": "rahul.k@paytm", "name": "Rahul Kumar", "avg_amt": 450, "std_amt": 200, "home_loc": "Bengaluru", "reg_device": "dev_iphone_14"},
    {"user_id": "usr_priya", "upi_id": "priya.sharma@apl", "name": "Priya Sharma", "avg_amt": 2200, "std_amt": 800, "home_loc": "Mumbai", "reg_device": "dev_iphone_15"},
    {"user_id": "usr_arjun", "upi_id": "arjun.reddy@axl", "name": "Arjun Reddy", "avg_amt": 1500, "std_amt": 600, "home_loc": "Hyderabad", "reg_device": "dev_galaxy_a54"},
    {"user_id": "usr_ananya", "upi_id": "ananya.v@ybl", "name": "Ananya V", "avg_amt": 950, "std_amt": 300, "home_loc": "Chennai", "reg_device": "dev_vivo_v27"},
    {"user_id": "usr_karthik", "upi_id": "karthik.m@barodampay", "name": "Karthik M", "avg_amt": 3100, "std_amt": 1100, "home_loc": "Pune", "reg_device": "dev_oneplus_10"},
]

TRUSTED_MERCHANTS = [
    "swiggy@icici", "zomato@hdfcbank", "amazon.pay@apl", "flipkart@axisbank",
    "blinkit@kotak", "zepto@indus", "irctc@sbi", "tatacliq@okhdfcbank",
    "dmart.retail@paytm", "canteen.central@upi", "metro.card@paytm"
]

SUSPICIOUS_RECEIVERS = [
    "lottery_claim_991@ybl", "crypto_fastpay_77@axl", "instant_loan_bonus@okaxis",
    "rewards_refund_kfx@sbi", "unknown_merchant_8819@paytm", "dark_market_transfer@ybl"
]

INDIAN_CITIES = ["Hyderabad", "Secunderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai", "Kolkata", "Pune", "Jaipur", "Dubai", "Lagos"]

def generate_upi_dataset(num_samples=16000, fraud_ratio=0.085):
    data = []
    base_time = datetime(2026, 3, 1, 8, 0, 0)
    
    num_fraud = int(num_samples * fraud_ratio)
    num_normal = num_samples - num_fraud

    # Normal Transactions
    for i in range(num_normal):
        user = random.choice(COMMON_USERS)
        day_offset = random.randint(0, 28)
        hour = random.randint(6, 23) if random.random() < 0.94 else random.choice([0, 1, 2, 3, 4, 5])
            
        tx_time = base_time + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        
        # Amount distribution
        if random.random() < 0.05:
            # Genuine big purchase
            amount = round(user["avg_amt"] * random.uniform(2.5, 6.0), 2)
        else:
            amount = max(10.0, float(np.random.normal(user["avg_amt"], user["std_amt"])))
            amount = round(amount, 2)
            
        recipient = random.choice(TRUSTED_MERCHANTS + [u["upi_id"] for u in COMMON_USERS if u["upi_id"] != user["upi_id"]])
        is_new_device = 1 if random.random() < 0.07 else 0
        location_change_km = 0.0 if random.random() < 0.92 else round(random.uniform(15.0, 450.0), 2)
        
        tx_count_1h = random.choices([1, 2, 3, 4, 5], weights=[0.72, 0.18, 0.06, 0.03, 0.01])[0]
        tx_count_24h = random.randint(1, 10)
        velocity_score = round(random.uniform(0.02, 0.45), 3)
        
        amount_ratio = round(amount / max(1.0, user["avg_amt"]), 3)
        amount_deviation = round(abs(amount - user["avg_amt"]), 2)
        
        is_first_interaction = 1 if random.random() < 0.25 else 0
        is_receiver_flagged = 1 if random.random() < 0.015 else 0
        ip_risk_score = round(random.uniform(0.02, 0.55), 3)
        failed_pin_attempts = random.choices([0, 1, 2], weights=[0.90, 0.08, 0.02])[0]
        
        data.append({
            "transaction_id": f"TXN{2603000000 + i}",
            "user_id": user["user_id"],
            "sender_upi": user["upi_id"],
            "receiver_upi": recipient,
            "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
            "hour": hour,
            "day_of_week": tx_time.weekday(),
            "amount": amount,
            "user_avg_amount": user["avg_amt"],
            "amount_deviation": amount_deviation,
            "amount_ratio": amount_ratio,
            "tx_count_1h": tx_count_1h,
            "tx_count_24h": tx_count_24h,
            "velocity_score": velocity_score,
            "is_new_device": is_new_device,
            "location_change_km": location_change_km,
            "ip_risk_score": ip_risk_score,
            "is_first_interaction": is_first_interaction,
            "is_receiver_flagged": is_receiver_flagged,
            "failed_pin_attempts": failed_pin_attempts,
            "is_fraud": 0
        })

    # Fraudulent Transactions
    scenarios = ["drain", "velocity", "device_takeover", "phishing", "geo_anomaly"]
    
    for i in range(num_fraud):
        user = random.choice(COMMON_USERS)
        day_offset = random.randint(0, 28)
        sc = random.choice(scenarios)
        
        if sc == "drain":
            hour = random.choice([0, 1, 2, 3, 4, 23])
            amount = round(float(user["avg_amt"] * random.uniform(12.0, 45.0)), 2)
            tx_count_1h = random.randint(2, 6)
            tx_count_24h = random.randint(5, 15)
            velocity_score = round(random.uniform(0.45, 0.85), 3)
            is_new_device = 1 if random.random() < 0.75 else 0
            location_change_km = round(random.uniform(150.0, 2500.0), 2)
            recipient = random.choice(SUSPICIOUS_RECEIVERS)
            is_receiver_flagged = 1 if random.random() < 0.70 else 0
            ip_risk_score = round(random.uniform(0.40, 0.88), 3)
            failed_pin_attempts = random.choices([0, 1, 2], weights=[0.45, 0.35, 0.20])[0]

        elif sc == "velocity":
            hour = random.randint(0, 23)
            amount = round(float(user["avg_amt"] * random.uniform(1.8, 6.5)), 2)
            tx_count_1h = random.randint(5, 14)
            tx_count_24h = random.randint(12, 32)
            velocity_score = round(random.uniform(0.68, 0.96), 3)
            is_new_device = 1 if random.random() < 0.50 else 0
            location_change_km = round(random.uniform(0.0, 300.0), 2)
            recipient = random.choice(SUSPICIOUS_RECEIVERS)
            is_receiver_flagged = 1 if random.random() < 0.60 else 0
            ip_risk_score = round(random.uniform(0.35, 0.82), 3)
            failed_pin_attempts = random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15])[0]

        elif sc == "device_takeover":
            hour = random.randint(0, 23)
            amount = round(float(user["avg_amt"] * random.uniform(5.0, 22.0)), 2)
            tx_count_1h = random.randint(2, 5)
            tx_count_24h = random.randint(4, 10)
            velocity_score = round(random.uniform(0.40, 0.78), 3)
            is_new_device = 1
            location_change_km = round(random.uniform(300.0, 1800.0), 2)
            recipient = random.choice(SUSPICIOUS_RECEIVERS)
            is_receiver_flagged = 1 if random.random() < 0.65 else 0
            ip_risk_score = round(random.uniform(0.50, 0.92), 3)
            failed_pin_attempts = random.choices([1, 2], weights=[0.60, 0.40])[0]

        elif sc == "geo_anomaly":
            hour = random.randint(0, 23)
            amount = round(float(user["avg_amt"] * random.uniform(3.0, 15.0)), 2)
            tx_count_1h = random.randint(1, 4)
            tx_count_24h = random.randint(3, 8)
            velocity_score = round(random.uniform(0.35, 0.70), 3)
            is_new_device = 1 if random.random() < 0.80 else 0
            location_change_km = round(random.uniform(1200.0, 6500.0), 2)
            recipient = random.choice(SUSPICIOUS_RECEIVERS)
            is_receiver_flagged = 1 if random.random() < 0.60 else 0
            ip_risk_score = round(random.uniform(0.55, 0.95), 3)
            failed_pin_attempts = random.choices([0, 1], weights=[0.65, 0.35])[0]

        else: # phishing
            hour = random.randint(9, 22)
            amount = round(float(user["avg_amt"] * random.uniform(2.0, 8.0)), 2)
            tx_count_1h = random.randint(1, 3)
            tx_count_24h = random.randint(2, 6)
            velocity_score = round(random.uniform(0.20, 0.55), 3)
            is_new_device = 0
            location_change_km = 0.0
            recipient = random.choice(SUSPICIOUS_RECEIVERS)
            is_receiver_flagged = 1
            ip_risk_score = round(random.uniform(0.35, 0.75), 3)
            failed_pin_attempts = 0

        tx_time = base_time + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        amount_ratio = round(amount / max(1.0, user["avg_amt"]), 3)
        amount_deviation = round(abs(amount - user["avg_amt"]), 2)
        
        data.append({
            "transaction_id": f"TXN{2603090000 + i}",
            "user_id": user["user_id"],
            "sender_upi": user["upi_id"],
            "receiver_upi": recipient,
            "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
            "hour": hour,
            "day_of_week": tx_time.weekday(),
            "amount": amount,
            "user_avg_amount": user["avg_amt"],
            "amount_deviation": amount_deviation,
            "amount_ratio": amount_ratio,
            "tx_count_1h": tx_count_1h,
            "tx_count_24h": tx_count_24h,
            "velocity_score": velocity_score,
            "is_new_device": is_new_device,
            "location_change_km": location_change_km,
            "ip_risk_score": ip_risk_score,
            "is_first_interaction": 1,
            "is_receiver_flagged": is_receiver_flagged,
            "failed_pin_attempts": failed_pin_attempts,
            "is_fraud": 1
        })
        
    df = pd.DataFrame(data)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'upi_transactions.csv')
    df = generate_upi_dataset(num_samples=16000, fraud_ratio=0.085)
    df.to_csv(out_file, index=False)
    print(f'Balanced dataset generated: {out_file} (Fraud={sum(df["is_fraud"]==1)})')
