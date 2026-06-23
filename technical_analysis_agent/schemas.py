from pydantic import BaseModel, Field
from typing import List, Literal

class MasterThesisOutput(BaseModel):
    ticker: str
    final_verdict: Literal["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"] = Field(description="The consolidated institutional investment thesis verdict.")
    conviction_level: Literal["HIGH", "MEDIUM", "LOW"] = Field(description="The conviction level in the verdict.")
    synthesis_summary: str = Field(description="Detailed synthesis explaining how fundamentals and technicals align or diverge to support this thesis.")
    risk_factors: List[str] = Field(description="List of key risk factors identified from both fundamental risks and technical decay/overextension.")
