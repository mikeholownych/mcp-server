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

    # Sanitize and log
    text = clean_text(raw_text)
    log_request("mcp-process", text)

    # Run agents
    safe = compliance.rewrite_safe(text, client)
    formatted = formatter.format_post(safe, platform)
    headlines = headline.generate_variants(text, client)

    return {
        "safe": safe,
        "formatted": formatted,
        "headlines": headlines
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
