# Quant Technical Analysis — Frontend

Claude-style web UI for the Technical Analysis Multi-Agent platform.

## Features

- **Home page** — highlights all platform capabilities, architecture, and pipeline
- **Analysis chat** — streaming SSE chat with the ADK root agent
- **Artifact management** — browse, download, version, and delete PDF/Excel exports
- **Pipeline status** — live progress through validation → export steps

## Prerequisites

The ADK backend must be running (with BYOK support):

```bash
# From project root
uv run python -m technical_analysis_agent.server
```

This starts the API server at `http://localhost:8000` and accepts per-user Gemini keys via the `X-Gemini-Api-Key` header.

## Bring Your Own Key (BYOK)

1. Click **API Key** in the sidebar
2. Paste your [Gemini API key](https://aistudio.google.com/apikey)
3. The key is stored in your browser's localStorage and attached to each request
4. Keys are never persisted on the server

You can still set `GEMINI_API_KEY` in `.env` as a server-side fallback when no BYOK header is sent.

## Development

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The frontend proxies ADK API requests through `/api/adk/*` using a **runtime** Route Handler (`src/app/api/adk/[...path]/route.ts`). The backend URL is read from `ADK_API_URL` on each server start — no rebuild required when it changes.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `ADK_API_URL` | `http://localhost:8000` | ADK backend URL (read at **runtime** by the API proxy) |
| `NEXT_PUBLIC_ADK_API_URL` | `/api/adk` | Client-side API base path (relative proxy endpoint) |

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — feature overview and architecture |
| `/chat` | Interactive analysis chat with artifact sidebar |
| `/artifacts` | Global artifact browser across all sessions |
