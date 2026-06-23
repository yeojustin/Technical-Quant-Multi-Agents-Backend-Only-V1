import unittest
import asyncio
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events import Event
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import Agent
from technical_analysis_agent.agent import quant_portfolio_pipeline
from technical_analysis_agent.callbacks.validate_ticker_callback import validate_ticker_callback

class TestValidationCallback(unittest.TestCase):
    def test_invalid_ticker_aborts(self):
        print("\nRunning Test: Invalid Ticker Aborts")
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        
        runner = Runner(
            agent=quant_portfolio_pipeline,
            app_name="validation_test_app",
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        session_id = "session-invalid"
        query_msg = types.Content(
            parts=[types.Part.from_text(text="Analyze INVALIDTICKER")]
        )
        
        async def run_invalid():
            outputs = []
            async for event in runner.run_async(
                session_id=session_id,
                user_id="test-user",
                new_message=query_msg
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            outputs.append(part.text)
            return "".join(outputs)
            
        result = asyncio.run(run_invalid())
        self.assertIn("Error: Cannot find stock ticker 'INVALIDTICKER'", result)
        
        # Verify ticker is not stored in state
        session = asyncio.run(session_service.get_session(
            app_name="validation_test_app",
            session_id=session_id,
            user_id="test-user"
        ))
        self.assertNotIn("ticker", session.state)

    def test_regex_does_not_match_word_suffixes(self):
        print("\nRunning Test: Regex Suffix Match Prevention")
        session_service = InMemorySessionService()
        session = asyncio.run(session_service.create_session(
            app_name="validation_test_app",
            user_id="test-user",
            session_id="session-suffix"
        ))
        
        session.events.append(
            Event(
                invocation_id="1",
                author="user",
                content=types.Content(parts=[types.Part.from_text(text="Analyze XYZOSOFT")])
            )
        )
        
        test_agent = Agent(name="test_agent", model="gemini-2.5-flash", instruction="")
        inv_ctx = InvocationContext(
            session=session,
            invocation_id="2",
            agent=test_agent,
            session_service=session_service
        )
        cb_ctx = CallbackContext(inv_ctx)
        
        # This will resolve to XYZOSOFT (fallback to last word) since XYZOSOFT is too long to match the 1-6 letter regex
        # If the regex bug were present, it would extract OSOFT (5 letters suffix ending at word boundary)
        res = validate_ticker_callback(cb_ctx)
        self.assertIsNotNone(res) # Should abort because XYZOSOFT is not a valid ticker symbol
        self.assertIn("'XYZOSOFT'", res.parts[0].text)
        self.assertNotIn("ticker", cb_ctx.state)

    def test_callback_context_resolution(self):
        print("\nRunning Test: Callback Context Resolution")
        session_service = InMemorySessionService()
        session_resolved = asyncio.run(session_service.create_session(
            app_name="validation_test_app",
            user_id="test-user",
            session_id="session-resolved"
        ))
        
        session_resolved.events.append(
            Event(
                invocation_id="1",
                author="user",
                content=types.Content(parts=[types.Part.from_text(text="Do you think Apple is a buy?")])
            )
        )
        session_resolved.events.append(
            Event(
                invocation_id="2",
                author="root_agent",
                content=types.Content(parts=[types.Part.from_text(text="I will transfer to the QuantPortfolioPipeline to analyze Apple. Ticker: AAPL")])
            )
        )
        
        test_agent = Agent(name="test_agent", model="gemini-2.5-flash", instruction="")
        inv_ctx = InvocationContext(
            session=session_resolved,
            invocation_id="3",
            agent=test_agent,
            session_service=session_service
        )
        cb_ctx = CallbackContext(inv_ctx)
        
        res = validate_ticker_callback(cb_ctx)
        self.assertIsNone(res)
        self.assertEqual(cb_ctx.state.get("ticker"), "AAPL")

if __name__ == '__main__':
    unittest.main()
