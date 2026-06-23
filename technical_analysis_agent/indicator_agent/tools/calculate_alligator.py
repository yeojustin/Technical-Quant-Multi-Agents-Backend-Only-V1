import pandas as pd
import pandas_ta as ta

def calculate_alligator(df: pd.DataFrame) -> pd.DataFrame:
    # Standard Williams Alligator uses Median Price: (High + Low) / 2
    if 'High' in df.columns and 'Low' in df.columns:
        median_price = (df['High'] + df['Low']) / 2
    else:
        median_price = df['Close']
    
    return ta.alligator(median_price)
