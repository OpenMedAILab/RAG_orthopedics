"""Markdown 切分工具。"""

from __future__ import annotations

from typing import Callable, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def _tiktoken_length() -> Callable[[str], int]:
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("cl100k_base")

        def _count(text: str) -> int:
            # 使用 tiktoken 进行 token 计数
            return max(1, len(enc.encode(text)))

        return _count
    except Exception:
        def _fallback(text: str) -> int:
            # 简单的 token 估算（离线 fallback）
            return max(1, len(text) // 4)

        return _fallback


def get_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    length_function = _tiktoken_length()
    separators = [
        # 分隔符按优先级从高到低
        "\n#### ",
        "\n### ",
        "\n## ",
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        ", ",
        " ",
        "",
    ]
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        separators=separators,
    )


def split_markdown(text: str, source_path: str, chunk_size: int, chunk_overlap: int) -> List[Dict]:
    splitter = get_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_text(text)
    length_fn = splitter._length_function
    results: List[Dict] = []
    for idx, chunk in enumerate(chunks):
        # 每个 chunk 都保留必要元信息，便于后续检索与展示
        results.append(
            {
                "content": chunk,
                "tokens": int(length_fn(chunk)),
                "chunk_order_index": idx,
                "source_path": source_path,
            }
        )
    return results
