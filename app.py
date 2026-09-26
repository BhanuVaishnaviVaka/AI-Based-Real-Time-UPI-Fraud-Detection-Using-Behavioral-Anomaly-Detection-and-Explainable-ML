"""
AI-Based Real-Time UPI Fraud Detection Web Application
Production Risk Defense & Behavioral Anomaly Scoring Engine
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ml.hybrid_engine import UPIFraudEngine
from ml.dataset_generator import COMMON_USERS, TRUSTED_MERCHANTS, SUSPICIOUS_RECEIVERS

app = Flask(__name__)
app.config["SECRET_KEY"] = "upi-fraud-defense-g13-secret-key-2026"

# Initialize hybrid detection engine
engine = UPIFraudEngine()

# In-memory transaction storage initialized with recent sample transactions from dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "ml", "data", "upi_transactions.csv")
CACHE_PATH = os.path.join(os.path.dirname(__file__), "ml", "data", "initial_transactions.json")
LIVE_TRANSACTIONS = []

def init_live_transactions():
    global LIVE_TRANSACTIONS
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                LIVE_TRANSACTIONS = json.load(f)
                return
        except Exception as e:
            print("Error loading initial cache:", e)

init_live_transactions()

@app.route("/")
def dashboard():
    total_txns = len(LIVE_TRANSACTIONS)
    fraud_count = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Fraudulent")
    suspicious_count = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Suspicious")
    safe_count = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Safe")
    
    total_volume = sum(t["amount"] for t in LIVE_TRANSACTIONS)
    blocked_volume = sum(t["amount"] for t in LIVE_TRANSACTIONS if t["status"] == "Fraudulent")
    
    fraud_rate = round((fraud_count / max(1, total_txns)) * 100, 2)
    
    recent_txns = LIVE_TRANSACTIONS[:15]
    
    return render_template(
        "dashboard.html",
        total_txns=total_txns,
        fraud_count=fraud_count,
        suspicious_count=suspicious_count,
        safe_count=safe_count,
        total_volume=f"{total_volume:,.2f}",
        blocked_volume=f"{blocked_volume:,.2f}",
        fraud_rate=fraud_rate,
        recent_txns=recent_txns,
        active_page="dashboard"
    )

@app.route("/simulator")
def simulator():
    return render_template(
        "simulator.html",
        users=COMMON_USERS,
        merchants=TRUSTED_MERCHANTS,
        suspicious_receivers=SUSPICIOUS_RECEIVERS,
        active_page="simulator"
    )

@app.route("/transactions")
def transactions():
    status_filter = request.args.get("status", "all")
    tx_list = LIVE_TRANSACTIONS
    if status_filter != "all":
        tx_list = [t for t in LIVE_TRANSACTIONS if t["status"].lower() == status_filter.lower()]
        
    return render_template(
        "transactions.html",
        transactions=tx_list,
        status_filter=status_filter,
        active_page="transactions"
    )

@app.route("/models")
def models():
    metrics = engine.metadata.get("metrics", {})
    feature_importances = engine.metadata.get("feature_importances", [])
    dataset_stats = engine.metadata.get("dataset_stats", {})
    return render_template(
        "models.html",
        metrics=metrics,
        feature_importances=feature_importances,
        dataset_stats=dataset_stats,
        active_page="models"
    )

@app.route("/batch")
def batch():
    return render_template(
        "batch.html",
        active_page="batch"
    )

# --- API ENDPOINTS ---

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}
    
    # Enrich with default user profile if user_id is provided
    user_id = data.get("user_id", "usr_anil")
    matched_user = next((u for u in COMMON_USERS if u["user_id"] == user_id), None)
    if matched_user and "user_avg_amount" not in data:
        data["user_avg_amount"] = matched_user["avg_amt"]

    now = datetime.now()
    if "hour" not in data:
        data["hour"] = now.hour
    if "day_of_week" not in data:
        data["day_of_week"] = now.weekday()
        
    result = engine.score_transaction(data)
    
    # Create transaction record and prepend to live stream
    tx_id = f"TXN{random.randint(10000000, 99999999)}"
    record = {
        "transaction_id": tx_id,
        "user_id": user_id,
        "sender_upi": data.get("sender_upi", "user@upi"),
        "receiver_upi": data.get("receiver_upi", "receiver@upi"),
        "amount": float(data.get("amount", 100.0)),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": result["risk_score"],
        "status": result["status"],
        "badge_class": result["badge_class"],
        "action": result["action"],
        "recommendation": result["recommendation"],
        "models": result["models"],
        "features": result["features"],
        "explanations": result["explanations"]
    }
    
    LIVE_TRANSACTIONS.insert(0, record)
    if len(LIVE_TRANSACTIONS) > 200:
        LIVE_TRANSACTIONS.pop()
        
    return jsonify({
        "success": True,
        "transaction": record
    })

@app.route("/api/simulate-stream", methods=["POST"])
def api_simulate_stream():
    """Generates 3-5 real-time simulated transactions of varied risk for live demonstration"""
    scenarios = [
        {"type": "normal", "amt_mult": 0.8, "dev": 0, "vel": 0.12, "hr": 14, "rec": "swiggy@icici", "loc": 0.0, "pin": 0},
        {"type": "normal", "amt_mult": 1.2, "dev": 0, "vel": 0.20, "hr": 19, "rec": "amazon.pay@apl", "loc": 0.0, "pin": 0},
        {"type": "suspicious", "amt_mult": 3.8, "dev": 1, "vel": 0.55, "hr": 23, "rec": "unknown_store_99@paytm", "loc": 180.0, "pin": 1},
        {"type": "fraud", "amt_mult": 35.0, "dev": 1, "vel": 0.92, "hr": 3, "rec": "crypto_fastpay_77@axl", "loc": 2200.0, "pin": 2},
    ]
    
    chosen = random.choice(scenarios)
    user = random.choice(COMMON_USERS)
    amt = round(user["avg_amt"] * chosen["amt_mult"], 2)
    
    tx_data = {
        "user_id": user["user_id"],
        "sender_upi": user["upi_id"],
        "receiver_upi": chosen["rec"],
        "amount": amt,
        "user_avg_amount": user["avg_amt"],
        "hour": chosen["hr"],
        "day_of_week": random.randint(0, 6),
        "tx_count_1h": 1 if chosen["type"] == "normal" else random.randint(4, 8),
        "tx_count_24h": random.randint(2, 15),
        "velocity_score": chosen["vel"],
        "is_new_device": chosen["dev"],
        "location_change_km": chosen["loc"],
        "ip_risk_score": 0.15 if chosen["type"] == "normal" else (0.45 if chosen["type"] == "suspicious" else 0.88),
        "is_first_interaction": 1 if chosen["type"] != "normal" else 0,
        "is_receiver_flagged": 1 if chosen["type"] == "fraud" else 0,
        "failed_pin_attempts": chosen["pin"]
    }
    
    res = engine.score_transaction(tx_data)
    record = {
        "transaction_id": f"TXN{random.randint(10000000, 99999999)}",
        "user_id": user["user_id"],
        "sender_upi": user["upi_id"],
        "receiver_upi": chosen["rec"],
        "amount": amt,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "risk_score": res["risk_score"],
        "status": res["status"],
        "badge_class": res["badge_class"],
        "action": res["action"],
        "recommendation": res["recommendation"],
        "models": res["models"],
        "features": res["features"],
        "explanations": res["explanations"]
    }
    LIVE_TRANSACTIONS.insert(0, record)
    return jsonify({"success": True, "transaction": record})

@app.route("/api/chart-data")
def api_chart_data():
    """Provides aggregated metrics for Chart.js"""
    safe = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Safe")
    suspicious = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Suspicious")
    fraud = sum(1 for t in LIVE_TRANSACTIONS if t["status"] == "Fraudulent")
    
    # Recent scores
    recent_scores = [t["risk_score"] for t in LIVE_TRANSACTIONS[:20]][::-1]
    recent_labels = [t["transaction_id"][-4:] for t in LIVE_TRANSACTIONS[:20]][::-1]

    return jsonify({
        "distribution": {
            "labels": ["Safe (0-39)", "Suspicious (40-74)", "Fraudulent (75-100)"],
            "counts": [safe, suspicious, fraud]
        },
        "recent_trend": {
            "labels": recent_labels,
            "scores": recent_scores
        }
    })


@app.route("/api/run-batch-benchmark", methods=["POST"])
def api_run_batch_benchmark():
    import time
    start = time.time()
    df = pd.read_csv(DATA_PATH).sample(n=500, random_state=random.randint(1, 1000)).reset_index(drop=True)
    
    scores, xgb_p, rf_p, iso_a = engine.score_batch(df)
    
    safe = int(sum(scores < 40.0))
    suspicious = int(sum((scores >= 40.0) & (scores < 75.0)))
    fraud = int(sum(scores >= 75.0))
    
    flagged = []
    for idx in range(len(df)):
        s = float(scores[idx])
        if s >= 40.0:
            row = df.iloc[idx]
            status = "Fraudulent" if s >= 75.0 else "Suspicious"
            b_class = "fraud" if s >= 75.0 else "suspicious"
            
            # Key reason heuristic
            amt_rat = row.get("amount_ratio", 1.0)
            reason = f"Amount anomaly ({amt_rat}x baseline)" if amt_rat > 3.0 else (
                "Device signature mismatch" if row.get("is_new_device", 0) == 1 else "Velocity & network anomaly"
            )
            
            flagged.append({
                "transaction_id": str(row.get("transaction_id", f"TXN{idx}")),
                "sender_upi": str(row.get("sender_upi", "")),
                "receiver_upi": str(row.get("receiver_upi", "")),
                "amount": float(row.get("amount", 0)),
                "risk_score": s,
                "status": status,
                "badge_class": b_class,
                "reason": reason
            })
            
    elapsed = round(time.time() - start, 3)
    tps = round(500 / max(0.001, elapsed), 1)
    
    return jsonify({
        "total": 500,
        "duration_sec": elapsed,
        "tps": tps,
        "safe": safe,
        "suspicious": suspicious,
        "fraud": fraud,
        "flagged": flagged[:35]
    })

if __name__ == "__main__":
    print("=================================================================")
    print("  AI-Based Real-Time UPI Fraud Detection Platform")
    print("  Real-Time Security Operations & Fraud Defense Engine")
    print("  Server starting at: http://127.0.0.1:5000 (also http://localhost:5000)")
    print("=================================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)

