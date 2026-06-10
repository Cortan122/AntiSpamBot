from difflib import SequenceMatcher
from config import SIMILARITY_THRESHOLD


def get_embedding(text):
    """Return text as-is (no embedding needed for simple matching)."""
    return text.lower()


def compute_similarity(text1, text2):
    """Compute similarity using SequenceMatcher (0.0 to 1.0)."""
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def find_similar_spam(message_text, spam_patterns, threshold=SIMILARITY_THRESHOLD):
    """Find similar spam patterns to a message.

    Returns (pattern_id, text, similarity_score) or None.
    """
    best_match = None
    best_similarity = threshold

    for pattern_id, text, _ in spam_patterns:
        similarity = compute_similarity(message_text.lower(), text.lower())

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = (pattern_id, text, similarity)

    return best_match
