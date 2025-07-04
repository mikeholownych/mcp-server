def format_post(content, platform):
    if platform == "LinkedIn":
        return content[:3000]  # character-safe with line breaks
    elif platform == "ConvertKit":
        return f"<p>{content.replace('\n', '<br>')}</p>"
    elif platform == "Medium":
        return content  # markdown/raw
    return content
