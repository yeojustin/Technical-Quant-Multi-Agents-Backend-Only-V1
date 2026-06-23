import yfinance as yf
import pandas as pd

def map_timeframe_to_yf(timeframe: str) -> tuple[str, str]:
    tf = timeframe.lower()
    if tf == "4h": return "730d", "60m"
    elif tf == "1d": return "10y", "1d"
    elif tf == "1w": return "10y", "1wk"
    elif tf == "1m": return "10y", "1mo"
    elif tf == "1q": return "10y", "3mo"
    return "5y", "1d"


def fetch_data(ticker: str, timeframe: str) -> pd.DataFrame:
    period, interval = map_timeframe_to_yf(timeframe)
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError("No data found.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df
