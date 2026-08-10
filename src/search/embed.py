"""
Embedding helper -- wraps Gemini's embedding model for text -> vector.
"""
import numpy as np
from google import genai
from google.genai import types

from src.config import API_KEY, EMBED_MODEL

client = genai.Client(api_key=API_KEY)


def embed_texts(texts: list[str], batch_size: int = 20) -> np.ndarray:
    """
    Embed a list of strings and return a (n, dim) numpy array.
    Batches requests to stay within API limits.
    """
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
        )
        for embedding_obj in result.embeddings:
            all_embeddings.append(embedding_obj.values)
        print(f"  embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    return np.array(all_embeddings, dtype="float32")


def embed_single(text: str) -> np.ndarray:
    """Embed a single string, e.g. a candidate profile summary or a search query."""
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[text],
    )
    return np.array(result.embeddings[0].values, dtype="float32")
