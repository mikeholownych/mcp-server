# app/utils/github.py

import os
import tempfile
import shutil
from github import Github, GithubException
from git import Repo, InvalidGitRepositoryError, GitCommandError  # pip install gitpython
import logging

# --- CONFIGURATION ---

# Environment variables (required)
GITHUB_TOKEN = os.getenv("BOT_GH_TOKEN")   # GitHub PAT with repo permissions
GITHUB_USER = os.getenv("BOT_GH_USER")     # GitHub bot username (not required for all API calls)
GITHUB_REPO = os.getenv("BOT_GH_REPO")     # Format: mikeholownych/mcp-server

# Use a temp dir for thread/process safety
CLONE_PATH = os.getenv("MCP_CLONE_PATH") or tempfile.mkdtemp(prefix="mcp-git-")

# Logging setup
logger = logging.getLogger("mcp-github")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

# --- UTILITY FUNCTIONS ---

def _check_env():
    for k, v in [
        ("BOT_GH_TOKEN", GITHUB_TOKEN),
        ("BOT_GH_REPO", GITHUB_REPO),
    ]:
        if not v:
            raise EnvironmentError(f"Required env var {k} is missing!")

def clone_or_pull_repo():
    # Use your actual values
    REPO_URL = "https://github.com/mikeholownych/mcp-server.git"
    CLONE_PATH = "/tmp/mcp-git-fkp_6mw6"

    # If path exists but is not a repo, delete it first (optional safety)
    if os.path.exists(CLONE_PATH):
        try:
            _ = Repo(CLONE_PATH)
        except InvalidGitRepositoryError:
            import shutil
            shutil.rmtree(CLONE_PATH)
            # Re-clone below

    if not os.path.exists(CLONE_PATH):
        Repo.clone_from(REPO_URL, CLONE_PATH)
    else:
        # Already a valid repo, pull
        repo = Repo(CLONE_PATH)
        repo.remotes.origin.pull()

def safe_branch_name(summary):
    # Lowercase, dash, 32 chars for slug, and "feature/" prefix
    slug = (
        summary.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
        .replace(".", "-")
    )
    return f"feature/{slug[:32]}"

def create_feature_branch(branch):
    repo = Repo(CLONE_PATH)
    branch_names = [h.name for h in repo.heads]
    if branch in branch_names:
        logger.info(f"Checking out existing branch {branch}")
        repo.git.checkout(branch)
    else:
        logger.info(f"Creating and checking out branch {branch}")
        repo.git.checkout("HEAD", b=branch)

def file_write(rel_path, content):
    abs_path = os.path.join(CLONE_PATH, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Wrote file: {rel_path}")
    return abs_path

def commit_and_push(files, branch, message):
    repo = Repo(CLONE_PATH)
    rel_files = [os.path.relpath(f, CLONE_PATH) for f in files]
    repo.index.add(rel_files)
    # Only commit if there are changes
    if repo.is_dirty(untracked_files=True):
        logger.info(f"Committing and pushing to branch {branch}")
        repo.index.commit(message)
        try:
            repo.git.push('--set-upstream', 'origin', branch)
        except GitCommandError as e:
            logger.error(f"Push failed: {e}")
            raise
    else:
        logger.info("No changes to commit.")

def create_pull_request(branch, title, body):
    _check_env()
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    # Try to create a PR; if it already exists, return its URL
    try:
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base="main"
        )
        logger.info(f"PR created: {pr.html_url}")
        return pr.html_url
    except GithubException as e:
        # If PR already exists, try to fetch it
        logger.warning(f"Exception on PR creation: {e}")
        pulls = repo.get_pulls(state='open', head=f"{branch}")
        for p in pulls:
            if p.head.ref == branch:
                logger.info(f"Existing PR found: {p.html_url}")
                return p.html_url
        raise

def cleanup():
    if os.path.exists(CLONE_PATH):
        logger.info(f"Cleaning up repo at {CLONE_PATH}")
        shutil.rmtree(CLONE_PATH)

# --- Optional: run cleanup at process exit ---
import atexit
atexit.register(cleanup)
