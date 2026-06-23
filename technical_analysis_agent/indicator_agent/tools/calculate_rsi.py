import pandas as pd
import pandas_ta as ta

def calculate_rsi(series: pd.Series, length: int = 14) -> pd.Series:
    return ta.rsi(series, length=length)
