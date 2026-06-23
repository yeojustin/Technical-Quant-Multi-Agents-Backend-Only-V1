import pandas as pd
from .fetch_common import fetch_data
from .calculate_rsi import calculate_rsi
from .calculate_macd import calculate_macd

def calculate_all_indicators(ticker: str) -> str:
    """
    Safely calculates RSI and MACD across all timeframes in a single data pass.
    
    Args:
        ticker (str): The exact stock ticker symbol (e.g., 'AAPL', 'TSLA').
    """
    timeframes = ['4h', '1d', '1w', '1q']
    
    rsi_results = [f"### Multi-Timeframe RSI Analysis for {ticker}"]
    macd_results = [f"### Multi-Timeframe MACD Analysis for {ticker}"]
    
    for tf in timeframes:
        try:
            # 1. Fetch data ONLY ONCE per timeframe
            df = fetch_data(ticker, tf)
            
            # 2. Calculate Indicators
            df['RSI'] = calculate_rsi(df['Close'], length=14)
            macd_df = calculate_macd(df['Close'], fast=12, slow=26, signal=9)
            
            # 3. Merge safely and drop invalid rows
            df = pd.concat([df, macd_df], axis=1).dropna()
            
            # 4. Extract data safely (Ensure we have at least 2 rows for momentum checks)
            if len(df) >= 2:
                # RSI Logic
                current_rsi = df['RSI'].iloc[-1]
                prev_rsi = df['RSI'].iloc[-2]
                rsi_trend = "rising" if current_rsi > prev_rsi else "falling"
                rsi_results.append(f"- **[{tf.upper()}] RSI(14)**: {current_rsi:.2f} (Prev: {prev_rsi:.2f}, Momentum: {rsi_trend})")
                
                # MACD Logic (Using dynamic column indices to prevent pandas_ta version errors)
                macd_col = macd_df.columns[0] # MACD Line
                hist_col = macd_df.columns[1] # MACD Histogram
                
                current_macd = df[macd_col].iloc[-1]
                current_hist = df[hist_col].iloc[-1]
                prev_hist = df[hist_col].iloc[-2]
                hist_trend = "accelerating" if abs(current_hist) > abs(prev_hist) else "decelerating"
                macd_results.append(f"- **[{tf.upper()}] MACD**: Line = {current_macd:.4f} | Hist = {current_hist:.4f} ({hist_trend})")
            
            else:
                rsi_results.append(f"- **[{tf.upper()}]**: Insufficient data.")
                macd_results.append(f"- **[{tf.upper()}]**: Insufficient data.")
                
        except Exception as e:
            rsi_results.append(f"- **[{tf.upper()}]**: Error - {str(e)}")
            macd_results.append(f"- **[{tf.upper()}]**: Error - {str(e)}")
            
            
    # Combine everything into the exact text format the Strategy Agent expects
    return "\n".join(rsi_results) + "\n\n" + "\n".join(macd_results)
