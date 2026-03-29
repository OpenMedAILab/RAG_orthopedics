"""FAISS 索引工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import faiss
import numpy as np


@dataclass
class FaissIndex:
    index: faiss.Index
    dim: int


def build_faiss_index(vectors: np.ndarray) -> FaissIndex:
    if vectors.size == 0:
        raise ValueError("No vectors provided to build FAISS index")
    dim = vectors.shape[1]
    # 使用 Inner Product，配合 L2 normalize 等价 cosine
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    return FaissIndex(index=index, dim=dim)


def save_faiss_index(index: faiss.Index, path: str) -> None:
    faiss.write_index(index, path)


def load_faiss_index(path: str) -> faiss.Index:
    return faiss.read_index(path)


def search_index(index: faiss.Index, query_vec: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
    if query_vec.ndim == 1:
        query_vec = query_vec.reshape(1, -1)
    # 返回 top_k 的分数和 id
    scores, ids = index.search(query_vec.astype(np.float32), top_k)
    return scores[0], ids[0]
