"""RAG 的嵌入向量后端实现（ModelScope + 在线 API）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import hashlib
import os

import numpy as np
import requests

from .config import RAGConfig


@dataclass
class EmbeddingResult:
    """统一的嵌入结果结构。"""

    vectors: np.ndarray
    metadata: Dict


class BaseEmbedder:
    """嵌入接口定义。"""

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingResult:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        raise NotImplementedError


class ModelScopeEmbedder(BaseEmbedder):
    """使用 ModelScope 本地模型进行嵌入。"""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._pipeline = _build_modelscope_pipeline(model_name)

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingResult:
        total = len(texts)
        vectors: List[List[float]] = []
        for idx, text in enumerate(texts, start=1):
            outputs = self._pipeline(text)
            extracted = _extract_modelscope_vectors(outputs)
            if extracted and isinstance(extracted[0], (int, float)):
                vectors.append(extracted)  # single vector
            else:
                vectors.extend(extracted)
            _log_progress("ModelScope embedding", idx, total)
        arr = np.asarray(vectors, dtype=np.float32)
        return EmbeddingResult(vectors=_l2_normalize(arr), metadata={"type": "modelscope", "model": self.model_name})

    def embed_query(self, text: str) -> np.ndarray:
        outputs = self._pipeline(text)
        extracted = _extract_modelscope_vectors(outputs)
        vector = extracted if extracted and isinstance(extracted[0], (int, float)) else extracted[0]
        arr = np.asarray([vector], dtype=np.float32)
        return _l2_normalize(arr)[0]


class SiliconFlowEmbedder(BaseEmbedder):
    """使用硅基流动在线 API 进行嵌入。"""

    def __init__(self, model_name: str, api_key_env: str, base_url: str) -> None:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key in env: {api_key_env}")
        self.model_name = model_name
        self.api_key = api_key
        self.api_key_env = api_key_env
        self.base_url = base_url.rstrip("/")

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingResult:
        total = len(texts)
        vectors: List[List[float]] = []
        for idx, text in enumerate(texts, start=1):
            vectors.append(self._embed_single(text))
            _log_progress("SiliconFlow embedding", idx, total)
        if not vectors:
            empty = np.zeros((0, 0), dtype=np.float32)
            return EmbeddingResult(
                vectors=empty,
                metadata={
                    "type": "siliconflow",
                    "model": self.model_name,
                    "base_url": self.base_url,
                    "api_key_env": self.api_key_env,
                },
            )
        arr = np.asarray(vectors, dtype=np.float32)
        return EmbeddingResult(
            vectors=_l2_normalize(arr),
            metadata={
                "type": "siliconflow",
                "model": self.model_name,
                "base_url": self.base_url,
                "api_key_env": self.api_key_env,
            },
        )

    def embed_query(self, text: str) -> np.ndarray:
        vector = self._embed_single(text)
        arr = np.asarray([vector], dtype=np.float32)
        return _l2_normalize(arr)[0]

    def _embed_single(self, text: str) -> List[float]:
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "input": text,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"SiliconFlow embeddings failed: {response.status_code} {response.text}")
        data = response.json()
        vectors = _extract_siliconflow_vectors(data)
        if not vectors:
            raise RuntimeError("Invalid SiliconFlow response: empty embeddings")
        return vectors[0]


class LocalHashEmbedder(BaseEmbedder):
    """本地哈希嵌入（仅用于测试/离线开发）。"""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed_documents(self, texts: Sequence[str]) -> EmbeddingResult:
        total = len(texts)
        vectors: List[np.ndarray] = []
        for idx, text in enumerate(texts, start=1):
            vectors.append(self._hash_to_vec(text))
            _log_progress("Local hash embedding", idx, total)
        stacked = np.vstack(vectors).astype(np.float32) if vectors else np.zeros((0, self.dim), dtype=np.float32)
        vectors = stacked
        return EmbeddingResult(vectors=_l2_normalize(vectors), metadata={"type": "local", "dim": self.dim})

    def embed_query(self, text: str) -> np.ndarray:
        vec = self._hash_to_vec(text).astype(np.float32)
        return _l2_normalize(vec.reshape(1, -1))[0]

    def _hash_to_vec(self, text: str) -> np.ndarray:
        # 将文本 hash 成稳定的向量，保证可重复性
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw = np.frombuffer(digest, dtype=np.uint8)
        repeated = np.resize(raw, self.dim)
        return repeated.astype(np.float32)


def get_embedder(config: RAGConfig) -> BaseEmbedder:
    """根据配置选择嵌入后端。"""

    provider = config.embed_provider.lower()
    if provider == "modelscope":
        return ModelScopeEmbedder(model_name=config.embed_model)
    if provider == "siliconflow":
        return SiliconFlowEmbedder(
            model_name=config.embed_model,
            api_key_env=config.siliconflow_api_key_env,
            base_url=config.siliconflow_base_url,
        )
    if provider == "local":
        return LocalHashEmbedder(dim=config.local_embed_dim)
    raise ValueError(f"Unknown embed provider: {config.embed_provider}")


def _build_modelscope_pipeline(model_name: str):
    """构建 ModelScope pipeline。"""

    try:
        from modelscope.pipelines import pipeline  # type: ignore
        from modelscope.utils.constant import Tasks  # type: ignore
    except Exception as exc:
        raise RuntimeError("modelscope is required for local embeddings") from exc

    # 部分模型使用 text-embedding 或 feature-extraction 任务
    try:
        return pipeline(Tasks.text_embedding, model=model_name)
    except Exception:
        return pipeline(task="text-embedding", model=model_name)


def _extract_modelscope_vectors(outputs) -> List[List[float]]:
    """兼容多种 ModelScope 输出结构。"""

    if isinstance(outputs, dict):
        for key in ("embeddings", "embedding", "vector", "vectors"):
            if key in outputs:
                return outputs[key]
    if isinstance(outputs, list):
        if outputs and isinstance(outputs[0], dict):
            vectors: List[List[float]] = []
            for item in outputs:
                for key in ("embeddings", "embedding", "vector", "vectors"):
                    if key in item:
                        vectors.append(item[key])
                        break
            if vectors:
                return vectors
        return outputs
    raise RuntimeError("Unsupported ModelScope output format")


def _extract_siliconflow_vectors(data: Dict) -> List[List[float]]:
    """解析硅基流动 API 的嵌入响应。"""

    if "data" not in data:
        raise RuntimeError("Invalid SiliconFlow response: missing 'data'")
    vectors = [item.get("embedding") for item in data["data"]]
    if not vectors or any(v is None for v in vectors):
        raise RuntimeError("Invalid SiliconFlow response: missing embeddings")
    return vectors


def _l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """归一化后可用 inner product 近似 cosine。"""

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


def _log_progress(prefix: str, current: int, total: int, every: int = 10) -> None:
    if total <= 0:
        return
    if current == 1 or current % every == 0 or current == total:
        print(f"{prefix}: {current}/{total}", flush=True)
