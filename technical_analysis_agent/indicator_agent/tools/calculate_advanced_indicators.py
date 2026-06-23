import pandas as pd
from .fetch_common import fetch_data
from .calculate_rsi import calculate_rsi
from .calculate_alligator import calculate_alligator
from .calculate_divergence import find_rsi_divergence

def calculate_advanced_indicators(ticker: str) -> str:
    """
    Calculates Williams Alligator and RSI Divergences across all timeframes.
    
    Args:
        ticker (str): The exact stock ticker symbol (e.g., 'AAPL', 'TSLA').
    """
    timeframes = ['4h', '1d', '1w', '1q']
    
    alligator_results = [f"### Williams Alligator Analysis for {ticker}"]
    divergence_results = [f"### RSI Divergence Analysis for {ticker}"]
    
    for tf in timeframes:
        try:
            df = fetch_data(ticker, tf)
            
            # Williams Alligator requires at least 21 bars to compute Jaw (length 13 + offset 8)
            if len(df) < 21:
                alligator_results.append(f"- **[{tf.upper()}]**: Insufficient data.")
                divergence_results.append(f"- **[{tf.upper()}]**: Insufficient data.")
                continue
            
            # Calculate RSI
            df['RSI'] = calculate_rsi(df['Close'], length=14)
            
            # Calculate Alligator using standard Median Price
            alli = calculate_alligator(df)
            df = pd.concat([df, alli], axis=1)
            
            # Safely resolve columns by prefix to handle varied pandas-ta version schemas
            jaw_col = next((c for c in alli.columns if c.startswith('AGj')), alli.columns[0])
            teeth_col = next((c for c in alli.columns if c.startswith('AGt')), alli.columns[1])
            lips_col = next((c for c in alli.columns if c.startswith('AGl')), alli.columns[2])
            
            current_jaw = df[jaw_col].iloc[-1]
            current_teeth = df[teeth_col].iloc[-1]
            current_lips = df[lips_col].iloc[-1]
            
            if pd.isna(current_jaw) or pd.isna(current_teeth) or pd.isna(current_lips):
                alligator_state = "Insufficient data (NaN values)"
                alligator_results.append(f"- **[{tf.upper()}]**: Jaw={current_jaw}, Teeth={current_teeth}, Lips={current_lips} | State: {alligator_state}")
            else:
                if current_lips > current_teeth > current_jaw:
                    alligator_state = "Bullish (Eating / Open Mouth Up)"
                elif current_lips < current_teeth < current_jaw:
                    alligator_state = "Bearish (Eating / Open Mouth Down)"
                else:
                    alligator_state = "Sleeping / Converging"
                    
                alligator_results.append(f"- **[{tf.upper()}]**: Jaw={current_jaw:.2f}, Teeth={current_teeth:.2f}, Lips={current_lips:.2f} | State: {alligator_state}")
            
            # Divergence analysis
            bull_div, bear_div = find_rsi_divergence(df)
            divergence_results.append(f"- **[{tf.upper()}]**: Bullish Divergence: {bull_div} | Bearish Divergence: {bear_div}")
            
        except Exception as e:
            alligator_results.append(f"- **[{tf.upper()}]**: Error - {str(e)}")
            divergence_results.append(f"- **[{tf.upper()}]**: Error - {str(e)}")
            
    return "\n".join(alligator_results) + "\n\n" + "\n".join(divergence_results)
