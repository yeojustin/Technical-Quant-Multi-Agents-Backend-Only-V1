from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .schemas import FundamentalStrategyOutput
from .tools import get_comprehensive_financials, calculate_fundamental_scores
from .callbacks.validate_fundamentals_callback import validate_fundamentals_callback

from .prompt import FUNDAMENTAL_STRATEGY_AGENT_INS, FUNDAMENTAL_PRESENTATION_AGENT_INS

class FundamentalGathererAgent(BaseAgent):
    """Programmatic agent that gathers comprehensive financials and calculates fundamental scores without calling LLM."""
    
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        ticker = state.get("ticker", "UNKNOWN")
        
        try:
            financials_raw = get_comprehensive_financials(ticker)
            state["fundamental_raw"] = financials_raw
            
            calculated_scores = calculate_fundamental_scores(ticker)
            state["fundamental_calculated_scores"] = calculated_scores
            
            message = f"Successfully gathered financials and calculated fundamental scores for {ticker}."
        except Exception as e:
            message = f"Error gathering fundamentals for {ticker}: {str(e)}"
            
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            message=message
        )

fundamental_gatherer = FundamentalGathererAgent(name="fundamental_gatherer")

fundamental_strategy_agent = LlmAgent(
    name="fundamental_strategy_agent",
    model="gemini-2.5-pro", 
    instruction=FUNDAMENTAL_STRATEGY_AGENT_INS,
    output_schema=FundamentalStrategyOutput,
    output_key="fundamental_results"
)

# # For testing
# fundamental_presentation_agent = LlmAgent(
#     name="fundamental_presentation_agent",
#     model="gemini-2.5-flash",
#     instruction=FUNDAMENTAL_PRESENTATION_AGENT_INS
# )


# Core Pipeline orchestration
fundamental_agent_pipeline = SequentialAgent(
    name="FundamentalAgentPipeline",
    sub_agents=[fundamental_gatherer, fundamental_strategy_agent],
    before_agent_callback=validate_fundamentals_callback,
    description="Pipeline that gathers multi-timeframe indicator data and runs strategy analysis."
)