# AI-Based Real-Time UPI Fraud Detection and Prevention

## Problem statement
- UPI payments require risk assessment before funds move.
- Static rules may miss behavioral anomalies and risky receivers.
- Rare fraud labels make raw accuracy misleading.
- Goal: detect, explain, hold or block risky simulated payments.

## Abstract
- Analyze transaction behavior and receiver trustworthiness.
- Combine Isolation Forest, Random Forest and XGBoost.
- Produce a 0-100 fraud risk score and four actionable risk categories.
- Explain predictions using TreeSHAP and show them in a Flask dashboard.

## Objectives and scope
- Detect known fraud patterns and unusual behavior.
- Introduce Receiver Reputation Score (RRS).
- Hold suspicious/high-risk payments and block critical-risk payments.
- Use synthetic data, fake balances and simulated verification only.

## Proposed methodology
- 1. Data collection: Synthetic UPI transactions and profiles
- 2. Split and preprocessing: Train / validation / test; clean and encode
- 3. Feature engineering: Behavioral signals and receiver reputation
- 4. Class imbalance handling: Class weighting on training data
- 5. Hybrid training: Isolation Forest + Random Forest + XGBoost
- 6. Fusion and thresholds: Four risk bands; validation check
- 7. Evaluate and save: PR-AUC, recall, FPR; model artifacts
- 8. Transaction request: Simulated UPI payment
- 9. Real-time features: Transaction context and receiver score
- 10. Hybrid risk scoring: 0-100 risk score and TreeSHAP
- 11. Decision routing: Safe / Suspicious / High / Critical
- 12. Approve, hold or block: Explanation; held funds do not move
- 13. Verification / security action: Confirm, extra code, cancel or block
- 14. Log and monitor: History, dashboard and review flags

## Receiver reputation score
- Trust score: 0-100; unknown receivers start at 50.
- Fraud-free record 30%; legitimate history 25%; account age 15%.
- Normal behavior 15%; device/location consistency 10%; activity consistency 5%.
- Final risk = max(hybrid ML score, 100 minus receiver reputation).

## Hybrid machine learning and XAI
- Isolation Forest: anomaly detection (30%).
- Random Forest: supervised classification (20%).
- XGBoost: supervised classification (50%).
- XGBoost TreeSHAP: signed contributions in raw log-odds; separate policy explanation.

## Four-level fraud prevention
- Safe (<40): approve simulated payment.
- Suspicious (40-<75): hold and ask user to confirm or cancel.
- High Risk (75-<90): hold; simulated extra verification plus confirmation.
- Critical Risk (>=90): automatically block; no user override.
- 60-second timeout; balance recheck before release.

## Software and hardware requirements
- Python, Flask, pandas, NumPy, scikit-learn, XGBoost, joblib.
- HTML, CSS, JavaScript, Chart.js; VS Code or another editor.
- Standard laptop or desktop; 8 GB RAM recommended for local development.
- CSV data and in-memory demo balances; no bank connection.

## Evaluation and limitations
- Stratified 70/15/15 training, validation and test split; class weights.
- Precision, recall, F1, ROC-AUC, average precision, FPR and alert rate.
- 500-transaction batch benchmark for throughput.
- Synthetic data and provisional thresholds; results must be verified before reporting.

## References
- Keles & Gokturk (2026), BI-GBDT, Applied Sciences 16, 876.
- Liu et al. (2008), Isolation Forest, ICDM.
- Chen & Guestrin (2016), XGBoost, KDD.
- Breiman (2001), Random Forests; Lundberg & Lee (2017), SHAP.