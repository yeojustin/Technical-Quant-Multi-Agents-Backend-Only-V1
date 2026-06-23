import pandas as pd
import pandas_ta as ta

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    return ta.macd(series, fast=fast, slow=slow, signal=signal)
