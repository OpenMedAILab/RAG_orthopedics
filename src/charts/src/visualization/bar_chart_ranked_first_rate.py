"""
垂直柱状统计图可视化模块

本模块提供通用的垂直柱状图绘图函数，用于展示不同类别的数值数据。
图表采用简洁学术风格，支持自定义数据、标签、颜色、轴标签等参数。

本模块为通用绘图工具，不预置任何业务语义参数。
所有数据、标签、颜色、轴标签等应通过函数参数传入。

参考风格：EyeRAG 项目 (https://github.com/OpenMedAILab/EyeRAG)

使用示例:
---------
>>> from visualization.bar_chart_ranked_first_rate import plot_ranked_first_rate
>>>
>>> # 准备数据
>>> data = [75.5, 82.3, 68.9, 91.2]
>>> labels = ["方法 A", "方法 B", "方法 C", "方法 D"]
>>>
>>> # 绘制图表
>>> fig, ax = plot_ranked_first_rate(
...     data=data,
...     labels=labels,
...     title="性能对比",
...     ylabel="百分比 (%)",
...     save_path="output.png"
... )
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List, Optional, Tuple


# ==================== 默认配色方案 ====================
# 低饱和度柔和配色方案，避免高饱和度颜色
# 配色灵感来自 matplotlib 的 Set2 和 Pastel1 配色
DEFAULT_SOFT_COLORS = [
    "#A8D5BA",  # 薄荷绿 - 清新柔和
    "#B8D8E8",  # 淡蓝 - 宁静优雅
    "#D4E8A8",  # 淡黄绿 - 自然舒适
    "#F5D5B8",  # 淡橙 - 温暖柔和
    "#D3D3D3",  # 浅灰 - 中性稳重
    "#E8C8E8",  # 淡紫 - 优雅柔和
    "#F8E8A8",  # 淡黄 - 明亮温馨
    "#B8E8D8",  # 淡青 - 清爽宜人
]

# 字体大小配置（统一 16pt）
FONTSIZE = 16
LARGE_FONTSIZE = 16
TITLE_FONTSIZE = 16


def plot_ranked_first_rate(
    data: List[float],
    labels: List[str],
    title: str = "",
    ylabel: str = "",
    figsize: Tuple[int, int] = (12, 8),
    colors: Optional[List[str]] = None,
    fontsize: Optional[int] = None,
    large_fontsize: Optional[int] = None,
    title_fontsize: Optional[int] = None,
    label_rotation: float = 45,
    y_max: Optional[float] = None,
    show_value_labels: bool = True,
    value_label_fontsize_offset: int = -2,
    bar_width: float = 0.6,
    bar_edge_color: str = "black",
    bar_edge_width: float = 1.5,
    bar_alpha: float = 0.9,
    dpi: int = 300,
    save_path: Optional[str] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制垂直柱状统计图

    本函数生成简洁学术风格的垂直柱状图，采用以下设计特点：
    - 白色背景，仅保留左侧和底部坐标轴
    - 低饱和度柔和配色方案（可通过 colors 参数自定义）
    - 柱体顶部显示数值标签
    - X 轴标签旋转防止重叠

    本函数为通用绘图函数，不预置任何业务语义参数。
    所有数据、标签、颜色、轴标签等应通过函数参数传入。

    参数说明:
    ----------
    data : List[float]
        数值列表，表示每个类别的 Y 轴数值
        例如：[75.5, 82.3, 68.9, 91.2]

    labels : List[str]
        类别标签列表，对应每个柱体的名称
        例如：["类别 A", "类别 B", "类别 C", "类别 D"]

    title : str, optional
        图表标题，默认为空字符串（不显示标题）

    ylabel : str, optional
        Y 轴标签，默认为空字符串（不显示 Y 轴标签）

    figsize : Tuple[int, int], optional
        图表尺寸（宽，高），单位为英寸，默认 (12, 8)

    colors : List[str], optional
        自定义颜色列表，每个元素为颜色代码（十六进制或颜色名）
        如果为 None，则使用模块默认的低饱和度柔和配色方案

    fontsize : int, optional
        坐标轴标签和刻度字体大小，默认为模块定义的 FONTSIZE

    large_fontsize : int, optional
        特殊场景下的大字体大小，默认为模块定义的 LARGE_FONTSIZE

    title_fontsize : int, optional
        标题字体大小，默认为模块定义的 TITLE_FONTSIZE

    label_rotation : float, optional
        X 轴标签旋转角度（度），默认 45 度以防止重叠

    y_max : float, optional
        Y 轴最大值，用于控制刻度范围
        如果为 None，则根据数据自动调整（起始点为 0）

    show_value_labels : bool, optional
        是否在柱体顶部显示数值标签，默认 True

    value_label_fontsize_offset : int, optional
        数值标签相对于基础字体大小的偏移量，默认 -2（略小于坐标轴字体）

    bar_width : float, optional
        柱体宽度，默认 0.6（适中宽度，疏密得当）

    bar_edge_color : str, optional
        柱体边框颜色，默认 "black"

    bar_edge_width : float, optional
        柱体边框线宽，默认 1.5

    bar_alpha : float, optional
        柱体透明度，默认 0.9（轻微透明）

    dpi : int, optional
        保存图片的分辨率，默认 300

    save_path : str, optional
        图片保存路径，如果为 None 则直接显示不保存

    返回:
    -----
    Tuple[plt.Figure, plt.Axes]
        返回 matplotlib 的 Figure 和 Axes 对象，便于后续操作

    示例:
    -----
    >>> # 示例 1：使用默认配色
    >>> data = [75.5, 82.3, 68.9, 91.2]
    >>> labels = ["A", "B", "C", "D"]
    >>> fig, ax = plot_ranked_first_rate(data, labels, title="示例图表", ylabel="百分比")

    >>> # 示例 2：自定义配色
    >>> colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33F5"]
    >>> fig, ax = plot_ranked_first_rate(data, labels, colors=colors)
    """
    
    # ==================== 参数验证与初始化 ====================
    # 验证数据长度匹配
    if len(data) != len(labels):
        raise ValueError(f"data 和 labels 长度必须一致：data 长度为 {len(data)}, labels 长度为 {len(labels)}")
    
    if len(data) == 0:
        raise ValueError("data 和 labels 不能为空")
    
    # 设置字体大小（使用默认值或传入值）
    fontsize = fontsize if fontsize is not None else FONTSIZE
    large_fontsize = large_fontsize if large_fontsize is not None else LARGE_FONTSIZE
    title_fontsize = title_fontsize if title_fontsize is not None else TITLE_FONTSIZE
    
    # 设置颜色方案
    if colors is None:
        colors = DEFAULT_SOFT_COLORS
    # 如果数据量超过预定义颜色数量，循环使用颜色
    if len(data) > len(colors):
        colors = (colors * ((len(data) // len(colors)) + 1))[:len(data)]
    
    # ==================== 创建图表 ====================
    # 创建画布和坐标轴
    fig, ax = plt.subplots(figsize=figsize)
    
    # 生成柱体位置
    x_pos = np.arange(len(labels))
    
    # ==================== 绘制柱体 ====================
    # 绘制垂直柱状图
    # 参考 EyeRAG 的 plot_ranked_first_ratio 函数风格
    bars = ax.bar(
        x_pos, 
        data, 
        width=bar_width, 
        color=colors, 
        alpha=bar_alpha,
        edgecolor=bar_edge_color, 
        linewidth=bar_edge_width
    )
    
    # ==================== 设置坐标轴 ====================
    # 设置 Y 轴标签
    ax.set_ylabel(ylabel, fontsize=fontsize)
    
    # 设置标题（如果有）
    if title:
        ax.set_title(title, fontsize=title_fontsize)
    
    # 设置 X 轴刻度和标签
    # 旋转 45 度以防止标签重叠，ha='center' 确保标签居中对齐
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=fontsize, rotation=label_rotation, ha='center')
    
    # 设置 Y 轴范围（起始点为 0）
    if y_max is not None:
        ax.set_ylim(0, y_max)
    else:
        # 自动调整 Y 轴上限，留出 10% 的空间用于显示数值标签
        max_value = max(data)
        ax.set_ylim(0, max_value * 1.15)
    
    # ==================== 设置图表边框样式 ====================
    # 简洁学术风格：仅保留左侧和底部坐标轴，隐藏顶部和右侧边框
    # 参考 EyeRAG 的 spines 设置方式
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # 设置左侧和底部边框为深灰色细实线
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    
    # ==================== 添加数值标签 ====================
    # 在每个柱体顶部居中显示具体的百分比数值（保留一位小数）
    if show_value_labels:
        value_label_fontsize = 16  # 统一字体大小 16pt
        for bar, value in zip(bars, data):
            height = bar.get_height()
            # 计算标签位置：柱体高度上方，留出 Y 轴范围 2.5% 的间距
            y_position = height + y_max * 0.025 if y_max else height + max(data) * 0.025
            # 在柱体顶部居中显示数值标签（保留一位小数）
            ax.text(
                bar.get_x() + bar.get_width() / 2.,  # X 坐标：柱体中心
                y_position,  # Y 坐标：柱体顶部上方
                f'{value:.1f}%',  # 显示格式：保留一位小数的百分比
                ha='center',  # 水平居中对齐
                va='bottom',  # 垂直底部对齐
                fontsize=value_label_fontsize,
                color='#333333'  # 深灰色字体
            )
    
    # ==================== 布局调整 ====================
    # 使用 tight_layout 确保布局疏密得当，避免标签被截断
    plt.tight_layout()
    
    # ==================== 保存或显示图表 ====================
    if save_path:
        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # 保存图表，使用 bbox_inches='tight' 确保内容完整
        plt.savefig(save_path, dpi=300, bbox_inches='tight', format='tiff')
        plt.close()
        print(f"图表已保存至：{os.path.abspath(save_path)}")
    else:
        plt.show()
    
    return fig, ax


def generate_test_data(
    num_categories: int = 5,
    value_range: Tuple[float, float] = (60.0, 95.0),
    label_prefix: str = "Category",
    seed: Optional[int] = None
) -> Tuple[List[float], List[str]]:
    """
    生成随机模拟测试数据

    本函数为测试辅助函数，用于生成随机数据以测试绘图函数。
    生产环境中应使用实际业务数据调用 plot_ranked_first_rate 函数。

    参数:
    -----
    num_categories : int, optional
        类别数量，默认 5

    value_range : Tuple[float, float], optional
        数值范围（最小值，最大值），默认 (60.0, 95.0)

    label_prefix : str, optional
        标签前缀，默认 "Category"

    seed : int, optional
        随机种子，用于复现结果

    返回:
    -----
    Tuple[List[float], List[str]]
        (数据列表，标签列表)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 生成随机百分比数据
    data = np.random.uniform(value_range[0], value_range[1], num_categories).tolist()
    # 生成类别标签
    labels = [f"{label_prefix} {chr(65 + i)}" for i in range(num_categories)]
    
    return data, labels


# ==================== 主函数入口 ====================
if __name__ == "__main__":
    # ==================== 构造随机测试数据 ====================
    print("Generating random test data...")
    test_data, test_labels = generate_test_data(
        num_categories=6,
        value_range=(65.0, 92.0),
        label_prefix="Method",
        seed=42  # Fixed seed for reproducibility
    )

    print(f"Test data: {test_data}")
    print(f"Test labels: {test_labels}")

    # ==================== 调用绘图函数 ====================
    print("\nGenerating chart...")

    # 定义输出路径
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "bar_chart_ranked_first_rate_test_en.tif")

    # 调用绘图函数生成图表（纯英文标签）
    # Note: All parameters are passed via function arguments
    fig, ax = plot_ranked_first_rate(
        data=test_data,
        labels=test_labels,
        title="Ranked First Rate Comparison",
        ylabel="Ranked First Rate (%)",
        figsize=(12, 8),
        fontsize=14,
        label_rotation=45,
        save_path=output_path,
        dpi=300
    )

    print(f"\nChart generated successfully!")
    print(f"Output path: {os.path.abspath(output_path)}")
