# 雷达图统计方法说明

## 概述

雷达图（Radar Chart）用于可视化展示每个评估者（医生）对 6 个方法（3 模型 × 2 模式）在三个评估维度上的平均评分对比，直观呈现 **No-RAG** 与 **RAG** 两种模式的差异。

---

## 数据结构

### 原始数据

| 数据源 | 评估者 | 评分维度 | 评分范围 |
|--------|--------|---------|---------|
| 人工评分.xlsx | 医生 1-3 | 医学准确性、关键要点召回率、逻辑完整性 | 1-3 分 |

### 数据规模

- **病例数**：40 个医学病例
- **方法数**：6 个（GPT_No-RAG, GPT_RAG, Gemini_No-RAG, Gemini_RAG, Grok_No-RAG, Grok_RAG）
- **总样本数**：240（40 病例 × 6 方法）

---

## 统计计算

### 综合分数计算

对于每个样本（病例 × 方法），计算综合分数：

$$\text{Score}_{\text{综合}} = \frac{\text{医学准确性} + \text{关键要点召回率} + \text{逻辑完整性}}{3}$$

**Python 实现**：

```python
# 对每个医生
exp_df['avg_score'] = (exp_df['医学准确性 [1-3 分]'] +
                       exp_df['关键要点召回率 [1-3 分]'] +
                       exp_df['逻辑完整性 [1-3 分]']) / 3
```

### 按方法分组求平均

对每个医生，计算其对 6 个方法的平均综合分数：

$$\bar{X}_{\text{医生，方法}} = \frac{1}{N}\sum_{i=1}^{N} \text{Score}_{\text{综合}, i}$$

其中 $N$ 为该医生对该方法的评分次数（约 40 次，每个病例一次）。

**Python 实现**：

```python
# 创建方法标识
exp_df['method'] = exp_df['被评估模型'] + '_' + exp_df['模式']

# 按方法分组求平均
method_scores = exp_df.groupby('method')['avg_score'].mean()
```

### 三维度分别计算

除了综合分数，还分别计算三个维度的平均分：

$$\bar{X}_{\text{医学准确性}} = \frac{1}{N}\sum_{i=1}^{N} \text{医学准确性}_i$$

$$\bar{X}_{\text{关键要点召回率}} = \frac{1}{N}\sum_{i=1}^{N} \text{关键要点召回率}_i$$

$$\bar{X}_{\text{逻辑完整性}} = \frac{1}{N}\sum_{i=1}^{N} \text{逻辑完整性}_i$$

---

## 雷达图绘制原理

### 极坐标系

雷达图使用极坐标系，每个维度对应一个从中心辐射的轴：

- **角度**：每个维度均匀分布，角度间隔 = $360° / \text{维度数}$
- **半径**：表示评分大小，从中心（最小值）到外圈（最大值）

### 角度计算

对于 3 个维度：

$$\theta_i = \frac{2\pi}{3} \times i, \quad i = 0, 1, 2$$

**Python 实现**：

```python
N = len(labels)  # 维度数 = 3
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # 闭合图形
```

### 数据闭合

为了绘制闭合的多边形，需要在数据末尾添加第一个值：

```python
values = [医学准确性，关键要点召回率，逻辑完整性]
values_closed = values + values[:1]
angles_closed = angles + angles[:1]
```

---

## 图形元素

### 网格线

绘制同心圆作为参考网格，通常选择等间距的刻度：

```python
for r in [1, 1.5, 2, 2.5, 3]:
    ax.plot(angles, [r] * (N + 1), color='grey', linewidth=0.4, linestyle='--', alpha=0.5)
```

### 数据线和填充

每个模式（No-RAG / RAG）绘制一条数据线和填充区域：

```python
# 绘制数据线
ax.plot(angles, values_closed, color=color, linewidth=2.2, linestyle='solid', label=label)

# 填充区域
ax.fill(angles, values_closed, alpha=0.18, color=color)

# 数据点标记
for a, val in zip(angles[:-1], values):
    ax.plot(a, val, 'o', color=color, markersize=5)
```

### 图例位置

图例放置在右上角，使用 `bbox_to_anchor` 参数定位：

```python
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=14)
```

---

## 输出结果

### 单个医生雷达图

为每个医生生成一个雷达图，展示该医生对 No-RAG 和 RAG 两种模式的评分对比。

| 文件 | 说明 |
|------|------|
| `outputs/radar_rater1.tif` | 医生 1 雷达图 |
| `outputs/radar_rater2.tif` | 医生 2 雷达图 |
| `outputs/radar_rater3.tif` | 医生 3 雷达图 |

### 汇总雷达图

汇总 3 个医生的平均评分，生成一个综合雷达图。

| 文件 | 说明 |
|------|------|
| `outputs/radar_aggregated.tif` | 3 个医生平均雷达图 |

---

## 计算结果

### 各医生评分对比

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

### RAG 相比 No-RAG 的提升

| 维度 | 提升幅度 | 提升百分比 |
|------|---------|-----------|
| Medical Accuracy | +0.60 | +31.7% |
| Key Point Recall | +0.47 | +25.3% |
| Logical Completeness | +0.59 | +34.1% |

---

## Python 代码实现

### 核心函数

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def get_rater_dim_scores(rdata, mode):
    """
    计算单个医生在指定模式下的三维度平均分
    
    参数:
        rdata: 单个医生的数据列表
        mode: 'No-RAG' 或 'RAG'
    
    返回:
        [accuracy_mean, recall_mean, logic_mean]
    """
    DIM_KEYS = ['accuracy', 'recall', 'logic']
    scores = {k: [] for k in DIM_KEYS}
    
    for row in rdata:
        if row['mode'] == mode:
            for k in DIM_KEYS:
                if row[k] is not None:
                    scores[k].append(row[k])
    
    return [np.mean(scores[k]) for k in DIM_KEYS]


def radar(ax, values_list, labels, colors, legend_labels, title, max_val=3.0):
    """
    绘制雷达图
    
    参数:
        ax: matplotlib polar axis
        values_list: 多条线的数据列表，如 [[norag 三维度], [rag 三维度]]
        labels: 维度标签列表
        colors: 每条线的颜色列表
        legend_labels: 图例标签列表
        title: 图表标题
        max_val: Y 轴最大值
    """
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=14, fontweight='bold')

    # 网格线
    for r in [1, 1.5, 2, 2.5, 3]:
        ax.plot(angles, [r] * (N + 1), color='grey', linewidth=0.4, 
                linestyle='--', alpha=0.5)
    
    ax.set_ylim(0, max_val)
    ax.set_yticks([1, 1.5, 2, 2.5, 3])
    ax.set_yticklabels(['1', '1.5', '2', '2.5', '3'], fontsize=12, color='grey')

    # 绘制数据线和填充
    for vals, color, lbl in zip(values_list, colors, legend_labels):
        v = vals + vals[:1]  # 闭合图形
        ax.plot(angles, v, color=color, linewidth=2.2, linestyle='solid', label=lbl)
        ax.fill(angles, v, alpha=0.18, color=color)
        
        # 数据点标记
        for a, val in zip(angles[:-1], vals):
            ax.plot(a, val, 'o', color=color, markersize=5)

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    
    # 图例
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=14)
    ax.spines['polar'].set_visible(False)
```

### 使用示例

```python
# 创建图形
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))

# 计算评分
norag_scores = get_rater_dim_scores(rater_data, 'No-RAG')
rag_scores = get_rater_dim_scores(rater_data, 'RAG')

# 绘制雷达图
radar(ax,
      [norag_scores, rag_scores],
      ['Medical\nAccuracy', 'Key Point\nRecall', 'Logical\nCompleteness'],
      ['#4C72B0', '#DD8452'],
      ['No-RAG', 'RAG'],
      'Rater 1: No-RAG vs RAG')

# 保存
plt.savefig('outputs/radar_rater1.tif', dpi=300, bbox_inches='tight')
```

---

## 图形样式规范

### 配色方案

| 元素 | 颜色代码 | 说明 |
|------|---------|------|
| No-RAG 线 | #4C72B0 | 蓝色 |
| RAG 线 | #DD8452 | 橙色 |
| 网格线 | grey | 灰色虚线 |
| 填充 | 同色，alpha=0.18 | 半透明填充 |

### 字体大小

| 元素 | 字号 |
|------|------|
| 标题 | 16pt, bold |
| 维度标签 | 14pt, bold |
| Y 轴刻度 | 12pt |
| 图例 | 14pt |

### 图片规格

| 属性 | 值 |
|------|-----|
| 尺寸 | 8 × 6 英寸 |
| DPI | 300 |
| 格式 | TIF |
| 边框 | 无边框（spines 隐藏） |

---

## 结果解读

### 雷达图形状分析

- **面积大小**：面积越大表示综合评分越高
- **形状对称性**：形状越规则表示各维度发展越均衡
- **覆盖关系**：如果一个多边形完全覆盖另一个，表示在所有维度上都优于对方

### 本例观察

1. **RAG 模式优势**：RAG 的多边形面积明显大于 No-RAG，表明 RAG 在三个维度上均优于 No-RAG

2. **维度差异**：
   - **Key Point Recall**：No-RAG 与 RAG 差距最大
   - **Logical Completeness**：No-RAG 与 RAG 差距较大
   - **Medical Accuracy**：No-RAG 与 RAG 差距相对较小

3. **医生间一致性**：3 个医生的雷达图形状相似，表明评估标准较为一致

---

## 参考文献

1. Friendly, M. (2001). Milestones in the history of thematic cartography, statistical graphics, and data visualization.

2. Wilkinson, L. (2005). The grammar of graphics (2nd ed.). Springer.

3. Matplotlib Documentation. https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot.html#matplotlib.pyplot.subplot.polar

---

*文档生成日期：2026-03-04*
