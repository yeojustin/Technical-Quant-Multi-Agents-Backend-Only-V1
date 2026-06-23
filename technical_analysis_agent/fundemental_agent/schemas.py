from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class AnnualFinancials(BaseModel):
    fiscal_year: int
    revenue_millions: float
    net_income_millions: float
    free_cash_flow_millions: float
    eps: float


# Companies with no revenue or net_income < 0 will not have these metrics, so they are optional
class CurrentValuation(BaseModel):
    trailing_pe: Optional[float] = Field(description="Current Price-to-Earnings. Null if unprofitable.")
    forward_pe: Optional[float] = Field(description="Estimated future Price-to-Earnings. Null if no estimates.")
    peg_ratio: Optional[float] = Field(description="Price/Earnings-to-Growth ratio. Null if not available.")
    price_to_book: Optional[float] = Field(description="Price-to-Book ratio.")


class FundamentalScoreBreakdown(BaseModel):
    cagr_points: int = Field(description="Points contribution from Revenue CAGR growth.")
    eps_points: int = Field(description="Points contribution from EPS growth trend.")
    fcf_points: int = Field(description="Points contribution from Free Cash Flow health.")
    pe_growth_points: int = Field(description="Points contribution from forward P/E versus trailing P/E.")
    peg_points: int = Field(description="Points contribution from PEG ratio valuation.")
    high_pe_penalty: int = Field(description="Penalty points from high P/E combined with low growth.")
    cash_burn_penalty: int = Field(description="Penalty points from unprofitable cash burning.")


class FundamentalStrategyOutput(BaseModel):
    ticker: str
    data_points: int
    revenue_cagr: float
    eps_trend_verdict: Literal["ACCELERATING", "STABLE", "DECELERATING", "NEGATIVE"]
    valuation_verdict: Literal["UNDERVALUED", "FAIR VALUE", "OVERVALUED", "DISTRESSED"]
    fundamental_score: int 
    valuation_metrics: CurrentValuation 
    catalyst_summary: str 
    timeframe_breakdown: List[AnnualFinancials]
    score_breakdown: FundamentalScoreBreakdown = Field(description="Detailed breakdown of how the fundamental score was computed.")