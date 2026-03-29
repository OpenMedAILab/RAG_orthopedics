# RAG vs Vanilla LLM 医学问答质量评估图表说明

## 项目概述

本项目对三个大语言模型（GPT-4o Mini、Gemini 3 Flash、Grok 4 Fast）在医学问答任务上的表现进行评估，对比 **RAG（检索增强生成）** 与 **Vanilla LLM（原始模型）** 两种模式的回答质量。

---

## 数据结构

### 评估数据

| 字段 | 说明 |
|------|------|
| 病例号 | 40 个医学病例 |
| 被评估模型 | GPT / Gemini / Grok |
| 模式 | RAG / No-RAG（Vanilla LLM） |
| 评估维度 | 医学准确性、关键要点召回率、逻辑完整性 |
| 评估者 | 3 个（GPT、Gemini、Grok） |
| 评分范围 | 1-10 分 |

### 数据规模

- **总病例数**: 40
- **总回答数**: 240（40 病例 × 3 模型 × 2 模式）
- **总评估分数**: 2160（240 回答 × 9 评分）

---

## 生成的图表

### 1. RAG vs Vanilla LLM 平均排名对比

**文件**: `bar_chart_rag_vs_norag_comparison.png`

**说明**: 展示 RAG 和 Vanilla LLM 在 40 个病例中的平均排名对比。

| 统计指标 | RAG | Vanilla LLM |
|---------|-----|-------------|
| 平均排名 | 1.10 | 1.90 |
| 标准差 | 0.30 | 0.30 |

**算法**:
1. 对每个病例，计算 RAG 和 Vanilla LLM 的总分（3 个模型×3 个维度的平均）
2. 分数高的模式排名为 1，低的为 2
3. 计算 40 个病例的平均排名和标准差

---

### 2. RAG vs Vanilla LLM 首选率对比

**文件**: `bar_chart_ranked_first_rate.png`

**说明**: 展示 RAG 和 Vanilla LLM 获得第 1 名的病例百分比。

| 模式 | 首选率 | 标准差 |
|------|--------|--------|
| RAG | 90.0% | ±4.7% |
| Vanilla LLM | 10.0% | ±4.7% |

**算法**:
1. 对每个病例，比较 RAG 和 Vanilla LLM 的总分
2. 分数高的获得第 1 名
3. 统计 40 个病例中各模式获得第 1 名的百分比
4. 标准差使用二项分布公式：√(p×(100-p)/n)

---

### 3. 模型首选率（RAG）

**文件**: `bar_chart_model_first_rate.png`

**说明**: 展示每个模型 RAG 获得第 1 名的百分比。

| 模型 | RAG 首选率 | 标准差 |
|------|-----------|--------|
| GPT-4o Mini | 77.5% | ±6.6% |
| Gemini 3 Flash | 92.5% | ±4.2% |
| Grok 4 Fast | 82.5% | ±6.0% |

**算法**:
1. 对每个模型，在每个病例中独立比较 RAG 和 Vanilla LLM
2. 统计每个模型 RAG 获得第 1 名的病例数
3. 计算百分比和二项分布标准差

---

### 4. 模型首选率对比（RAG vs Vanilla LLM）

**文件**: `bar_chart_model_first_rate_comparison.png`

**说明**: 展示每个模型 RAG 和 Vanilla LLM 获得第 1 名的百分比对比。

| 模型 | RAG 首选率 | Vanilla LLM 首选率 |
|------|-----------|-------------------|
| GPT-4o Mini | 77.5% ± 6.6% | 22.5% ± 6.6% |
| Gemini 3 Flash | 92.5% ± 4.2% | 7.5% ± 4.2% |
| Grok 4 Fast | 82.5% ± 6.0% | 17.5% ± 6.0% |

**算法**: 同图表 3，同时展示 RAG 和 Vanilla LLM 的数据。

---

### 5. 模型分组排名对比

**文件**: `grouped_bar_llm_ranking.png`

**说明**: 展示每个模型 RAG 和 Vanilla LLM 的平均排名对比。

| 模型 | RAG 平均排名 | Vanilla LLM 平均排名 |
|------|-------------|---------------------|
| GPT-4o Mini | 1.23 ± 0.42 | 1.77 ± 0.42 |
| Gemini 3 Flash | 1.07 ± 0.26 | 1.93 ± 0.26 |
| Grok 4 Fast | 1.18 ± 0.38 | 1.82 ± 0.38 |

**算法**:
1. 对每个模型，在每个病例中比较 RAG 和 Vanilla LLM 的 9 个评分平均值
2. 分数高的排名为 1，低的为 2
3. 计算 40 个病例的平均排名和标准差

---

### 6. 三维度雷达图

**文件**: `radar_chart_average_rank.png`

**说明**: 展示 RAG 和 Vanilla LLM 在三个评估维度上的平均分数对比。

| 模式 | 医学准确性 | 关键要点召回率 | 逻辑完整性 |
|------|-----------|--------------|-----------|
| RAG | 8.48 | 8.34 | 8.68 |
| Vanilla LLM | 7.92 | 7.26 | 8.22 |

**算法**:
1. 对每个模式，计算该维度下所有回答的平均分（3 个评估者×40 病例×3 模型）
2. Y 轴范围自动调整为数据范围±20%

---

## 统计算法说明

### 排名计算

对每个病例（或每个模型×病例），比较 RAG 和 Vanilla LLM 的分数：
- 分数高的排名为 **1**
- 分数低的排名为 **2**

### 首选率计算

$$ \text{First Place Rate} = \frac{\text{获得第 1 名的病例数}}{\text{总病例数}} \times 100\% $$

### 标准差计算（二项分布）

$$ \text{Std} = \sqrt{\frac{p \times (100 - p)}{n}} $$

其中：
- $p$ = 首选率（0-1）
- $n$ = 样本量（40 个病例）

---

## 关键发现

1. **RAG 整体优势明显**: 在 90% 的病例中 RAG 表现优于 Vanilla LLM

2. **模型间差异**: 
   - Gemini 3 Flash 的 RAG 优势最大（92.5% 首选率）
   - GPT-4o Mini 的 RAG 优势相对较小（77.5% 首选率）

3. **维度分析**:
   - RAG 在**关键要点召回率**上优势最明显（+1.08 分）
   - RAG 在**逻辑完整性**上优势最小（+0.46 分）

---

## 文件结构

```
RAGAnswer_Graph/
├── 模型评分.xlsx              # 原始评估数据
├── scripts/                   # 图表生成脚本
│   ├── generate_rag_comparison_chart.py
│   ├── generate_ranked_first_rate_chart.py
│   ├── generate_llm_ranking_chart.py
│   ├── generate_radar_chart.py
│   ├── generate_model_first_rate_chart.py
│   └── generate_model_first_rate_comparison_chart.py
├── src/
│   ├── data_processor.py      # 数据处理模块
│   └── visualization/         # 可视化模块
├── outputs/                   # 生成的图表
│   ├── bar_chart_rag_vs_norag_comparison.png
│   ├── bar_chart_ranked_first_rate.png
│   ├── bar_chart_model_first_rate.png
│   ├── bar_chart_model_first_rate_comparison.png
│   ├── grouped_bar_llm_ranking.png
│   └── radar_chart_average_rank.png
└── 图表说明.md                # 本文档
```

---

## 复现步骤

```bash
cd /path/to/RAGAnswer_Graph

# 生成所有图表
python scripts/generate_rag_comparison_chart.py
python scripts/generate_ranked_first_rate_chart.py
python scripts/generate_llm_ranking_chart.py
python scripts/generate_radar_chart.py
python scripts/generate_model_first_rate_chart.py
python scripts/generate_model_first_rate_comparison_chart.py
```

---

## 版本信息

- **生成日期**: 2026 年 2 月 26 日
- **Python 版本**: 3.x
- **依赖库**: pandas, numpy, matplotlib
