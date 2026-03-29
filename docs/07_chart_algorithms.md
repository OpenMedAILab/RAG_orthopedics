# RAG vs Vanilla LLM 评估图表统计算法说明

## 概述

本文档描述了 RAG（检索增强生成）与 Vanilla LLM（原始大语言模型）医学问答质量对比评估中使用的统计算法。所有图表基于同一评估数据集生成。

---

## 数据结构

### 原始数据

评估数据存储在 `模型评分.xlsx` 中，包含以下关键字段：

| 字段 | 说明 |
|------|------|
| 病例号 | 病例唯一标识 |
| 被评估模型 | GPT / Gemini / Grok |
| 模式 | RAG / No-RAG |
| GPT-医学准确性 [1-10 分] | GPT 评估者的医学准确性评分 |
| GPT-关键要点召回率 [1-10 分] | GPT 评估者的关键要点召回率评分 |
| GPT-逻辑完整性 [1-10 分] | GPT 评估者的逻辑完整性评分 |
| Gemini-* | Gemini 评估者的三个维度评分 |
| Grok-* | Grok 评估者的三个维度评分 |

### 数据规模

- **总病例数**: 40 个
- **总回答数**: 240 条（每个病例 6 条：3 模型 × 2 模式）
- **评估维度**: 3 个（医学准确性、关键要点召回率、逻辑完整性）
- **评估者**: 3 个（GPT、Gemini、Grok）

---

## 核心统计算法

### 1. 单行分数计算

对于每一行数据（即每个模型在每个病例的每个模式的回答），计算 **9 个评分的平均值**：

```python
def calculate_row_score(row, model):
    """
    计算单行数据的综合分数
    
    参数:
        row: 数据行
        model: 被评估模型名称
    
    返回:
        9 个评分的平均值（3 个评估者 × 3 个维度）
    """
    scores = []
    evaluators = ['GPT', 'Gemini', 'Grok']
    dimensions = ['医学准确性', '关键要点召回率', '逻辑完整性']
    
    for evaluator in evaluators:
        for dimension in dimensions:
            # 查找对应列并获取分数
            col_name = f'{evaluator}-{dimension}[1-10 分]'
            scores.append(row[col_name])
    
    return np.mean(scores)
```

**示例**: 某回答的 9 个评分为 [8, 9, 7, 7, 8, 8, 9, 9, 9]，则综合分数 = 8.11

---

### 2. 图表一：RAG vs Vanilla LLM 平均排名对比

**文件**: `bar_chart_rag_vs_norag_comparison.png`

#### 算法步骤

1. **按病例号分组**：将 240 行数据按 `病例号` 分为 40 组

2. **计算每个病例内各模式的总分**：
   ```python
   for each case:
       rag_total = mean(RAG 模式下所有回答的综合分数)
       vanilla_total = mean(Vanilla LLM 模式下所有回答的综合分数)
   ```

3. **分配排名**（每个病例内）：
   - 如果 `rag_total >= vanilla_total`：
     - RAG 排名 = 1
     - Vanilla LLM 排名 = 2
   - 否则：
     - RAG 排名 = 2
     - Vanilla LLM 排名 = 1

4. **收集所有病例的排名**：
   - RAG 排名列表：[1, 1, 2, 1, 1, ...]（共 120 个）
   - Vanilla LLM 排名列表：[2, 2, 1, 2, 2, ...]（共 120 个）

5. **计算统计量**：
   ```python
   RAG 平均排名 = np.mean(RAG 排名列表)
   RAG 标准差 = np.std(RAG 排名列表)
   Vanilla LLM 平均排名 = np.mean(Vanilla LLM 排名列表)
   Vanilla LLM 标准差 = np.std(Vanilla LLM 排名列表)
   ```

#### 输出示例

| 模式 | 平均排名 | 标准差 |
|------|---------|--------|
| RAG | 1.10 | 0.30 |
| Vanilla LLM | 1.90 | 0.30 |

**解读**: 平均排名越接近 1 表示表现越好。RAG 平均排名 1.10，说明在大多数病例中 RAG 获得第 1 名。

---

### 3. 图表二：RAG vs Vanilla LLM 首选率对比

**文件**: `bar_chart_ranked_first_rate.png`

#### 算法步骤

1. **按病例号分组**：将数据按 `病例号` 分为 40 组

2. **计算每个病例内各模式的总分**（同图表一）

3. **分配第 1 名**（每个病例）：
   - 如果 `rag_total >= vanilla_total`：
     - RAG 获得第 1 名（计数 +1）
   - 否则：
     - Vanilla LLM 获得第 1 名（计数 +1）

4. **统计首选率**：
   ```python
   RAG 首选率 = (RAG 获得第 1 名的病例数 / 总病例数) × 100%
   Vanilla LLM 首选率 = (Vanilla LLM 获得第 1 名的病例数 / 总病例数) × 100%
   ```

5. **计算标准差**（二项分布）：
   ```python
   std = sqrt(rate × (100 - rate) / n)
   ```
   其中 `n` 为病例总数（40）

#### 输出示例

| 模式 | 首选率 | 标准差 |
|------|--------|--------|
| RAG | 90.0% | 4.7% |
| Vanilla LLM | 10.0% | 4.7% |

**解读**: RAG 在 90% 的病例中表现优于 Vanilla LLM。

---

### 4. 图表三：LLM 分组排名对比

**文件**: `grouped_bar_llm_ranking.png`

#### 算法步骤

1. **按病例号和模型分组**：将数据按 `(病例号，被评估模型)` 分为 120 组（40 病例 × 3 模型）

2. **对每个模型在每个病例中**：
   ```python
   for each case, for each model:
       # 计算 9 个评分的平均分
       rag_score = mean(RAG 模式下所有评分)
       vanilla_score = mean(Vanilla LLM 模式下所有评分)
       
       # 分配排名
       if rag_score >= vanilla_score:
           rag_rank = 1
           vanilla_rank = 2
       else:
           rag_rank = 2
           vanilla_rank = 1
   ```

3. **收集每个模型的排名列表**：
   - GPT-4o Mini RAG 排名：[1, 2, 1, 1, ...]（40 个）
   - GPT-4o Mini Vanilla LLM 排名：[2, 1, 2, 2, ...]（40 个）
   - Gemini 3 Flash RAG 排名：[...]
   - ...

4. **计算每个模型的统计量**：
   ```python
   for each model:
       RAG 平均排名 = np.mean(RAG 排名列表)
       RAG 标准差 = np.std(RAG 排名列表)
       Vanilla LLM 平均排名 = np.mean(Vanilla LLM 排名列表)
       Vanilla LLM 标准差 = np.std(Vanilla LLM 排名列表)
   ```

#### 输出示例

| 模型 | RAG 排名 | Vanilla LLM 排名 |
|------|---------|-----------------|
| GPT-4o Mini | 1.23 ± 0.42 | 1.77 ± 0.42 |
| Gemini 3 Flash | 1.07 ± 0.26 | 1.93 ± 0.26 |
| Grok 4 Fast | 1.18 ± 0.38 | 1.82 ± 0.38 |

**解读**: 每个模型内部比较 RAG 和 Vanilla LLM 的表现。Gemini 3 Flash 的 RAG 模式表现最佳（1.07）。

---

### 5. 图表四：三维度雷达图

**文件**: `radar_chart_average_rank.png`

#### 算法步骤

1. **按模式分组**：将数据按 `模式` 分为 RAG 和 Vanilla LLM 两组

2. **对每个模式和每个维度**：
   ```python
   for each mode in ['RAG', 'Vanilla LLM']:
       for each dimension in ['医学准确性', '关键要点召回率', '逻辑完整性']:
           scores = []
           for each row with this mode:
               # 获取该维度下 3 个评估者的评分
               for evaluator in ['GPT', 'Gemini', 'Grok']:
                   score = row[f'{evaluator}-{dimension}[1-10 分]']
                   scores.append(score)
           
           dimension_score = np.mean(scores)
   ```

3. **生成雷达图数据**：
   - RAG: [医学准确性分数，关键要点召回率分数，逻辑完整性分数]
   - Vanilla LLM: [医学准确性分数，关键要点召回率分数，逻辑完整性分数]

4. **Y 轴范围自动计算**：
   ```python
   all_scores = [所有维度的分数]
   min_score = min(all_scores)
   max_score = max(all_scores)
   data_range = max_score - min_score
   margin = data_range × 0.2
   
   y_min = min_score - margin
   y_max = max_score + margin
   ```

#### 输出示例

| 模式 | 医学准确性 | 关键要点召回率 | 逻辑完整性 |
|------|-----------|--------------|-----------|
| RAG | 8.48 | 8.34 | 8.68 |
| Vanilla LLM | 7.92 | 7.26 | 8.22 |

**解读**: RAG 在三个维度上均优于 Vanilla LLM，其中关键要点召回率差距最大（1.08 分）。

---

## 统计方法总结

| 图表 | 比较单位 | 排名范围 | 统计指标 |
|------|---------|---------|---------|
| 平均排名对比 | 病例 | 1-2 | 均值 ± 标准差 |
| 首选率对比 | 病例 | - | 百分比 ± 二项分布标准差 |
| LLM 分组排名 | 病例 × 模型 | 1-2 | 均值 ± 标准差 |
| 三维度雷达图 | 维度 | - | 平均分 |

---

## 关键设计决策

### 1. 为什么使用排名而非原始分数？

- **消除评估者偏差**：不同评估者可能有不同的评分标准，排名可以消除这种偏差
- **病例间可比性**：不同病例的难度不同，排名可以在病例间进行比较
- **直观解释**：排名 1 表示"更好"，易于理解

### 2. 为什么每个病例内比较？

- **控制混杂变量**：同一病例的患者信息、病情复杂度相同，可以公平比较 RAG 和 Vanilla LLM
- **配对设计**：类似于配对 t 检验的设计，提高统计效力

### 3. 为什么使用 9 个评分的平均？

- **综合评估**：整合 3 个评估者和 3 个维度的信息
- **减少随机误差**：多个评分的平均可以减少单一评分的随机误差

---

## 复现步骤

```bash
# 1. 准备数据
# 确保 模型评分.xlsx 在项目根目录

# 2. 运行数据处理和图表生成
cd /path/to/RAGAnswer_Graph

# 生成所有图表
python scripts/generate_rag_comparison_chart.py
python scripts/generate_ranked_first_rate_chart.py
python scripts/generate_llm_ranking_chart.py
python scripts/generate_radar_chart.py

# 3. 查看输出
# 图表保存在 outputs/ 目录
```

---

## 版本信息

- **数据处理模块**: `src/data_processor.py`
- **可视化模块**: `src/visualization/`
- **图表生成脚本**: `scripts/`
- **生成日期**: 2026 年 2 月 26 日
