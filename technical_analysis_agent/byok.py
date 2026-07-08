"""Bring Your Own Key (BYOK) support for Gemini API keys."""

from __future__ import annotations

import contextvars
from functools import cached_property
from typing import Any, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

BYOK_HEADER = "x-gemini-api-key"

_byok_api_key: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "byok_gemini_api_key", default=None
)


def get_byok_api_key() -> Optional[str]:
    return _byok_api_key.get()


def install_byok_patches() -> None:
    """Patch GoogleLLM to honor per-request BYOK API keys."""
    from google.adk.models import google_llm
    from google.genai import Client
    from google.genai import types

    gemini_cls = google_llm.Gemini
    original_fget = gemini_cls.api_client.func

    def _build_client(self, api_key: Optional[str] = None) -> Client:
        base_url, api_version = self._base_url_and_api_version
        kwargs_for_http_options: dict[str, Any] = {
            "headers": self._tracking_headers(),
            "retry_options": self.retry_options,
            "base_url": base_url,
        }
        if api_version:
            kwargs_for_http_options["api_version"] = api_version

        kwargs: dict[str, Any] = {
            "http_options": types.HttpOptions(**kwargs_for_http_options),
        }
        if self.model.startswith("projects/"):
            kwargs["vertexai"] = True
        if api_key:
            kwargs["api_key"] = api_key

        return Client(**kwargs)

    def api_client_property(self):
        byok_key = _byok_api_key.get()
        if byok_key:
            return _build_client(self, api_key=byok_key)

        cache_attr = "_byok_api_client_cache"
        cached = getattr(self, cache_attr, None)
        if cached is None:
            cached = original_fget(self)
            setattr(self, cache_attr, cached)
        return cached

    cls = gemini_cls
    if isinstance(cls.__dict__.get("api_client"), cached_property):
        delattr(cls, "api_client")
    cls.api_client = property(api_client_property)


class ByokMiddleware(BaseHTTPMiddleware):
    """Reads X-Gemini-Api-Key and scopes it to the current async request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        raw_key = request.headers.get(BYOK_HEADER) or request.headers.get(
            "X-Gemini-Api-Key"
        )
        api_key = raw_key.strip() if raw_key else None

        if not api_key:
            return await call_next(request)

        token = _byok_api_key.set(api_key)
        try:
            return await call_next(request)
        finally:
            _byok_api_key.reset(token)
