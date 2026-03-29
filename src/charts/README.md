# RAGAnswer_Graph

医学 RAG（检索增强生成）系统评估结果可视化项目

## 项目结构

```
RAGAnswer_Graph/
├── docs/              # 统计方法文档
├── references/        # 参考文件
├── outputs/           # 输出文件
├── scripts/           # 脚本文件
├── modules/           # 核心模块（数据处理）
├── viz/               # 可视化模块
├── 模型评分.xlsx       # 原始数据
└── 人工评分.xlsx       # 原始数据
```

## 根目录文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目快速入门 |
| `QWEN.md` | 原有项目说明 |

## 快速开始

### 生成 Table 1 统计表格

```bash
python3 scripts/generate_table1.py
```

### 生成雷达图

```bash
python3 scripts/generate_radar_raters.py
```

## 输出文件

- **Table 1**: `outputs/table1_statistical_results.tif` (300 DPI)
- **雷达图**: `outputs/radar_rater*.tif`, `outputs/radar_aggregated.tif`
- **中间数据**: `outputs/*_avg_ranks.csv`

## 文档

- **统计方法**: `docs/00_overview.md`
- **Table 1 生成**: `docs/03_table1_generation_guide.md`
- **项目报告**: `docs/04_project_report.md`
- **项目结构**: `docs/05_project_structure.md`
- **图表说明**: `docs/06_chart_description.md`

## 文件清理建议

以下文件为历史遗留文件，可根据需要保留或删除：

| 文件 | 建议 |
|------|------|
| `图表说明.md` | 保留（原有文档） |
| `图表统计算法说明.md` | 保留（原有文档） |
| `QWEN.md` | 保留（项目说明） |
| `outputs/bar_chart_*.tif` | 根据需要保留 |
| `outputs/radar_chart_*.tif` | 根据需要保留 |
| `modules/` 目录 | 保留（数据处理模块） |
| `viz/` 目录 | 保留（可视化模块包） |

## 依赖

```bash
pip install pandas numpy scipy matplotlib openpyxl
```

## 参考文件

以下文件存放在 `references/` 目录：

| 文件 | 说明 |
|------|------|
| `01_table1_reference_example.png` | Table 1 参考图片 |
| `02_eyerag_manuscript.pdf` | EyeRAG 论文稿件 |

## 核心结果

### Table 1

| 评估组合 | Kendall's W | P-value |
|---------|-------------|---------|
| LLM-as-a-judge (n=3) | 0.358 | 0.068 |
| Expert Evaluators (n=3) | 0.582 | 0.013 |
| Cross-method (n=6) | 0.318 | 0.089 |

### RAG vs No-RAG（3 医生平均）

| 模式 | Medical Accuracy | Key Point Recall | Logical Completeness |
|------|-----------------|------------------|---------------------|
| No-RAG | 1.89 | 1.86 | 1.73 |
| RAG | 2.49 | 2.33 | 2.32 |

---

*生成日期：2026-03-04*
