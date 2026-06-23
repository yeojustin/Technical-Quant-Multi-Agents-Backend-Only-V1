from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class SentimentInput(BaseModel):
    ticker: str = Field(description="The stock ticker symbol to analyze sentiment for (e.g., 'AAPL', 'TSLA').")

class NewsArticle(BaseModel):
    title: str = Field(description="The headline of the news article or post.")
    source: str = Field(description="The source or provider of the article.")
    published_at: str = Field(description="The publication date or relative time of the article.")
    sentiment_contribution: Literal["BULLISH", "BEARISH", "NEUTRAL"] = Field(description="The sentiment impact of this specific article.")
    summary: str = Field(description="A brief one-sentence summary of the article's core content.")
    url: Optional[str] = Field(description="The URL to the news article, if available.", default=None)

class SentimentOutput(BaseModel):
    ticker: str
    sentiment_score: int = Field(description="Numeric sentiment score between -10 (extremely bearish) and +10 (extremely bullish).")
    sentiment_verdict: Literal["BULLISH", "BEARISH", "NEUTRAL", "CONFLICTED"]
    future_outlook: str = Field(description="A concise summary of the future outlook, key upcoming catalysts, and earnings/events expectations.")
    key_themes: List[str] = Field(description="List of core themes/narratives repeating across the news articles.")
    news_articles: List[NewsArticle] = Field(description="Detailed list of key news articles analyzed, with headlines, source, date, sentiment contribution, and summary/URL.")

