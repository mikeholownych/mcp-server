# app/routes/api.py

import os
import json
import traceback
import time
import logging

from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from openai import OpenAI

from app.agents import headline, compliance, formatter
from app.utils import clean_text, log_request, estimate_tokens
from app.utils import github

# Setup logger
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

router = APIRouter()

# ---- Environment Variable Validation ----
REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "OPENAI_ASSISTANT_ID",
    "MCP_SECRET",
    "BOT_GH_TOKEN",
    "BOT_GH_USER",
    "BOT_GH_REPO"
]
missing_vars = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MCP_SECRET = os.getenv("MCP_SECRET", "")
ENH_FILE = "/app/enhancements.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")


@router.get("/", tags=["Health"])
async def health_check():
    """Basic health check."""
    return {"status": "ok"}


@router.post("/process", tags=["Processing"])
async def process_content(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    """Process content through MCP agents with brand/pillar/platform context."""
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    raw_text = body.get("text", "")
    platform = body.get("platform", "LinkedIn")
    pillar = body.get("pillar", "AI Risk")
    name = body.get("name", "")
    brand = body.get("brand", "Ethical AI Insider")
    context = body.get("context", "")

    if not raw_text or not platform or not pillar:
        raise HTTPException(status_code=400, detail="Missing required fields: text, platform, pillar")

    # Sanitize and log
    text = clean_text(raw_text)
    log_request("mcp-process", text)

    prompt_context = f"""
You are the content engine for {brand}—a leading advisory on AI risk, compliance, and responsible innovation for technology executives and startup founders.

Requirements:
- All content must be actionable, practical, and directly relevant to ethical AI, governance, compliance, or risk management.
- Use the pillar: "{pillar}" for voice, theme, and context.
- Format and structure for platform: "{platform}". Best practices:
    - LinkedIn: strong hook, brief insights, practical/personal angle, clear CTA.
    - Medium: SEO headline, intro story, detailed body, reflective close.
    - WordPress: SEO meta, H2/H3, bullets, summary/CTA.
    - ConvertKit: Catchy subject, brief actionable intro, clear CTA.
- Always align with {brand}'s mission: helping tech leaders, founders, and compliance professionals build ethical, trusted AI.
- Never produce generic or off-brand content.
- The idea is: "{text}"
- Draft name (for internal use): "{name}"
- Additional context: "{context}"
After writing, also return a field "brandCompliance" (True/False) with a one-sentence rationale.
""".strip()

    try:
        # Run agents
        safe = compliance.rewrite_safe(
            prompt_context,
            client,
            brand=brand,
            pillar=pillar,
            platform=platform
        )
        formatted = formatter.format_post(safe, platform)
        headlines = headline.generate_variants(
            prompt_context,
            client,
            brand=brand,
            pillar=pillar,
            platform=platform
        )
    except Exception as e:
        logger.error(f"OpenAI agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI agent error: {str(e)}")

    # Brand Compliance QA
    compliance_keywords = [
        "ethical AI", "compliance", "risk", "governance", "AI Insider", "tech leader", "startup founder"
    ]
    brand_compliance = any(kw.lower() in safe.lower() for kw in compliance_keywords)
    brand_compliance_note = (
        "True: Content references key Ethical AI Insider themes."
        if brand_compliance
        else "False: Content may not reference Ethical AI Insider themes—please revise prompt."
    )

    return {
        "safe": safe,
        "formatted": formatted,
        "headlines": headlines,
        "platform": platform,
        "pillar": pillar,
        "brand": brand,
        "brandCompliance": brand_compliance_note,
        "name": name,
        "context": context
    }


@router.post("/tokens", tags=["Debug"])
async def token_count(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    """Estimate OpenAI token count for a given string."""
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    raw_text = body.get("text", "")
    model = body.get("model", "gpt-4")

    text = clean_text(raw_text)
    count = estimate_tokens(text, model)

    return {"tokens": count, "model": model}


# ---------- Enhancement Automation Section ----------

def validate_enhancement(enh: dict):
    """Ensure enhancement request has required fields."""
    if not enh or not enh.get("summary") or not enh.get("details"):
        raise ValueError("Enhancement request must include 'summary' and 'details'.")

def run_enhancement_agent():
    """Background task to process queued enhancement requests using OpenAI coding agent and GitHub."""
    if not os.path.exists(ENH_FILE):
        with open(ENH_FILE, "w") as f:
            json.dump([], f)
    with open(ENH_FILE, "r") as f:
        queue = json.load(f)

    updated = False

    for i, enh in enumerate(queue):
        if enh.get("status") != "new":
            continue
        try:
            validate_enhancement(enh)
            summary = enh["summary"]
            details = enh["details"]
            ai_prompt = f"""
You are the coding agent for MCP-server (Python FastAPI, Docker).
Enhancement request: {summary}
Details: {details}
Provide a JSON object with:
- files: [{{
    "path": <relative file>,
    "content": <full file content to write>
  }}]
- commit_message: <commit summary>
- pr_title: <PR title>
- pr_body: <PR body>
"""
            ai_response = call_openai_for_code(ai_prompt)
            files = ai_response["files"]
            commit_message = ai_response["commit_message"]
            pr_title = ai_response["pr_title"]
            pr_body = ai_response["pr_body"]

            # GitHub workflow
            github.clone_or_pull_repo()
            branch = github.safe_branch_name(summary)
            github.create_feature_branch(branch)
            changed_files = []
            for file_obj in files:
                rel = file_obj["path"]
                content = file_obj["content"]
                abs_path = github.file_write(rel, content)
                changed_files.append(abs_path)
            github.commit_and_push(changed_files, branch, commit_message)
            pr_url = github.create_pull_request(branch, pr_title, pr_body)

            enh["status"] = "pr-submitted"
            enh["pr_url"] = pr_url
            updated = True
            logger.info(f"Enhancement '{summary}' submitted as PR: {pr_url}")
        except Exception as e:
            enh["status"] = "error"
            enh["error"] = str(e) + "\n" + traceback.format_exc()
            updated = True
            logger.error(f"Enhancement processing error: {str(e)}")

    # Persist updated queue
    if updated:
        with open(ENH_FILE, "w") as f:
            json.dump(queue, f, indent=2)


def call_openai_for_code(prompt: str) -> dict:
    """
    Calls an OpenAI Assistant (with Code Interpreter enabled) to generate code enhancements.
    Expects the Assistant to output a single JSON object with the required structure.
    """
    try:
        code_client = OpenAI(api_key=OPENAI_API_KEY)
        thread = code_client.beta.threads.create()
        code_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        run = code_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=OPENAI_ASSISTANT_ID,
            instructions=(
                "You are an expert Python/DevOps/Automation agent. "
                "Your reply MUST be a single valid JSON block with the keys: files, commit_message, pr_title, pr_body. "
                "If you output code, always use triple backticks with correct syntax highlighting. "
                "No markdown or prose outside the code block."
            )
        )
        # Wait for completion
        timeout = 120
        elapsed = 0
        while run.status not in ("completed", "failed", "cancelled"):
            time.sleep(2)
            elapsed += 2
            if elapsed > timeout:
                raise RuntimeError("OpenAI run timed out")
            run = code_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status != "completed":
            raise RuntimeError(f"OpenAI run failed: {run.status}")

        messages = code_client.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            for c in msg.content:
                if c.type == "text":
                    content = c.text.value.strip()
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    try:
                        return json.loads(content)
                    except Exception as e:
                        logger.error(f"OpenAI Assistant output parse error: {e} - Content: {content}")
                        continue
        raise RuntimeError("No valid JSON response from OpenAI Assistant.")

    except Exception as e:
        logger.error(f"OpenAI Assistant error: {str(e)}")
        raise

# --- Enhancement Automation Routes ---

@router.post("/trigger-enhancement-cycle", tags=["Enhancement Automation"])
async def trigger_enhancement_cycle(
    background_tasks: BackgroundTasks,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    """Trigger the enhancement automation cycle in the background."""
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    background_tasks.add_task(run_enhancement_agent)
    return {"ok": True, "status": "Enhancement automation started"}

@router.post("/enhancement-request", tags=["Enhancement Automation"])
async def add_enhancement(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    """Queue a new enhancement request for code automation."""
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    enh = await request.json()
    try:
        validate_enhancement(enh)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Enhancement validation failed: {str(e)}")
    enh["status"] = "new"
    # Ensure file exists and is list
    if not os.path.exists(ENH_FILE):
        with open(ENH_FILE, "w") as f:
            json.dump([], f)
    with open(ENH_FILE, "r+") as f:
        queue = json.load(f)
        queue.append(enh)
        f.seek(0)
        json.dump(queue, f, indent=2)
        f.truncate()
    logger.info(f"Enhancement queued: {enh['summary']}")
    return {"ok": True, "msg": "Enhancement queued"}

@router.get("/enhancements", tags=["Enhancement Automation"])
async def list_enhancements(x_mcp_secret: str = Header(..., alias="x-mcp-secret")):
    """List all enhancement requests and statuses."""
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not os.path.exists(ENH_FILE):
        return []
    with open(ENH_FILE, "r") as f:
        return json.load(f)
