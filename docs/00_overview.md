# RAGAnswer_Graph 统计方法总览

## 文档目的

本文档汇总了 RAGAnswer_Graph 项目中使用的所有统计方法，为 Table 1 统计表格和雷达图的生成提供方法学参考。

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [01_table1_statistics.md](01_table1_statistics.md) | Table 1 统计方法：Friedman 检验和 Kendall's W |
| [02_radar_chart_statistics.md](02_radar_chart_statistics.md) | 雷达图统计方法：评分计算和可视化 |
| [03_table1_generation_guide.md](03_table1_generation_guide.md) | Table 1 生成说明 |
| [04_project_report.md](04_project_report.md) | 项目统计分析报告 |
| [05_project_structure.md](05_project_structure.md) | 项目结构说明 |
| [06_chart_description.md](06_chart_description.md) | 图表说明 |
| [07_chart_algorithms.md](07_chart_algorithms.md) | 图表统计算法说明 |

---

## 项目概述

### 研究问题

评估 **RAG（检索增强生成）** 与 **No-RAG（原始模型）** 两种模式在医学问答任务上的表现差异，并分析不同评估者（LLM 和医生）之间评估结果的一致性。

### 评估设计

| 要素 | 描述 |
|------|------|
| 评估对象 | 6 个方法（3 模型 × 2 模式） |
| 评估者 | 3 个 LLM（GPT, Gemini, Grok）+ 3 个医生 |
| 样本 | 40 个医学病例 |
| 评估维度 | 医学准确性、关键要点召回率、逻辑完整性 |

---

## 统计方法汇总

### 1. Friedman 检验

**用途**：检验多个评估者的排名是否存在显著差异

**原假设**：所有评估者的排名分布相同

**统计量**：
$$Q = \frac{12}{k^2 \times n \times (n + 1)} \times \sum_{j=1}^{k} R_j^2 - 3 \times k \times (n + 1)$$

**P 值**：基于卡方分布 $\chi^2_{k-1}$

**详细文档**：[01_table1_statistics.md](01_table1_statistics.md)

---

### 2. Kendall's W 协调系数

**用途**：衡量多个评估者之间排名的一致性程度

**公式**：
$$W = \frac{12 \times S}{k^2 \times n \times (n^2 - 1)}$$

**取值范围**：0（完全不一致）到 1（完全一致）

**解释标准**：

| W 值 | 一致性程度 |
|------|-----------|
| > 0.9 | 高度一致 |
| 0.7-0.9 | 中度一致 |
| 0.5-0.7 | 低至中度一致 |
| 0.3-0.5 | 低度一致 |
| < 0.3 | 一致性很低 |

**详细文档**：[01_table1_statistics.md](01_table1_statistics.md)

---

### 3. 平均排名计算

**用途**：将原始评分转换为排名，消除评估者间的评分标准差异

**步骤**：
1. 对每个病例内的 6 个方法按综合分数排名
2. 跨 40 个病例计算每个方法的平均排名

**排名方法**：平均排名法（处理并列情况）

**详细文档**：[01_table1_statistics.md](01_table1_statistics.md)

---

### 4. 综合分数计算

**用途**：整合三个评估维度的信息

**公式**：
$$\text{Score}_{\text{综合}} = \frac{\text{医学准确性} + \text{关键要点召回率} + \text{逻辑完整性}}{3}$$

**详细文档**：[02_radar_chart_statistics.md](02_radar_chart_statistics.md)

---

### 5. 雷达图可视化

**用途**：直观展示各维度评分的对比

**坐标系**：极坐标系

**元素**：
- 角度：维度均匀分布
- 半径：评分大小
- 多边形面积：综合表现

**详细文档**：[02_radar_chart_statistics.md](02_radar_chart_statistics.md)

---

## 数据流

```
原始数据 (Excel)
    │
    ▼
综合分数计算
    │
    ├──→ 按病例排名 ──→ 平均排名 ──→ Friedman + Kendall's W ──→ Table 1
    │
    └──→ 按方法平均 ──→ 三维度平均 ──→ 雷达图可视化
```

---

## 输出文件

### 统计表格

| 文件 | 格式 | 内容 |
|------|------|------|
| `outputs/table1_statistical_results.tif` | TIF (300 DPI) | Table 1 学术论文风格表格 |
| `outputs/table1_statistical_results.md` | Markdown | Table 1 Markdown 格式 |

### 雷达图

| 文件 | 格式 | 内容 |
|------|------|------|
| `outputs/radar_rater1.tif` | TIF (300 DPI) | 医生 1 雷达图 |
| `outputs/radar_rater2.tif` | TIF (300 DPI) | 医生 2 雷达图 |
| `outputs/radar_rater3.tif` | TIF (300 DPI) | 医生 3 雷达图 |
| `outputs/radar_aggregated.tif` | TIF (300 DPI) | 汇总 3 医生平均雷达图 |

### 中间数据

| 文件 | 格式 | 内容 |
|------|------|------|
| `outputs/llm_avg_ranks.csv` | CSV | LLM 评估者平均排名 |
| `outputs/expert_avg_ranks.csv` | CSV | 专家评估者平均排名 |
| `outputs/combined_avg_ranks.csv` | CSV | 合并评估者平均排名 |

---

## 关键结果

### Table 1 统计结果

| 评估组合 | Friedman Q | P-value | Kendall's W |
|---------|-----------|---------|-------------|
| LLM-as-a-judge (n=3) | 5.370 | 0.068 | 0.358 |
| Expert Evaluators (n=3) | 8.729 | 0.013 | 0.582 |
| Cross-method (n=6) | 9.552 | 0.089 | 0.318 |

### 雷达图结果（3 医生平均）

| 模式 | Medical Accuracy | Key Point Recall | Logical Completeness |
|------|-----------------|------------------|---------------------|
| No-RAG | 1.89 | 1.86 | 1.73 |
| RAG | 2.49 | 2.33 | 2.32 |

---

## Python 依赖

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import openpyxl
```

---

## 脚本文件

| 脚本 | 功能 |
|------|------|
| `scripts/generate_table1.py` | 生成 Table 1 统计表格 |
| `scripts/generate_radar_raters.py` | 生成医生雷达图 |

---

## 参考文献

1. Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the analysis of variance. *Journal of the American Statistical Association*, 32(200), 675-701.

2. Kendall, M. G., & Smith, B. B. (1939). The problem of m rankings. *The Annals of Mathematical Statistics*, 10(3), 275-287.

3. Siegel, S., & Castellan, N. J. (1988). *Nonparametric statistics for the behavioral sciences* (2nd ed.). McGraw-Hill.

4. EyeRAG Project. https://github.com/OpenMedAILab/EyeRAG

---

## 参考文件

| 文件 | 说明 |
|------|------|
| `references/01_table1_reference_example.png` | Table 1 参考图片 |
| `references/02_eyerag_manuscript.pdf` | EyeRAG 论文稿件 |

---

## 版本信息

| 项目 | 信息 |
|------|------|
| 文档生成日期 | 2026-03-04 |
| Python 版本 | 3.x |
| 依赖库 | pandas, numpy, scipy, matplotlib, openpyxl |

---

*本文档是 RAGAnswer_Graph 项目统计方法的总览，详细方法请参考各分文档。*
