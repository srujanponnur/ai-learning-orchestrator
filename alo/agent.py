"""Claude Agent SDK wiring.

Runs one-shot text generations on the **Max subscription** (no `ANTHROPIC_API_KEY`).
The Agent SDK spawns the `claude` CLI; on this machine the CLI ships inside the VSCode
extension and is not on PATH, so `ensure_claude_cli()` discovers it and prepends its dir.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from shutil import which

import anyio
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query


def _extension_binaries() -> list[Path]:
    """All bundled `claude.exe` binaries from VSCode extensions, sorted lowest→highest version."""
    root = Path.home() / ".vscode" / "extensions"
    found: list[tuple[tuple[int, ...], Path]] = []
    for ext in root.glob("anthropic.claude-code-*"):
        binary = ext / "resources" / "native-binary" / "claude.exe"
        if binary.exists():
            m = re.search(r"anthropic\.claude-code-(\d+(?:\.\d+)*)", ext.name)
            ver = tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
            found.append((ver, binary))
    return [b for _, b in sorted(found)]


def ensure_claude_cli() -> str:
    """Guarantee a `claude` executable is discoverable on PATH; return the path used.

    Order: existing PATH → newest bundled VSCode-extension binary → error with guidance.
    """
    on_path = which("claude")
    if on_path:
        return on_path
    binaries = _extension_binaries()
    if binaries:
        newest = binaries[-1]
        os.environ["PATH"] = str(newest.parent) + os.pathsep + os.environ.get("PATH", "")
        return str(newest)
    raise RuntimeError(
        "Could not find the `claude` CLI. Install it with `npm i -g @anthropic-ai/claude-code` "
        "and log in with your Max subscription (run `claude`), then retry."
    )


async def run_text(prompt: str, system_prompt: str, *, model: str | None = None,
                   max_turns: int = 1) -> str:
    """One-shot, tool-free generation via the Agent SDK. Returns concatenated assistant text."""
    cli = ensure_claude_cli()
    # Enforce Max-subscription auth — a stray API key would bill the metered API (repo convention).
    if os.environ.pop("ANTHROPIC_API_KEY", None):
        print("note: ignoring ANTHROPIC_API_KEY for this run — using the Max subscription.")
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=[],          # pure generation — no tools
        max_turns=max_turns,
        model=model,               # None → CLI default
        cli_path=cli,
    )
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "".join(parts)


def run_text_sync(prompt: str, system_prompt: str, *, model: str | None = None,
                  max_turns: int = 1) -> str:
    return anyio.run(lambda: run_text(prompt, system_prompt, model=model, max_turns=max_turns))


async def run_research(prompt: str, system_prompt: str, *,
                       allowed_tools: tuple[str, ...] = ("WebSearch", "WebFetch"),
                       max_turns: int = 20, model: str | None = None) -> str:
    """Multi-turn run with read-only web tools allow-listed (no bypassPermissions). Returns text.

    Used by the discovery swarm — scouts search/fetch the web on the Max subscription. We allow-list
    only WebSearch/WebFetch (scoped) rather than disabling all approval gates.
    """
    cli = ensure_claude_cli()
    if os.environ.pop("ANTHROPIC_API_KEY", None):
        print("note: ignoring ANTHROPIC_API_KEY for this run — using the Max subscription.")
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=list(allowed_tools),
        max_turns=max_turns,
        model=model,
        cli_path=cli,
    )
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "".join(parts)


def run_research_sync(prompt: str, system_prompt: str, *,
                      allowed_tools: tuple[str, ...] = ("WebSearch", "WebFetch"),
                      max_turns: int = 20, model: str | None = None) -> str:
    return anyio.run(lambda: run_research(prompt, system_prompt, allowed_tools=allowed_tools,
                                          max_turns=max_turns, model=model))
