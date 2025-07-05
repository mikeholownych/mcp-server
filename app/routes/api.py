# app/routes/api.py

import os
import json
import traceback
import time

from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from openai import OpenAI

from app.agents import headline, compliance, formatter
from app.utils import clean_text, log_request, estimate_tokens
from app.utils import github

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MCP_SECRET = os.getenv("MCP_SECRET", "")

ENH_FILE = "/app/enhancements.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

@router.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@router.post("/process", tags=["Processing"])
async def process_content(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    # Authenticate request
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    raw_text = body.get("text", "")
    platform = body.get("platform", "LinkedIn")
    pillar = body.get("pillar", "AI Risk")
    name = body.get("name", "")
    brand = body.get("brand", "Ethical AI Insider")
    context = body.get("context", "")

    # Sanitize and log
    text = clean_text(raw_text)
    log_request("mcp-process", text)

    # Brand/pillar/platform prompt context
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

    # Run agents with brand, pillar, platform awareness
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

    # Brand Compliance QA (basic version)
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
    # Authenticate request
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    raw_text = body.get("text", "")
    model = body.get("model", "gpt-4")

    text = clean_text(raw_text)
    count = estimate_tokens(text, model)

    return {"tokens": count, "model": model}

# --------------------- Enhancement Automation Section -------------------------

def run_enhancement_agent():
    # 1. Load enhancements queue
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
            summary = enh["summary"]
            details = enh["details"]
            # Compose AI prompt for code agent
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
            # 3. Call OpenAI/coding agent (implement OpenAI/Assistant API call here)
            ai_response = call_openai_for_code(ai_prompt)  # Implement this function

            files = ai_response["files"]
            commit_message = ai_response["commit_message"]
            pr_title = ai_response["pr_title"]
            pr_body = ai_response["pr_body"]

            # 4. GitHub operations
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
        except Exception as e:
            enh["status"] = "error"
            enh["error"] = str(e) + "\n" + traceback.format_exc()
            updated = True

    # 5. Write back queue
    if updated:
        with open(ENH_FILE, "w") as f:
            json.dump(queue, f, indent=2)

def call_openai_for_code(prompt):
    """
    Calls an OpenAI Assistant (with Code Interpreter enabled) to generate code enhancements.
    Expects the Assistant to output a single JSON object with the required structure.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    # 1. Create a new thread
    thread = client.beta.threads.create()

    # 2. Add the prompt as a message
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # 3. Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=OPENAI_ASSISTANT_ID,
        instructions=(
            "You are an expert Python/DevOps/Automation agent. "
            "Your reply MUST be a single valid JSON block with the keys: files, commit_message, pr_title, pr_body. "
            "If you output code, always use triple backticks with correct syntax highlighting. "
            "No markdown or prose outside the code block."
        )
    )

    # 4. Wait for run to complete
    while run.status not in ("completed", "failed", "cancelled"):
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status != "completed":
        raise RuntimeError(f"OpenAI run failed: {run.status}")

    # 5. Get the assistant’s message
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in reversed(messages.data):  # newest first
        for c in msg.content:
            if c.type == "text":
                content = c.text.value.strip()
                # Extract only the JSON block (strip code fences if present)
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                try:
                    import json
                    return json.loads(content)
                except Exception as e:
                    raise RuntimeError(f"Assistant output was not valid JSON: {e}\n{content}")

    raise RuntimeError("No valid message returned by OpenAI Assistant.")

@router.post("/trigger-enhancement-cycle", tags=["Enhancement Automation"])
async def trigger_enhancement_cycle(
    background_tasks: BackgroundTasks,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    background_tasks.add_task(run_enhancement_agent)
    return {"ok": True, "status": "Enhancement automation started"}

@router.post("/enhancement-request", tags=["Enhancement Automation"])
async def add_enhancement(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    enh = await request.json()
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
    return {"ok": True, "msg": "Enhancement queued"}
