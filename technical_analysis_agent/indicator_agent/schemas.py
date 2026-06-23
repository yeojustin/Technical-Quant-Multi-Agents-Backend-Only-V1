from pydantic import BaseModel, Field
from typing import List, Literal

class TechnicalIndicatorInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol to analyze (e.g., 'AAPL', 'TSLA').")

class TimeframeAnalysis(BaseModel):
    timeframe: Literal["4h", "1d", "1w", "1q"]
    signal: Literal["BUY LONG", "SELL SHORT", "HOLD"]
    score_contribution: int = Field(description="Points awarded or penalized for this timeframe (e.g., -3 to +3).")
    justification: str = Field(description="The structural logic for this timeframe's signal and score.")

class IndicatorStrategyOutput(BaseModel):
    ticker: str
    short_term_recommendation: Literal["BUY LONG", "SELL SHORT", "HOLD"] = Field(description="Short-term trading recommendation based on 4h, 1d, and 1w timeframes.")
    long_term_recommendation: Literal["BUY LONG", "SELL SHORT", "HOLD"] = Field(description="Long-term trading recommendation based on the 1q timeframe.")
    total_score: int = Field(description="The final calculated net score between -20 and +20, including all advanced indicators and overrides.")
    overextension_override_applied: bool = Field(description="True if the Weekly (1W) RSI penalty/bonus was triggered.")
    macro_summary: str = Field(description="High-level synthesis of momentum and trend across all timeframes.")
    alligator_status: str = Field(description="Quantitative synthesis of Williams Alligator states across all timeframes.")
    divergence_status: str = Field(description="Quantitative analysis of bullish or bearish RSI divergences across all timeframes.")
    timeframe_breakdown: List[TimeframeAnalysis] = Field(description="Individual breakdown for each required timeframe.")