# RAG Orthopedics 骨科 RAG 问答评估系统

RAG（检索增强生成）与 No-RAG 模式下大语言模型在骨科医学问答任务中的表现对比评估系统。

## 项目简介

本项目包含三个独立的子项目，用于对比评估 RAG 与 No-RAG 两种模式下大语言模型在骨科医学问答任务中的表现差异。

## 子项目

| 项目 | 目录 | 说明 |
|------|------|------|
| **问答评估** | `answer/` | RAG 问答生成与自动评估系统 |
| **图表生成** | `charts/` | 评估结果统计可视化 |
| **Web 评分** | `web/` | 人工评分 Web 界面 |

## 快速开始

### 环境准备

```bash
# 安装 uv 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目（包含 submodule）
git clone --recursive https://github.com/OpenMedAILab/RAG_orthopedics.git
cd RAG_orthopedics
```

### 运行问答评估

```bash
cd answer
uv sync
python main.py
```

### 运行图表生成

```bash
cd charts
uv sync
python scripts/generate_table1.py
```

### 运行 Web 评分系统

```bash
cd web
uv sync
python app.py
# 访问 http://localhost:5000
```

## 项目结构

```
RAG_orthopedics/
├── README.md                      # 项目说明
├── pyproject.toml                 # 根工作区配置
├── .gitignore                     # Git 忽略规则
├── .gitmodules                    # Git submodule 配置
├── .python-version                # Python 版本
├── config/
│   └── .env.example               # 环境变量模板
├── data/
│   └── knowledge_base/            # RAG 知识库（50+ 骨科医学指南）
├── docs/                          # 公共文档
├── answer/                        # 问答评估项目
│   ├── main.py                    # 入口
│   ├── core/                      # 核心处理器
│   ├── rag/                       # RAG 工具
│   ├── utils/                     # 工具函数
│   └── NaiveRag/                  # NaiveRAG (git submodule)
├── charts/                        # 图表生成项目
│   ├── scripts/                   # 生成脚本
│   ├── modules/                   # 数据处理
│   └── viz/                       # 可视化
└── web/                           # Web 评分项目
    ├── app.py                     # Flask 应用
    ├── backend/                   # 后端代码
    └── frontend/                  # React 前端
```

## 依赖安装

每个子项目都有独立的依赖配置：

```bash
# 问答评估
cd answer && uv sync

# 图表生成
cd charts && uv sync

# Web 评分
cd web && uv sync
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
