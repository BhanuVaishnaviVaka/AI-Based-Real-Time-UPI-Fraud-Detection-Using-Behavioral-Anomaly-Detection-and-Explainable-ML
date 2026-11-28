"""Synthetic historical receiver profiles; never infer reputation from the current fraud label."""
from .dataset_generator import COMMON_USERS, TRUSTED_MERCHANTS, SUSPICIOUS_RECEIVERS

WEIGHTS = (0.30, 0.25, 0.15, 0.15, 0.10, 0.05)
TRUSTED = set(TRUSTED_MERCHANTS) | {u["upi_id"] for u in COMMON_USERS}
FLAGGED = set(SUSPICIOUS_RECEIVERS)

def receiver_reputation(upi):
    upi = str(upi or "").strip().lower()
    # Fictional, pre-existing demo profiles; no bank or NPCI connection.
    if upi in TRUSTED:
        values = (100, 95, 95, 90, 95, 95)
        reports = 0
    elif upi in FLAGGED:
        values = (0, 15, 20, 15, 20, 10)
        reports = 2
    else:
        # Unknown is uncertain, not confirmed fraud.
        values = (50, 50, 50, 50, 50, 50)
        reports = None
    score = round(sum(w*v for w,v in zip(WEIGHTS, values)), 1)
    category = ("Highly trusted" if score >= 80 else "Trusted" if score >= 60
                else "Moderate risk" if score >= 40 else "Suspicious" if score >= 20
                else "Very high risk")
    return {"score": score, "category": category, "confirmed_reports": reports,
            "known_profile": upi in TRUSTED or upi in FLAGGED}

def combined_risk(xgb, rf, anomaly, reputation):
    """Provisional policy: reputation may raise, never lower, ML risk."""
    ml = 100 * (0.50*xgb + 0.20*rf + 0.30*anomaly)
    # Reputation cannot exonerate unusual sender behavior.
    return max(0.0, min(100.0, max(ml, 100-reputation)))

def risk_band(score):
    if score < 40:
        return "Safe", "safe", "Approved automatically"
    if score < 75:
        return "Suspicious", "suspicious", "Held for user confirmation"
    if score < 90:
        return "High Risk", "high-risk", "Held for additional verification"
    return "Critical Risk", "fraud", "Blocked; security review required"
