"""
Model Trainer for Real-Time UPI Fraud Detection
Trains:
1. Random Forest (Supervised)
2. XGBoost (Supervised, inspired by BI-GBDT)
3. Isolation Forest (Unsupervised Anomaly Detection)
4. Hybrid Framework (Blended Risk Scoring)

Evaluates performance metrics and serializes models to disk.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.reputation import receiver_reputation
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, classification_report
)

FEATURE_COLS = [
    "amount", "hour", "day_of_week", "user_avg_amount",
    "amount_deviation", "amount_ratio", "tx_count_1h", "tx_count_24h",
    "velocity_score", "is_new_device", "location_change_km",
    "ip_risk_score", "is_first_interaction", "is_receiver_flagged",
    "failed_pin_attempts", "receiver_reputation_score"
]

def train_and_evaluate():
    data_path = os.path.join(os.path.dirname(__file__), "data", "upi_transactions.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    
    df["receiver_reputation_score"] = df["receiver_upi"].map(lambda v: receiver_reputation(v)["score"])
    X = df[FEATURE_COLS]
    y = df["is_fraud"]
    
    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_holdout, y_holdout, test_size=0.50, random_state=42, stratify=y_holdout
    )
    
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    
    # 1. Feature Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 2. Random Forest Classifier
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=120, max_depth=12, random_state=42, class_weight="balanced"
    )
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    # 3. XGBoost Classifier (Inspired by BI-GBDT)
    print("Training XGBoost Classifier...")
    pos_weight = (len(y_train) - sum(y_train)) / max(1, sum(y_train))
    xgb_model = XGBClassifier(
        n_estimators=130, max_depth=6, learning_rate=0.08,
        scale_pos_weight=pos_weight, random_state=42, eval_metric="logloss"
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    # 4. Isolation Forest (Anomaly Detection on normal + anomalous)
    print("Training Isolation Forest...")
    # Train primarily on normal patterns to model regular behavior
    iso_forest = IsolationForest(
        n_estimators=100, contamination=0.085, random_state=42
    )
    iso_forest.fit(X_train[y_train == 0])
    # Decision function: lower values mean more anomalous
    iso_scores_raw = iso_forest.decision_function(X_test)
    # Fixed transform matches inference; no test-set normalization.
    iso_scores = np.clip(0.5 - iso_scores_raw * 2.5, 0.0, 1.0)
    iso_preds = (iso_scores >= 0.60).astype(int)
    
    # 5. Hybrid Model (Supervised XGBoost + Isolation Forest Anomaly Score)
    # Match the deployed three-model fusion and reputation risk floor.
    hybrid_scores = np.maximum(0.50*xgb_probs + 0.20*rf_probs + 0.30*iso_scores, 1-X_test["receiver_reputation_score"].to_numpy()/100)
    hybrid_preds = (hybrid_scores >= 0.40).astype(int)
    
    # Measure the agreed fixed policy on validation before reporting test results.
    val_iso = np.clip(0.5 - iso_forest.decision_function(X_val)*2.5,0,1)
    val_score = np.maximum(.50*xgb_model.predict_proba(X_val)[:,1]+.20*rf_model.predict_proba(X_val)[:,1]+.30*val_iso,
                           1-X_val["receiver_reputation_score"].to_numpy()/100)
    def policy_report(labels, scores):
        out = {}
        for cut in (.40,.75,.90):
            tn,fp,fn,tp = confusion_matrix(labels, scores>=cut, labels=[0,1]).ravel()
            out[str(int(cut*100))] = {"recall":float(tp/max(1,tp+fn)), "fpr":float(fp/max(1,fp+tn)),
                                      "alert_rate":float(np.mean(scores>=cut))}
        return out

    # Compute Metrics Function
    def get_metrics(y_true, y_pred, y_prob):
        cm = confusion_matrix(y_true, y_pred)
        return {
            "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred)), 4),
            "f1_score": round(float(f1_score(y_true, y_pred)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4) if y_prob is not None else None,
            "confusion_matrix": {
                "tn": int(cm[0, 0]),
                "fp": int(cm[0, 1]),
                "fn": int(cm[1, 0]),
                "tp": int(cm[1, 1])
            }
        }
    
    metrics = {
        "Random Forest": get_metrics(y_test, rf_preds, rf_probs),
        "XGBoost (BI-GBDT)": get_metrics(y_test, xgb_preds, xgb_probs),
        "Isolation Forest": get_metrics(y_test, iso_preds, iso_scores),
        "Hybrid Proposed Framework": get_metrics(y_test, hybrid_preds, hybrid_scores)
    }
    
    # Feature importances from XGBoost
    importances = xgb_model.feature_importances_
    feat_imp = [
        {"feature": col, "importance": round(float(imp), 4)}
        for col, imp in sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)
    ]
    
    print("\n=== EVALUATION RESULTS ===")
    for model_name, m in metrics.items():
        print(f"\n{model_name}:")
        print(f"  Accuracy : {m['accuracy']*100:.2f}%")
        print(f"  Precision: {m['precision']*100:.2f}%")
        print(f"  Recall   : {m['recall']*100:.2f}%")
        print(f"  F1-Score : {m['f1_score']*100:.2f}%")
        if m['roc_auc']:
            print(f"  ROC-AUC  : {m['roc_auc']:.4f}")
        print(f"  Confusion Matrix: TP={m['confusion_matrix']['tp']}, FP={m['confusion_matrix']['fp']}, TN={m['confusion_matrix']['tn']}, FN={m['confusion_matrix']['fn']}")
        
    # Save artifacts
    print("\nSaving models and artifacts...")
    joblib.dump(scaler, os.path.join(models_dir, "scaler.joblib"))
    joblib.dump(rf_model, os.path.join(models_dir, "random_forest.joblib"))
    joblib.dump(xgb_model, os.path.join(models_dir, "xgboost_model.joblib"))
    joblib.dump(iso_forest, os.path.join(models_dir, "isolation_forest.joblib"))
    
    metrics_summary = {
        "risk_policy_version": 3,
        "validation_policy": policy_report(y_val,val_score),
        "test_policy": policy_report(y_test,hybrid_scores),
        "metrics": metrics,
        "feature_importances": feat_imp,
        "feature_columns": FEATURE_COLS,
        "dataset_stats": {
            "total_samples": len(df),
            "fraud_samples": int(sum(df["is_fraud"] == 1)),
            "normal_samples": int(sum(df["is_fraud"] == 0)),
            "fraud_rate": round(float(sum(df["is_fraud"] == 1) / len(df) * 100), 2),
            "train_samples": len(y_train),
            "validation_samples": len(y_val),
            "test_samples": len(y_test)
        }
    }
    
    with open(os.path.join(models_dir, "evaluation_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=2)
        
    print("Training and evaluation completed successfully!")

if __name__ == "__main__":
    train_and_evaluate()
