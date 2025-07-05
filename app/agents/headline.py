def generate_variants(prompt, client, brand="Ethical AI Insider", pillar="AI Risk", platform="LinkedIn"):
    """
    Generate 5 platform-optimized, brand-aligned, high-engagement headline variations,
    enforcing per-platform length limits.
    """
    # Length limits (in characters) per platform
    limits = {
        "linkedin": 70,
        "medium": 80,
        "wordpress": 70,
        "convertkit": 45,
    }
    platform_key = platform.lower()
    max_len = limits.get(platform_key, 70)  # Default to 70 if unknown

    system_msg = (
        f"You are a headline expert for {brand}. "
        "Generate 5 high-engagement, platform-optimized headline/title variations for the following content. "
        f"Audience: tech executives, startup founders, compliance leaders. "
        f"Pillar: {pillar}. Platform: {platform}. "
        "For LinkedIn: strong hook, curiosity, or controversy. For Medium: SEO/curiosity and clear value. "
        "For WordPress: include keywords and clarity. For ConvertKit: email subject style. "
        f"ALL HEADLINES must be actionable, on-brand, NEVER generic, and MUST NOT EXCEED {max_len} CHARACTERS."
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(model="gpt-4", messages=messages)
    raw_lines = response.choices[0].message.content.strip().split("\n")
    headlines = []
    for line in raw_lines:
        cleaned = line.lstrip("0123456789.●- ").strip()
        if cleaned and len(cleaned) <= max_len:
            headlines.append(cleaned)
        elif cleaned:
            # Truncate (optional: append ellipsis if cut)
            headlines.append(cleaned[:max_len].rstrip() + "…")
    return headlines
