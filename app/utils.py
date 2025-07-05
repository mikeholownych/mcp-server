"""
Utility functions for text processing, logging, and token estimation in the MCP server.
"""

import logging
import re
import tiktoken

# Initialize logger
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)

# Stream to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
if not logger.hasHandlers():
    logger.addHandler(console_handler)

def clean_text(text: str) -> str:
    """Remove excess whitespace and special chars for clean input/output."""
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned

def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Rough token count estimate using tiktoken."""
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def log_request(module: str, text: str) -> None:
    """Log structured input for tracing."""
    logger.info(f"[{module.upper()}] Processing input: {text[:80]}...")

def truncate_to_tokens(text: str, max_tokens: int = 3000, model: str = "gpt-4") -> str:
    """Ensure text input stays within OpenAI token limits."""
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    tokens = enc.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return enc.decode(tokens)
