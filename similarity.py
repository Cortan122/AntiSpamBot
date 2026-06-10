import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, SIMILARITY_THRESHOLD

# Load the model once at startup
model = SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text):
    """Compute embedding for a message."""
    return model.encode(text, convert_to_numpy=True)


def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    # Cosine similarity
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def find_similar_spam(message_embedding, spam_patterns, threshold=SIMILARITY_THRESHOLD):
    """Find similar spam patterns to a message.

    Returns (pattern_id, text, similarity_score) or None.
    """
    best_match = None
    best_similarity = threshold

    for pattern_id, text, pattern_embedding in spam_patterns:
        similarity = compute_similarity(message_embedding, pattern_embedding)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (pattern_id, text, similarity)

    return best_match
