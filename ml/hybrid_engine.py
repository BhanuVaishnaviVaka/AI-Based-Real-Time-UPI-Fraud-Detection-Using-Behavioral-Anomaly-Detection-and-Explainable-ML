"""
Hybrid Real-Time Inference & Explainable AI Engine
Combines:
1. Supervised XGBoost (BI-GBDT)
2. Supervised Random Forest
3. Unsupervised Isolation Forest Anomaly Detection
4. SHAP / Feature Attribution Explainer
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

FEATURE_COLS = [
    "amount", "hour", "day_of_week", "user_avg_amount",
    "amount_deviation", "amount_ratio", "tx_count_1h", "tx_count_24h",
    "velocity_score", "is_new_device", "location_change_km",
    "ip_risk_score", "is_first_interaction", "is_receiver_flagged",
    "failed_pin_attempts"
]

class UPIFraudEngine:
    def __init__(self):
        self.scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
        self.rf_model = joblib.load(os.path.join(MODELS_DIR, "random_forest.joblib"))
        self.xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgboost_model.joblib"))
        self.iso_forest = joblib.load(os.path.join(MODELS_DIR, "isolation_forest.joblib"))
        
        with open(os.path.join(MODELS_DIR, "evaluation_metrics.json"), "r") as f:
            self.metadata = json.load(f)

    def extract_features(self, tx):
        """Prepare feature vector from transaction dictionary"""
        amount = float(tx.get("amount", 500.0))
        user_avg = float(tx.get("user_avg_amount", 850.0))
        hour = int(tx.get("hour", 14))
        day_of_week = int(tx.get("day_of_week", 2))
        
        amount_deviation = round(abs(amount - user_avg), 2)
        amount_ratio = round(amount / max(1.0, user_avg), 3)
        
        tx_count_1h = int(tx.get("tx_count_1h", 1))
        tx_count_24h = int(tx.get("tx_count_24h", 2))
        velocity_score = float(tx.get("velocity_score", 0.10))
        is_new_device = int(tx.get("is_new_device", 0))
        location_change_km = float(tx.get("location_change_km", 0.0))
        ip_risk_score = float(tx.get("ip_risk_score", 0.15))
        is_first_interaction = int(tx.get("is_first_interaction", 0))
        is_receiver_flagged = int(tx.get("is_receiver_flagged", 0))
        failed_pin_attempts = int(tx.get("failed_pin_attempts", 0))

        feat_dict = {
            "amount": amount,
            "hour": hour,
            "day_of_week": day_of_week,
            "user_avg_amount": user_avg,
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
            "failed_pin_attempts": failed_pin_attempts
        }
        
        X_df = pd.DataFrame([feat_dict])[FEATURE_COLS]
        return feat_dict, X_df

    def score_transaction(self, tx):
        feat_dict, X_df = self.extract_features(tx)
        
        # 1. Supervised Inferences
        rf_prob = float(self.rf_model.predict_proba(X_df)[0, 1])
        xgb_prob = float(self.xgb_model.predict_proba(X_df)[0, 1])
        
        # 2. Unsupervised Anomaly Inference
        iso_raw = float(self.iso_forest.decision_function(X_df)[0])
        # In sklearn Isolation Forest, negative values = anomalous, positive = normal
        # We transform to 0.0 (very normal) to 1.0 (extreme anomaly)
        iso_anomaly_score = max(0.0, min(1.0, 0.5 - (iso_raw * 2.5)))
        
        # 3. Hybrid Blended Risk Score (0 to 100)
        # Weighting: 50% XGBoost + 20% Random Forest + 30% Isolation Forest
        raw_hybrid = (0.50 * xgb_prob) + (0.20 * rf_prob) + (0.30 * iso_anomaly_score)
        risk_score = round(max(0.0, min(100.0, raw_hybrid * 100)), 1)
        
        # 4. Categorization
        if risk_score < 40.0:
            status = "Safe"
            badge_class = "safe"
            action = "Approved automatically"
            recommendation = "Low behavioral risk. Transaction authorized."
        elif risk_score < 75.0:
            status = "Suspicious"
            badge_class = "suspicious"
            action = "2-Factor Step-Up Verification Required"
            recommendation = "Moderate deviation from user baseline. Trigger biometric or OTP re-authentication."
        else:
            status = "Fraudulent"
            badge_class = "fraud"
            action = "Blocked Immediately"
            recommendation = "Severe anomaly indicators match known fraud typologies. Payment halted and flagged for bank review."

        # 5. Explainable AI: Feature Contribution Analysis (SHAP-inspired)
        explanations = self._generate_explanations(feat_dict, risk_score)

        return {
            "risk_score": risk_score,
            "status": status,
            "badge_class": badge_class,
            "action": action,
            "recommendation": recommendation,
            "models": {
                "xgboost_prob": round(xgb_prob * 100, 1),
                "random_forest_prob": round(rf_prob * 100, 1),
                "isolation_forest_anomaly": round(iso_anomaly_score * 100, 1)
            },
            "features": feat_dict,
            "explanations": explanations
        }


    def score_batch(self, df_input):
        """Vectorized batch scoring for high-throughput evaluation"""
        df = df_input.copy()
        
        # Ensure derived features exist
        if "amount_deviation" not in df.columns:
            user_avg = df["user_avg_amount"] if "user_avg_amount" in df.columns else 850.0
            df["amount_deviation"] = (df["amount"] - user_avg).abs()
        if "amount_ratio" not in df.columns:
            user_avg = df["user_avg_amount"] if "user_avg_amount" in df.columns else 850.0
            df["amount_ratio"] = df["amount"] / user_avg.clip(lower=1.0)
            
        for col in FEATURE_COLS:
            if col not in df.columns:
                df[col] = 0
                
        X = df[FEATURE_COLS]
        rf_probs = self.rf_model.predict_proba(X)[:, 1]
        xgb_probs = self.xgb_model.predict_proba(X)[:, 1]
        iso_raw = self.iso_forest.decision_function(X)
        iso_anom = np.clip(0.5 - (iso_raw * 2.5), 0.0, 1.0)
        
        hybrid = (0.50 * xgb_probs) + (0.20 * rf_probs) + (0.30 * iso_anom)
        scores = np.round(np.clip(hybrid * 100, 0.0, 100.0), 1)
        
        return scores, xgb_probs, rf_probs, iso_anom

    def _generate_explanations(self, f, score):
        """Derive explicit XAI feature contributions and human-understandable rationale"""
        reasons = []
        factors = []
        
        # Amount Deviation / Ratio
        if f["amount_ratio"] >= 4.0:
            impact = min(35.0, (f["amount_ratio"] - 1.0) * 5.0)
            reasons.append(f"Amount is {f['amount_ratio']}× higher than user's 30-day baseline (₹{f['user_avg_amount']:,.2f}).")
            factors.append({"feature": "Amount Ratio Spike", "weight": round(impact, 1), "direction": "risk", "desc": f"{f['amount_ratio']}x baseline"})
        elif f["amount_ratio"] >= 2.0:
            impact = 15.0
            reasons.append(f"Higher than normal spending (₹{f['amount']:,.2f} vs average ₹{f['user_avg_amount']:,.2f}).")
            factors.append({"feature": "Amount Elevation", "weight": round(impact, 1), "direction": "risk", "desc": f"₹{f['amount']} vs ₹{f['user_avg_amount']}"})
        else:
            factors.append({"feature": "Amount Consistency", "weight": 10.0, "direction": "safe", "desc": "Matches historical spending"})

        # New Device
        if f["is_new_device"] == 1:
            reasons.append("Unrecognized device hardware signature / potential SIM swap takeover.")
            factors.append({"feature": "New Device Hardware", "weight": 22.0, "direction": "risk", "desc": "Untrusted device ID"})
        else:
            factors.append({"feature": "Trusted Registered Device", "weight": 15.0, "direction": "safe", "desc": "Matches known device"})

        # Transaction Velocity / Count
        if f["velocity_score"] >= 0.65 or f["tx_count_1h"] >= 4:
            reasons.append(f"High transaction frequency: {f['tx_count_1h']} transactions in past 60 min (velocity index: {f['velocity_score']}).")
            factors.append({"feature": "Rapid Transaction Burst", "weight": 18.0, "direction": "risk", "desc": f"{f['tx_count_1h']} txns in 1hr"})
        else:
            factors.append({"feature": "Normal Transaction Velocity", "weight": 10.0, "direction": "safe", "desc": "Standard pacing"})

        # Recipient Flag
        if f["is_receiver_flagged"] == 1:
            reasons.append("Receiver VPA address has prior fraud reports or mule account flags in NPCI registry.")
            factors.append({"feature": "Flagged Beneficiary VPA", "weight": 25.0, "direction": "risk", "desc": "Known suspicious entity"})

        # First Interaction
        if f["is_first_interaction"] == 1:
            factors.append({"feature": "First-Time Interaction", "weight": 8.0, "direction": "risk", "desc": "No prior sender-receiver history"})

        # Location Hop
        if f["location_change_km"] >= 300.0:
            reasons.append(f"Geographical discrepancy: Transaction originated {f['location_change_km']:,.0f} km from habitual region.")
            factors.append({"feature": "Geographical Velocity Hop", "weight": 16.0, "direction": "risk", "desc": f"{f['location_change_km']} km displacement"})

        # Late Night Hour
        if f["hour"] in [0, 1, 2, 3, 4]:
            reasons.append(f"Atypical transaction timing: Initiated at {f['hour']:02d}:00 hrs (quiet hours).")
            factors.append({"feature": "Off-Hour Timing", "weight": 12.0, "direction": "risk", "desc": f"{f['hour']:02d}:00 hrs"})

        # PIN Failures
        if f["failed_pin_attempts"] >= 2:
            reasons.append(f"Repeated authentication challenges: {f['failed_pin_attempts']} failed PIN entries recorded.")
            factors.append({"feature": "Multiple PIN Failures", "weight": 20.0, "direction": "risk", "desc": f"{f['failed_pin_attempts']} invalid attempts"})

        # IP Risk
        if f["ip_risk_score"] >= 0.55:
            reasons.append("Network risk: Connection originated through anonymous proxy/VPN node.")
            factors.append({"feature": "High-Risk Network / IP", "weight": 14.0, "direction": "risk", "desc": f"IP risk {f['ip_risk_score']}"})

        if not reasons and score < 40.0:
            reasons.append("All behavioral indicators, device fingerprints, and interaction histories conform to normal usage.")

        return {
            "key_reasons": reasons[:4],
            "factors": factors
        }

if __name__ == "__main__":
    engine = UPIFraudEngine()
    
    # Test 1: Normal Transaction
    sample_normal = {
        "amount": 250.0, "user_avg_amount": 850.0, "hour": 15, "day_of_week": 1,
        "tx_count_1h": 1, "tx_count_24h": 3, "velocity_score": 0.12,
        "is_new_device": 0, "location_change_km": 0.0, "ip_risk_score": 0.10,
        "is_first_interaction": 0, "is_receiver_flagged": 0, "failed_pin_attempts": 0
    }
    res_normal = engine.score_transaction(sample_normal)
    print("Normal Result:", res_normal["status"], "| Score:", res_normal["risk_score"])
    
    # Test 2: Fraud Transaction
    sample_fraud = {
        "amount": 65000.0, "user_avg_amount": 850.0, "hour": 2, "day_of_week": 4,
        "tx_count_1h": 6, "tx_count_24h": 14, "velocity_score": 0.88,
        "is_new_device": 1, "location_change_km": 1450.0, "ip_risk_score": 0.85,
        "is_first_interaction": 1, "is_receiver_flagged": 1, "failed_pin_attempts": 2
    }
    res_fraud = engine.score_transaction(sample_fraud)
    print("Fraud Result:", res_fraud["status"], "| Score:", res_fraud["risk_score"])
    print("Fraud Explanations:", res_fraud["explanations"]["key_reasons"])
