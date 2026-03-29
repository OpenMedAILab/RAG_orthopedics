# Naive RAG (Markdown + FAISS)

这个项目实现一个简洁的 RAG 管线：读取 Markdown、切分 chunk、嵌入向量、FAISS 检索、TF-IDF rerank。嵌入支持 ModelScope 本地模型或硅基流动在线 API。

## Features
- Recursive Markdown chunking via `RecursiveCharacterTextSplitter`
- Embeddings via ModelScope (local) or SiliconFlow API (online)
- FAISS `IndexFlatIP` with L2 normalization for cosine similarity
- TF-IDF rerank (enabled by default)
- Persistent index + metadata

## Install
```bash
pip install -e .
```

使用 conda（推荐）：
```bash
conda create -n naive-rag python=3.11 -y
conda activate naive-rag
pip install -e .
```

## Usage
构建索引（默认 ModelScope + bge-m3）：
```bash
python -m rag.cli --build --md_dir data
```

使用硅基流动 API：
```bash
export SILICONFLOW_API_KEY="your_key"
python -m rag.cli --build --md_dir data --embedder siliconflow --embed_model BAAI/bge-m3
```

查询：
```bash
python -m rag.cli --query "naive rag"
```

关闭 rerank：
```bash
python -m rag.cli --query "naive rag" --no_rerank
```

## Tests
```bash
pytest -q
```

说明：测试使用本地哈希嵌入（`--embedder local`），避免依赖外部模型或网络。
