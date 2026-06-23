import os
import json
import pandas as pd
from .fetch_common import fetch_data
from .calculate_rsi import calculate_rsi
from .calculate_macd import calculate_macd
from .calculate_alligator import calculate_alligator
from .calculate_divergence import find_rsi_divergence

def calculate_indicator_scores(ticker: str) -> dict:
    # 1. Load config
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "config", "scoring_rules.json")
    
    with open(config_path, "r") as f:
        config = json.load(f)
        
    tech_cfg = config["technical_scoring"]
    st_cfg = tech_cfg["short_term"]
    lt_cfg = tech_cfg["long_term"]
    
    timeframes = ['4h', '1d', '1w', '1q']
    data = {}
    
    # Gather telemetry for each timeframe
    for tf in timeframes:
        try:
            df = fetch_data(ticker, tf)
            df['RSI'] = calculate_rsi(df['Close'], length=14)
            macd_df = calculate_macd(df['Close'])
            df = pd.concat([df, macd_df], axis=1)
            
            # Find divergence
            bull_div, bear_div = find_rsi_divergence(df)
            
            # Williams Alligator
            alligator_state = "Sleeping / Converging"
            if len(df) >= 21:
                alli = calculate_alligator(df)
                jaw_col = next((c for c in alli.columns if c.startswith('AGj')), alli.columns[0])
                teeth_col = next((c for c in alli.columns if c.startswith('AGt')), alli.columns[1])
                lips_col = next((c for c in alli.columns if c.startswith('AGl')), alli.columns[2])
                
                current_jaw = alli[jaw_col].iloc[-1]
                current_teeth = alli[teeth_col].iloc[-1]
                current_lips = alli[lips_col].iloc[-1]
                
                if not (pd.isna(current_jaw) or pd.isna(current_teeth) or pd.isna(current_lips)):
                    if current_lips > current_teeth > current_jaw:
                        alligator_state = "Bullish"
                    elif current_lips < current_teeth < current_jaw:
                        alligator_state = "Bearish"
            
            macd_col = macd_df.columns[0]
            hist_col = macd_df.columns[1]
            
            data[tf] = {
                "rsi_current": float(df['RSI'].iloc[-1]) if not pd.isna(df['RSI'].iloc[-1]) else None,
                "rsi_prev": float(df['RSI'].iloc[-2]) if len(df) > 1 and not pd.isna(df['RSI'].iloc[-2]) else None,
                "macd_hist_current": float(df[hist_col].iloc[-1]) if not pd.isna(df[hist_col].iloc[-1]) else 0.0,
                "macd_hist_prev": float(df[hist_col].iloc[-2]) if len(df) > 1 and not pd.isna(df[hist_col].iloc[-2]) else 0.0,
                "alligator_state": alligator_state,
                "bullish_divergence": bull_div,
                "bearish_divergence": bear_div,
                "has_data": True
            }
        except Exception:
            data[tf] = {
                "rsi_current": None,
                "rsi_prev": None,
                "macd_hist_current": 0.0,
                "macd_hist_prev": 0.0,
                "alligator_state": "Sleeping / Converging",
                "bullish_divergence": "None",
                "bearish_divergence": "None",
                "has_data": False
            }

    # 2. Compute Short-Term Score (4H, 1D, 1W)
    short_term_score = 0
    st_breakdown = {}
    
    # Basic Momentum & Swing (1W, 1D): weight +/- 2 each
    w_macd_swing = st_cfg["weights"]["macd_weekly_daily_acceleration"]
    for tf in ['1w', '1d']:
        tf_data = data[tf]
        score_contrib = 0
        if tf_data["has_data"]:
            if tf_data["macd_hist_current"] > tf_data["macd_hist_prev"]:
                score_contrib = w_macd_swing
            elif tf_data["macd_hist_current"] < tf_data["macd_hist_prev"]:
                score_contrib = -w_macd_swing
        short_term_score += score_contrib
        st_breakdown[f"macd_{tf}"] = score_contrib

    # Basic Execution (4H): weight +/- 1
    w_macd_4h = st_cfg["weights"]["macd_4h_momentum"]
    tf_data_4h = data['4h']
    score_4h = 0
    if tf_data_4h["has_data"]:
        if tf_data_4h["macd_hist_current"] > 0:
            score_4h = w_macd_4h
        elif tf_data_4h["macd_hist_current"] < 0:
            score_4h = -w_macd_4h
    short_term_score += score_4h
    st_breakdown["macd_4h"] = score_4h

    # Williams Alligator (4H, 1D, 1W): weight +/- 1 each
    w_alli = st_cfg["weights"]["alligator_mouth"]
    for tf in ['4h', '1d', '1w']:
        tf_data = data[tf]
        score_alli = 0
        if tf_data["has_data"]:
            if tf_data["alligator_state"] == "Bullish":
                score_alli = w_alli
            elif tf_data["alligator_state"] == "Bearish":
                score_alli = -w_alli
        short_term_score += score_alli
        st_breakdown[f"alligator_{tf}"] = score_alli

    # RSI Divergences (4H, 1D, 1W): weight +/- 2 (consolidated check)
    w_div = st_cfg["weights"]["rsi_divergence"]
    bull_div_any = any(data[tf]["bullish_divergence"] != "None" for tf in ['4h', '1d', '1w'])
    bear_div_any = any(data[tf]["bearish_divergence"] != "None" for tf in ['4h', '1d', '1w'])
    
    score_div = 0
    if bull_div_any and not bear_div_any:
        score_div = w_div
    elif bear_div_any and not bull_div_any:
        score_div = -w_div
    short_term_score += score_div
    st_breakdown["rsi_divergence"] = score_div

    # Overextension Override
    overbought_th = st_cfg["overrides"]["weekly_rsi_overbought"]
    oversold_th = st_cfg["overrides"]["weekly_rsi_oversold"]
    penalty = st_cfg["overrides"]["penalty_points"]
    overextension_override_applied = False
    
    weekly_rsi = data['1w']["rsi_current"]
    if weekly_rsi is not None:
        if weekly_rsi > overbought_th:
            short_term_score -= penalty
            overextension_override_applied = True
            st_breakdown["overextension_override"] = -penalty
        elif weekly_rsi < oversold_th:
            short_term_score += penalty
            overextension_override_applied = True
            st_breakdown["overextension_override"] = penalty

    # Clamp Short-Term Score to [-10, 10]
    short_term_score = max(-10, min(10, short_term_score))

    # Short-Term Verdict
    st_verdict = "HOLD"
    if short_term_score >= st_cfg["verdict_thresholds"]["buy"]:
        st_verdict = "BUY LONG"
    elif short_term_score <= st_cfg["verdict_thresholds"]["sell"]:
        st_verdict = "SELL SHORT"

    # 3. Compute Long-Term Score (1Q)
    long_term_score = 0
    lt_breakdown = {}
    tf_data_1q = data['1q']
    
    if tf_data_1q["has_data"]:
        # Basic Macro (1Q): weight +/- 5
        w_lt_macd = lt_cfg["weights"]["macd_quarterly_health"]
        score_lt_macd = 0
        rsi_val = tf_data_1q["rsi_current"]
        macd_val = tf_data_1q["macd_hist_current"]
        
        if rsi_val is not None:
            if macd_val > 0 and (40 <= rsi_val <= 70):
                score_lt_macd = w_lt_macd
            elif macd_val < 0 or rsi_val > 75 or rsi_val < 30:
                score_lt_macd = -w_lt_macd
        long_term_score += score_lt_macd
        lt_breakdown["macd_1q"] = score_lt_macd

        # Williams Alligator (1Q): weight +/- 2
        w_lt_alli = lt_cfg["weights"]["alligator_mouth"]
        score_lt_alli = 0
        if tf_data_1q["alligator_state"] == "Bullish":
            score_lt_alli = w_lt_alli
        elif tf_data_1q["alligator_state"] == "Bearish":
            score_lt_alli = -w_lt_alli
        long_term_score += score_lt_alli
        lt_breakdown["alligator_1q"] = score_lt_alli

        # RSI Divergences (1Q): weight +/- 3
        w_lt_div = lt_cfg["weights"]["rsi_divergence"]
        score_lt_div = 0
        if tf_data_1q["bullish_divergence"] != "None":
            score_lt_div = w_lt_div
        elif tf_data_1q["bearish_divergence"] != "None":
            score_lt_div = -w_lt_div
        long_term_score += score_lt_div
        lt_breakdown["rsi_divergence_1q"] = score_lt_div

    # Clamp Long-Term Score to [-10, 10]
    long_term_score = max(-10, min(10, long_term_score))

    # Long-Term Verdict
    lt_verdict = "HOLD"
    if long_term_score >= lt_cfg["verdict_thresholds"]["buy"]:
        lt_verdict = "BUY LONG"
    elif long_term_score <= lt_cfg["verdict_thresholds"]["sell"]:
        lt_verdict = "SELL SHORT"

    # Universal Net Score
    total_score = short_term_score + long_term_score

    return {
        "short_term_score": short_term_score,
        "short_term_recommendation": st_verdict,
        "long_term_score": long_term_score,
        "long_term_recommendation": lt_verdict,
        "total_score": total_score,
        "overextension_override_applied": overextension_override_applied,
        "breakdown": {
            "short_term": st_breakdown,
            "long_term": lt_breakdown
        },
        "telemetry": data
    }
