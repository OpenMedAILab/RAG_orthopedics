"""
带误差线的单柱状统计图绘制模块

本模块提供用于绘制带误差线的柱状统计图的函数，
适用于展示多组数据的平均排名或评分，并支持统计检验信息展示。
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional, Tuple, Union


def plot_bar_chart_with_statistical_test(
    data: List[float],
    errors: List[float],
    labels: List[str],
    title: str,
    y_label: str = "平均排名",
    colors: Optional[List[str]] = None,
    stat_test_info: Optional[str] = None,
    value_labels: Optional[List[str]] = None,
    figsize: Tuple[float, float] = (8, 6),
    dpi: int = 100,
    save_path: Optional[str] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制带误差线的单柱状统计图
    
    本函数用于生成学术风格的柱状图，支持误差线、统计检验信息展示、
    数值标注等功能。所有数据参数通过函数参数传入，确保代码可复用于不同业务场景。
    
    参数说明
    --------
    data : List[float]
        柱状图的数据值列表，每个值对应一个柱体的高度
        示例：[2.5, 3.1, 1.8, 4.2]
    
    errors : List[float]
        误差值列表，对应每个柱体的误差线长度
        通常为标准差 (std) 或置信区间 (CI)
        示例：[0.3, 0.4, 0.2, 0.5]
    
    labels : List[str]
        X 轴标签列表，对应每个柱体的类别名称
        示例：['方法 A', '方法 B', '方法 C', '方法 D']
    
    title : str
        图表主标题，通常包含统计检验信息
        示例：'Friedman 检验：χ²(3) = 12.45, P = 0.006'
    
    y_label : str, 可选
        Y 轴标签，默认为"平均排名"
        示例：'平均评分', '准确率 (%)'
    
    colors : List[str], 可选
        柱体颜色列表，采用柔和的专业配色方案
        默认使用预设的学术风格配色
        示例：['#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0']
    
    stat_test_info : str, 可选
        统计检验详细信息，显示在标题下方
        示例：'事后检验：A vs B (P=0.03), A vs C (P=0.01)'
    
    value_labels : List[str], 可选
        柱体上方标注的数值标签
        如果为 None，则自动根据 data 和 errors 生成
        示例：['2.50±0.30', '3.10±0.40', '1.80±0.20', '4.20±0.50']
    
    figsize : Tuple[float, float], 可选
        图表尺寸 (宽，高)，单位为英寸
        默认 (8, 6) 适合大多数学术出版需求
    
    dpi : int, 可选
        图表分辨率，默认为 100
        出版质量建议设置为 300
    
    save_path : str, 可选
        图片保存路径
        如果为 None，则不保存文件
    
    返回
    ----
    Tuple[plt.Figure, plt.Axes]
        返回 figure 和 axes 对象，便于后续自定义修改
    
    示例
    ----
    >>> data = [2.5, 3.1, 1.8, 4.2]
    >>> errors = [0.3, 0.4, 0.2, 0.5]
    >>> labels = ['方法 A', '方法 B', '方法 C', '方法 D']
    >>> fig, ax = plot_bar_chart_with_statistical_test(
    ...     data=data,
    ...     errors=errors,
    ...     labels=labels,
    ...     title='Friedman 检验：χ²(3) = 12.45, P = 0.006'
    ... )
    >>> plt.show()
    """
    
    # ========== 参数验证 ==========
    # 检查数据长度一致性
    if not (len(data) == len(errors) == len(labels)):
        raise ValueError(
            f"data、errors 和 labels 的长度必须一致，"
            f"当前长度分别为 {len(data)}, {len(errors)}, {len(labels)}"
        )
    
    n_groups = len(data)
    
    # 设置默认颜色方案（柔和的学术风格配色）
    if colors is None:
        colors = [
            '#5DA5DA',  # 柔和蓝色
            '#FAA43A',  # 柔和橙色
            '#60BD68',  # 柔和绿色
            '#F17CB0',  # 柔和粉色
            '#B2912F',  # 柔和棕色
            '#815E9D',  # 柔和紫色
            '#F15854',  # 柔和红色
            '#D3D3D3',  # 浅灰色
        ]
    
    # 如果颜色数量不足，循环使用
    if len(colors) < n_groups:
        colors = colors * ((n_groups // len(colors)) + 1)
    colors = colors[:n_groups]
    
    # 生成默认数值标签
    if value_labels is None:
        value_labels = [f"{d:.2f}±{e:.2f}" for d, e in zip(data, errors)]
    
    # ========== 图表初始化 ==========
    # 创建图形和坐标轴对象
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # ========== 坐标轴设置 ==========
    # 设置坐标轴位置和样式（学术风格：仅显示左侧和底部边框）
    ax.spines['top'].set_visible(False)      # 隐藏顶部边框
    ax.spines['right'].set_visible(False)    # 隐藏右侧边框
    ax.spines['left'].set_color('#333333')   # 深灰色左边框
    ax.spines['bottom'].set_color('#333333') # 深灰色底部边框
    ax.spines['left'].set_linewidth(0.8)     # 细实线
    ax.spines['bottom'].set_linewidth(0.8)   # 细实线
    
    # 设置刻度线方向和样式
    ax.tick_params(axis='both', direction='in', length=4, width=0.8, colors='#333333')
    
    # ========== 柱状图绘制 ==========
    # 创建柱体位置
    x_positions = np.arange(n_groups)
    
    # 绘制柱状图，带误差线
    # capsize: 误差线两端横线的宽度
    # ecolor: 误差线颜色
    # error_kw: 误差线的详细样式设置
    bars = ax.bar(
        x_positions,
        data,
        yerr=errors,
        color=colors,
        edgecolor='none',          # 无边框
        capsize=5,                 # 误差线帽宽度
        error_kw={
            'ecolor': '#000000',   # 误差线为黑色
            'elinewidth': 1,       # 误差线宽度
            'capthick': 1,         # 误差线帽厚度
        },
        width=0.6,                 # 柱体宽度
        alpha=0.85,                # 透明度
    )
    
    # ========== 数值标签标注 ==========
    # 在每个柱体上方添加数值和误差范围标注
    for i, (bar, value_label) in enumerate(zip(bars, value_labels)):
        # 计算标注位置（柱体顶部 + 误差线 + 额外间距）
        label_y_pos = data[i] + errors[i] + (max(data) * 0.05)
        
        # 添加文本标注
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X 位置：柱体中心
            label_y_pos,                         # Y 位置：柱体上方
            value_label,                         # 标注内容
            ha='center',                         # 水平居中
            va='bottom',                         # 垂直底部对齐
            fontsize=9,                          # 字体大小
            color='#333333',                     # 深灰色字体
            weight='normal',                     # 常规字重
        )
    
    # ========== X 轴设置 ==========
    # 设置 X 轴刻度和标签
    ax.set_xticks(x_positions)
    ax.set_xticklabels(
        labels,
        fontsize=10,
        color='#333333',
        rotation=45,              # 旋转 45 度防止重叠
        ha='right',               # 右对齐
        rotation_mode='anchor',   # 旋转锚点
    )
    
    # ========== Y 轴设置 ==========
    # 设置 Y 轴标签
    ax.set_ylabel(
        y_label,
        fontsize=11,
        color='#333333',
        weight='normal',
    )
    
    # 设置 Y 轴范围（从 0 开始，顶部留白）
    y_max = max(data) + max(errors) + (max(data) * 0.15)
    ax.set_ylim(0, y_max)
    
    # 设置 Y 轴刻度
    ax.yaxis.set_tick_params(labelsize=10)
    ax.tick_params(axis='y', labelcolor='#333333')
    
    # ========== 标题设置 ==========
    # 主标题
    ax.set_title(
        title,
        fontsize=12,
        color='#333333',
        weight='normal',
        pad=10,  # 标题与图表的间距
    )
    
    # 统计检验副标题（如果提供）
    if stat_test_info:
        ax.text(
            0.5,
            0.98,
            stat_test_info,
            transform=ax.transAxes,
            ha='center',
            va='top',
            fontsize=9,
            color='#666666',
            weight='normal',
        )
    
    # ========== 布局优化 ==========
    # 自动调整布局，防止标签被截断
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    # ========== 保存图表 ==========
    if save_path:
        # 保存为高分辨率 PNG 文件
        fig.savefig(
            save_path,
            dpi=dpi,
            bbox_inches='tight',
            facecolor='white',      # 白色背景
            edgecolor='none',
        )
    
    return fig, ax
