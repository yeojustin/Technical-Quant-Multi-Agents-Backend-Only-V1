from google.adk.agents import Agent, ParallelAgent, LlmAgent, SequentialAgent

from .indicator_agent import indicator_agent_pipeline
from .fundemental_agent import fundamental_agent_pipeline
from .price_feed_agent import price_feed_agent
from .sentiment_agent import sentiment_agent_pipeline
from .exporter_agent import exporter_agent
from .schemas import MasterThesisOutput
from .callbacks.validate_ticker_callback import validate_ticker_callback
from .prompt import MASTER_ANALYSIS_INSTRUCTION, ROOT_INSTRUCTION


# Step 1: Run all data gathering and sub-strategy pipelines in parallel
parallel_agent = ParallelAgent(
    name="parallel_agent",
    sub_agents=[price_feed_agent, indicator_agent_pipeline, fundamental_agent_pipeline, sentiment_agent_pipeline]
)


# Step 2: Consolidate everything into a master institutional thesis
master_analysis_agent = LlmAgent(
    name="master_analysis_agent",
    model="gemini-2.5-pro",
    description="Consolidates technical indicators, advanced indicators, and fundamental metrics into a unified investment thesis.",
    instruction=MASTER_ANALYSIS_INSTRUCTION,
    output_schema=MasterThesisOutput,
    output_key="master_thesis_json"
)


# Complete Sequential Orchestration Pipeline
quant_portfolio_pipeline = SequentialAgent(
    name="QuantPortfolioPipeline",
    sub_agents=[
        parallel_agent,
        master_analysis_agent,
        exporter_agent
    ],
    before_agent_callback=validate_ticker_callback,
    description="Institutional analysis pipeline that executes parallel price/indicator/fundamental steps and exports report files."
)


# Root Supervisor Agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for stock analysis questions.',
    instruction=ROOT_INSTRUCTION,
    sub_agents=[quant_portfolio_pipeline]
)