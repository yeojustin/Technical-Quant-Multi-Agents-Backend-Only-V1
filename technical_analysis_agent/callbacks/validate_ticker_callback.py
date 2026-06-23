import re
import yfinance as yf
from google.genai import types
from google.adk.agents.callback_context import CallbackContext


def clear_state_key(state, key: str):
    """Safely removes a key from the state dict or ADK State wrapper."""
    if isinstance(state, dict):
        state.pop(key, None)
    else:
        if hasattr(state, "_value"):
            state._value.pop(key, None)
        if hasattr(state, "_delta"):
            state._delta.pop(key, None)


def validate_ticker_callback(callback_context: CallbackContext) -> types.Content | None:
    """Validates the stock ticker exists and has pricing data using yfinance."""
    state = callback_context.state
    # Always clear stale ticker and results from previous runs at the start
    keys_to_clear = [
        "ticker",
        "fundamental_results",
        "indicator_summary",
        "indicator_advanced_summary",
        "indicator_final_strategy",
        "price_feed_raw",
        "price_feed_results",
        "sentiment_raw",
        "sentiment_results",
        "master_thesis_json",
        "final_report_markdown",
    ]
    for key in keys_to_clear:
        clear_state_key(state, key)
    session = callback_context.session
    ticker = None
    
    # 1. First, search for a ticker resolved by the supervisor/root agent in the conversation history
    for event in reversed(session.events):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    match = re.search(
                        r'Ticker:\s*\[?(\^?[A-Z0-9]{1,6}(?:[\.\-][A-Z0-9]+)?(?:\=[A-Z0-9]+)?)\]?',
                        part.text,
                        re.IGNORECASE
                    )
                    if match:
                        ticker = match.group(1).upper()
                        break
            if ticker:
                break

    # 2. If no resolved ticker is found, fall back to parsing the raw user query
    if not ticker:
        user_query = ""
        for event in reversed(session.events):
            if event.author == "user" and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        user_query = part.text
                        break
                if user_query:
                    break
                    
        if not user_query:
            return None
            
        # Match standard stock ticker symbols: optional caret, 1 to 6 uppercase letters, optional suffixes, trailing boundary
        match = re.search(r'\b\^?[A-Z]{1,6}(?:[\.\-][A-Z0-9]+)?(?:\=[A-Z0-9]+)?\b', user_query)
        ticker = match.group(0) if match else None
        
        if not ticker:
            # Fallback to the last word
            words = user_query.strip().split()
            if words:
                ticker = words[-1].upper().strip("?.!,")
                
    if not ticker:
        return None
        
    try:
        t = yf.Ticker(ticker)
        info = t.info
        # Validate existence of ticker using key fields from yfinance info payload
        if not info or not (info.get('symbol') or info.get('shortName') or info.get('currentPrice') or info.get('regularMarketPrice')):
            raise ValueError("No ticker metadata found")
        # Resolve to the official ticker symbol if returned
        if info.get('symbol'):
            ticker = info['symbol'].upper()
    except Exception:
        # Ticker not found: return friendly error to the user and break the sequential loop
        return types.Content(
            parts=[
                types.Part.from_text(
                    text=f"❌ Error: Cannot find stock ticker '{ticker}'. Please verify the symbol and try again."
                )
            ]
        )
        
    # Store ticker in session state for downstream callbacks and agents to access
    callback_context.state["ticker"] = ticker
    return None