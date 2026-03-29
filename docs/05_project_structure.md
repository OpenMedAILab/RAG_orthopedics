# RAGAnswer_Graph 项目结构说明

## 项目概述

RAGAnswer_Graph 是一个医学 RAG（检索增强生成）系统评估结果的可视化项目，用于评估多个大语言模型在医学问答任务上的表现，并对比 RAG 与 No-RAG 模式下的回答质量。

---

## 目录结构

```
RAGAnswer_Graph/
├── README.md                        # 项目快速入门
├── QWEN.md                          # 项目说明（原有）
│
├── docs/                            # 统计方法文档
│   ├── 00_overview.md               # 统计方法总览
│   ├── 01_table1_statistics.md      # Table 1 统计方法
│   ├── 02_radar_chart_statistics.md # 雷达图统计方法
│   ├── 03_table1_generation_guide.md # Table 1 生成说明
│   ├── 04_project_report.md         # 项目统计分析报告
│   ├── 05_project_structure.md      # 项目结构说明
│   ├── 06_chart_description.md      # 图表说明
│   └── 07_chart_algorithms.md       # 图表统计算法说明
│
├── references/                      # 参考文件
│   ├── 01_table1_reference_example.png  # Table 1 参考图片
│   └── 02_eyerag_manuscript.pdf         # EyeRAG 论文稿件
│
├── outputs/                         # 输出文件
│   ├── table1_statistical_results.* # Table 1 统计表格
│   ├── radar_*.tif                  # 雷达图
│   ├── bar_chart_*.tif              # 柱状图
│   └── *_avg_ranks.csv              # 平均排名数据
│
├── scripts/                         # 脚本文件
│   ├── generate_table1.py           # Table 1 生成脚本
│   ├── generate_radar_raters.py     # 雷达图生成脚本
│   └── generate_*.py                # 其他图表生成脚本
│
├── src/                             # 源代码模块
│   ├── data_processor.py            # 数据处理模块
│   └── visualization/               # 可视化模块包
│
├── 模型评分.xlsx                     # LLM 评估原始数据
└── 人工评分.xlsx                     # 专家评估原始数据
```

---

## 核心文件说明

### 数据文件

| 文件 | 说明 |
|------|------|
| `模型评分.xlsx` | LLM 评估数据（GPT, Gemini, Grok 三个评估者） |
| `人工评分.xlsx` | 专家评估数据（4 个医生，其中第 4 个因质量问题被排除） |

### 脚本文件

| 脚本 | 功能 |
|------|------|
| `scripts/generate_table1.py` | 生成 Table 1 统计表格（Friedman 检验 + Kendall's W） |
| `scripts/generate_radar_raters.py` | 生成医生雷达图（No-RAG vs RAG 对比） |
| `scripts/generate_rag_comparison_chart.py` | RAG vs Vanilla LLM 平均排名对比 |
| `scripts/generate_ranked_first_rate_chart.py` | RAG vs Vanilla LLM 首选率对比 |
| `scripts/generate_llm_ranking_chart.py` | LLM 分组排名对比 |
| `scripts/generate_radar_chart.py` | 三维度雷达图 |
| `scripts/generate_model_first_rate_chart.py` | 模型首选率 |
| `scripts/generate_model_first_rate_comparison_chart.py` | 模型首选率对比 |

### 可视化模块（src/visualization/）

| 模块 | 功能 |
|------|------|
| `bar_chart_ranked_first_rate.py` | 垂直柱状图（首选率统计） |
| `bar_chart_with_errors.py` | 带误差线的柱状图 |
| `bar_chart_with_statistical_test.py` | 带统计检验的柱状图 |
| `grouped_bar_average_rank_comparison.py` | 分组柱状图（平均排名对比） |
| `grouped_bar_llm_ranking.py` | LLM 排名分组柱状图 |
| `grouped_bar_with_errors.py` | 带误差线的分组柱状图 |
| `radar_chart_average_rank.py` | 平均排名雷达图 |

### 输出文件

#### 统计表格
| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/table1_statistical_results.tif` | TIF (300 DPI) | Table 1 学术论文风格表格 |
| `outputs/table1_statistical_results.md` | Markdown | Table 1 Markdown 格式 |

#### 雷达图
| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/radar_rater1.tif` | TIF (300 DPI) | 医生 1 雷达图 |
| `outputs/radar_rater2.tif` | TIF (300 DPI) | 医生 2 雷达图 |
| `outputs/radar_rater3.tif` | TIF (300 DPI) | 医生 3 雷达图 |
| `outputs/radar_aggregated.tif` | TIF (300 DPI) | 汇总 3 医生平均雷达图 |

#### 中间数据
| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/llm_avg_ranks.csv` | CSV | LLM 评估者平均排名 |
| `outputs/expert_avg_ranks.csv` | CSV | 专家评估者平均排名 |
| `outputs/combined_avg_ranks.csv` | CSV | 合并评估者平均排名 |

### 文档文件

| 文档 | 说明 |
|------|------|
| `docs/00_overview.md` | 统计方法总览 |
| `docs/01_table1_statistics.md` | Table 1 统计方法详解 |
| `docs/02_radar_chart_statistics.md` | 雷达图统计方法详解 |
| `项目统计分析报告.md` | 项目完整总结报告 |
| `Table1_生成说明.md` | Table 1 生成说明 |

---

## 使用方式

### 生成 Table 1 统计表格

```bash
cd /home/kali/文档/实习/RAGAnswer_Graph
python3 scripts/generate_table1.py
```

**输出**：
- `outputs/table1_statistical_results.tif`
- `outputs/table1_statistical_results.md`
- `outputs/llm_avg_ranks.csv`
- `outputs/expert_avg_ranks.csv`
- `outputs/combined_avg_ranks.csv`

### 生成雷达图

```bash
cd /home/kali/文档/实习/RAGAnswer_Graph
python3 scripts/generate_radar_raters.py
```

**输出**：
- `outputs/radar_rater1.tif`
- `outputs/radar_rater2.tif`
- `outputs/radar_rater3.tif`
- `outputs/radar_aggregated.tif`

### 生成其他图表

```bash
# RAG vs Vanilla LLM 平均排名对比
python3 scripts/generate_rag_comparison_chart.py

# RAG vs Vanilla LLM 首选率对比
python3 scripts/generate_ranked_first_rate_chart.py

# LLM 分组排名对比
python3 scripts/generate_llm_ranking_chart.py

# 三维度雷达图
python3 scripts/generate_radar_chart.py

# 模型首选率
python3 scripts/generate_model_first_rate_chart.py

# 模型首选率对比
python3 scripts/generate_model_first_rate_comparison_chart.py
```

---

## 依赖库

```bash
pip install pandas numpy scipy matplotlib openpyxl
```

---

## 统计方法

### Friedman 检验
用于检验多个评估者的排名是否存在显著差异。

### Kendall's W 协调系数
用于衡量多个评估者之间排名的一致性程度（0-1）。

### 平均排名法
对每个病例内的 6 个方法进行排名，然后跨病例求平均。

**详细统计方法请参考**：`docs/` 目录下的文档。

---

## 版本信息

| 项目 | 信息 |
|------|------|
| 整理日期 | 2026-03-04 |
| Python 版本 | 3.x |
| 依赖库 | pandas, numpy, scipy, matplotlib, openpyxl |

---

## 根目录文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目快速入门 |
| `QWEN.md` | 原有项目说明 |

---

## 文件清理建议

以下文件已整理到 `docs/` 目录：

| 原文件 | 新位置 |
|--------|--------|
| `Table1_生成说明.md` | `docs/03_table1_generation_guide.md` |
| `项目统计分析报告.md` | `docs/04_project_report.md` |
| `项目结构说明.md` | `docs/05_project_structure.md` |
| `图表说明.md` | `docs/06_chart_description.md` |
| `图表统计算法说明.md` | `docs/07_chart_algorithms.md` |

其他历史遗留文件可根据需要保留或删除：

| 文件 | 建议 |
|------|------|
| `QWEN.md` | 保留（原有项目说明） |
| `outputs/bar_chart_*.tif` | 根据需要保留 |
| `outputs/radar_chart_average_rank.tif` | 根据需要保留 |
| `src/` 目录 | 保留（可视化模块包） |

---

## 参考文件

以下文件存放在 `references/` 目录：

| 文件 | 说明 |
|------|------|
| `Manuscript EyeRAG- track off.pdf` | EyeRAG 论文稿件 |
| `微信图片_20260224161344_419_85.png` | Table 1 参考图片 |

---

*项目结构整理完成日期：2026-03-04*
