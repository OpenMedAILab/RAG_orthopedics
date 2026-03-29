# RAGAnswer_Graph 项目统计分析报告

## 项目概述

本项目对三个大语言模型（GPT, Gemini, Grok）在医学问答任务上的表现进行评估，对比 **RAG（检索增强生成）** 与 **No-RAG（原始模型）** 两种模式的回答质量，并分析评估者间的一致性。

---

## 生成文件清单

### 表格文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/table1_statistical_results.tif` | TIF (300 DPI) | Table 1 学术论文风格表格 |
| `outputs/table1_statistical_results.md` | Markdown | Table 1 Markdown 格式 |
| `Table1_生成说明.md` | Markdown | Table 1 详细生成说明 |

### 雷达图文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/radar_rater1.tif` | TIF (300 DPI) | 医生 1 雷达图（No-RAG vs RAG） |
| `outputs/radar_rater2.tif` | TIF (300 DPI) | 医生 2 雷达图（No-RAG vs RAG） |
| `outputs/radar_rater3.tif` | TIF (300 DPI) | 医生 3 雷达图（No-RAG vs RAG） |
| `outputs/radar_aggregated.tif` | TIF (300 DPI) | 汇总 3 医生平均雷达图 |

### 中间数据文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `outputs/llm_avg_ranks.csv` | CSV | LLM 评估者平均排名 |
| `outputs/expert_avg_ranks.csv` | CSV | 专家评估者平均排名 |
| `outputs/combined_avg_ranks.csv` | CSV | 合并评估者平均排名 |

---

## Table 1 统计评估结果

### 表格内容

| Evaluation Comparison | Friedman Statistics | P-value | Kendall's W |
|:----------------------|:-------------------:|:-------:|:-----------:|
| **Inter-rater Reliability** | | | |
| LLM-as-a-judge (n=3) | 5.370 | 0.068 | 0.358 |
| Expert Evaluators (n=3) | 8.729 | 0.013 | 0.582 |
| **Cross-method Correlation** | | | |
| Expert vs. LLM-as-a-judge (n=6) | 9.552 | 0.089 | 0.318 |

### 计算方法

**两步法**：

1. **第一步**：对每个病例内 6 个方法（3 模型×2 模式）进行排名，计算每个评估者对每个方法的平均排名（跨 40 个病例）

2. **第二步**：基于平均排名矩阵计算 Friedman 统计量和 Kendall's W

**Kendall's W 公式**：
$$W = \frac{12 \times S}{k^2 \times n \times (n^2 - 1)}$$

**Friedman Q 公式**：
$$Q = W \times k \times (n - 1)$$

其中：
- $k$ = 评估者数
- $n$ = 方法数（6）
- $S$ = 秩和的离差平方和

### 结果解读

| 评估组合 | Kendall's W | 一致性程度 | P-value | 统计显著性 |
|---------|-------------|-----------|---------|-----------|
| LLM-as-a-judge (n=3) | 0.358 | 低度一致 | 0.068 | 接近显著 |
| Expert Evaluators (n=3) | 0.582 | 中度一致 | 0.013 | 显著 |
| Cross-method (n=6) | 0.318 | 低度一致 | 0.089 | 不显著 |

**解读**：
- **LLM 评估者**：3 个 LLM（GPT, Gemini, Grok）对 6 个方法的排名一致性较低（W=0.358），差异接近显著性水平（P=0.068）
- **医生评估者**：3 个医生对 6 个方法的排名一致性中等（W=0.582），差异具有统计学显著性（P=0.013）
- **跨方法评估**：6 个评估者（3 个 LLM + 3 个医生）之间的排名一致性较低（W=0.318），差异不显著（P=0.089）

---

## 雷达图结果

### 每个医生的评分对比

| 医生 | No-RAG (Acc/Rec/Log) | RAG (Acc/Rec/Log) |
|------|---------------------|-------------------|
| Rater 1 | 1.86 / 1.87 / 1.81 | 2.49 / 2.34 / 2.35 |
| Rater 2 | 1.89 / 1.84 / 1.70 | 2.48 / 2.32 / 2.32 |
| Rater 3 | 1.91 / 1.88 / 1.68 | 2.50 / 2.34 / 2.29 |

### 汇总平均（3 个医生）

| 模式 | Medical Accuracy | Key Point Recall | Logical Completeness |
|------|-----------------|------------------|---------------------|
| No-RAG | 1.89 | 1.86 | 1.73 |
| RAG | 2.49 | 2.33 | 2.32 |

**观察**：RAG 模式在三个维度上均优于 No-RAG 模式，其中：
- Medical Accuracy 提升：+0.60
- Key Point Recall 提升：+0.47
- Logical Completeness 提升：+0.59

---

## 脚本文件

| 脚本 | 功能 |
|------|------|
| `scripts/generate_table1.py` | 生成 Table 1 统计表格 |
| `scripts/generate_radar_raters.py` | 生成医生雷达图 |

### 运行方式

```bash
cd charts

# 生成 Table 1
python3 scripts/generate_table1.py

# 生成雷达图
python3 scripts/generate_radar_raters.py
```

---

## 数据来源

### 原始数据文件

| 文件 | 工作表 | 评估者 | 评分范围 |
|------|--------|--------|---------|
| `模型评分.xlsx` | 模型评分 | GPT, Gemini, Grok | 1-10 分 |
| `人工评分.xlsx` | 人工评分 -1 | 医生 1 | 1-3 分 |
| `人工评分.xlsx` | 人工评分 -2 | 医生 2 | 1-3 分 |
| `人工评分.xlsx` | 人工评分 -3 | 医生 3 | 1-3 分 |

**排除数据**：`人工评分 -4`（第 4 个医生）因数据质量问题被排除

### 数据结构

- **病例数**：40 个医学病例
- **方法数**：6 个（3 模型 × 2 模式）
- **总样本数**：240（40 病例 × 6 方法）

---

## 统计方法参考

1. **Friedman 检验**：用于检测多个相关样本的排名是否存在显著差异
   - 参考：https://en.wikipedia.org/wiki/Friedman_test
   
2. **Kendall's W**：评估者间一致性系数
   - 参考：https://en.wikipedia.org/wiki/Kendall%27s_rank_correlation

3. **EyeRAG 项目**：统计计算方法参考
   - 参考：https://github.com/OpenMedAILab/EyeRAG/blob/main/eye_rag/handle_results/cal_p.py

---

## 版本信息

| 项目 | 信息 |
|------|------|
| 生成日期 | 2026-03-04 |
| Python 版本 | 3.x |
| 依赖库 | pandas, numpy, scipy, matplotlib, openpyxl |

---

## 注意事项

1. **数据质量**：排除第 4 个医生数据（与其他医生评分呈负相关）

2. **排名计算**：对每个病例内的 6 个方法进行排名，然后跨病例求平均

3. **P 值规范**：
   - P < 0.001 显示为 `<0.001`
   - P ≥ 0.001 显示 3 位小数

4. **Kendall's W 解释**：
   - W > 0.7：高度一致
   - W > 0.5：中度一致
   - W > 0.3：低度一致
   - W < 0.3：一致性很低

5. **图片格式**：所有图片均为 TIF 格式，300 DPI，适合学术出版

---

## 项目文件结构

```
RAGAnswer_Graph/
├── 模型评分.xlsx                    # LLM 评估原始数据
├── 人工评分.xlsx                    # 专家评估原始数据
├── Table1_生成说明.md                # Table 1 详细说明
├── 项目统计分析报告.md               # 本文档
├── scripts/
│   ├── generate_table1.py           # Table 1 生成脚本
│   └── generate_radar_raters.py     # 雷达图生成脚本
└── outputs/
    ├── table1_statistical_results.tif
    ├── table1_statistical_results.md
    ├── radar_rater1.tif
    ├── radar_rater2.tif
    ├── radar_rater3.tif
    ├── radar_aggregated.tif
    ├── llm_avg_ranks.csv
    ├── expert_avg_ranks.csv
    └── combined_avg_ranks.csv
```

---

*报告生成日期：2026-03-04*
