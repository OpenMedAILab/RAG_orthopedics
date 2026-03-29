"""
带误差线的分组柱状图绘图模块

用于绘制学术风格的分组柱状图，支持误差线显示。
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional, Tuple


def plot_grouped_bar_with_errors(
    data: Dict[str, Dict[str, float]],
    errors: Dict[str, Dict[str, float]],
    categories: List[str],
    title: str,
    y_label: str = "Value",
    category_colors: Optional[Dict[str, str]] = None,
    figsize: Tuple[float, float] = (10, 7),
    fontsize: int = 14,
    bar_width: float = 0.25,
    save_path: Optional[str] = None,
    dpi: int = 300,
    y_max: Optional[float] = None,
    y_min: float = 0.0,
    show_value_labels: bool = True,
) -> None:
    """
    绘制带误差线的分组柱状图

    参数:
        data: 数据字典 {model: {'RAG': value, 'Vanilla LLM': value}}
        errors: 误差字典 {model: {'RAG': std, 'Vanilla LLM': std}}
        categories: 类别列表 ['RAG', 'Vanilla LLM']
        title: 图表标题
        y_label: Y 轴标签
        category_colors: 类别颜色字典
        figsize: 图表尺寸
        fontsize: 字体大小
        bar_width: 柱体宽度
        save_path: 保存路径
        dpi: 分辨率
        y_max: Y 轴最大值
        y_min: Y 轴最小值
        show_value_labels: 是否显示数值标签
    """
    # 设置默认颜色
    if category_colors is None:
        category_colors = {
            'RAG': '#1a9988',      # 深青绿色
            'Vanilla LLM': '#a8b8d8',   # 淡蓝紫色
        }
    
    # 获取模型列表
    models = list(data.keys())
    n_models = len(models)
    n_categories = len(categories)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    
    # 计算柱体位置
    x_positions = np.arange(n_models)
    
    # 绘制每个类别的柱状图
    for cat_idx, category in enumerate(categories):
        # 提取该类别的数据和误差
        values = [data[model][category] for model in models]
        errs = [errors[model][category] for model in models]
        
        # 计算柱体位置偏移
        offset = (cat_idx - (n_categories - 1) / 2) * bar_width
        x_current = x_positions + offset
        
        # 绘制柱状图带误差线
        ax.bar(
            x_current,
            values,
            yerr=errs,
            width=bar_width,
            color=category_colors.get(category, '#999999'),
            edgecolor='none',
            capsize=5,
            error_kw={'ecolor': '#000000', 'elinewidth': 1, 'capthick': 1},
            alpha=0.85,
            label=category,
        )
    
    # 设置坐标轴样式
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    
    # 设置 X 轴
    ax.set_xticks(x_positions)
    ax.set_xticklabels(models, fontsize=16, rotation=0, ha='center')
    
    # 设置 Y 轴
    ax.set_ylabel(y_label, fontsize=16)
    
    # 设置 Y 轴范围
    if y_max is None:
        all_values = [data[model][cat] for model in models for cat in categories]
        all_errors = [errors[model][cat] for model in models for cat in categories]
        y_max = max(v + e for v, e in zip(all_values, all_errors)) * 1.15
    ax.set_ylim(y_min, y_max * 1.2)  # Y 轴增加 20% 空间给图例
    
    # 设置标题（粗体）
    ax.set_title(title, fontsize=16, weight='bold', pad=10)
    
    # 添加图例（在标题下方，水平居中）
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 0.98),  # 图例位置往上移
        frameon=False,
        fontsize=16,
        ncol=2,
        columnspacing=1.0
    )
    
    # 添加数值标签（保留一位小数）
    if show_value_labels:
        for cat_idx, category in enumerate(categories):
            values = [data[model][category] for model in models]
            errs = [errors[model][category] for model in models]
            offset = (cat_idx - (n_categories - 1) / 2) * bar_width
            
            for i, (val, err) in enumerate(zip(values, errs)):
                x = x_positions[i] + offset
                y = val + err + y_max * 0.025  # 距离误差线更远（Y 轴范围的 2.5%）
                ax.text(
                    x, y,
                    f'{val:.1f}±{err:.1f}',  # 保留一位小数
                    ha='center',
                    va='bottom',
                    fontsize=16
                )
    
    # 调整布局（为顶部图例预留空间）
    plt.subplots_adjust(top=0.85)  # 顶部留 15% 空间给图例
    
    # 保存图表
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', format='tiff')
        print(f"Chart saved to: {save_path}")
    
    return fig, ax


if __name__ == '__main__':
    # 测试
    test_data = {
        'GPT': {'RAG': 1.5, 'Vanilla LLM': 1.8},
        'Gemini': {'RAG': 1.3, 'Vanilla LLM': 1.9},
        'Grok': {'RAG': 1.6, 'Vanilla LLM': 1.7},
    }
    test_errors = {
        'GPT': {'RAG': 0.3, 'Vanilla LLM': 0.4},
        'Gemini': {'RAG': 0.2, 'Vanilla LLM': 0.3},
        'Grok': {'RAG': 0.4, 'Vanilla LLM': 0.3},
    }

    plot_grouped_bar_with_errors(
        data=test_data,
        errors=test_errors,
        categories=['RAG', 'Vanilla LLM'],
        title='Test: Grouped Bar with Errors',
        y_label='Rank (Lower is Better)',
        save_path='test_grouped_bar.png',
        y_max=2.5,
        y_min=0,
    )
