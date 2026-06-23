import unittest
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from technical_analysis_agent.indicator_agent.tools.calculate_divergence import find_rsi_divergence

class TestRSIDivergence(unittest.TestCase):
    def test_aapl_divergence(self):
        print("\nRunning Test: AAPL RSI Divergence")
        df = yf.download("AAPL", period="5y", interval="1d", progress=False)
        self.assertFalse(df.empty, "Failed to download data for AAPL")
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bull_div, bear_div = find_rsi_divergence(df)
        
        print(f"AAPL Bullish Divergence: {bull_div}")
        print(f"AAPL Bearish Divergence: {bear_div}")
        self.assertIsNotNone(bull_div)
        self.assertIsNotNone(bear_div)

    def test_tsla_divergence(self):
        print("\nRunning Test: TSLA RSI Divergence")
        df = yf.download("TSLA", period="5y", interval="1d", progress=False)
        self.assertFalse(df.empty, "Failed to download data for TSLA")
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bull_div, bear_div = find_rsi_divergence(df)
        
        print(f"TSLA Bullish Divergence: {bull_div}")
        print(f"TSLA Bearish Divergence: {bear_div}")
        self.assertIsNotNone(bull_div)
        self.assertIsNotNone(bear_div)

if __name__ == '__main__':
    unittest.main()
