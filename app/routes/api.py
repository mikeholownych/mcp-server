# app/routes/api.py

import os
from fastapi import APIRouter, Request, Header, HTTPException
from openai import OpenAI

from app.agents import headline, compliance, formatter
from app.utils import clean_text, log_request, estimate_tokens

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MCP_SECRET = os.getenv("MCP_SECRET", "")

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

    # Build brand-aligned, pillar/platform-aware prompt context
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
