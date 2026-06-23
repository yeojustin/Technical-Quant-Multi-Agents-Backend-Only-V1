import unittest
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from technical_analysis_agent.exporter_agent.agent import ProgrammaticExporterAgent

class TestExporterProgrammatic(unittest.TestCase):
    def test_programmatic_exports(self):
        print("\nRunning Test: Programmatic Exporter")
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        
        agent = ProgrammaticExporterAgent(
            name="test_programmatic_exporter",
            description="Test exporter agent"
        )
        
        runner = Runner(
            agent=agent,
            app_name="exporter_test_app",
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        session_id = "mock-session-id"
        user_id = "mock-user-id"
        
        mock_state = {
            "master_thesis_json": {
                "ticker": "TSLA",
                "final_verdict": "STRONG BUY",
                "conviction_level": "HIGH",
                "synthesis_summary": "TSLA is looking strong fundamentals and indicators."
            },
            "final_report_markdown": """
# 🏛️ Institutional Quant Report: TSLA
## 🎯 Overall Thesis: **STRONG BUY** | Conviction: **HIGH**

### 💸 Live Market Price Feed
* **Current Price:** $180.00
* **Previous Close:** $178.00

### 📊 Fundamental Health & Valuation
**Health Score:** 8/10 | **Valuation:** UNDERVALUED

| Valuation Metric | Value |
| :--- | :--- |
| **Trailing P/E** | 45.2 |
| **Forward P/E** | 35.8 |
""",
            "indicator_final_strategy": {
                "ticker": "TSLA",
                "short_term_recommendation": "BUY LONG",
                "long_term_recommendation": "BUY LONG",
                "total_score": 8,
                "overextension_override_applied": False,
                "macro_summary": "TSLA exhibits solid macro momentum across long-term horizons.",
                "alligator_status": "Alligator is awake and feeding in a bullish stance.",
                "divergence_status": "No divergence detected.",
                "timeframe_breakdown": [
                    {"timeframe": "4h", "signal": "BUY LONG", "score_contribution": 4, "justification": "MA crossover"},
                    {"timeframe": "1d", "signal": "BUY LONG", "score_contribution": 4, "justification": "RSI recovery"}
                ]
            },
            "fundamental_results": {
                "fundamental_score": 8,
                "valuation_verdict": "UNDERVALUED",
                "eps_trend_verdict": "ACCELERATING",
                "revenue_cagr": 12.5,
                "catalyst_summary": "Strong growth in vehicle deliveries.",
                "valuation_metrics": {
                    "trailing_pe": "45.2",
                    "forward_pe": "35.8",
                    "peg_ratio": "1.2",
                    "price_to_book": "8.5"
                },
                "timeframe_breakdown": [
                    {"fiscal_year": "2025", "revenue_millions": 96773, "net_income_millions": 14974, "free_cash_flow_millions": 4357, "eps": 4.30}
                ],
                "score_breakdown": {
                    "cagr_points": 2,
                    "eps_points": 2,
                    "fcf_points": 2,
                    "pe_growth_points": 2,
                    "peg_points": 0,
                    "high_pe_penalty": 0,
                    "cash_burn_penalty": 0
                }
            },
            "indicator_calculated_scores": {
                "breakdown": {
                    "short_term": {
                        "macd_weekly_daily_acceleration": 2,
                        "macd_4h_momentum": 1,
                        "alligator_mouth": 1,
                        "rsi_divergence": 2
                    },
                    "long_term": {
                        "macd_quarterly_health": 5,
                        "alligator_mouth": 2,
                        "rsi_divergence": 3
                    }
                }
            },
            "sentiment_results": {
                "ticker": "TSLA",
                "sentiment_score": 8,
                "sentiment_verdict": "BULLISH",
                "future_outlook": "Highly bullish outlook on deliveries.",
                "key_themes": ["EV adoption acceleration", "Delivery beat"],
                "news_articles": [
                    {
                        "title": "Tesla Q4 Delivery Beats Estimates",
                        "source": "Bloomberg",
                        "published_at": "June 2026",
                        "sentiment_contribution": "BULLISH",
                        "summary": "Tesla delivered a record number of vehicles this quarter.",
                        "url": "https://bloomberg.com/tesla"
                    }
                ]
            }
        }
        
        async def run_export():
            await session_service.create_session(
                app_name="exporter_test_app",
                user_id=user_id,
                session_id=session_id,
                state=mock_state
            )
            
            import google.genai.types as types
            async for _ in runner.run_async(
                session_id=session_id,
                user_id=user_id,
                new_message=types.Content(parts=[types.Part.from_text(text="run")])
            ):
                pass
                
            return await artifact_service.list_artifact_keys(
                app_name="exporter_test_app",
                user_id=user_id,
                session_id=session_id
            )
            
        artifacts = asyncio.run(run_export())
        print(f"Generated Artifacts: {artifacts}")
        self.assertIn("TSLA_Quant_Report.pdf", artifacts)
        self.assertIn("TSLA_Scoring_Breakdown.xlsx", artifacts)

if __name__ == '__main__':
    unittest.main()
