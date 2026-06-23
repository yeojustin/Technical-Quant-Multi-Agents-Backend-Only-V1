from pydantic import BaseModel, Field

class PriceFeedInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol to fetch price feed for (e.g., 'AAPL', 'TSLA').")

class PriceFeedOutput(BaseModel):
    ticker: str
    current_price: float = Field(description="The current/latest price of the asset.")
    previous_close: float = Field(description="The previous day's close price.")
    daily_range: str = Field(description="The daily price range (e.g. '$150.00 - $155.00').")
    fifty_two_week_range: str = Field(description="The 52-week price range (e.g. '$120.00 - $180.00').")
    volume: int = Field(description="The trading volume of the current day.")
