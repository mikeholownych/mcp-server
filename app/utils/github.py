# app/utils/github.py

import os
from github import Github, GithubException
from git import Repo  # Requires gitpython: pip install gitpython
import tempfile
import shutil

# These should be set as environment variables for security
GITHUB_TOKEN = os.getenv("BOT_GH_TOKEN")   # Personal Access Token or bot token
GITHUB_USER = os.getenv("BOT_GH_USER")     # Bot username
GITHUB_REPO = os.getenv("BOT_GH_REPO")     # Format: mikeholownych/mcp-server
CLONE_PATH = "/tmp/mcp-git-tmp"            # Or use tempfile for unique dirs

def clone_or_pull_repo():
    if os.path.exists(CLONE_PATH):
        repo = Repo(CLONE_PATH)
        repo.remotes.origin.pull()
    else:
        Repo.clone_from(f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_REPO}.git", CLONE_PATH)
    return CLONE_PATH

def safe_branch_name(summary):
    # E.g. "Implement Slack Notifier" -> "feature/implement-slack-notifier"
    name = summary.lower().replace(" ", "-")
    return f"feature/{name[:32]}"

def create_feature_branch(branch):
    repo = Repo(CLONE_PATH)
    if branch in repo.heads:
        repo.git.checkout(branch)
    else:
        repo.git.checkout('HEAD', b=branch)

def file_write(rel_path, content):
    abs_path = os.path.join(CLONE_PATH, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return abs_path

def commit_and_push(files, branch, message):
    repo = Repo(CLONE_PATH)
    repo.index.add([os.path.relpath(f, CLONE_PATH) for f in files])
    repo.index.commit(message)
    repo.remotes.origin.push(branch)

def create_pull_request(branch, title, body):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch,
        base="main"  # Or "master", depending on your repo
    )
    return pr.html_url

def cleanup():
    if os.path.exists(CLONE_PATH):
        shutil.rmtree(CLONE_PATH)
