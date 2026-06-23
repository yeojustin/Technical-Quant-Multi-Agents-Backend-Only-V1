from typing import AsyncGenerator
from typing_extensions import override
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event

from .tools import export_report_to_pdf, export_scoring_to_excel, generate_report_markdown


class ProgrammaticExporterAgent(BaseAgent):
    """Automatically runs export tasks sequentially without using LLM tokens."""
    
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        
        # Extract ticker from state
        ticker = None
        thesis = state.get("master_thesis_json")
        if thesis:
            if isinstance(thesis, dict):
                ticker = thesis.get("ticker")
            elif hasattr(thesis, "ticker"):
                ticker = getattr(thesis, "ticker")
        
        if not ticker:
            indicators = state.get("indicator_final_strategy")
            if indicators:
                if isinstance(indicators, dict):
                    ticker = indicators.get("ticker")
                elif hasattr(indicators, "ticker"):
                    ticker = getattr(indicators, "ticker")
                    
        if not ticker:
            price_feed = state.get("price_feed_results")
            if price_feed:
                if isinstance(price_feed, dict):
                    ticker = price_feed.get("ticker")
                elif hasattr(price_feed, "ticker"):
                    ticker = getattr(price_feed, "ticker")
                    
        if not ticker:
            for val in state.values():
                if isinstance(val, dict) and "ticker" in val:
                    ticker = val["ticker"]
                    break
                elif hasattr(val, "ticker"):
                    ticker = getattr(val, "ticker")
                    if ticker:
                        break
                        
        if not ticker:
            ticker = "UNKNOWN"

        context = CallbackContext(ctx)
        try:
            pdf_res = await export_report_to_pdf(ticker, context)
        except Exception as e:
            pdf_res = f"PDF export error: {str(e)}"
            
        try:
            excel_res = await export_scoring_to_excel(ticker, context)
        except Exception as e:
            excel_res = f"Excel export error: {str(e)}"
            
        try:
            markdown_report = generate_report_markdown(state)
            state["final_report_markdown"] = markdown_report
        except Exception as e:
            markdown_report = f"Error generating markdown report: {str(e)}"
            
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            message=markdown_report,
            actions=context.actions
        )


exporter_agent = ProgrammaticExporterAgent(
    name="exporter_agent",
    description="Automatically saves files to PDF and Excel without using LLM tokens."
)
