# AI-Based Real-Time UPI Fraud Detection and Prevention

## COMPLETE PROJECT METHODOLOGY

Group G-13 | Guide: Mrs. N. Meghana

245623733418 - V. Bhanu Vaishnavi

245623733407 - S. Harshitha

245623733409 - N. Shravani

## 1. Problem statement

UPI payments are fast; suspicious payments should be identified before simulated funds move. Static rules can miss unusual user or receiver behavior, and rare fraud labels make accuracy alone misleading.

## 2. Data and preprocessing

Use the synthetic UPI CSV and historical demo receiver profiles. Prepare numeric behavioral features; preserve label separation. Use a stratified 70/15/15 train, validation and test split. The existing tree-based pipeline expects numeric inputs; generic missing-value handling and encoding are design requirements for future external datasets.

## 3. Behavioral features

Transaction amount and ratio, time, transaction frequency and velocity, new device, location displacement, IP risk, first interaction, prior receiver flag and failed PIN attempts. The current implementation uses first-interaction and receiver signals; GMM cluster interaction prevalence from the base-paper concept is not implemented.

## 4. Receiver Reputation Score (RRS)

Trust ranges from 0 to 100. Weighted favorable signals: fraud-free record 30%, legitimate history 25%, account age 15%, normal behavior 15%, device/location consistency 10%, activity consistency 5%. Unknown receiver: neutral score 50. Demo profiles are preassigned; no live registry access.

## 5. Hybrid machine learning

Random Forest and XGBoost use class weights; Isolation Forest is fitted to normal training examples. The proposed model blends 50% XGBoost, 20% Random Forest and 30% normalized Isolation Forest. Final risk is the maximum of the blended ML score and 100 minus RRS. The weights and cutoffs are provisional, not calibrated fraud probabilities.

## 6. Risk decision and verification

Safe: below 40, approve. Suspicious: 40 to below 75, hold and request confirmation. High Risk: 75 to below 90, hold and require a simulated verification code and confirmation. Critical Risk: 90 or above, block with no user override and flag for review. Holds expire after 60 seconds; funds remain unchanged unless released. Balances are checked again at release.

## 7. Explainability

XGBoost TreeSHAP gives signed contributions to raw log-odds, not the complete hybrid score. Plain-language behavioral warnings and the receiver risk floor are shown separately.

## 8. Application architecture

Flask backend and REST endpoints; HTML, CSS, JavaScript and Chart.js frontend. Pages: dashboard, simulator, audit ledger, model evaluation, methodology and batch benchmark. The ledger and fake balances are stored in memory. The demo code is displayed for illustration, not actual OTP authentication.

## 9. Evaluation

Report precision, recall, F1, ROC-AUC, average precision (PR-AUC summary), confusion matrix, false-positive rate and alert rate. Evaluate fixed thresholds separately on validation and held-out test data. Batch benchmark measures scoring throughput for 500 synthetic records; it is not an independent accuracy test. Retraining and runtime test results must be confirmed before making performance claims.

## 10. Testing and limitations

Test all threshold boundaries, safe debit/credit, held balance invariance, wrong verification, valid confirmation, cancellation, timeout, repeat release and critical-block bypass. Synthetic data, predefined receiver profiles, in-memory storage and simulated identity verification limit generalization. No real UPI network or automatic retraining/security review service is implemented.

## References

Keles, M. B.; Gokturk, M. (2026). BI-GBDT: A Graph-Free Behavioral Interaction-Aware Gradient Boosting Framework for Fraud Detection in Large-Scale Payment Systems. Applied Sciences, 16, 876.

Liu, F. T.; Ting, K. M.; Zhou, Z.-H. (2008). Isolation Forest. IEEE ICDM.

Chen, T.; Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. KDD, pp. 785-794.

Breiman, L. (2001). Random Forests. Machine Learning, 45, 5-32.

Lundberg, S. M.; Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS.
