def rewrite_safe(prompt, client, brand="Ethical AI Insider", pillar="AI Risk", platform="LinkedIn"):
    """
    Rewrite the content to remove risky claims, add disclaimers, and ensure alignment with brand, pillar, and platform.
    """
    system_content = (
        f"You are an expert compliance editor for {brand}. "
        "Your job is to rewrite any content to remove risky claims, minimize legal/ethical liability, "
        "add practical disclaimers where appropriate, and make sure it fits the audience and best practices for the specified pillar and platform. "
        f"For this content, the pillar is: '{pillar}', and the platform is: '{platform}'. "
        "Be especially mindful of compliance, ethical language, and actionable clarity for tech leaders and founders."
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": prompt}
    ]
    return client.chat.completions.create(model="gpt-4", messages=messages).choices[0].message.content
