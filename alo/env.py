"""Tiny .env loader — the Notion MCP/token isn't auto-injected from .env, so we read it here.

Prefers the .env file value over the process environment (the process env may hold the stale
`ntn_your_secret_here` placeholder from an early `setx`).
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOTENV = REPO / ".env"


def load_dotenv(path: Path = DOTENV) -> dict[str, str]:
    out: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def notion_token() -> str | None:
    """Real token from .env wins; fall back to the process env."""
    return load_dotenv().get("NOTION_TOKEN") or os.environ.get("NOTION_TOKEN")
