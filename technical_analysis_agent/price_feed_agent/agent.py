import yfinance as yf
from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class PriceFeedAgent(BaseAgent):
    """Programmatic agent that gathers and structures stock pricing data without calling LLM."""
    
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        ticker = state.get("ticker", "UNKNOWN")
        
        try:
            t = yf.Ticker(ticker)
            info = t.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                df = t.history(period="5d")
                if not df.empty:
                    current_price = df['Close'].iloc[-1]
                    prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
                else:
                    raise ValueError("No historical price data found.")
            else:
                prev_close = info.get('previousClose') or current_price
                
            day_high = info.get('dayHigh') or current_price
            day_low = info.get('dayLow') or current_price
            volume = info.get('volume') or 0
            fifty_two_week_high = info.get('fiftyTwoWeekHigh') or day_high
            fifty_two_week_low = info.get('fiftyTwoWeekLow') or day_low
            
            results = {
                "ticker": ticker,
                "current_price": float(current_price),
                "previous_close": float(prev_close),
                "daily_range": f"${day_low:.2f} - ${day_high:.2f}",
                "fifty_two_week_range": f"${fifty_two_week_low:.2f} - ${fifty_two_week_high:.2f}",
                "volume": int(volume)
            }
            state["price_feed_results"] = results
            message = f"Successfully fetched price feed for {ticker}."
        except Exception as e:
            message = f"Error fetching price feed for {ticker}: {str(e)}"
            
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            message=message
        )

# Core Sequential Pipeline
# price_feed_pipeline = SequentialAgent(
#     name="PriceFeedPipeline",
#     sub_agents=[PriceFeedAgent(name="price_feed_gatherer_agent")],
#     description="Pipeline that gathers live market pricing data and structures it."
# )

price_feed_agent = PriceFeedAgent(name="price_feed_agent")