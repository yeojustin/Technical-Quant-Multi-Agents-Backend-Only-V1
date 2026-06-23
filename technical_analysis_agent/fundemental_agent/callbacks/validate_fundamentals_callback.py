import re
import yfinance as yf
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from ..schemas import FundamentalStrategyOutput, CurrentValuation



def validate_fundamentals_callback(callback_context: CallbackContext) -> types.Content | None:
    """Checks if yfinance can retrieve financial statements for the ticker.
    If not, bypasses the fundamental analysis workflow and populates default/skipped values.
    """
    state = callback_context.state
    ticker = state.get("ticker")
    if not ticker:
        # Fallback to extract ticker from user query if state doesn't have it
        session = callback_context.session
        user_query = ""
        for event in reversed(session.events):
            if event.author == "user" and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        user_query = part.text
                        break
                if user_query:
                    break
        if user_query:
            match = re.search(r'\b\^?[A-Z]{1,6}(?:[\.\-][A-Z0-9]+)?(?:\=[A-Z0-9]+)?\b', user_query)
            ticker = match.group(0) if match else None
            if not ticker:
                words = user_query.strip().split()
                if words:
                    ticker = words[-1].upper().strip("?.!,")
            if ticker:
                state["ticker"] = ticker

    if not ticker:
        return None

    has_financials = True
    try:
        stock = yf.Ticker(ticker)
        income_stmt = stock.financials
        if income_stmt.empty:
            has_financials = False
    except Exception:
        has_financials = False

    if not has_financials:
        # Instantiate the schema classes to guarantee type-safety and structural correctness
        skipped_obj = FundamentalStrategyOutput(
            ticker=ticker,
            data_points=0,
            revenue_cagr=0.0,
            eps_trend_verdict="NEGATIVE",
            valuation_verdict="DISTRESSED",
            fundamental_score=0,
            valuation_metrics=CurrentValuation(
                trailing_pe=None,
                forward_pe=None,
                peg_ratio=None,
                price_to_book=None
            ),
            catalyst_summary="Fundamental analysis skipped: No financial statements or valuation data found on yfinance.",
            timeframe_breakdown=[]
        )
        
        # Convert Pydantic object to a standard Python dictionary to ensure JSON serializability in ADK
        if hasattr(skipped_obj, "model_dump"):
            skipped_output = skipped_obj.model_dump()
        else:
            skipped_output = skipped_obj.dict()
            
        # Write to the state key that fundamental_strategy_agent would have populated
        state["fundamental_results"] = skipped_output
        
        # Return a Content object to skip execution of the fundamental pipeline
        return types.Content(
            parts=[
                types.Part.from_text(
                    text="⚠️ Fundamental analysis workflow skipped: No financial data could be retrieved."
                )
            ],
            role="model"
        )
        
    return None
