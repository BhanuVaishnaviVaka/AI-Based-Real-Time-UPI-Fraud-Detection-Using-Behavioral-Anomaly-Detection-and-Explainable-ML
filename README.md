# AI-Based Real-Time UPI Fraud Detection and Prevention

Academic prototype using synthetic profiles, transactions and fake balances only. No bank/NPCI connection, real payments, or real identity authentication.

## Updated methodology
- Offline: synthetic data, preprocessing, behavioral features, receiver reputation, class weighting, Random Forest + XGBoost + Isolation Forest, fusion and evaluation.
- Online: transaction validation, real-time features, reputation and hybrid scoring, explainable risk signals, policy routing, verification, audit and dashboard.
- Receiver reputation is a 0–100 trust score based on six weighted synthetic historical signals: fraud-free record (30%), legitimate history (25%), age (15%), behavior (15%), device/location consistency (10%), activity consistency (5%). Unknown receivers receive a neutral 50, not a fraud label.
- Existing saved models remain compatible. Reputation is an independent risk floor (max of hybrid score and 100 minus reputation); retraining also includes it as a model feature. Thresholds and weights are provisional, not calibrated probabilities.
- Safe <40: approve. Suspicious 40–<75: hold, confirm/cancel. High Risk 75–<90: hold, simulated code verification and confirmation. Critical Risk >=90: block; no user override, flag for review. All holds expire at 60 seconds, enforced server-side, and balances are rechecked before release.
- Actual XGBoost TreeSHAP contributions are shown in raw log-odds alongside separate rule-based warnings and the reputation policy floor. Independent data validation remains future work.
- Demo verification code is deliberately displayed, not real OTP or authentication. In-memory balances and ledger reset on restart. No production security review interface or automatic retraining is implemented.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Visit http://127.0.0.1:5000.

To retrain with the added reputation feature and obtain updated metrics:
```bash
python ml/model_trainer.py
python app.py
```
The synthetic receiver list is strongly correlated with the generated labels, so metrics may overstate real-world performance. Evaluate on independent profiles and real authorized data before claiming real-world detection. Existing saved model metrics are hidden until retraining. Batch scoring measures throughput, not independent accuracy.

Run policy tests: `python -m unittest discover -s tests`.

The methodology diagram is available at `/methodology`. Training uses a stratified 70/15/15 split; fixed thresholds are evaluated on validation and test separately. GitHub Actions runs retraining and automated tests and uploads the resulting models and metrics as an artifact when successful.
