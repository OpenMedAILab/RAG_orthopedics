"""RAG 流程编排。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .config import RAGConfig
from .embeddings import BaseEmbedder, get_embedder, LocalHashEmbedder, ModelScopeEmbedder, SiliconFlowEmbedder
from .faiss_store import build_faiss_index, load_faiss_index, save_faiss_index, search_index
from .rerank import rerank_tfidf
from .splitter import split_markdown


class RAGPipeline:
    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = (config or RAGConfig()).resolve_paths()

    def build(self, md_dir: str) -> None:
        # 构建索引：读取 Markdown -> 切分 -> 生成向量 -> 写入 FAISS
        md_files = list(_collect_markdown(md_dir))
        if not md_files:
            raise ValueError(f"No markdown files found under: {md_dir}")
        print(f"Found {len(md_files)} markdown files. Splitting...", flush=True)

        chunks: List[Dict] = []
        for path in md_files:
            text = Path(path).read_text(encoding="utf-8")
            chunks.extend(
                split_markdown(
                    text=text,
                    source_path=str(path),
                    chunk_size=self.config.chunk_size,
                    chunk_overlap=self.config.chunk_overlap,
                )
            )
        print(f"Prepared {len(chunks)} chunks. Embedding...", flush=True)

        texts = [c["content"] for c in chunks]
        embedder = get_embedder(self.config)
        embed_result = embedder.embed_documents(texts)
        index = build_faiss_index(embed_result.vectors)

        # 保存索引与元数据
        save_faiss_index(index.index, str(self.config.index_path))
        print("Index saved. Writing metadata...", flush=True)

        embed_meta = dict(embed_result.metadata)

        meta = {
            "config": _serialize_config(self.config),
            "embedder": embed_meta,
            "chunks": chunks,
        }
        self.config.meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Metadata saved. Build complete.", flush=True)

    def query(self, query_text: str, top_k: Optional[int] = None, retrieve_k: Optional[int] = None, rerank: Optional[bool] = None) -> List[Dict]:
        cfg = self.config
        top_k = top_k or cfg.top_k
        retrieve_k = retrieve_k or cfg.retrieve_k
        rerank = cfg.rerank_enabled if rerank is None else rerank

        if not cfg.index_path.exists() or not cfg.meta_path.exists():
            raise FileNotFoundError("Index or metadata not found. Run with --build first.")

        meta = json.loads(cfg.meta_path.read_text(encoding="utf-8"))
        chunks: List[Dict] = meta.get("chunks", [])
        embedder = _load_embedder(meta.get("embedder", {}))
        index = load_faiss_index(str(cfg.index_path))

        # 先用 FAISS 召回，再根据需要 rerank
        query_vec = embedder.embed_query(query_text)
        faiss_scores, ids = search_index(index, query_vec, top_k=retrieve_k)

        candidates: List[Dict] = []
        for score, idx in zip(faiss_scores, ids):
            if idx < 0 or idx >= len(chunks):
                continue
            chunk = dict(chunks[idx])
            chunk["faiss_score"] = float(score)
            candidates.append(chunk)

        if rerank:
            candidates = rerank_tfidf(query_text, candidates)
        else:
            for cand in candidates:
                cand["rerank_score"] = None

        return candidates[:top_k]


def _collect_markdown(md_dir: str) -> Iterable[str]:
    # 递归读取目录下所有 Markdown 文件
    for root, _, files in os.walk(md_dir):
        for name in files:
            if name.lower().endswith(".md"):
                yield os.path.join(root, name)


def _load_embedder(embed_meta: Dict) -> BaseEmbedder:
    # 根据元数据恢复 embedder
    embed_type = embed_meta.get("type", "modelscope")
    if embed_type == "modelscope":
        model_name = embed_meta.get("model", "BAAI/bge-m3")
        return ModelScopeEmbedder(model_name=model_name)
    if embed_type == "siliconflow":
        model_name = embed_meta.get("model", "BAAI/bge-m3")
        base_url = embed_meta.get("base_url", "https://api.siliconflow.cn/v1")
        api_key_env = embed_meta.get("api_key_env", RAGConfig().siliconflow_api_key_env)
        return SiliconFlowEmbedder(
            model_name=model_name,
            api_key_env=api_key_env,
            base_url=base_url,
        )
    if embed_type == "local":
        dim = int(embed_meta.get("dim", RAGConfig().local_embed_dim))
        return LocalHashEmbedder(dim=dim)
    raise ValueError(f"Unknown embedder type: {embed_type}")


def _serialize_config(config: RAGConfig) -> Dict:
    # JSON 序列化时将 Path 转为字符串
    data = asdict(config)
    for key, value in list(data.items()):
        if isinstance(value, Path):
            data[key] = str(value)
    return data
