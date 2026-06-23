import unittest
from technical_analysis_agent.indicator_agent.tools.calculate_scores import calculate_indicator_scores
from technical_analysis_agent.fundemental_agent.tools import calculate_fundamental_scores

class TestProgrammaticScoring(unittest.TestCase):
    def test_indicator_scoring_keys(self):
        print("\nRunning Test: Indicator Scoring Keys & Bounds")
        res = calculate_indicator_scores("AAPL")
        self.assertIn("short_term_score", res)
        self.assertIn("long_term_score", res)
        self.assertIn("total_score", res)
        self.assertIn("short_term_recommendation", res)
        self.assertIn("long_term_recommendation", res)
        self.assertIn("overextension_override_applied", res)
        
        # Verify bounds clamping
        self.assertTrue(-10 <= res["short_term_score"] <= 10)
        self.assertTrue(-10 <= res["long_term_score"] <= 10)
        self.assertTrue(-20 <= res["total_score"] <= 20)
        self.assertIn(res["short_term_recommendation"], ["BUY LONG", "SELL SHORT", "HOLD"])
        self.assertIn(res["long_term_recommendation"], ["BUY LONG", "SELL SHORT", "HOLD"])

    def test_fundamental_scoring_keys(self):
        print("\nRunning Test: Fundamental Scoring Keys & Bounds")
        res = calculate_fundamental_scores("AAPL")
        self.assertIn("fundamental_score", res)
        self.assertIn("valuation_verdict", res)
        self.assertIn("revenue_cagr", res)
        self.assertIn("eps_trend_verdict", res)
        self.assertIn("valuation_metrics", res)
        
        self.assertIn("score_breakdown", res)
        self.assertTrue(-10 <= res["fundamental_score"] <= 10)
        self.assertIn(res["valuation_verdict"], ["UNDERVALUED", "FAIR VALUE", "OVERVALUED", "DISTRESSED"])
        self.assertIn(res["eps_trend_verdict"], ["ACCELERATING", "STABLE", "DECELERATING", "NEGATIVE"])
        
        breakdown = res["score_breakdown"]
        self.assertIn("cagr_points", breakdown)
        self.assertIn("eps_points", breakdown)
        self.assertIn("fcf_points", breakdown)
        self.assertIn("pe_growth_points", breakdown)
        self.assertIn("peg_points", breakdown)
        self.assertIn("high_pe_penalty", breakdown)
        self.assertIn("cash_burn_penalty", breakdown)


if __name__ == '__main__':
    unittest.main()
