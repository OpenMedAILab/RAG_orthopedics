# Table 1 统计方法说明

## 概述

Table 1 展示了评估者间信度（Inter-rater Reliability）和跨方法相关性（Cross-method Correlation）的统计分析结果，使用 **Friedman 检验** 和 **Kendall's W 协调系数** 来评估多个评估者之间排名的一致性。

---

## 统计原理

### Friedman 检验

Friedman 检验是一种非参数统计方法，用于检验多个相关样本（评估者）的排名是否存在显著差异。它是对参数方法（重复测量 ANOVA）的非参数替代。

#### 原假设 (H₀)
所有评估者的排名分布相同，即评估者间无系统性差异。

#### 备择假设 (H₁)
至少有一个评估者的排名分布与其他评估者不同。

#### 计算公式

$$Q = \frac{12}{k^2 \times n \times (n + 1)} \times \sum_{j=1}^{k} R_j^2 - 3 \times k \times (n + 1)$$

或等价形式（基于离差平方和）：

$$Q = \frac{12}{k \times n \times (n + 1)} \times S$$

其中：
- $k$ = 评估者数量
- $n$ = 方法（被评估对象）数量
- $R_j$ = 第 $j$ 个评估者的秩和
- $S$ = 秩和的离差平方和 = $\sum_{j=1}^{k} (R_j - \bar{R})^2$
- $\bar{R}$ = 平均秩和 = $\frac{n(n+1)}{2}$

#### P 值计算

Friedman 统计量 $Q$ 近似服从自由度为 $k-1$ 的卡方分布：

$$p = P(\chi^2_{k-1} > Q)$$

---

### Kendall's W 协调系数

Kendall's W（也称为 Kendall's coefficient of concordance）用于衡量多个评估者之间排名的一致性程度。

#### 定义

$$W = \frac{12 \times S}{k^2 \times n \times (n^2 - 1)}$$

其中：
- $S$ = 秩和的离差平方和 = $\sum_{i=1}^{n} (R_i - \bar{R})^2$
- $R_i$ = 第 $i$ 个方法获得的秩和（所有评估者对该方法的排名之和）
- $\bar{R}$ = 期望的平均秩和 = $\frac{k(n+1)}{2}$
- $k$ = 评估者数量
- $n$ = 方法数量

#### 取值范围与解释

| W 值范围 | 一致性程度 | 解释 |
|---------|-----------|------|
| 0.9 - 1.0 | 高度一致 | 评估者间排名几乎完全相同 |
| 0.7 - 0.9 | 中度一致 | 评估者间排名有较好的一致性 |
| 0.5 - 0.7 | 低至中度一致 | 评估者间排名有一定一致性 |
| 0.3 - 0.5 | 低度一致 | 评估者间排名一致性较低 |
| 0.0 - 0.3 | 一致性很低 | 评估者间排名几乎没有一致性 |

#### 与 Friedman Q 的关系

$$Q = W \times k \times (n - 1)$$

---

## 计算步骤（两步法）

### 第一步：计算每个评估者对 6 个方法的平均排名

对于每个评估者（LLM 或医生）：

1. **对每个病例内**的 6 个方法（3 模型 × 2 模式）按综合分数进行排名
   - 综合分数 = （医学准确性 + 关键要点召回率 + 逻辑完整性）/ 3
   - 排名方法：使用平均排名法（method='average'）处理并列情况

2. **跨 40 个病例**，计算每个评估者对每个方法的平均排名

**示例数据结构**：

| 评估者 | GPT_No-RAG | GPT_RAG | Gemini_No-RAG | Gemini_RAG | Grok_No-RAG | Grok_RAG |
|--------|-----------|---------|---------------|------------|-------------|----------|
| GPT | 2.76 | 2.49 | 4.10 | 4.46 | 3.73 | 3.46 |
| Gemini | 1.49 | 2.03 | 4.66 | 5.06 | 3.46 | 4.30 |
| Grok | 1.48 | 3.51 | 2.60 | 5.41 | 2.69 | 5.31 |

### 第二步：基于平均排名矩阵计算统计量

**输入**：平均排名矩阵（行=评估者，列=方法）

**计算流程**：

```python
def friedman_kendall_from_ranks(rank_matrix):
    """
    从平均排名矩阵计算 Friedman 统计量和 Kendall's W
    
    参数:
        rank_matrix: numpy array, 形状 (k, n), k=评估者数，n=方法数
    
    返回:
        Q, p_value, W
    """
    k, n = rank_matrix.shape
    
    # 1. 计算每个方法的秩和（对行求和）
    rank_sums = rank_matrix.sum(axis=0)  # 形状 (n,)
    
    # 2. 计算秩和的离差平方和 S
    mean_rank_sum = np.mean(rank_sums)
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    
    # 3. 计算 Kendall's W
    W = (12 * S) / (k**2 * n * (n**2 - 1))
    W = max(0, min(1, W))
    
    # 4. 计算 Friedman Q
    Q = W * k * (n - 1)
    
    # 5. 计算 P 值（卡方分布）
    p_value = 1 - stats.chi2.cdf(Q, k - 1)
    
    return Q, p_value, W
```

---

## 具体计算示例

### LLM-as-a-judge (n=3)

**输入数据**（3 个 LLM 对 6 个方法的平均排名）：

| 评估者 | GPT_No-RAG | GPT_RAG | Gemini_No-RAG | Gemini_RAG | Grok_No-RAG | Grok_RAG | 秩和 |
|--------|-----------|---------|---------------|------------|-------------|----------|------|
| GPT | 2.7625 | 2.4875 | 4.1000 | 4.4625 | 3.7250 | 3.4625 | 21.00 |
| Gemini | 1.4875 | 2.0250 | 4.6625 | 5.0625 | 3.4625 | 4.3000 | 21.00 |
| Grok | 1.4750 | 3.5125 | 2.6000 | 5.4125 | 2.6875 | 5.3125 | 21.00 |
| **方法秩和** | **5.725** | **8.025** | **11.363** | **14.938** | **9.875** | **13.075** | **63.00** |

**计算过程**：

1. 每个方法的秩和（列求和）：
   - R_GPT_No-RAG = 2.7625 + 1.4875 + 1.4750 = 5.725
   - R_GPT_RAG = 2.4875 + 2.0250 + 3.5125 = 8.025
   - ...

2. 平均秩和：
   - $\bar{R} = 63.00 / 6 = 10.5$

3. 离差平方和 S：
   - $S = (5.725-10.5)^2 + (8.025-10.5)^2 + (11.363-10.5)^2 + (14.938-10.5)^2 + (9.875-10.5)^2 + (13.075-10.5)^2$
   - $S = 22.80 + 6.13 + 0.74 + 19.71 + 0.39 + 6.63 = 56.40$

4. Kendall's W：
   - $W = \frac{12 \times 56.40}{3^2 \times 6 \times (6^2 - 1)} = \frac{676.8}{9 \times 6 \times 35} = \frac{676.8}{1890} = 0.358$

5. Friedman Q：
   - $Q = W \times k \times (n - 1) = 0.358 \times 3 \times 5 = 5.370$

6. P 值：
   - $p = P(\chi^2_{3-1} > 5.370) = P(\chi^2_2 > 5.370) = 0.068$

**结果**：
- Friedman Q = 5.370
- P-value = 0.068
- Kendall's W = 0.358

---

### Expert Evaluators (n=3)

**输入数据**（3 个医生对 6 个方法的平均排名）：

| 评估者 | GPT_No-RAG | GPT_RAG | Gemini_No-RAG | Gemini_RAG | Grok_No-RAG | Grok_RAG |
|--------|-----------|---------|---------------|------------|-------------|----------|
| expert1 | 2.6250 | 5.0125 | 2.1875 | 4.8125 | 1.9375 | 4.4250 |
| expert2 | 2.5625 | 5.0000 | 2.1000 | 4.9750 | 1.8500 | 4.5125 |
| expert3 | 2.6500 | 5.0375 | 2.1625 | 4.7250 | 1.9375 | 4.4875 |

**计算结果**：
- Friedman Q = 8.729
- P-value = 0.013
- Kendall's W = 0.582

---

### Cross-method Correlation (n=6)

**输入数据**（6 个评估者：3 个 LLM + 3 个医生）：

| 评估者 | GPT_No-RAG | GPT_RAG | Gemini_No-RAG | Gemini_RAG | Grok_No-RAG | Grok_RAG |
|--------|-----------|---------|---------------|------------|-------------|----------|
| Expert_expert1 | 2.6250 | 5.0125 | 2.1875 | 4.8125 | 1.9375 | 4.4250 |
| Expert_expert2 | 2.5625 | 5.0000 | 2.1000 | 4.9750 | 1.8500 | 4.5125 |
| Expert_expert3 | 2.6500 | 5.0375 | 2.1625 | 4.7250 | 1.9375 | 4.4875 |
| LLM_GPT | 2.7625 | 2.4875 | 4.1000 | 4.4625 | 3.7250 | 3.4625 |
| LLM_Gemini | 1.4875 | 2.0250 | 4.6625 | 5.0625 | 3.4625 | 4.3000 |
| LLM_Grok | 1.4750 | 3.5125 | 2.6000 | 5.4125 | 2.6875 | 5.3125 |

**计算结果**：
- Friedman Q = 9.552
- P-value = 0.089
- Kendall's W = 0.318

---

## 结果解读

### LLM-as-a-judge (W=0.358, P=0.068)

- **Kendall's W = 0.358**：3 个 LLM 评估者对 6 个方法的排名一致性较低
- **P = 0.068**：差异接近显著性水平（0.05），但未达到统计学显著
- **解读**：GPT、Gemini、Grok 三个评估者对 6 个方法的排名有一定的一致性，但存在差异

### Expert Evaluators (W=0.582, P=0.013)

- **Kendall's W = 0.582**：3 个医生评估者对 6 个方法的排名一致性中等
- **P = 0.013**：差异具有统计学显著性（P < 0.05）
- **解读**：3 个医生对 6 个方法的排名有较好的一致性，且这种一致性不是偶然的

### Cross-method (W=0.318, P=0.089)

- **Kendall's W = 0.318**：6 个评估者（3 个 LLM + 3 个医生）之间的排名一致性较低
- **P = 0.089**：差异不具有统计学显著性
- **解读**：LLM 评估和医生评估对 6 个方法的排名模式存在差异，但这种差异不够显著

---

## Python 代码实现

### 核心函数

```python
from scipy import stats
import numpy as np

def friedman_kendall_from_ranks(rank_matrix):
    """
    从平均排名矩阵计算 Friedman 统计量和 Kendall's W
    
    参数:
        rank_matrix: numpy array, 形状 (k, n)
                     k=评估者数，n=方法数
                     值=每个评估者对每个方法的平均排名
    
    返回:
        Q: Friedman 统计量
        p_value: P 值
        W: Kendall's W 协调系数
    """
    k, n = rank_matrix.shape  # k=评估者数，n=方法数
    
    # 1. 计算每个方法的秩和（对行求和）
    rank_sums = rank_matrix.sum(axis=0)
    
    # 2. 计算秩和的离差平方和 S
    mean_rank_sum = np.mean(rank_sums)
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    
    # 3. 计算 Kendall's W
    # W = 12S / (k² × n × (n² - 1))
    W = (12 * S) / (k**2 * n * (n**2 - 1))
    W = max(0, min(1, W))
    
    # 4. 计算 Friedman Q
    # Q = W × k × (n - 1)
    Q = W * k * (n - 1)
    
    # 5. 计算 P 值（卡方分布，自由度 = k-1）
    p_value = 1 - stats.chi2.cdf(Q, k - 1)
    
    return Q, p_value, W
```

### 使用示例

```python
# LLM 评估者平均排名矩阵（3 个评估者 × 6 个方法）
llm_ranks = np.array([
    [2.7625, 2.4875, 4.1000, 4.4625, 3.7250, 3.4625],  # GPT
    [1.4875, 2.0250, 4.6625, 5.0625, 3.4625, 4.3000],  # Gemini
    [1.4750, 3.5125, 2.6000, 5.4125, 2.6875, 5.3125],  # Grok
])

Q, p, W = friedman_kendall_from_ranks(llm_ranks)
print(f"Friedman Q = {Q:.3f}")
print(f"P-value = {p:.3f}")
print(f"Kendall's W = {W:.3f}")
```

---

## 参考文献

1. Friedman, M. (1937). The use of ranks to avoid the assumption of normality implicit in the analysis of variance. *Journal of the American Statistical Association*, 32(200), 675-701.

2. Kendall, M. G., & Smith, B. B. (1939). The problem of m rankings. *The Annals of Mathematical Statistics*, 10(3), 275-287.

3. Siegel, S., & Castellan, N. J. (1988). *Nonparametric statistics for the behavioral sciences* (2nd ed.). McGraw-Hill.

4. EyeRAG Project. https://github.com/OpenMedAILab/EyeRAG

---

## 附录：P 值格式化规范

按照学术论文规范，P 值按以下方式格式化：

| P 值范围 | 显示格式 |
|---------|---------|
| P < 0.001 | `<0.001` |
| 0.001 ≤ P < 0.01 | `0.XXX`（3 位小数） |
| P ≥ 0.01 | `0.XXX`（3 位小数） |

---

*文档生成日期：2026-03-04*
