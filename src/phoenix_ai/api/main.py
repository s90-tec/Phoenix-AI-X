"""FastAPI presentation adapter; routes delegate to application services."""

from fastapi import FastAPI

from phoenix_ai import __version__

app = FastAPI(title="Phoenix AI X", version=__version__)


@app.get("/health", tags=["operations"])
def health_check() -> dict[str, str]:
    """Liveness endpoint with no dependency on trading services."""
    return {"status": "ok", "service": "phoenix-ai-x"}

