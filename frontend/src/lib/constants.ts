export const APP_NAME = "technical_analysis_agent";
export const DEFAULT_USER_ID = "quant_user";

export const FEATURES = [
  {
    id: "price-feed",
    title: "Live Price Feed",
    description:
      "Real-time market data including current price, daily range, volume, and 52-week ranges.",
    icon: "TrendingUp",
  },
  {
    id: "technicals",
    title: "Technical Indicators",
    description:
      "Multi-timeframe analysis across 4h, 1d, 1w, and 1q with RSI, MACD, Williams Alligator, and RSI divergences.",
    icon: "LineChart",
  },
  {
    id: "fundamentals",
    title: "Fundamental Analysis",
    description:
      "Multi-year financials, revenue CAGR, EPS trends, valuation multiples (P/E, PEG, P/B), and programmatic scoring.",
    icon: "BarChart3",
  },
  {
    id: "sentiment",
    title: "News Sentiment",
    description:
      "Google Search-driven news analysis with sentiment scoring, key themes, catalysts, and future outlook.",
    icon: "Newspaper",
  },
  {
    id: "thesis",
    title: "Master Thesis Synthesizer",
    description:
      "Gemini 2.5 Pro consolidates all signals into an institutional verdict with conviction level and risk factors.",
    icon: "Brain",
  },
  {
    id: "export",
    title: "PDF & Excel Export",
    description:
      "Premium vector PDF reports and multi-sheet Excel workbooks saved as versioned artifacts.",
    icon: "FileOutput",
  },
] as const;

export const PIPELINE_STEPS = [
  { id: "validate", label: "Ticker Validation", agent: "validate_ticker_callback" },
  { id: "price", label: "Price Feed", agent: "price_feed_agent" },
  { id: "technicals", label: "Technical Indicators", agent: "indicator_agent_pipeline" },
  { id: "fundamentals", label: "Fundamentals", agent: "fundamental_agent_pipeline" },
  { id: "sentiment", label: "Sentiment Analysis", agent: "sentiment_agent_pipeline" },
  { id: "thesis", label: "Master Thesis", agent: "master_analysis_agent" },
  { id: "export", label: "Report Export", agent: "exporter_agent" },
] as const;

export const SUGGESTED_PROMPTS = [
  "Analyze AAPL",
  "Analyze NVDA",
  "Analyze MSFT",
  "What is a P/E ratio?",
  "Analyze TSLA",
];
