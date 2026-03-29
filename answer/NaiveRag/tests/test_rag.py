from __future__ import annotations

from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.config import RAGConfig
from rag.rag_pipeline import RAGPipeline


def test_build_and_query_with_tfidf(tmp_path: Path) -> None:
    # 使用本地哈希嵌入，避免依赖外部模型或网络
    md_dir = tmp_path / "md"
    md_dir.mkdir()

    (md_dir / "fruit.md").write_text(
        "# Fruit Guide\n\nApple is a popular fruit.\nBananas are yellow.",
        encoding="utf-8",
    )
    (md_dir / "tech.md").write_text(
        "# Tech Notes\n\nPython is great for data work.\nRust is fast.",
        encoding="utf-8",
    )

    config = RAGConfig(base_dir=tmp_path, embed_provider="local", local_embed_dim=64)
    pipeline = RAGPipeline(config=config)
    pipeline.build(md_dir=str(md_dir))

    results = pipeline.query("apple", top_k=5, retrieve_k=10, rerank=True)
    assert results, "Expected at least one retrieval result"
    assert any("apple" in r["content"].lower() for r in results)


def _manual_run() -> None:
    # 手动运行的简单入口，便于快速验证
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        md_dir = tmp_path / "md"
        md_dir.mkdir()
        (md_dir / "fruit.md").write_text(
            "# Fruit Guide\n\nApple is a popular fruit.\nBananas are yellow.",
            encoding="utf-8",
        )
        (md_dir / "tech.md").write_text(
            "# Tech Notes\n\nPython is great for data work.\nRust is fast.",
            encoding="utf-8",
        )

        config = RAGConfig(base_dir=tmp_path, embed_provider="local", local_embed_dim=64)
        pipeline = RAGPipeline(config=config)
        pipeline.build(md_dir=str(md_dir))
        results = pipeline.query("apple", top_k=5, retrieve_k=10, rerank=True)
        print("manual results:", results)


if __name__ == "__main__":
    _manual_run()
