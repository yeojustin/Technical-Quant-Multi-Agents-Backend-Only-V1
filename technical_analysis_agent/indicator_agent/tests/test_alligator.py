import unittest
from technical_analysis_agent.indicator_agent.tools.calculate_advanced_indicators import calculate_advanced_indicators

class TestWilliamsAlligator(unittest.TestCase):
    def test_aapl_alligator(self):
        print("\nRunning Test: AAPL Williams Alligator & Divergences")
        output = calculate_advanced_indicators("AAPL")
        print(output)
        self.assertIn("Williams Alligator Analysis for AAPL", output)
        self.assertIn("RSI Divergence Analysis for AAPL", output)

    def test_tsla_alligator(self):
        print("\nRunning Test: TSLA Williams Alligator & Divergences")
        output = calculate_advanced_indicators("TSLA")
        print(output)
        self.assertIn("Williams Alligator Analysis for TSLA", output)
        self.assertIn("RSI Divergence Analysis for TSLA", output)

if __name__ == '__main__':
    unittest.main()
