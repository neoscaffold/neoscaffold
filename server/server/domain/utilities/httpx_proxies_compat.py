"""Accept the removed httpx/OpenAI ``proxies=`` argument.

httpx 0.28 dropped ``Client(proxies=...)`` in favor of ``proxy=``. Older
openai/cerebras clients still pass ``proxies``, which raises:

    TypeError: Client.__init__() got an unexpected keyword argument 'proxies'

Newer openai.Client also rejects ``proxies``. Apply this before any SDK
client is constructed so CursorAgent and the harness can start.
"""

from __future__ import annotations

import inspect

_APPLIED = False


def _normalize_proxy(proxies, proxy):
    if proxy is not None:
        return proxy
    if proxies is None:
        return None
    if isinstance(proxies, dict):
        return (
            proxies.get("https://")
            or proxies.get("http://")
            or proxies.get("https")
            or proxies.get("http")
            or next(iter(proxies.values()), None)
        )
    return proxies


def _wrap_init(original):
    def patched(self, *args, proxies=None, **kwargs):
        if proxies is not None:
            params = inspect.signature(original).parameters
            if "proxy" in params:
                kwargs.setdefault("proxy", _normalize_proxy(proxies, kwargs.get("proxy")))
        return original(self, *args, **kwargs)

    return patched


def _patch_if_missing_proxies(client_cls):
    if client_cls is None:
        return
    try:
        params = inspect.signature(client_cls.__init__).parameters
    except (TypeError, ValueError):
        return
    if "proxies" in params:
        return
    client_cls.__init__ = _wrap_init(client_cls.__init__)


def apply_httpx_proxies_compat():
    """Idempotently patch httpx and OpenAI clients to accept ``proxies``."""
    global _APPLIED
    if _APPLIED:
        return
    _APPLIED = True

    try:
        import httpx
    except ImportError:
        httpx = None
    if httpx is not None:
        _patch_if_missing_proxies(getattr(httpx, "Client", None))
        _patch_if_missing_proxies(getattr(httpx, "AsyncClient", None))

    try:
        from openai import AsyncOpenAI, OpenAI
    except ImportError:
        OpenAI = None
        AsyncOpenAI = None
    _patch_if_missing_proxies(OpenAI)
    _patch_if_missing_proxies(AsyncOpenAI)

    try:
        from cursor_sdk import Client as CursorClient
    except ImportError:
        CursorClient = None
    _patch_if_missing_proxies(CursorClient)
