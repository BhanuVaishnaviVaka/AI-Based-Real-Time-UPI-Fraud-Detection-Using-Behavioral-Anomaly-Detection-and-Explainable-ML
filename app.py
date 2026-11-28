"""UPI fraud prevention prototype. All balances, profiles and verification are simulated."""
import os
import math
import time
import uuid
import secrets
import threading
import random
from datetime import datetime
from decimal import Decimal, InvalidOperation
import pandas as pd
from flask import Flask, render_template, request, jsonify, session
from ml.hybrid_engine import UPIFraudEngine
from ml.dataset_generator import COMMON_USERS, TRUSTED_MERCHANTS, SUSPICIOUS_RECEIVERS
from ml.reputation import receiver_reputation, risk_band

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
engine = UPIFraudEngine()
DATA_PATH = os.path.join(os.path.dirname(__file__), "ml", "data", "upi_transactions.csv")
LOCK = threading.RLock()
LIVE_TRANSACTIONS = []
PENDING = {}
BALANCES = {}
USERS = {u["user_id"]: u for u in COMMON_USERS}
UPIS = {u["upi_id"]: u for u in COMMON_USERS}
BANDS = ("Safe", "Suspicious", "High Risk", "Critical Risk")

def balance(upi):
    return BALANCES.setdefault(upi, 10000000 if upi in UPIS else 0)

def transfer(record):
    sender, receiver, cents = record["sender_upi"], record["receiver_upi"], record["amount_cents"]
    if balance(sender) < cents:
        record.update(state="Cancelled", action="Insufficient demo balance", money_transferred=False)
        return
    BALANCES[sender] -= cents
    BALANCES[receiver] = balance(receiver) + cents
    record.update(state="Released" if record["state"] == "Held" else "Approved",
                  action="Simulated money transferred", money_transferred=True)

def expire_holds():
    for tid, pending in list(PENDING.items()):
        if time.monotonic() >= pending["deadline"]:
            pending["record"].update(state="Expired", action="Cancelled after 60-second timeout", money_transferred=False)
            del PENDING[tid]

def owner():
    if "demo_session" not in session:
        session["demo_session"] = secrets.token_urlsafe(24)
    return session["demo_session"]

def public(record):
    return {**record, "sender_balance": balance(record["sender_upi"])/100,
            "receiver_balance": balance(record["receiver_upi"])/100}

def process(data, session_id):
    if not isinstance(data, dict):
        raise ValueError("Invalid transaction")
    user = USERS.get(data.get("user_id", "usr_anil"))
    if not user:
        raise ValueError("Unknown demo sender")
    sender = user["upi_id"]
    receiver = str(data.get("receiver_upi", "")).strip().lower()
    if not receiver or "@" not in receiver or len(receiver) > 100 or receiver == sender:
        raise ValueError("Choose a valid, different demo receiver")
    try:
        amount = Decimal(str(data.get("amount")))
        if not amount.is_finite() or amount <= 0 or amount > 10000000 or amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Enter a positive amount with at most two decimal places")
        cents = int(amount*100)
    except (InvalidOperation, TypeError, OverflowError):
        raise ValueError("Invalid amount")
    now = datetime.now()
    data = {**data, "sender_upi": sender, "receiver_upi": receiver, "amount": float(amount),
            "user_avg_amount": user["avg_amt"], "day_of_week": now.weekday()}
    data.setdefault("hour", now.hour)
    for name, lo, hi, default in [
        ("hour",0,23,now.hour),("tx_count_1h",0,1000,1),("tx_count_24h",0,10000,2),
        ("velocity_score",0,1,.1),("is_new_device",0,1,0),("location_change_km",0,40000,0),
        ("ip_risk_score",0,1,.15),("is_first_interaction",0,1,0),
        ("is_receiver_flagged",0,1,0),("failed_pin_attempts",0,100,0)]:
        value = float(data.get(name, default))
        if not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError("Invalid " + name)
        data[name] = value
    with LOCK:
        expire_holds()
        if balance(sender) < cents:
            raise ValueError("Insufficient demo balance")
        res = engine.score_transaction(data)
        tid = "TXN" + uuid.uuid4().hex[:12]
        record = {**res, "transaction_id": tid, "user_id": user["user_id"],
                  "sender_upi": sender, "receiver_upi": receiver, "amount": float(amount),
                  "amount_cents": cents, "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                  "state": "New", "money_transferred": False}
        if res["status"] == "Critical Risk":
            record.update(state="Blocked", security_review=True)
        elif res["status"] == "Safe":
            transfer(record)
        else:
            record["state"] = "Held"
            code = str(secrets.randbelow(900000)+100000) if res["status"] == "High Risk" else None
            PENDING[tid] = {"record": record, "owner": session_id, "deadline": time.monotonic()+60, "code": code}
        LIVE_TRANSACTIONS.insert(0, record)
        out = public(record)
        if tid in PENDING:
            out["expires_in"] = 60
            # Displayed only to demonstrate step-up verification; NOT real OTP.
            out["demo_code"] = PENDING[tid]["code"]
        return out

@app.route("/")
def dashboard():
    with LOCK:
        expire_holds()
        rows = list(LIVE_TRANSACTIONS)
    counts = {s: sum(t["status"] == s for t in rows) for s in BANDS}
    return render_template("dashboard.html", total_txns=len(rows), fraud_count=counts["Critical Risk"],
        high_count=counts["High Risk"], suspicious_count=counts["Suspicious"], safe_count=counts["Safe"],
        total_volume=f'{sum(t["amount"] for t in rows):,.2f}',
        blocked_volume=f'{sum(t["amount"] for t in rows if t["state"]=="Blocked"):,.2f}',
        fraud_rate=round(counts["Critical Risk"]/max(1,len(rows))*100,2), recent_txns=rows[:15], active_page="dashboard")

@app.route("/simulator")
def simulator():
    return render_template("simulator.html",users=COMMON_USERS,merchants=TRUSTED_MERCHANTS,
        suspicious_receivers=SUSPICIOUS_RECEIVERS,active_page="simulator")

@app.route("/transactions")
def transactions():
    status = request.args.get("status","all")
    with LOCK:
        expire_holds()
        rows = [t for t in LIVE_TRANSACTIONS if status=="all" or t["status"].lower()==status.lower()]
    return render_template("transactions.html",transactions=rows,status_filter=status,active_page="transactions")

@app.route("/models")
def models():
    fresh = engine.metadata.get("risk_policy_version") == 3
    return render_template("models.html", metrics=engine.metadata.get("metrics",{}) if fresh else {},
        feature_importances=engine.metadata.get("feature_importances",[]),
        dataset_stats=engine.metadata.get("dataset_stats",{}),active_page="models",legacy_metrics=not fresh,
        validation_policy=engine.metadata.get("validation_policy",{}) if fresh else {},
        test_policy=engine.metadata.get("test_policy",{}) if fresh else {})

@app.route("/methodology")
def methodology():
    return render_template("methodology.html",active_page="methodology")

@app.route("/batch")
def batch():
    return render_template("batch.html",active_page="batch")

@app.post("/api/predict")
def api_predict():
    try:
        return jsonify(success=True,transaction=process(request.get_json(silent=True),owner()))
    except (ValueError, TypeError, OverflowError) as exc:
        return jsonify(success=False,error=str(exc)),400

@app.post("/api/transactions/<tid>/decision")
def decide(tid):
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(success=False,error="Invalid decision"),400
    with LOCK:
        expire_holds()
        item = PENDING.get(tid)
        if item is None or item["owner"] != owner():
            return jsonify(success=False,error="No active hold for this session (blocked, expired or already resolved)"),409
        record = item["record"]
        if data.get("decision") == "cancel":
            record.update(state="Cancelled", action="Cancelled by user")
        elif data.get("decision") == "proceed":
            if record["status"] == "Critical Risk":
                return jsonify(success=False,error="Critical risk cannot be overridden"),403
            if record["status"] == "High Risk" and not secrets.compare_digest(str(data.get("code","")),item["code"]):
                record.update(state="Cancelled",action="Demo verification failed")
            else:
                transfer(record)
        else:
            return jsonify(success=False,error="Choose proceed or cancel"),400
        del PENDING[tid]
        return jsonify(success=True,transaction=public(record))

@app.post("/api/simulate-stream")
def api_simulate_stream():
    user=random.choice(COMMON_USERS)
    risky=random.choice([False,False,True])
    data={"user_id":user["user_id"],"receiver_upi":random.choice(SUSPICIOUS_RECEIVERS if risky else TRUSTED_MERCHANTS),
          "amount":min(30000,user["avg_amt"]*(8 if risky else 1)), "hour":3 if risky else 14,
          "is_new_device":int(risky),"velocity_score":.9 if risky else .1,
          "is_receiver_flagged":int(risky),"tx_count_1h":8 if risky else 1}
    try:
        return jsonify(success=True,transaction=process(data,owner()))
    except ValueError as exc:
        return jsonify(success=False,error=str(exc)),400

@app.get("/api/chart-data")
def chart_data():
    with LOCK:
        expire_holds()
        recent=LIVE_TRANSACTIONS[:20][::-1]
        counts=[sum(t["status"]==s for t in LIVE_TRANSACTIONS) for s in BANDS]
    return jsonify(distribution={"labels":list(BANDS),"counts":counts},
        recent_trend={"labels":[t["transaction_id"][-4:] for t in recent],"scores":[t["risk_score"] for t in recent]})

@app.post("/api/run-batch-benchmark")
def batch_benchmark():
    start=time.perf_counter()
    df=pd.read_csv(DATA_PATH).sample(n=500,random_state=42).reset_index(drop=True)
    scores,*_=engine.score_batch(df)
    counts={s:0 for s in BANDS}
    flagged=[]
    for i,s in enumerate(scores):
        status,badge,action=risk_band(float(s))
        counts[status]+=1
        if status!="Safe":
            row=df.iloc[i]
            flagged.append({"transaction_id":str(row["transaction_id"]),"sender_upi":str(row["sender_upi"]),
                "receiver_upi":str(row["receiver_upi"]),"amount":float(row["amount"]),"risk_score":float(s),
                "status":status,"badge_class":badge,"reason":action})
    elapsed=max(.001,time.perf_counter()-start)
    return jsonify(total=500,duration_sec=round(elapsed,3),tps=round(500/elapsed,1),
        safe=counts["Safe"],suspicious=counts["Suspicious"],high=counts["High Risk"],fraud=counts["Critical Risk"],flagged=flagged[:35])

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
