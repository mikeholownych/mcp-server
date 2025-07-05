def generate_variants(prompt, client, brand="Ethical AI Insider", pillar="AI Risk", platform="LinkedIn"):
    """
    Generate 5 platform-optimized, brand-aligned, high-engagement headline variations.
    """
    system_msg = (
        f"You are a headline expert for {brand}. "
        "Generate 5 high-engagement, platform-optimized headline/title variations for the following content. "
        f"Audience: tech executives, startup founders, compliance leaders. "
        f"Pillar: {pillar}. Platform: {platform}. "
        "For LinkedIn: strong hook, curiosity, or controversy. For Medium: SEO/curiosity and clear value. "
        "For WordPress: include keywords and clarity. For ConvertKit: email subject style. "
        "All headlines must be actionable, on-brand, and never generic."
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(model="gpt-4", messages=messages)
    # Parse output: split on newlines, remove empty, strip numbers/bullets, and whitespace
    raw_lines = response.choices[0].message.content.strip().split("\n")
    # Remove leading numbering/bullets and trim
    headlines = []
    for line in raw_lines:
        cleaned = line.lstrip("0123456789.●- ").strip()
        if cleaned:
            headlines.append(cleaned)
    return headlines
