import yfinance as yf

def get_price_feed(ticker: str) -> str:
    """
    Fetches real-time / latest pricing info for the stock ticker using yfinance.
    
    Args:
        ticker (str): The stock ticker (e.g. 'AAPL', 'TSLA').
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        prev_close = info.get('previousClose')
        
        # If real-time info dict is empty, fetch historical data to extract
        if not current_price:
            df = t.history(period="5d")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
            else:
                raise ValueError("No historical price data found via yfinance.")
        
        day_high = info.get('dayHigh') or (df['High'].iloc[-1] if 'df' in locals() and not df.empty else current_price)
        day_low = info.get('dayLow') or (df['Low'].iloc[-1] if 'df' in locals() and not df.empty else current_price)
        volume = info.get('volume') or (df['Volume'].iloc[-1] if 'df' in locals() and not df.empty else 0)
        fifty_two_week_high = info.get('fiftyTwoWeekHigh') or day_high
        fifty_two_week_low = info.get('fiftyTwoWeekLow') or day_low
        
        # Format output as a clean string
        lines = [
            f"Ticker: {ticker}",
            f"Current Price: {current_price}",
            f"Previous Close: {prev_close}",
            f"Daily High: {day_high}",
            f"Daily Low: {day_low}",
            f"Volume: {volume}",
            f"52-Week High: {fifty_two_week_high}",
            f"52-Week Low: {fifty_two_week_low}"
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching price feed for {ticker}: {str(e)}"
