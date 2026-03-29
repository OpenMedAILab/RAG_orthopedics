"""Naive RAG 的命令行入口。"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from .config import RAGConfig
from .rag_pipeline import RAGPipeline


def _print_results(results):
    # 输出结果时截断内容，便于阅读
    for i, item in enumerate(results, start=1):
        content = item.get("content", "")
        snippet = content[:800]
        print(f"[{i}] source_path={item.get('source_path')}")
        print(f"    chunk_order_index={item.get('chunk_order_index')}")
        print(f"    faiss_score={item.get('faiss_score')}")
        print(f"    rerank_score={item.get('rerank_score')}")
        print("    content:")
        print(textwrap.indent(snippet, "      "))
        print("-")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Naive RAG CLI")
    parser.add_argument("--build", action="store_true", help="Build and persist the index")
    parser.add_argument("--md_dir", type=str, default="data", help="Directory containing markdown files")
    parser.add_argument("--query", type=str, help="Query text")
    parser.add_argument("--top_k", type=int, default=5, help="Final number of chunks to return")
    parser.add_argument("--retrieve_k", type=int, default=20, help="Number of candidates to retrieve from FAISS")
    parser.add_argument("--no_rerank", action="store_true", help="Disable reranking")
    parser.add_argument(
        "--embedder",
        type=str,
        default="modelscope",
        choices=["modelscope", "siliconflow", "local"],
        help="Embedding provider",
    )
    parser.add_argument("--embed_model", type=str, default="BAAI/bge-m3", help="Embedding model name")
    parser.add_argument(
        "--siliconflow_base_url",
        type=str,
        default="https://api.siliconflow.cn/v1",
        help="SiliconFlow API base URL",
    )
    parser.add_argument(
        "--siliconflow_api_key_env",
        type=str,
        default="SILICONFLOW_API_KEY",
        help="Environment variable name for SiliconFlow API key",
    )
    parser.add_argument("--local_embed_dim", type=int, default=256, help="Local hash embedder dimension")
    return parser


def main() -> None:
    # CLI 主入口：可构建索引或进行查询
    parser = build_arg_parser()
    args = parser.parse_args()

    config = RAGConfig(
        top_k=args.top_k,
        retrieve_k=args.retrieve_k,
        rerank_enabled=not args.no_rerank,
        embed_provider=args.embedder,
        embed_model=args.embed_model,
        siliconflow_api_key_env=args.siliconflow_api_key_env,
        siliconflow_base_url=args.siliconflow_base_url,
        local_embed_dim=args.local_embed_dim,
    )
    pipeline = RAGPipeline(config=config)

    if args.build:
        # 基于当前脚本目录解析相对路径，避免工作目录变化导致找不到数据
        md_dir = args.md_dir
        if not md_dir.startswith(("/", "\\")):
            md_dir = str((Path(__file__).resolve().parents[1] / md_dir).resolve())
        pipeline.build(md_dir=md_dir)
        print(f"Index built at {pipeline.config.index_path}")

    if args.query:
        results = pipeline.query(
            query_text=args.query,
            top_k=args.top_k,
            retrieve_k=args.retrieve_k,
            rerank=not args.no_rerank,
        )
        _print_results(results)

    if not args.build and not args.query:
        parser.print_help()


if __name__ == "__main__":
    main()
