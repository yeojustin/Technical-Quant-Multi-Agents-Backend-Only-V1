import unittest
import asyncio
import os
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from technical_analysis_agent.agent import root_agent

class TestAgentPipeline(unittest.TestCase):
    @unittest.skipIf(not os.getenv("GOOGLE_CLOUD_PROJECT"), "Vertex AI credentials are not configured")
    def test_e2e_pipeline_tsla(self):
        print("\nRunning Test: E2E Pipeline TSLA")
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        
        runner = Runner(
            agent=root_agent,
            app_name="technical_analysis_agent_test",
            session_service=session_service,
            artifact_service=artifact_service,
            auto_create_session=True
        )
        
        session_id = "test-session-1"
        query_msg = types.Content(
            parts=[types.Part.from_text(text="Analyze TSLA")]
        )
        
        async def run_pipeline():
            output_text = []
            async for event in runner.run_async(
                session_id=session_id,
                user_id="test-user",
                new_message=query_msg
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            output_text.append(part.text)
            return "".join(output_text)
            
        result = asyncio.run(run_pipeline())
        print(f"Pipeline finished. Output length: {len(result)}")
        self.assertTrue(len(result) > 0, "Pipeline returned empty output")

if __name__ == '__main__':
    unittest.main()
