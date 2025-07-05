# app/utils/github.py

import os
import shutil
from github import Github, GithubException
from git import Repo, InvalidGitRepositoryError, GitCommandError
import logging

# --- CONFIGURATION ---

GITHUB_TOKEN = os.getenv("BOT_GH_TOKEN")
GITHUB_USER = os.getenv("BOT_GH_USER")
GITHUB_REPO = os.getenv("BOT_GH_REPO")
CLONE_PATH = "/tmp/mcp-git"  # Fixed path for all enhancement cycles

# Logging setup
logger = logging.getLogger("mcp-github")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

def _check_env():
    for k, v in [
        ("BOT_GH_TOKEN", GITHUB_TOKEN),
        ("BOT_GH_REPO", GITHUB_REPO),
    ]:
        if not v:
            raise EnvironmentError(f"Required env var {k} is missing!")

def clone_or_pull_repo():
    """Ensures a clean and valid local repo for PR automation."""
    REPO_URL = f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_REPO}.git"

    # If path exists but not a valid git repo, delete and re-clone
    if os.path.exists(CLONE_PATH):
        try:
            repo = Repo(CLONE_PATH)
            # Test if we can get current branch
            _ = repo.active_branch
            repo.remotes.origin.fetch()
            repo.git.checkout("main")
            repo.remotes.origin.pull()
            logger.info(f"Updated repo at {CLONE_PATH}")
            return
        except Exception as e:
            logger.warning(f"Invalid repo at {CLONE_PATH}: {e} – Re-cloning.")
            shutil.rmtree(CLONE_PATH)
    # Clone fresh
    logger.info(f"Cloning fresh repo to {CLONE_PATH}")
    Repo.clone_from(REPO_URL, CLONE_PATH, branch="main")

def safe_branch_name(summary):
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
    if branch in [h.name for h in repo.heads]:
        logger.info(f"Checking out existing branch {branch}")
        repo.git.checkout(branch)
    else:
        logger.info(f"Creating and checking out branch {branch}")
        repo.git.checkout("main")
        repo.git.checkout(b=branch)

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
        logger.warning(f"Exception on PR creation: {e}")
        pulls = repo.get_pulls(state='open', head=branch)
        for p in pulls:
            if p.head.ref == branch:
                logger.info(f"Existing PR found: {p.html_url}")
                return p.html_url
        raise

def cleanup():
    if os.path.exists(CLONE_PATH):
        logger.info(f"Cleaning up repo at {CLONE_PATH}")
        shutil.rmtree(CLONE_PATH)

import atexit
atexit.register(cleanup)
