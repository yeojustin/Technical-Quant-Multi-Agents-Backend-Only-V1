"""ADK web server with BYOK middleware for per-user Gemini API keys."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from .byok import ByokMiddleware, install_byok_patches


def create_app():
    install_byok_patches()

    from google.adk.cli.fast_api import get_fast_api_app

    project_root = Path(__file__).resolve().parent.parent

    app = get_fast_api_app(
        agents_dir=str(project_root),
        web=True,
        use_local_storage=True,
    )
    app.add_middleware(ByokMiddleware)
    return app


def main() -> None:
    host = os.environ.get("ADK_HOST", "127.0.0.1")
    port = int(os.environ.get("ADK_PORT", "8000"))
    app = create_app()

    print(
        f"\n+-----------------------------------------------------------------------------+\n"
        f"| Quant Analysis Server (BYOK enabled)                                        |\n"
        f"|                                                                             |\n"
        f"| Frontend: http://localhost:3000                                           |\n"
        f"| API:      http://{host}:{port}                                              |\n"
        f"+-----------------------------------------------------------------------------+\n"
    )

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
