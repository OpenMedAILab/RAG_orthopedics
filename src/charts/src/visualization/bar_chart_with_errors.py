"""
带误差线的柱状统计图绘制模块（英文版）

用于绘制学术风格的柱状图，支持误差线、统计检验信息展示。
所有标签使用英文，避免中文字体问题。
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional, Tuple


# 配色方案
DEFAULT_COLORS = [
    '#1a9988',  # Deep Teal - for RAG
    '#a8b8d8',  # Light Blue Purple - for Vanilla LLM
]


def plot_bar_chart_with_errors(
    data: List[float],
    errors: List[float],
    labels: List[str],
    title: str,
    y_label: str = "Average Rank",
    x_label: str = "",
    colors: Optional[List[str]] = None,
    stat_annotation: Optional[str] = None,
    value_labels: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (8, 6),
    dpi: int = 300,
    save_path: Optional[str] = None,
    y_max: Optional[float] = None,
    y_min: float = 0.0,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制带误差线的柱状图（英文标签）
    
    参数:
        data: 柱状图数据值列表
        errors: 误差值列表（标准差或置信区间）
        labels: X 轴类别标签
        title: 图表标题
        y_label: Y 轴标签
        x_label: X 轴标签
        colors: 柱体颜色列表
        stat_annotation: 统计检验信息（显示在标题下方）
        value_labels: 柱体上方数值标签
        figsize: 图表尺寸 (宽，高)
        dpi: 分辨率
        save_path: 保存路径
        y_max: Y 轴最大值
        y_min: Y 轴最小值
    
    返回:
        (fig, ax): matplotlib Figure 和 Axes 对象
    """
    # 参数验证
    if not (len(data) == len(errors) == len(labels)):
        raise ValueError("data, errors, and labels must have the same length")
    
    n_groups = len(data)
    
    # 设置颜色
    if colors is None:
        colors = DEFAULT_COLORS
    if len(colors) < n_groups:
        colors = colors * ((n_groups // len(colors)) + 1)
    colors = colors[:n_groups]
    
    # 生成默认数值标签
    if value_labels is None:
        value_labels = [f"{d:.2f}±{e:.2f}" for d, e in zip(data, errors)]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # 设置坐标轴样式（仅保留左侧和底部边框）
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    
    # 设置刻度线样式
    ax.tick_params(axis='both', direction='in', length=4, width=0.8, colors='#333333')
    
    # 绘制柱状图
    x_positions = np.arange(n_groups)
    bars = ax.bar(
        x_positions,
        data,
        yerr=errors,
        color=colors,
        edgecolor='none',
        capsize=5,
        error_kw={'ecolor': '#000000', 'elinewidth': 1, 'capthick': 1},
        width=0.6,
        alpha=0.85,
    )

    # 设置 X 轴
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, fontsize=16, color='#333333', rotation=0, ha='center')
    if x_label:
        ax.set_xlabel(x_label, fontsize=16, color='#333333')
    
    # 设置 Y 轴
    ax.set_ylabel(y_label, fontsize=16, color='#333333')
    
    # 设置 Y 轴范围
    if y_max is None:
        y_max = max(data) + max(errors) + (max(data) * 0.15)
    ax.set_ylim(y_min, y_max)
    
    # 设置 Y 轴刻度
    ax.yaxis.set_tick_params(labelsize=16)
    ax.tick_params(axis='y', labelcolor='#333333')
    
    # 设置标题（粗体）
    if title:
        ax.set_title(title, fontsize=16, weight='bold', color='#333333', pad=20)

    # 添加数值标签
    for i, (bar, value_label) in enumerate(zip(bars, value_labels)):
        # 计算数值标签位置：柱体高度 + 误差 + Y 轴范围的 3% 间距
        label_y_pos = data[i] + errors[i] + y_max * 0.03
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            label_y_pos,
            value_label,
            ha='center',
            va='bottom',
            fontsize=16,  # 字体大小 16pt
            color='#333333',
        )
    
    # 布局优化
    plt.tight_layout()
    
    # 保存图表
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', format='tiff')
    
    return fig, ax


if __name__ == '__main__':
    # 测试示例
    data = [2.5, 3.1, 1.8, 4.2]
    errors = [0.3, 0.4, 0.2, 0.5]
    labels = ['Method A', 'Method B', 'Method C', 'Method D']
    
    fig, ax = plot_bar_chart_with_errors(
        data=data,
        errors=errors,
        labels=labels,
        title='Friedman Test: χ²(3) = 12.45, P = 0.006',
        y_label='Average Rank (Lower is Better)',
        stat_annotation='Post-hoc: A vs B (P=0.03), A vs C (P=0.01)',
        save_path='test_output.png',
    )
    print("Test chart saved to test_output.png")
