def generate_variants(prompt, client):
    messages = [{"role": "system", "content": "Generate 5 high-engagement headline variations."},
                {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model="gpt-4", messages=messages)
    return response.choices[0].message.content.strip().split("\n")
