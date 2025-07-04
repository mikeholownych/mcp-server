def rewrite_safe(prompt, client):
    messages = [{"role": "system", "content": "Rewrite the content to remove risky claims and add disclaimers if needed."},
                {"role": "user", "content": prompt}]
    return client.chat.completions.create(model="gpt-4", messages=messages).choices[0].message.content
