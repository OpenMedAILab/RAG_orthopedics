# Table 1 统计表格生成说明

## 概述

本文档详细描述了 `Table 1. Statistical Evaluation Results` 的生成方法，包括数据来源、统计计算方法、代码实现等内容。

---

## 输出文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/table1_statistical_results.tif` | TIF (300 DPI) | 学术论文风格表格图片 |
| `outputs/table1_statistical_results.md` | Markdown | Markdown 格式表格及说明 |
| `outputs/llm_avg_ranks.csv` | CSV | LLM 评估者平均排名数据 |
| `outputs/expert_avg_ranks.csv` | CSV | 专家评估者平均排名数据 |
| `outputs/combined_avg_ranks.csv` | CSV | 合并评估者平均排名数据 |

---

## 数据来源

### 数据文件

| 文件 | 工作表 | 评估者 | 样本数 |
|------|--------|--------|--------|
| `模型评分.xlsx` | 模型评分 | GPT, Gemini, Grok (LLM-as-a-judge) | 240 (40 病例 × 6 方法) |
| `人工评分.xlsx` | 人工评分 -1 | 医生 1 | 240 (40 病例 × 6 方法) |
| `人工评分.xlsx` | 人工评分 -2 | 医生 2 | 240 (40 病例 × 6 方法) |
| `人工评分.xlsx` | 人工评分 -3 | 医生 3 | 240 (40 病例 × 6 方法) |

**注意**: 排除 `人工评分 -4`（第 4 个医生），因其数据存在质量问题。

### 数据结构

**6 个方法**（被评估对象）:
- GPT_No-RAG, GPT_RAG
- Gemini_No-RAG, Gemini_RAG
- Grok_No-RAG, Grok_RAG

**LLM 评估数据**（模型评分.xlsx）:
- 40 个医学病例
- 3 个评估者：GPT, Gemini, Grok
- 评估维度：医学准确性、关键要点召回率、逻辑完整性（1-10 分）

**专家评估数据**（人工评分.xlsx）:
- 40 个医学病例
- 3 个评估者：医生 1, 医生 2, 医生 3
- 评估维度：医学准确性、关键要点召回率、逻辑完整性（1-3 分）

---

## 计算逻辑（两步法）

### 第一步：计算每个评估者对 6 个方法的平均排名

1. **对每个病例内**，每个评估者对 6 个方法进行排名（基于综合分数）
2. **跨 40 个病例**，计算每个评估者对每个方法的平均排名

**示例**（LLM 评估者）:

| 评估者 | GPT_No-RAG | GPT_RAG | Gemini_No-RAG | Gemini_RAG | Grok_No-RAG | Grok_RAG |
|--------|-----------|---------|---------------|------------|-------------|----------|
| GPT | 2.76 | 2.49 | 4.10 | 4.46 | 3.73 | 3.46 |
| Gemini | 1.49 | 2.03 | 4.66 | 5.06 | 3.46 | 4.30 |
| Grok | 1.48 | 3.51 | 2.60 | 5.41 | 2.69 | 5.31 |

### 第二步：基于平均排名矩阵计算 Friedman 统计量和 Kendall's W

**Kendall's W 公式**:

$$W = \frac{12 \times S}{k^2 \times n \times (n^2 - 1)}$$

其中:
- $k$ = 评估者数
- $n$ = 方法数（6）
- $S$ = 秩和的离差平方和 = $\sum_{j=1}^{n} (R_j - \bar{R})^2$
- $R_j$ = 第 $j$ 个方法的秩和（所有评估者对该方法排名的总和）

**Friedman Q 公式**:

$$Q = W \times k \times (n - 1)$$

**P 值**: 基于卡方分布 $\chi^2(k-1)$

---

## 统计方法解释

### Friedman 检验

Friedman 检验是一种非参数统计检验，用于检测多个相关样本（评估者）的排名是否存在显著差异。

- **P < 0.05**: 评估者间排名存在显著差异
- **P ≥ 0.05**: 评估者间排名无显著差异

### Kendall's W (协调系数)

Kendall's W 用于衡量多个评估者之间排名的一致性程度。

| W 值范围 | 一致性程度 |
|---------|-----------|
| 0.9 - 1.0 | 高度一致 |
| 0.7 - 0.9 | 中度一致 |
| 0.5 - 0.7 | 低至中度一致 |
| 0.3 - 0.5 | 低度一致 |
| < 0.3 | 一致性很低 |

---

## 计算结果

### Inter-rater Reliability（评估者间信度）

| 评估组合 | Friedman Q | P-value | Kendall's W | 解读 |
|---------|-----------|---------|-------------|------|
| LLM-as-a-judge (n=3) | 5.370 | 0.068 | 0.358 | 3 个 LLM 评估者间一致性较低（W=0.358），差异接近显著（P=0.068） |
| Expert Evaluators (n=3) | 8.729 | 0.013 | 0.582 | 3 个医生评估者间一致性中等（W=0.582），差异显著（P=0.013） |

### Cross-method Correlation（跨方法相关性）

| 评估组合 | Friedman Q | P-value | Kendall's W | 解读 |
|---------|-----------|---------|-------------|------|
| Expert vs. LLM-as-a-judge (n=6) | 9.552 | 0.089 | 0.318 | 6 个评估者间一致性较低（W=0.318），差异不显著（P=0.089） |

---

## 代码实现

### 脚本位置

`scripts/generate_table1.py`

### 依赖库

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
```

### 运行方式

```bash
cd charts
python3 scripts/generate_table1.py
```

### 输出

```
Table 1 图片已保存至：outputs/table1_statistical_results.tif
Markdown 表格已保存至：outputs/table1_statistical_results.md
平均排名数据已保存至:
  - outputs/llm_avg_ranks.csv
  - outputs/expert_avg_ranks.csv
  - outputs/combined_avg_ranks.csv
```

---

## 表格样式

表格采用学术论文三线表风格：
- 顶线和底线：粗线（1.2pt）
- 列头下横线：细线（0.8pt）
- 分类间横线：细线（0.8pt）
- 字体：Serif
- 分辨率：300 DPI

---

## 结果解读

### LLM-as-a-judge (W=0.358, P=0.068)

3 个 LLM 评估者（GPT, Gemini, Grok）对 6 个方法的排名一致性较低（W=0.358）。P=0.068 接近显著性水平（0.05），表明评估者间可能存在一定的排名差异。

### Expert Evaluators (W=0.582, P=0.013)

3 个医生评估者对 6 个方法的排名一致性中等（W=0.582）。P=0.013 < 0.05，表明评估者间的排名差异具有统计学显著性。

### Cross-method (W=0.318, P=0.089)

6 个评估者（3 个 LLM + 3 个医生）之间的排名一致性较低（W=0.318）。P=0.089 > 0.05，差异不具有统计学显著性，表明 LLM 评估和专家评估的排名模式存在差异但不够显著。

---

## 参考

1. EyeRAG 项目统计计算方法：https://github.com/OpenMedAILab/EyeRAG/blob/main/eye_rag/handle_results/cal_p.py
2. Friedman 检验：https://en.wikipedia.org/wiki/Friedman_test
3. Kendall's W：https://en.wikipedia.org/wiki/Kendall%27s_rank_correlation

---

## 版本信息

- **生成日期**: 2026-03-04
- **Python 版本**: 3.x
- **依赖库**: pandas, numpy, scipy, matplotlib

---

## 注意事项

1. **排除第 4 个医生**: 由于数据质量问题（与其他医生评分呈负相关），仅使用前 3 个医生的数据
2. **排名计算方式**: 对每个病例内的 6 个方法进行排名，然后跨病例求平均
3. **P 值规范**: P < 0.001 时显示为 `<0.001`，P ≥ 0.001 时显示 3 位小数
4. **Kendall's W 解释**: 
   - W > 0.7: 高度一致
   - W > 0.5: 中度一致
   - W < 0.5: 一致性较低
