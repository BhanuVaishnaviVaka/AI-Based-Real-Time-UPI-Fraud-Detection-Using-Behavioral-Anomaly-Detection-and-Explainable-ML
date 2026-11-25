import unittest
from ml.reputation import receiver_reputation, combined_risk, risk_band

class PreventionPolicyTests(unittest.TestCase):
    def test_boundaries(self):
        for n, expected in [(0,"Safe"),(39.9,"Safe"),(40,"Suspicious"),(74.9,"Suspicious"),(75,"High Risk"),(89.9,"High Risk"),(90,"Critical Risk"),(100,"Critical Risk")]:
            self.assertEqual(risk_band(n)[0],expected)
    def test_reputation(self):
        self.assertGreater(receiver_reputation("canteen.central@upi")["score"],80)
        self.assertLess(receiver_reputation("crypto_fastpay_77@axl")["score"],20)
        self.assertEqual(receiver_reputation("unknown@demo")["score"],50)
    def test_reputation_never_lowers_ml_risk(self):
        self.assertGreaterEqual(combined_risk(.9,.9,.9,100),89.9)
        self.assertEqual(combined_risk(0,0,0,0),100)

if __name__=="__main__":
    unittest.main()
