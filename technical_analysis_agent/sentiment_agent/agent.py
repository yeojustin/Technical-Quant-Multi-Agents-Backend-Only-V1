from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

from .schemas import SentimentInput, SentimentOutput
from .prompt import SENTIMENT_GATHERER_INS, SENTIMENT_STRATEGY_INS


sentiment_gatherer = LlmAgent(
    name="sentiment_gatherer",
    model="gemini-2.5-flash",
    description="Gathers live news and event details for a stock ticker using Google Search.",
    instruction=SENTIMENT_GATHERER_INS,
    input_schema=SentimentInput,
    tools=[google_search],
    output_key="sentiment_raw"
)

sentiment_strategy_agent = LlmAgent(
    name="sentiment_strategy_agent",
    model="gemini-2.5-pro",
    description="Analyzes raw news headlines and summaries to score sentiment and forecast future outlook.",
    instruction=SENTIMENT_STRATEGY_INS,
    output_schema=SentimentOutput,
    output_key="sentiment_results"
)

# sentiment_presentation_agent = LlmAgent(
#     name="sentiment_presentation_agent",
#     model="gemini-2.5-flash",
#     description="Formats parsed sentiment results into a professional markdown section.",
#     instruction=SENTIMENT_PRESENTATION_INS
# )

sentiment_agent_pipeline = SequentialAgent(
    name="SentimentAgentPipeline",
    sub_agents=[sentiment_gatherer, sentiment_strategy_agent],
    description="Pipeline that gathers stock-related news and analyzes its sentiment and future outlook."
)
