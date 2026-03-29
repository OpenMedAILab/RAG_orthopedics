"""候选重排实现。"""

from __future__ import annotations

from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rerank_tfidf(query: str, candidates: List[Dict]) -> List[Dict]:
    if not candidates:
        return candidates
    texts = [c["content"] for c in candidates]
    # 基于 TF-IDF 的候选集内重排
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([query] + texts)
    query_vec = matrix[0:1]
    doc_vecs = matrix[1:]
    scores = cosine_similarity(query_vec, doc_vecs)[0]
    for cand, score in zip(candidates, scores):
        cand["rerank_score"] = float(score)
    return sorted(candidates, key=lambda x: x.get("rerank_score", 0.0), reverse=True)
