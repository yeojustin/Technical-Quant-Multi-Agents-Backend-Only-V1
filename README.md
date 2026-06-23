# 🏛️ Institutional Quant Technical Analysis Agent

A modern, orchestrator-driven multi-agent quantitative portfolio system built with the **Google Agent Development Kit (ADK)** and powered by **Gemini**. This platform automatically gathers price feeds, computes complex technical indicators (e.g. Williams Alligator, RSI divergences), fetches fundamental metrics, analyzes web news sentiment, synthesizes them into an institutional investment thesis, and exports reports into premium PDF and Excel formats.

---

## 🏗️ Architecture

The system utilizes parallel and sequential orchestration to orchestrate multiple specialized agents:

```
                      [User Query]
                           │
                           ▼
                  [Root Supervisor]
                           │
                (validate_ticker_callback)
                           │
                           ▼
               [QuantPortfolioPipeline]
                           │
         ┌─────────────────┼─────────────────┬─────────────────┐
         ▼                 ▼                 ▼                 ▼
   [Price Feed]       [Technicals]     [Fundamentals]     [Sentiment]
   (Programmatic)     (Programmatic)   (Programmatic)     (LlmAgent)
         │                 │                 │                 │
         └─────────────────┼─────────────────┴─────────────────┘
                           │ (Combined State)
                           ▼
                [Master Thesis Synthesizer]
                     (Gemini 2.5 Pro)
                           │
                           ▼
               [Presentation Generator]
                    (Markdown Template)
                           │
                           ▼
                    [Exporter Agent]
                 (PDF & Excel Outputs)
```

1. **Intent Routing**: The `root_agent` determines the user's intent. Crypto tickers or digital assets are filtered out immediately.
2. **Ticker Validation**: The `validate_ticker_callback` confirms the ticker has valid price history on yfinance.
3. **Data Gathering & Sub-Strategy Analysis**:
   - **Price Feed Agent**: Fetches current prices, daily range, volume, and 52-week ranges.
   - **Indicator Agent Pipeline**: Computes basic indicators (RSI, MACD) and advanced indicators (Williams Alligator, RSI Divergences) across multi-timeframes (`4h`, `1d`, `1w`, `1q`).
   - **Fundamental Agent Pipeline**: Gathers multi-year financials (Revenue, Income, Free Cash Flow, EPS) and current valuation multiples.
   - **Sentiment Agent Pipeline**: Performs Google Search queries to capture live news headlines, catalysts, and narratives.
4. **Master Merger Analysis**: A `gemini-2.5-pro` agent synthesizes all gathered data into a single coherent thesis, outputting a structured `MasterThesisOutput` schema containing the verdict, conviction level, risks, and synthesis.
5. **Presentation formatting**: Formats results into a deterministic Markdown template.
6. **Programmatic Exporter**: Saves the Markdown quant report to a premium-grade vector **PDF** and saves raw data/metrics to a multi-sheet **Excel Workbook** via ADK's artifact storage.

---

## 🚀 Getting Started

### Prerequisites

- Python >= 3.12
- Google Cloud project with Vertex AI API enabled (if running live LLM invocations)
- [uv](https://github.com/astral-sh/uv) (recommended Python package manager)

### Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/yeojustin/Technical-Quant-Multi-Agents-Backend-Only-V1.git
   cd Technical-Quant-Multi-Agents-Backend-Only-V1
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Set up environment variables:
   Copy `.env.example` to `.env` (either in the root directory or inside `technical_analysis_agent/`):
   ```bash
   cp .env.example .env
   ```

   Open `.env` and configure your credentials. The application supports two modes:

   #### Option A: Gemini Developer API (Recommended / Default)
   Configure this if you want to use the standard Google GenAI SDK with an API key from Google AI Studio:
   ```ini
   GOOGLE_GENAI_USE_VERTEXAI=0
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   #### Option B: Vertex AI (Google Cloud Platform)
   Configure this if you want to run within a GCP environment utilizing Vertex AI models:
   ```ini
   GOOGLE_GENAI_USE_VERTEXAI=1
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

---

## 💻 Running the Application

### Web UI (ADK Web client)

Launch the interactive web portal to chat with the root supervisor agent:

```bash
uv run adk web
```

Open the browser at `http://localhost:8000` (or the port specified by the CLI).

### CLI Execution

You can run the agent in the command line using the ADK CLI runner.

#### Interactive CLI Mode
To start an interactive, conversational session in the terminal, run:
```bash
uv run adk run technical_analysis_agent
```

#### Single Query CLI Mode
To run the agent for a single query (e.g., asking it to analyze a specific ticker) and output the result immediately, run:
```bash
uv run adk run technical_analysis_agent "Analyze TSLA"
```

---

## 🧪 Testing

The repository includes a comprehensive unit testing suite using `pytest`.

To execute all tests:

```bash
uv run pytest
```

---

## 📂 Project Structure

```
.
├── README.md                      # Project documentation
├── pyproject.toml                 # Dependencies and project config
├── technical_analysis_agent/
│   ├── __init__.py
│   ├── agent.py                   # Main orchestration and agent definitions
│   ├── prompt.py                  # Instruction prompts for the master agents
│   ├── schemas.py                 # Pydantic schemas for structured output
│   ├── callbacks/                 # Orchestrator validation callbacks
│   ├── exporter_agent/            # Handles PDF and Excel document exports
│   ├── fundemental_agent/         # Financial data fetching & scoring
│   ├── indicator_agent/           # Technical indicator computations
│   ├── sentiment_agent/           # Search-driven sentiment summaries
│   └── local_data_lake/           # Cached yfinance JSON data
└── tests/                         # Integration and unit tests
```

---

## 🛡️ License

Confidential - For Internal Use Only.
