# Literature Review

AI-Based Real-Time UPI Fraud Detection and Prevention | Group G-13

This review distinguishes published techniques from our proposed implementation. The original secondary-paper citations are retained as unverified bibliographic leads; their reported metrics are not treated as confirmed.

## 1. Keles, M. B.; Gokturk, M. (2026). BI-GBDT: A Graph-Free Behavioral Interaction-Aware Gradient Boosting Framework for Fraud Detection in Large-Scale Payment Systems. Applied Sciences, 16, 876.

Behavioral profiles and sender-receiver interactions with gradient boosting. The base paper is retained unchanged; no numerical results are copied.

## 2. Ganga dari Yaswanth; Chaitanya Krishna (2026). Secure Digital Payments: Fraud Detection in UPI Using Machine Learning Techniques. (Original project bibliography; bibliographic details require verification.)

Original literature review describes preprocessing, behavioral features and supervised classifiers. No unverified performance figures are reproduced.

## 3. Indoria; Geogen George; M. K. Priya (2025). Enhancing Digital Payment Security: UPI Fraud Detection with Advanced ML Algorithms. (Original project bibliography; details require verification.)

Original review describes advanced classifiers and class imbalance handling; this motivates balanced class weights and precision/recall evaluation.

## 4. IJARCCE authors (2024). Real Time Hybrid Sequence Aware Ensemble Framework with Adaptive Learning and Explainable AI for Advanced UPI Fraud Detection. (Original project bibliography; details require verification.)

Original review describes hybrid detection and explainability. We retain it as a lead, not as verified evidence of results.

## 5. Liu, F. T.; Ting, K. M.; Zhou, Z.-H. (2008). Isolation Forest. IEEE ICDM.

Unsupervised anomaly detection using random isolation trees; used for unusual transaction patterns.

## 6. Chen, T.; Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD, pp. 785-794.

Gradient-boosted trees for structured data and supervised fraud classification.

## 7. Breiman, L. (2001). Random Forests. Machine Learning, 45, 5-32.

Bagged randomized trees provide a complementary supervised classification model.

## 8. Lundberg, S. M.; Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS.

SHAP motivates local explanations; the prototype uses XGBoost's exact TreeSHAP contributions in raw log-odds.

## Proposed project and research gap

The project combines Random Forest, XGBoost and Isolation Forest with receiver reputation scoring, four-level prevention decisions, a simulated verification workflow, critical-risk blocking and actual XGBoost TreeSHAP. The platform uses Flask, pandas, NumPy, scikit-learn and Chart.js. Evaluation is on synthetic data; measured results are pending confirmation.
