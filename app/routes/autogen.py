import glob

@router.post("/autogen-enhancements", tags=["Enhancement Automation"])
async def autogen_enhancements(
    request: Request,
    x_mcp_secret: str = Header(..., alias="x-mcp-secret")
):
    if x_mcp_secret != MCP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    code_dir = body.get("code_dir", "/app")
    file_limit = body.get("max_files", 10)

    # Collect code (limit to N files for token safety)
    py_files = glob.glob(f"{code_dir}/**/*.py", recursive=True)[:file_limit]
    code_samples = []
    for path in py_files:
        with open(path, "r") as f:
            code_samples.append(f"# {path}\n" + f.read())

    code_context = "\n\n".join(code_samples)

    prompt = f"""
Act as a senior Python code review agent. Analyze the following codebase and suggest up to 5 high-value enhancements, bug fixes, or improvements. For each, provide a clear summary and a detailed description. 
Respond with valid JSON in this format: [{{"summary": "...", "details": "..."}}]

CODEBASE:
{code_context}
"""

    # Call LLM (reusing your call_openai_for_code, but expects a list output)
    try:
        suggestions = call_openai_for_code(prompt)
        if not isinstance(suggestions, list):
            suggestions = [suggestions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI enhancement generation failed: {str(e)}")

    # Append each suggestion to the enhancement queue
    if not os.path.exists(ENH_FILE):
        with open(ENH_FILE, "w") as f:
            json.dump([], f)
    with open(ENH_FILE, "r+") as f:
        queue = json.load(f)
        for enh in suggestions:
            enh["status"] = "new"
            queue.append(enh)
        f.seek(0)
        json.dump(queue, f, indent=2)
        f.truncate()
    logger.info(f"Auto-generated {len(suggestions)} enhancements.")
    return {"queued": len(suggestions)}
