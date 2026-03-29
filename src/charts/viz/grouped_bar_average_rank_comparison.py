"""
分组柱状平均排名比较图 (Grouped Bar Average Rank Comparison)

本模块提供通用的分组柱状图绘图函数，用于展示多个模型/方法在不同评估维度下的平均排名比较。
图表采用简洁学术风格，白色背景，坐标轴仅保留左侧和底部边框。

参考仓库：https://github.com/OpenMedAILab/EyeRAG
参考文件：eye_rag/handle_results/rank_result_plot.py

使用示例:
    from src.visualization.grouped_bar_average_rank_comparison import plot_grouped_bar_average_rank_comparison

    # 准备数据 - 所有数据通过参数传入，函数本身不预置任何具体数据
    methods = ['Model A', 'Model B', 'Model C']
    series_data = [
        [1.5, 2.3, 3.1],  # 系列 1 数据
        [2.0, 1.8, 2.5],  # 系列 2 数据
    ]
    series_labels = ['Series 1', 'Series 2']

    # 调用绘图函数
    fig, ax = plot_grouped_bar_average_rank_comparison(
        methods=methods,
        series_data=series_data,
        series_labels=series_labels,
        series_colors=['#1a9988', '#a8b8d8'],
        save_path='output/grouped_bar_rank_comparison.png',
        title='Average Rank Comparison'
    )
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List, Optional, Tuple


# ============================================================================
# 全局常量配置 (参考 EyeRAG 仓库风格)
# ============================================================================

FONTSIZE = 16  # 基础字体大小
LARGE_FONTSIZE = 16  # 大字体大小（用于标题等）

# 默认颜色方案 - 深青绿色和淡蓝紫色
DEFAULT_SERIES_COLORS = [
    '#1a9988',  # 深青绿色 (Deep Teal Green) - 用于 Expert
    '#a8b8d8',  # 淡蓝紫色 (Light Blue Purple) - 用于 LLM-as-a-judge
]

# 默认图表尺寸
DEFAULT_FIGSIZE = (12, 7)

# 默认 Y 轴范围 (排名范围 0-6)
DEFAULT_YLIM = (0, 6)


# ============================================================================
# 核心绘图函数
# ============================================================================

def plot_grouped_bar_average_rank_comparison(
    methods: List[str],
    series_data: List[List[float]],
    series_labels: List[str],
    series_colors: Optional[List[str]] = None,
    figsize: Tuple[int, int] = DEFAULT_FIGSIZE,
    ylim: Tuple[int, int] = DEFAULT_YLIM,
    title: Optional[str] = None,
    ylabel: str = 'Average Rank',
    save_path: Optional[str] = None,
    dpi: int = 300,
    fontsize: int = FONTSIZE,
    large_fontsize: int = LARGE_FONTSIZE,
    bar_width: float = 0.30,
    intra_group_spacing: float = 0.0,
    inter_group_spacing: float = 0.5,
    show_value_labels: bool = True,
    value_label_format: str = '.2f',
    value_label_fontsize_offset: int = -2,
    legend_loc: str = 'upper left',
    legend_frameon: bool = False,
    legend_bbox_to_anchor: Optional[Tuple[float, float]] = None,
    x_tick_rotation: float = 45,
    draw_top_right_spines: bool = False,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    绘制分组柱状平均排名比较图。
    
    本函数创建一个学术风格的分组柱状图，用于比较不同模型/方法在多个评估维度下的平均排名。
    图表采用简洁设计：白色背景、仅保留左侧和底部坐标轴、柱体顶部显示数值标签。
    
    参数说明:
        methods (List[str]): 
            X 轴显示的模型/方法名称列表。
            例如：['EyeRAG', 'Hierarchical Index RAG', 'Naive RAG', 'Vanilla LLM']
            标签会自动旋转 45 度以防止重叠。
        
        series_data (List[List[float]]): 
            每个系列的排名数据列表。外层列表索引对应不同系列（如 Expert、LLM-as-a-judge），
            内层列表索引对应不同方法。每个内层列表长度必须与 methods 长度一致。
            例如：[[1.00, 2.50, 3.33, 4.67], [1.33, 2.00, 3.67, 5.00]]
        
        series_labels (List[str]): 
            每个系列的标签，用于图例显示。
            例如：['Expert', 'LLM-as-a-judge']
        
        series_colors (Optional[List[str]]): 
            每个系列的柱体颜色。如果为 None，使用默认颜色方案。
            颜色可以使用十六进制 (#RRGGBB)、RGB 元组或 matplotlib 支持的任何格式。
            默认：['#1a9988' (深青绿色), '#a8b8d8' (淡蓝紫色)]
        
        figsize (Tuple[int, int]): 
            图表尺寸 (宽度，高度)，单位为英寸。
            默认：(12, 7)
        
        ylim (Tuple[int, int]): 
            Y 轴显示范围 (最小值，最大值)。
            排名通常从 0 开始，最大值根据数据设定。
            默认：(0, 6)
        
        title (Optional[str]): 
            图表标题。如果为 None，不显示标题。
            默认：None
        
        ylabel (str): 
            Y 轴标签文本。
            默认：'Average Rank'
        
        save_path (Optional[str]): 
            图片保存路径。如果为 None，不保存图片，仅显示。
            路径目录会自动创建。
            默认：None
        
        dpi (int): 
            保存图片的分辨率 (dots per inch)。
            默认：300 (印刷质量)
        
        fontsize (int): 
            基础字体大小，用于坐标轴标签、刻度标签等。
            默认：16
        
        large_fontsize (int): 
            大字体大小，用于标题等需要强调的文本。
            默认：20
        
        bar_width (float):
            单个柱体的宽度。
            默认：0.30

        intra_group_spacing (float):
            组内间距参数，控制同一组内不同系列柱体之间的间隙。
            值越大，组内柱体间距越大。设为 0 时柱体紧挨着。
            默认：0.0

        inter_group_spacing (float):
            组间间距参数，控制不同方法组之间的间隙。
            值越大，组间空白越多。
            默认：0.5
        
        show_value_labels (bool): 
            是否在柱体顶部显示具体数值标签。
            默认：True
        
        value_label_format (str): 
            数值标签的格式化字符串。
            默认：'.2f' (保留两位小数，如 1.00)
        
        value_label_fontsize_offset (int): 
            数值标签字体大小相对于基础字体的偏移量。
            默认：-2 (比基础字体小 2 号)
        
        legend_loc (str): 
            图例位置。支持 matplotlib 的所有位置字符串。
            常用值：'upper left', 'upper right', 'lower left', 'lower right', 'best'
            默认：'upper left' (左上角)
        
        legend_frameon (bool): 
            是否显示图例边框。
            默认：False (无边框，简洁风格)
        
        legend_bbox_to_anchor (Optional[Tuple[float, float]]): 
            图例位置的精细调整参数，与 legend_loc 配合使用。
            如果为 None，使用默认位置。
            例如：(1.01, 1) 可将图例放置在图表外部右上角。
            默认：None
        
        x_tick_rotation (float): 
            X 轴刻度标签的旋转角度（度）。
            默认：45 (防止长标签重叠)
        
        draw_top_right_spines (bool): 
            是否绘制顶部和右侧坐标轴边框。
            学术风格通常设为 False 以获得更简洁的外观。
            默认：False
    
    返回:
        Tuple[plt.Figure, plt.Axes]: 
            返回 matplotlib 的 Figure 和 Axes 对象，可用于后续自定义修改。
    
    异常:
        ValueError: 当输入数据维度不匹配时抛出。
        RuntimeError: 当保存路径的目录无法创建时抛出。
    
    注意事项:
        1. series_data 中每个系列的长度必须与 methods 长度一致。
        2. series_data 的外层列表长度必须与 series_labels 和 series_colors (如果提供) 一致。
        3. 如果 save_path 指定的目录不存在，函数会自动创建。
        4. 数值标签会自动计算位置，确保在柱体顶部居中显示。
    
    示例:
        >>> methods = ['EyeRAG', 'Hierarchical Index RAG', 'Naive RAG', 'Vanilla LLM']
        >>> expert_ranks = [1.00, 2.50, 3.33, 4.67]
        >>> llm_ranks = [1.33, 2.00, 3.67, 5.00]
        >>> fig, ax = plot_grouped_bar_average_rank_comparison(
        ...     methods=methods,
        ...     series_data=[expert_ranks, llm_ranks],
        ...     series_labels=['Expert', 'LLM-as-a-judge'],
        ...     series_colors=['#1a9988', '#a8b8d8'],
        ...     title='Average Rank Comparison',
        ...     save_path='output/rank_comparison.png'
        ... )
    """
    # ========================================================================
    # 步骤 1: 数据验证
    # ========================================================================
    num_methods = len(methods)
    num_series = len(series_data)
    
    # 验证每个系列的数据长度是否与 methods 一致
    for i, series in enumerate(series_data):
        if len(series) != num_methods:
            raise ValueError(
                f"系列 {i} 的数据长度 ({len(series)}) 与 methods 长度 ({num_methods}) 不匹配"
            )
    
    # 验证 series_labels 长度
    if len(series_labels) != num_series:
        raise ValueError(
            f"series_labels 长度 ({len(series_labels)}) 与 series_data 长度 ({num_series}) 不匹配"
        )
    
    # 验证并设置颜色
    if series_colors is None:
        # 如果颜色数量不足，循环使用默认颜色
        series_colors = DEFAULT_SERIES_COLORS * ((num_series // len(DEFAULT_SERIES_COLORS)) + 1)
    series_colors = series_colors[:num_series]
    
    # ========================================================================
    # 步骤 2: 创建图表和坐标轴
    # ========================================================================
    fig, ax = plt.subplots(figsize=figsize)
    
    # ========================================================================
    # 步骤 3: 计算柱体位置并绘制分组柱状图
    # ========================================================================
    # x 轴位置：每个方法组的中心位置
    x_positions = np.arange(num_methods)

    # 计算每个系列在组内的偏移量
    # 使柱体在组内均匀分布，同一组内的柱体并排显示不重叠
    # 组内总宽度 = 所有柱体宽度 + 柱体之间的间隙
    intra_group_total_width = bar_width * num_series + intra_group_spacing * (num_series - 1)
    start_offset = -intra_group_total_width / 2 + bar_width / 2

    # 存储每个柱体对象，用于后续添加数值标签
    all_bars = []

    for series_idx, (series_values, color, label) in enumerate(
        zip(series_data, series_colors, series_labels)
    ):
        # 计算当前系列每个柱体的 x 位置
        # 每个系列柱体相对于组中心的偏移量
        offset = start_offset + series_idx * (bar_width + intra_group_spacing)
        x_current = x_positions + offset

        # 绘制柱体 - 使用纯色填充，无边框
        bars = ax.bar(
            x_current,
            series_values,
            width=bar_width,
            color=color,
            label=label,
            edgecolor='none',  # 无边框
            linewidth=0,
        )
        all_bars.append(bars)
    
    # ========================================================================
    # 步骤 4: 配置坐标轴
    # ========================================================================
    # 设置 Y 轴标签和范围
    ax.set_ylabel(ylabel, fontsize=fontsize, fontweight='bold')
    ax.set_ylim(ylim)

    # 设置 Y 轴刻度 - 清晰显示整数刻度
    y_ticks = list(range(ylim[0], ylim[1] + 1))
    ax.set_yticks(y_ticks)
    ax.tick_params(axis='y', labelsize=fontsize)

    # 设置 X 轴刻度和标签
    ax.set_xticks(x_positions)
    ax.set_xticklabels(
        methods,
        fontsize=fontsize,
        rotation=x_tick_rotation,
        ha='right',  # 右对齐，配合旋转角度
    )

    # 设置图表标题（如果提供）
    if title:
        ax.set_title(title, fontsize=fontsize, fontweight='bold', pad=15)
    
    # ========================================================================
    # 步骤 5: 配置坐标轴边框 (Spines)
    # ========================================================================
    # 学术风格：仅保留左侧和底部边框，隐藏顶部和右侧
    ax.spines['top'].set_visible(draw_top_right_spines)
    ax.spines['right'].set_visible(draw_top_right_spines)
    
    # 设置左侧和底部边框为深灰色细实线
    if not draw_top_right_spines:
        ax.spines['left'].set_color('#333333')
        ax.spines['left'].set_linewidth(0.8)
        ax.spines['bottom'].set_color('#333333')
        ax.spines['bottom'].set_linewidth(0.8)
    
    # ========================================================================
    # 步骤 6: 添加柱体顶部数值标签
    # ========================================================================
    if show_value_labels:
        value_label_fontsize = fontsize + value_label_fontsize_offset
        # 计算 Y 轴范围的 1% 作为标签与柱体顶部的间距
        y_margin = (ylim[1] - ylim[0]) * 0.01
        
        for bars in all_bars:
            for bar in bars:
                height = bar.get_height()
                # 标签位置：柱体顶部居中，略微上移
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + y_margin,
                    f'{height:{value_label_format}}',
                    ha='center',
                    va='bottom',
                    fontsize=value_label_fontsize,
                    fontweight='normal',
                )
    
    # ========================================================================
    # 步骤 7: 配置图例
    # ========================================================================
    # 准备图例参数
    legend_kwargs = {
        'loc': legend_loc,
        'frameon': legend_frameon,
        'fontsize': fontsize,
    }
    
    # 如果提供了 bbox_to_anchor，添加到图例配置
    if legend_bbox_to_anchor is not None:
        legend_kwargs['bbox_to_anchor'] = legend_bbox_to_anchor
    
    # 添加图例
    ax.legend(**legend_kwargs)
    
    # ========================================================================
    # 步骤 8: 调整布局并保存图片
    # ========================================================================
    # 自动调整布局，防止标签被截断
    plt.tight_layout()
    
    # 保存图片（如果指定了路径）
    if save_path:
        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"无法创建保存目录 '{save_dir}': {e}")
        
        # 保存图片
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        print(f"分组柱状图已保存至：{os.path.abspath(save_path)}")
    else:
        # 不保存图片，保持 Figure 打开状态以便显示
        pass
    
    return fig, ax


# ============================================================================
# 测试函数 - 示例数据演示
# ============================================================================

def run_test():
    """
    运行测试：使用示例数据生成分组柱状图并保存。

    此函数演示如何使用 plot_grouped_bar_average_rank_comparison 函数。
    所有数据在函数内部定义，仅作为使用示例，不包含任何预置业务逻辑。

    示例数据结构:
        - methods: 模型/方法名称列表
        - series_data: 每个系列的排名数据（嵌套列表）
        - series_labels: 系列标签（用于图例）

    异常:
        任何错误都会直接抛出，不会静默处理，便于调试。
    """
    # ================================================================
    # 示例数据 - 实际使用时请替换为您自己的数据
    # ================================================================

    # X 轴：模型/方法名称列表
    methods = [
        'EyeRAG',
        'Hierarchical Index RAG',
        'Naive RAG',
        'Hypothetical RAG',
        'Vanilla LLM',
    ]

    # Y 轴数据：每个系列的排名值
    # 外层列表索引 = 系列索引，内层列表索引 = 方法索引
    # 示例：series_data[0] 对应第一个系列（Expert）的所有方法排名
    series_data = [
        [1.00, 2.33, 3.50, 4.17, 5.00],   # 系列 1: Expert 评估
        [1.33, 2.00, 3.67, 4.33, 4.67],   # 系列 2: LLM-as-a-judge 评估
    ]

    # 系列标签：用于图例显示
    series_labels = ['Expert', 'LLM-as-a-judge']
    
    # 定义保存路径
    save_path = 'output/grouped_bar_average_rank_comparison_test.png'
    
    # 调用绘图函数
    fig, ax = plot_grouped_bar_average_rank_comparison(
        methods=methods,
        series_data=series_data,
        series_labels=series_labels,
        series_colors=['#1a9988', '#a8b8d8'],  # 深青绿色，淡蓝紫色
        figsize=(12, 7),
        ylim=(0, 6),
        title='Average Rank Comparison by Evaluation Method',
        ylabel='Average Rank (Lower is Better)',
        save_path=save_path,
        dpi=300,
        fontsize=FONTSIZE,
        large_fontsize=LARGE_FONTSIZE,
        bar_width=0.30,
        intra_group_spacing=0.0,
        inter_group_spacing=0.5,
        show_value_labels=True,
        value_label_format='.2f',
        legend_loc='upper left',
        legend_frameon=False,
        legend_bbox_to_anchor=None,  # 使用默认位置
        x_tick_rotation=45,
        draw_top_right_spines=False,
    )
    
    print(f"测试完成！图片已保存至：{os.path.abspath(save_path)}")
    
    return fig, ax


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == '__main__':
    # 运行测试
    fig, ax = run_test()
