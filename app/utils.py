"""
Utility functions for text processing, logging, token estimation, and (optionally) GitHub automation for the MCP server.
"""

import logging
import re
import tiktoken

# =========================
# Logging and Text Utilities
# =========================

# Initialize logger (avoid duplicate handlers in multiprocess setups)
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
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

# =========================
# GitHub Automation Stub
# =========================

# This is a placeholder. Replace with your real implementation, e.g., using PyGithub or subprocess/gitpython.

class GitHubUtility:
    """
    Utility class for automating GitHub repo operations for enhancement orchestration.
    Fill in methods as needed.
    """
    def __init__(self):
        # e.g., set repo url, clone directory, token, etc.
        pass

    def clone_or_pull_repo(self):
        # TODO: Implement GitHub clone or pull (git CLI or GitPython)
        raise NotImplementedError("Implement clone_or_pull_repo()")

    def safe_branch_name(self, summary):
        # Return a git-safe, unique branch name based on summary
        import re, uuid
        name = re.sub(r"[^a-zA-Z0-9\-]", "-", summary.lower())[:40]
        return f"enh-{name}-{str(uuid.uuid4())[:8]}"

    def create_feature_branch(self, branch):
        # TODO: Implement branch creation
        raise NotImplementedError("Implement create_feature_branch()")

    def file_write(self, rel_path, content):
        # Write file content (overwriting if exists)
        import os
        abs_path = os.path.join("/app", rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return abs_path

    def commit_and_push(self, changed_files, branch, commit_message):
        # TODO: git add, commit, push for changed files to branch
        raise NotImplementedError("Implement commit_and_push()")

    def create_pull_request(self, branch, title, body):
        # TODO: Use GitHub API to create PR, return PR URL
        raise NotImplementedError("Implement create_pull_request()")

# Export instance for import elsewhere (like: from app.utils import github)
github = GitHubUtility()
