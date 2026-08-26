import hashlib
import math


def create_text_embedding(text: str, dimensions: int = 12) -> list[float]:
    normalized = text.lower().strip().encode("utf-8")
    digest = hashlib.sha256(normalized).digest()
    values = []
    for index in range(dimensions):
        raw = digest[index] / 255
        values.append(round(raw * 2 - 1, 4))
    return values


def cosine_similarity(first: list[float], second: list[float]) -> float:
    if not first or not second or len(first) != len(second):
        return 0
    dot = sum(a * b for a, b in zip(first, second))
    first_norm = math.sqrt(sum(a * a for a in first))
    second_norm = math.sqrt(sum(b * b for b in second))
    if first_norm == 0 or second_norm == 0:
        return 0
    return round(dot / (first_norm * second_norm), 4)
