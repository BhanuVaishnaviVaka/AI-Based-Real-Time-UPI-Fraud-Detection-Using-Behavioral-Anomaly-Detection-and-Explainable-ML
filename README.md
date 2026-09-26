# AI-Based Real-Time UPI Fraud Detection Using Behavioral Anomaly Detection and Explainable Machine Learning

### Enterprise Security Platform | Real-Time Payment Risk Defense

---

## 📌 Project Overview
The rapid growth of the Unified Payments Interface (UPI) has made digital payments ubiquitous across India. However, it has also led to evolving, sophisticated fraud typologies including SIM swap device takeovers, midnight account draining, mule accounts, and velocity bot attacks.

This project implements a **Hybrid AI Defense Architecture** combining:
1. **Supervised Classification:** XGBoost (inspired by the BI-GBDT framework) and Random Forest to detect known fraud patterns.
2. **Unsupervised Anomaly Detection:** Isolation Forest to detect novel zero-day behavioral deviations.
3. **Hybrid Risk Scoring:** A blended risk score $(0 - 100)$ triaging transactions into **Safe (< 40)**, **Suspicious (40 - 74)**, or **Fraudulent (≥ 75)**.
4. **Explainable AI (XAI):** SHAP-inspired feature attribution detailing the exact reasons behind each risk score.
5. **Executive FinTech Web Platform:** A professional banking SOC portal featuring a live transaction simulator, real-time analytics, empirical evaluation benchmarks, and methodology showcase.

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Packages: Flask, scikit-learn, xgboost, pandas, numpy, joblib)*

### 2. (Optional) Re-generate Dataset and Re-train Models
```bash
python ml/dataset_generator.py
python ml/model_trainer.py
```

### 3. Launch the Web Application
```bash
python app.py
```
Open your web browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🌐 Web Application Modules
- **Security Operations Center (SOC) Dashboard (`/`):** Real-time monitoring metrics, volume analyzed, risk distribution doughnut chart, temporal risk trajectory, and live streaming transaction feed.
- **UPI Payment Simulator (`/simulator`):** Interactive UPI transaction checkout with instant attack presets (*Normal Canteen*, *High-Value Appliance*, *Midnight Drain*, *Velocity Attack*, *SIM Swap*), interactive sliders, risk meter, and SHAP explainability breakdown.
- **Live Audit Ledger (`/transactions`):** Forensic ledger with filtering by Safe, Suspicious, or Fraudulent.
- **Model Evaluation (`/models`):** Empirical performance comparison table (Accuracy, Precision, Recall, F1, ROC-AUC), confusion matrices (TP, FP, FN, TN), and BI-GBDT feature importance rankings.
- **Project Methodology (`/methodology`):** High-resolution architecture diagram (`Proposed Methodology.png`), abstract, base paper citation (BI-GBDT, MDPI 2026), and literature review.
- **Batch Audit (`/batch`):** High-throughput batch evaluation across 500 transactions testing latency and throughput.
