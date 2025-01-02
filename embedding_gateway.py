import ollama


def ollama_calculate_embedding(text: str):
    embed = ollama.embed(model="mxbai-embed-large", input=text)
    return embed.embeddings[0]
