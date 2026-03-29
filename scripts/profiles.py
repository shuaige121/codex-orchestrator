"""
Stack Profiles (机能包) — loader for language-specific coding rules, toolchains,
verification sequences, common pitfalls, and project structure guides.

Loads profiles from stacks/ directory (each stack = config.json + *.md files).
Supports custom stack directory via CLCO_STACKS_DIR environment variable.

Sources:
  - trailofbits/claude-code-config (toolchain configs, strict rules)
  - affaan-m/everything-claude-code (per-language rules, skills, agents)
  - justinlietz93/Perfect_Prompts (per-language prompt templates)
  - Ranrar/rustic-prompt (Rust-specific AI coding instructions)
  - astral-sh/ruff (Python linter patterns)
  - Next.js official documentation (App Router, Server Components)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# TOOLCHAIN_SCHEMA
# Required keys for every stack `toolchain`: lint, format, test
# Optional keys when applicable: typecheck, build, migrate

_SCRIPT_DIR = Path(__file__).resolve().parent
_PLUGIN_DIR = _SCRIPT_DIR.parent
_DEFAULT_STACKS_DIR = _PLUGIN_DIR / "stacks"

_MD_FIELDS = ("coding_rules", "verification_sequence", "common_pitfalls", "project_structure")


def _load_stack(stack_dir: Path) -> dict | None:
    """Load a single stack profile from a directory."""
    config_path = stack_dir / "config.json"
    if not config_path.is_file():
        return None

    try:
        with open(config_path, encoding="utf-8") as f:
            stack = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    # Load markdown fields from separate files
    for field in _MD_FIELDS:
        md_path = stack_dir / f"{field}.md"
        if md_path.is_file():
            try:
                stack[field] = md_path.read_text(encoding="utf-8").rstrip("\n")
            except OSError:
                stack[field] = ""
        else:
            stack.setdefault(field, "")

    return stack


def _load_all_stacks() -> dict[str, dict]:
    """Load all stack profiles from stacks directory."""
    env_dir = os.environ.get("CLCO_STACKS_DIR", "").strip()
    stacks_dir = Path(env_dir) if env_dir else _DEFAULT_STACKS_DIR

    if not stacks_dir.is_dir():
        return {}

    result: dict[str, dict] = {}
    for entry in sorted(stacks_dir.iterdir()):
        if entry.is_dir() and (entry / "config.json").exists():
            stack = _load_stack(entry)
            if stack is not None:
                result[entry.name] = stack

    return result


STACKS: dict[str, dict] = _load_all_stacks()
