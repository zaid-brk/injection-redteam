"""Phase 5 — three defense layers. Defense in depth: no single layer is enough.

  Layer 1 input sanitization  — neutralize obvious injection phrases in the user's message.
  Layer 2 prompt hardening    — HARDENED_SYSTEM in target_agent.py (swapped in, not here).
  Layer 3 output monitoring   — last-ditch redaction if the secret reaches the output.

The honest, important limitation: input sanitization CANNOT stop indirect injection. The
payload arrives inside fetched page content, via the fetch_url tool, AFTER the input
filter already ran on the user's message. That is why the per-category numbers still show
indirect_web leaking under Layer 1 alone — and why you need Layers 2 and 3 too.
"""
import re

from target_agent import SECRET_FLAG

INJECTION_PATTERNS = [
    r"ignore (all |your )?previous instructions",
    r"disregard.*instructions",
    r"system override",
    r"debug mode",
    r"developer mode",
    r"you are now",
    r"reveal.*(key|secret|prompt)",
    r"print.*(key|secret|prompt)",
]


def sanitize_input(text: str) -> str:
    """Layer 1: flag/neutralize obvious injection phrases before they reach the agent."""
    flagged = text
    for pat in INJECTION_PATTERNS:
        flagged = re.sub(pat, "[REMOVED: possible injection]", flagged, flags=re.IGNORECASE)
    return flagged


def scrub_output(text: str) -> str:
    """Layer 3: redact the secret if it somehow made it into the output."""
    return text.replace(SECRET_FLAG, "[REDACTED]")
