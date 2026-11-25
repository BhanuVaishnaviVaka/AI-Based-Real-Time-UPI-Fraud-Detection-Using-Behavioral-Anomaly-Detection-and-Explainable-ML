# AI-Based Real-Time UPI Fraud Detection and Prevention

## ABSTRACT

The growing adoption of the Unified Payments Interface (UPI) has increased the need for fraud prevention before payment completion. Conventional rule-based systems may fail to recognize evolving fraud patterns or unusual interactions between senders and receivers. This project proposes a real-time, explainable fraud detection and prevention prototype using synthetic UPI transactions and behavioral analytics.

The framework analyzes transaction amount, spending deviation, transaction velocity, time, device changes, location changes, recipient history and a Receiver Reputation Score (RRS). The reputation score estimates receiver trustworthiness from six weighted historical signals, including confirmed fraud reports, legitimate transaction history, account age, behavior, device and location consistency, and activity consistency. Isolation Forest detects anomalies, while Random Forest and XGBoost learn labeled fraud patterns. Their outputs and the receiver risk floor produce a transaction risk score from 0 to 100.

Transactions are classified as Safe, Suspicious, High Risk or Critical Risk. Safe payments are approved, suspicious payments are held for confirmation, high-risk payments require simulated additional verification, and critical-risk payments are automatically blocked without a user override. Unresolved holds expire after 60 seconds. XGBoost TreeSHAP provides feature contributions alongside plain-language risk explanations. A Flask application supports transaction simulation, monitoring, audit history and batch evaluation. The prototype uses fake balances and does not connect to banks. Its effectiveness is assessed using held-out synthetic data; real-world performance remains to be validated.

## KEYWORDS

UPI, hybrid machine learning, behavioral anomaly detection, receiver reputation score, Isolation Forest, Random Forest, XGBoost, TreeSHAP, fraud prevention, risk scoring.

## GROUP: G-13

245623733418 - V. Bhanu Vaishnavi

245623733407 - S. Harshitha

245623733409 - N. Shravani

Project guide: Mrs. N. Meghana

Signature of the guide: _____________________
