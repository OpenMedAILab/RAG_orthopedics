"""Naive RAG 的配置定义。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RAGConfig:
    """保存 RAG 流程的参数与默认路径。"""

    base_dir: Path = Path(".")
    # 索引与元数据文件路径
    index_path: Path = Path("rag_index.faiss")
    meta_path: Path = Path("rag_meta.json")
    # 切分与检索参数
    chunk_size: int = 1000
    chunk_overlap: int = 100
    top_k: int = 3
    retrieve_k: int = 10
    rerank_enabled: bool = True
    # 嵌入模型配置
    embed_provider: str = "modelscope"
    embed_model: str = "BAAI/bge-m3"
    siliconflow_api_key_env: str = "SILICONFLOW_API_KEY"
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    # 本地测试用嵌入维度
    local_embed_dim: int = 256

    def resolve_paths(self) -> "RAGConfig":
        """将路径与 base_dir 结合，返回新的配置对象。"""
        return RAGConfig(
            base_dir=self.base_dir,
            index_path=(self.base_dir / self.index_path).resolve(),
            meta_path=(self.base_dir / self.meta_path).resolve(),
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            top_k=self.top_k,
            retrieve_k=self.retrieve_k,
            rerank_enabled=self.rerank_enabled,
            embed_provider=self.embed_provider,
            embed_model=self.embed_model,
            siliconflow_api_key_env=self.siliconflow_api_key_env,
            siliconflow_base_url=self.siliconflow_base_url,
            local_embed_dim=self.local_embed_dim,
        )
