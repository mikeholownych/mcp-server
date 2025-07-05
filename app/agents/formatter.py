# app/agents/formatter.py

def format_post(content: str, platform: str) -> str:
    """
    Format processed content for a specific platform using best practices.
    """

    html_body = content.replace("\n", "<br>")

    if platform.lower() == "linkedin":
        # LinkedIn best practices: plain text, ≤3000 chars, emoji ok, simple paragraphs.
        return content[:3000]

    elif platform.lower() == "convertkit":
        # ConvertKit: HTML, short readable blocks.
        return f"<p>{html_body}</p>"

    elif platform.lower() == "medium":
        # Medium: raw text, supports markdown and paragraphs, long-form welcome.
        return content

    elif platform.lower() == "wordpress":
        # WordPress: HTML with headings and paragraphs, 1-2 <h2> for structure.
        # Simple heuristic: bold the first line as a title, wrap paragraphs.
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if not lines:
            return ""
        title = f"<h2>{lines[0]}</h2>"
        body = "<br>".join(lines[1:])
        return f"{title}<p>{body}</p>"

    # Default: return as-is for unknown platforms
    return content
