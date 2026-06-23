import pandas as pd

def find_rsi_divergence(df: pd.DataFrame, window: int = 5, max_distance: int = 35, min_distance: int = 5) -> tuple[str, str]:
    k = window // 2
    if 'RSI' not in df.columns or len(df) < window * 2:
        return "None", "None"
    
    # Use High/Low for extrema, falling back to Close if missing
    price_low = df['Low'] if 'Low' in df.columns else df['Close']
    price_high = df['High'] if 'High' in df.columns else df['Close']
    
    df_clean = pd.DataFrame({
        'Low': price_low,
        'High': price_high,
        'Close': df['Close'],
        'RSI': df['RSI']
    }).dropna()
    
    n = len(df_clean)
    if n < window * 2:
        return "None", "None"
        
    local_minima = []
    local_maxima = []
    
    for i in range(k, n - k):
        low_val = df_clean['Low'].iloc[i]
        high_val = df_clean['High'].iloc[i]
        rsi_val = df_clean['RSI'].iloc[i]
        
        low_window = df_clean['Low'].iloc[i-k:i+k+1]
        high_window = df_clean['High'].iloc[i-k:i+k+1]
        rsi_window = df_clean['RSI'].iloc[i-k:i+k+1]
        
        # Bullish: price low is local minimum AND RSI is local minimum
        if low_val == low_window.min() and rsi_val == rsi_window.min():
            local_minima.append({
                'index': i,
                'price': low_val,
                'rsi': rsi_val
            })
            
        # Bearish: price high is local maximum AND RSI is local maximum
        if high_val == high_window.max() and rsi_val == rsi_window.max():
            local_maxima.append({
                'index': i,
                'price': high_val,
                'rsi': rsi_val
            })
            
    bull_div = "None"
    if len(local_minima) >= 2:
        # Start from the most recent local minimum as the right point (m2)
        # and look backward for a suitable left point (m1)
        for i_m2 in range(len(local_minima) - 1, -1, -1):
            m2 = local_minima[i_m2]
            found = False
            for i_m1 in range(i_m2 - 1, -1, -1):
                m1 = local_minima[i_m1]
                dist = m2['index'] - m1['index']
                if dist > max_distance:
                    break  # since we are scanning backward, further ones will be even further
                if dist >= min_distance:
                    if m2['price'] < m1['price'] and m2['rsi'] > m1['rsi']:
                        bull_div = f"Bullish Divergence (Price: {m1['price']:.2f}->{m2['price']:.2f}, RSI: {m1['rsi']:.1f}->{m2['rsi']:.1f}, Dist: {dist} bars)"
                        found = True
                        break
            if found:
                break
            
    bear_div = "None"
    if len(local_maxima) >= 2:
        for i_p2 in range(len(local_maxima) - 1, -1, -1):
            p2 = local_maxima[i_p2]
            found = False
            for i_p1 in range(i_p2 - 1, -1, -1):
                p1 = local_maxima[i_p1]
                dist = p2['index'] - p1['index']
                if dist > max_distance:
                    break
                if dist >= min_distance:
                    if p2['price'] > p1['price'] and p2['rsi'] < p1['rsi']:
                        bear_div = f"Bearish Divergence (Price: {p1['price']:.2f}->{p2['price']:.2f}, RSI: {p1['rsi']:.1f}->{p2['rsi']:.1f}, Dist: {dist} bars)"
                        found = True
                        break
            if found:
                break
            
    return bull_div, bear_div
