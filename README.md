# RAG Orthopedics 骨科 RAG 问答评估系统

RAG（检索增强生成）与 No-RAG 模式下大语言模型在骨科医学问答任务中的表现对比评估系统。

## 项目简介

本项目用于对比评估 RAG（检索增强生成）与 No-RAG（无检索增强）两种模式下，大语言模型在骨科医学问答任务中的表现差异。系统包含三个核心模块：

1. **问答评估模块** (`src/answer/`) - RAG 问答生成与自动评估
2. **图表生成模块** (`src/charts/`) - 评估结果统计可视化
3. **Web 评分系统** (`src/web/`) - 人工评分 Web 界面

## 核心功能

- **双模式对比**：同一问题分别在 RAG 模式和 No-RAG 模式下生成回答
- **多模型支持**：支持 GPT、Gemini、Grok 等多个大语言模型
- **自动评估**：三维度自动评分（医学准确性、关键要点召回率、逻辑完整性）
- **知识检索**：基于 FAISS 向量数据库检索骨科医学指南
- **专业领域识别**：自动识别病例所属医学专科，限定检索范围
- **人工评分**：Web 界面支持多医生独立评分
- **统计可视化**：生成学术论文风格图表（Table 1、雷达图、柱状图）

## 项目结构

```
RAG_orthopedics/
├── README.md                      # 项目说明
├── pyproject.toml                 # Python 依赖配置
├── .gitignore                     # Git 忽略规则
├── config/
│   └── .env.example               # 环境变量模板
├── data/
│   └── knowledge_base/            # RAG 知识库（50+ 骨科医学指南）
├── docs/                          # 项目文档
│   ├── evaluation_standards.md    # 评估标准
│   ├── answer_system.md           # 问答系统说明
│   ├── charts_system.md           # 图表系统说明
│   ├── prompt_design.md           # Prompt 设计
│   ├── web_system.md              # Web 系统说明
│   └── web_data_format.md         # Web 数据格式
├── src/
    ├── answer/                    # 问答评估模块
    │   ├── core/                  # 核心处理器
    │   ├── rag/                   # RAG 引擎
    │   └── utils/                 # 工具函数
├── NaiveRag/                      # Naive RAG (git submodule)
├── src/
│   ├── answer/                    # 问答评估模块
│   │   ├── core/                  # 核心处理器
│   │   ├── rag/                   # RAG 引擎
│   │   └── utils/                 # 工具函数
│   ├── charts/                    # 图表生成模块
│   │   ├── scripts/               # 生成脚本
│   │   ├── modules/               # 数据处理模块
│   │   └── viz/                   # 可视化模块
│   └── web/                       # Web 评分系统
│       ├── backend/               # Flask 后端
│       └── frontend/              # React 前端
```

## 快速开始

### 环境要求

- Python 3.14+
- uv 包管理器（推荐）或 pip

### 安装依赖

**注意**: 本项目使用 git submodule 管理 NaiveRAG 依赖。克隆仓库时请使用：

```bash
# 克隆仓库（包含 submodule）
git clone --recursive https://github.com/YourOrg/RAG_orthopedics.git

# 或如果已经克隆，初始化 submodule
git submodule update --init --recursive
```

然后安装依赖：

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 配置环境变量

```bash
# 复制环境变量模板
cp config/.env.example .env

# 编辑 .env 文件，填入 API Key
# - OPEN_ROUTER_KEY (OpenRouter API Key)
# - SILICONFLOW_API_KEY (硅基流动 API Key)
# - SECRET_KEY (Flask JWT 密钥)
```

### 运行问答评估

```bash
# 运行主程序
python src/answer/main.py
```

### 运行图表生成

```bash
# 生成 Table 1 统计表格
python src/charts/scripts/generate_table1.py

# 生成雷达图
python src/charts/scripts/generate_radar_raters.py
```

### 运行 Web 评分系统

```bash
# 启动 Web 服务
python src/web/backend/app.py

# 访问 http://localhost:5000
```

## 评估维度

系统采用三维度评估体系，每个维度评分范围为 1-10 分（自动评估）或 1-3 分（人工评分）：

| 维度 | 权重 | 说明 |
|------|------|------|
| 医学准确性 | 40% | 医学信息的准确性和可靠性 |
| 关键要点召回率 | 30% | 对问题关键要点的覆盖程度 |
| 逻辑完整性 | 30% | 推理过程的逻辑性和完整性 |

## 知识库

RAG 知识库包含 50+ 份骨科医学指南和专家共识，涵盖：

- 脊柱外科（颈椎病、腰椎间盘突出、脊柱创伤等）
- 关节外科（骨关节炎、股骨头坏死、髋臼骨折等）
- 创伤骨科（骨盆骨折、骨质疏松性骨折等）
- 运动医学（前交叉韧带损伤、髌骨脱位等）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.14+, Flask, OpenAI SDK |
| 前端 | React 18, Material-UI, JavaScript |
| 数据 | Pandas, OpenPyXL, FAISS |
| 可视化 | Matplotlib, NumPy, SciPy |
| 认证 | JWT (PyJWT), PBKDF2-SHA256 |
| RAG | FAISS, BAAI/bge-m3 嵌入模型 |

## 文档

详细文档请参阅 `docs/` 目录：

- [评估标准](docs/evaluation_standards.md)
- [问答系统说明](docs/answer_system.md)
- [图表系统说明](docs/charts_system.md)
- [Prompt 设计](docs/prompt_design.md)
- [Web 系统说明](docs/web_system.md)
- [Web 数据格式](docs/web_data_format.md)

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
