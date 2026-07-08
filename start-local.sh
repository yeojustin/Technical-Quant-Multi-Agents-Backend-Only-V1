#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Stopping existing servers..."
pkill -f "technical_analysis_agent.server" 2>/dev/null || true
pkill -f "adk web" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
screen -S adk-web -X quit 2>/dev/null || true
screen -S frontend -X quit 2>/dev/null || true
sleep 1

echo "Starting ADK backend with BYOK (screen: adk-web)..."
screen -dmS adk-web bash -lc "cd '$ROOT' && uv run python -m technical_analysis_agent.server"

echo "Starting frontend (screen: frontend)..."
screen -dmS frontend bash -lc "cd '$ROOT/frontend' && npm run dev -- --hostname 0.0.0.0 --port 3000"

echo "Waiting for servers..."
for i in $(seq 1 30); do
  ADK_OK=0
  FE_OK=0
  curl -sf http://127.0.0.1:8000/list-apps >/dev/null 2>&1 && ADK_OK=1
  curl -sf http://127.0.0.1:3000 >/dev/null 2>&1 && FE_OK=1
  if [ "$ADK_OK" = "1" ] && [ "$FE_OK" = "1" ]; then
    echo ""
    echo "✓ Both servers are running!"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://127.0.0.1:8000"
    echo ""
    echo "To stop:  screen -S adk-web -X quit; screen -S frontend -X quit"
    echo "To view:  screen -r adk-web   or   screen -r frontend"
    open http://localhost:3000 2>/dev/null || true
    exit 0
  fi
  sleep 1
done

echo "✗ Servers failed to start."
screen -ls
exit 1
