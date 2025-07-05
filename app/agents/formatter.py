# app/agents/formatter.py

def format_post(content: str, platform: str) -> str:
    """
    Format processed content for a specific platform.
    """
    # precompute HTML-safe body
    html_body = content.replace("\n", "<br>")

    if platform == "LinkedIn":
        return content[:3000]

    elif platform == "ConvertKit":
        # now safe to f-string without backslashes
        return "<p>" + html_body + "</p>"

    elif platform == "Medium":
        return content

    return content
