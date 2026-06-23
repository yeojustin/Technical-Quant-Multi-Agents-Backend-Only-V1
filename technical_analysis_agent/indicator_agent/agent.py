from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from .schemas import IndicatorStrategyOutput
from .prompt import (
    INDICATOR_STRATEGY_AGENT_INS,
    PRESENTATION_AGENT_INS
)
from .tools.calculate_all_indicators import calculate_all_indicators
from .tools.calculate_advanced_indicators import calculate_advanced_indicators
from .tools.calculate_scores import calculate_indicator_scores

class IndicatorGathererAgent(BaseAgent):
    """Programmatic agent that calculates basic and advanced technical indicators and runs mathematical scoring without calling LLM."""
    
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        ticker = state.get("ticker", "UNKNOWN")
        
        try:
            summary = calculate_all_indicators(ticker)
            state["indicator_summary"] = summary
            
            advanced_summary = calculate_advanced_indicators(ticker)
            state["indicator_advanced_summary"] = advanced_summary
            
            calculated_scores = calculate_indicator_scores(ticker)
            state["indicator_calculated_scores"] = calculated_scores
            
            message = f"Successfully gathered indicators and calculated programmatic scores for {ticker}."
        except Exception as e:
            message = f"Error gathering indicators for {ticker}: {str(e)}"
            
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            message=message
        )

# Step 2: Consolidate data into the final structured strategy schema
indicator_strategy_agent = LlmAgent(
    name="IndicatorStrategyAgent",
    model="gemini-2.5-pro",
    description="Processes raw indicator summaries to generate structured trading recommendations.",
    instruction=INDICATOR_STRATEGY_AGENT_INS,
    output_schema=IndicatorStrategyOutput,  # Strictly enforces the target schema
    output_key="indicator_final_strategy"  # Persists the final valid JSON object
)

# # For testing
# presentation_agent = LlmAgent(
#     name="PresentationAgent",
#     model="gemini-2.5-flash",
#     description="Presents the final structured strategy schema in a highly readable, professional markdown report.",
#     instruction=PRESENTATION_AGENT_INS
# )

# Core Pipeline orchestration (Sequential execution)
indicator_agent_pipeline = SequentialAgent(
    name="IndicatorAgentPipeline",
    sub_agents=[IndicatorGathererAgent(name="indicator_gatherer_agent"), indicator_strategy_agent],
    description="Pipeline that gathers multi-timeframe indicator data (standard & advanced) and runs strategy analysis."
)