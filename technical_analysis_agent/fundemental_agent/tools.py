import json
import os
import time
import yfinance as yf
import pandas as pd
CACHE_EXPIRATION_SECONDS = 30 * 24 * 60 * 60  

def get_comprehensive_financials(ticker: str) -> str:
    """
    Retrieves both historical financial arrays and current forward/trailing valuation metrics.
    Checks local cache first.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_lake_dir = os.path.abspath(os.path.join(current_dir, "..", "local_data_lake"))
    os.makedirs(data_lake_dir, exist_ok=True)
    file_path = os.path.join(data_lake_dir, f"{ticker}_comprehensive.json")
    
    # 1. CHECK CACHE
    if os.path.exists(file_path) and (time.time() - os.path.getmtime(file_path)) < CACHE_EXPIRATION_SECONDS:
        with open(file_path, "r") as f:
            return f.read() 
                
    # 2. FETCH NEW DATA
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.financials
        cash_flow = stock.cashflow
        info = stock.info
        
        if income_stmt.empty:
            return json.dumps({"error": f"No data found for {ticker}."})

        # Process Historicals
        historical_records = []
        for date in income_stmt.columns:
            year = date.year
            def get_metric(df, row_name):
                try:
                    val = df.loc[row_name, date]
                    return None if pd.isna(val) else float(val)
                except:
                    return None

            rev_raw = get_metric(income_stmt, 'Total Revenue')
            if rev_raw is None:
                continue

            net_inc_raw = get_metric(income_stmt, 'Net Income')
            fcf_raw = get_metric(cash_flow, 'Free Cash Flow')
            eps_raw = get_metric(income_stmt, 'Basic EPS')

            historical_records.append({
                "fiscal_year": year,
                "revenue_millions": round(rev_raw / 1e6, 2),
                "net_income_millions": round((net_inc_raw if net_inc_raw is not None else 0.0) / 1e6, 2),
                "free_cash_flow_millions": round((fcf_raw if fcf_raw is not None else 0.0) / 1e6, 2),
                "eps": round(eps_raw if eps_raw is not None else 0.0, 2)
            })

        # Process Valuation (Safely handle missing data for unprofitable tickers)
        valuation_records = {
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook")
        }

        # Combine into master payload
        final_payload = {
            "historical_data": historical_records,
            "current_valuation": valuation_records
        }
        
        json_output = json.dumps(final_payload, indent=4)
        
        # 3. SAVE & RETURN
        with open(file_path, "w") as f:
            f.write(json_output)
            
        return json_output
        
    except Exception as e:
        return json.dumps({"error": f"API execution failed: {str(e)}"})

def calculate_fundamental_scores(ticker: str) -> dict:
    """Calculates Revenue CAGR, EPS trend, Valuation Verdict, and Fundamental Health Score programmatically."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "scoring_rules.json")
    
    with open(config_path, "r") as f:
        config = json.load(f)
        
    fund_cfg = config["fundamental_scoring"]
    weights = fund_cfg["weights"]
    thresholds = fund_cfg["thresholds"]
    
    # Get financials JSON
    try:
        financials_raw = get_comprehensive_financials(ticker)
        financials = json.loads(financials_raw)
    except Exception as e:
        financials = {"error": str(e)}
    
    if "error" in financials or not financials.get("historical_data"):
        return {
            "ticker": ticker,
            "data_points": 0,
            "revenue_cagr": 0.0,
            "eps_trend_verdict": "NEGATIVE",
            "valuation_verdict": "DISTRESSED",
            "fundamental_score": -10,
            "valuation_metrics": {
                "trailing_pe": None,
                "forward_pe": None,
                "peg_ratio": None,
                "price_to_book": None
            },
            "timeframe_breakdown": [],
            "score_breakdown": {
                "cagr_points": 0,
                "eps_points": 0,
                "fcf_points": 0,
                "pe_growth_points": 0,
                "peg_points": 0,
                "high_pe_penalty": 0,
                "cash_burn_penalty": -10
            }
        }
        
    records = sorted(financials["historical_data"], key=lambda x: x["fiscal_year"])
    val = financials.get("current_valuation", {})
    
    # 1. Revenue CAGR
    cagr = 0.0
    if len(records) >= 2:
        start_year = records[0]["fiscal_year"]
        end_year = records[-1]["fiscal_year"]
        start_rev = records[0]["revenue_millions"]
        end_rev = records[-1]["revenue_millions"]
        years = end_year - start_year
        if years > 0 and start_rev > 0 and end_rev > 0:
            cagr = ((end_rev / start_rev) ** (1 / years) - 1) * 100
            
    # 2. EPS Trend
    eps_vals = [r["eps"] for r in records if r["eps"] is not None]
    if not eps_vals:
        eps_trend = "NEGATIVE"
    elif all(e < 0 for e in eps_vals):
        eps_trend = "NEGATIVE"
    elif len(eps_vals) >= 2:
        is_increasing = all(eps_vals[i] > eps_vals[i-1] for i in range(1, len(eps_vals)))
        if is_increasing:
            eps_trend = "ACCELERATING"
        elif eps_vals[-1] > eps_vals[0]:
            eps_trend = "STABLE"
        else:
            eps_trend = "DECELERATING"
    else:
        eps_trend = "STABLE"
        
    # 3. Fundamental Health Score (Symmetric: Starts at 0, goes from -10 to +10)
    score = 0
    cagr_points = 0
    eps_points = 0
    fcf_points = 0
    pe_growth_points = 0
    peg_points = 0
    high_pe_penalty = 0
    cash_burn_penalty = 0
    
    # Revenue growth
    if cagr > 15:
        cagr_points = weights["cagr_positive_points"]
    elif cagr > 5:
        cagr_points = weights["cagr_positive_points"] // 2
    elif cagr < 0:
        cagr_points = -1 # penalty
    score += cagr_points
        
    # EPS trend
    if eps_trend == "ACCELERATING":
        eps_points = weights["eps_growing_points"]
    elif eps_trend == "STABLE":
        eps_points = weights["eps_growing_points"] // 2
    elif eps_trend == "DECELERATING":
        eps_points = -1
    elif eps_trend == "NEGATIVE":
        eps_points = -2
    score += eps_points
        
    # Free Cash Flow
    fcf_vals = [r["free_cash_flow_millions"] for r in records if r["free_cash_flow_millions"] is not None]
    if fcf_vals:
        if all(f > 0 for f in fcf_vals):
            fcf_points = weights["fcf_positive_points"]
        elif fcf_vals[-1] < 0:
            fcf_points = -1
        elif all(f < 0 for f in fcf_vals):
            fcf_points = -2
    score += fcf_points
            
    # Valuation parameters
    trailing_pe = val.get("trailing_pe")
    forward_pe = val.get("forward_pe")
    peg_ratio = val.get("peg_ratio")
    price_to_book = val.get("price_to_book")
    
    # PE Growth point
    if forward_pe and trailing_pe and forward_pe > 0 and trailing_pe > 0:
        if forward_pe < trailing_pe:
            pe_growth_points = weights["valuation_pe_growth_points"]
    score += pe_growth_points
            
    # PEG point
    if peg_ratio and 0 < peg_ratio < thresholds["peg_ratio_limit"]:
        peg_points = weights["valuation_peg_points"]
    score += peg_points
        
    # High PE Low Growth penalty
    if forward_pe and forward_pe > thresholds["high_pe_limit"] and cagr < thresholds["low_growth_limit"]:
        high_pe_penalty = weights["valuation_high_pe_low_growth_penalty"]
    score += high_pe_penalty
        
    # Unprofitable cash burn penalty
    is_burning_fcf = len(fcf_vals) > 0 and fcf_vals[-1] < 0
    is_unprofitable = (trailing_pe is None or trailing_pe <= 0)
    if is_unprofitable and is_burning_fcf:
        cash_burn_penalty = weights["valuation_unprofitable_cash_burn_penalty"]
    score += cash_burn_penalty
        
    score = max(-10, min(10, score))
    
    # 4. Valuation Verdict
    verdict = "FAIR VALUE"
    if score >= 7 or (peg_ratio and 0 < peg_ratio < 1.0):
        verdict = "UNDERVALUED"
    elif score <= 3 or (forward_pe and forward_pe > 45) or (peg_ratio and peg_ratio > 2.5):
        verdict = "OVERVALUED"
    
    if is_unprofitable and is_burning_fcf:
        verdict = "DISTRESSED"
        
    return {
        "ticker": ticker,
        "data_points": len(records),
        "revenue_cagr": round(cagr, 2),
        "eps_trend_verdict": eps_trend,
        "valuation_verdict": verdict,
        "fundamental_score": score,
        "valuation_metrics": {
            "trailing_pe": trailing_pe,
            "forward_pe": forward_pe,
            "peg_ratio": peg_ratio,
            "price_to_book": price_to_book
        },
        "timeframe_breakdown": records,
        "score_breakdown": {
            "cagr_points": cagr_points,
            "eps_points": eps_points,
            "fcf_points": fcf_points,
            "pe_growth_points": pe_growth_points,
            "peg_points": peg_points,
            "high_pe_penalty": high_pe_penalty,
            "cash_burn_penalty": cash_burn_penalty
        }
    }