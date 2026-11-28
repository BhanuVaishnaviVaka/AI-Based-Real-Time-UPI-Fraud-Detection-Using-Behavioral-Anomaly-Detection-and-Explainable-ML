import unittest
from unittest.mock import patch
import app as a
from ml.reputation import risk_band

class TransactionWorkflowTests(unittest.TestCase):
    def setUp(self):
        a.LIVE_TRANSACTIONS.clear()
        a.PENDING.clear()
        a.BALANCES.clear()
        self.client=a.app.test_client()
        self.payload={"user_id":"usr_anil","receiver_upi":"canteen.central@upi","amount":500}
    def submit(self, score):
        status,badge,action=risk_band(score)
        with patch.object(a.engine,"score_transaction",return_value={"risk_score":score,"status":status,"badge_class":badge,"action":action}):
            r=self.client.post("/api/predict",json=self.payload)
        self.assertEqual(r.status_code,200,r.get_json())
        return r.get_json()["transaction"]
    def decide(self,tx,**kwargs):
        return self.client.post("/api/transactions/"+tx["transaction_id"]+"/decision",json=kwargs)
    def test_safe(self):
        self.assertEqual(self.submit(15)["sender_balance"],99500)
    def test_critical_cannot_release(self):
        tx=self.submit(95)
        self.assertEqual(tx["state"],"Blocked")
        self.assertEqual(self.decide(tx,decision="proceed").status_code,409)
        self.assertEqual(a.balance("anil.k@okhdfcbank"),10000000)
    def test_suspicious_release_once(self):
        tx=self.submit(55)
        self.assertEqual(tx["sender_balance"],100000)
        self.assertEqual(self.decide(tx,decision="proceed").get_json()["transaction"]["state"],"Released")
        self.assertEqual(self.decide(tx,decision="proceed").status_code,409)
    def test_high_verification(self):
        tx=self.submit(80)
        self.assertEqual(self.decide(tx,decision="proceed",code="wrong").get_json()["transaction"]["state"],"Cancelled")
        tx=self.submit(80)
        self.assertTrue(self.decide(tx,decision="proceed",code=tx["demo_code"]).get_json()["transaction"]["money_transferred"])
    def test_cancel_expiry_and_other_session(self):
        tx=self.submit(50)
        stranger=a.app.test_client()
        self.assertEqual(stranger.post("/api/transactions/"+tx["transaction_id"]+"/decision",json={"decision":"proceed"}).status_code,409)
        self.assertEqual(self.decide(tx,decision="cancel").get_json()["transaction"]["state"],"Cancelled")
        tx=self.submit(50)
        a.PENDING[tx["transaction_id"]]["deadline"]=0
        self.assertEqual(self.decide(tx,decision="proceed").status_code,409)
        self.assertEqual(a.LIVE_TRANSACTIONS[0]["state"],"Expired")
        self.assertEqual(a.balance("anil.k@okhdfcbank"),10000000)
    def test_real_engine_and_pages(self):
        tx=self.client.post("/api/predict",json=self.payload).get_json()["transaction"]
        self.assertIn("shap",tx["explanations"])
        self.assertTrue(tx["explanations"]["shap"]["contributions"])
        for path in ("/","/simulator","/transactions","/models","/batch","/methodology","/api/chart-data"):
            self.assertEqual(self.client.get(path).status_code,200,path)
        batch=self.client.post("/api/run-batch-benchmark").get_json()
        self.assertEqual(sum(batch[k] for k in ("safe","suspicious","high","fraud")),500)
    def test_bad_amount(self):
        self.assertEqual(self.client.post("/api/predict",json={**self.payload,"amount":-5}).status_code,400)

if __name__=="__main__":
    unittest.main()
