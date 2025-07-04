from fastapi import APIRouter, Request
import os
from openai import OpenAI
from app.agents import headline, compliance, formatter
from app.utils import clean_text, log_request
from app.utils import estimate_tokens

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/process")
async def process_content(request: Request):
    body = await request.json()
    raw_text = body.get("text", "")
    platform = body.get("platform", "LinkedIn")

    text = clean_text(raw_text)
    log_request("MCP", text)

    rewritten = compliance.rewrite_safe(text, client)
    formatted = formatter.format_post(rewritten, platform)
    variations = headline.generate_variants(text, client)

    return {"formatted": formatted, "safe": rewritten, "headlines": variations}

@router.post("/tokens")
async def token_count(request: Request):
    body = await request.json()
    text = clean_text(body.get("text", ""))
    model = body.get("model", "gpt-4")

    tokens = estimate_tokens(text, model)
    return {"tokens": tokens, "model": model}
