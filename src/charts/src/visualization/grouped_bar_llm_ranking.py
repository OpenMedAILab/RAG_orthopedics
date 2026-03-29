"""
分组柱状图绘图模块

本模块提供通用的分组柱状图绘图函数，用于展示多组数据的对比。
图表采用学术简洁风格，支持完全参数化配置。

视觉风格特点:
- 白色背景，仅保留左侧和底部坐标轴
- Y 轴表示数值，刻度从 0 开始向上递增
- X 轴展示不同分组名称，标签旋转 45 度
- 每个分组包含多个不同颜色的柱体
- 图例位于图表右上角，无边框
- 标题可包含统计检验信息
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional, Tuple
from scipy import stats as scipy_stats


def plot_grouped_bar_chart(
    data: Dict[str, List[Tuple[str, float]]],
    categories: List[str],
    category_colors: Optional[Dict[str, str]] = None,
    category_display_names: Optional[Dict[str, str]] = None,
    title: Optional[str] = None,
    statistic_value: Optional[float] = None,
    p_value: Optional[float] = None,
    figsize: Tuple[float, float] = (12, 7),
    fontsize: int = 16,
    bar_width: float = 0.15,
    legend_location: str = 'upper right',
    save_path: Optional[str] = None,
    dpi: int = 300,
    color_palette: Optional[str] = None,
    ylabel: str = 'Value',
) -> None:
    """
    绘制通用分组柱状图

    参数说明:
    --------
    data : Dict[str, List[Tuple[str, float]]]
        分组数据字典，键为分组名称（X 轴标签），值为该分组内的数据列表。
        每个数据项为 (类别名，数值) 的元组。
        示例: {
            "Group_A": [("Category_1", 10.5), ("Category_2", 20.3)],
            "Group_B": [("Category_1", 15.2), ("Category_2", 18.7)],
        }

    categories : List[str]
        所有类别的名称列表，用于确定图例顺序和颜色分配。

    category_colors : Dict[str, str], optional
        类别名称到颜色的映射字典。如果未提供，将使用色板自动生成。
        示例: {"Category_1": "#1f77b4", "Category_2": "#2ca02c"}

    category_display_names : Dict[str, str], optional
        类别名称到显示名称的映射字典，用于图例显示。
        如果未提供，将直接使用 categories 中的名称。

    title : str, optional
        图表主标题。如果提供 statistic_value 和 p_value，将自动添加到标题中。

    statistic_value : float, optional
        统计检验值（如 Friedman 统计量），用于显示在标题中。

    p_value : float, optional
        统计检验 P 值，用于显示在标题中。

    figsize : Tuple[float, float], default=(12, 7)
        图表尺寸（宽，高），单位为英寸。

    fontsize : int, default=16
        基础字体大小，用于坐标轴标签、刻度等。

    bar_width : float, default=0.15
        柱体宽度，控制每个柱子的粗细。

    legend_location : str, default='upper right'
        图例位置，支持 matplotlib 的标准位置字符串。
        常用值：'upper right', 'upper left', 'lower right', 'lower left'

    save_path : str, optional
        图片保存路径。如果为 None，则直接显示图片而不保存。

    dpi : int, default=300
        保存图片时的分辨率（每英寸点数）。

    color_palette : str, optional
        matplotlib 色板名称，用于自动生成颜色。
        常用值：'Set1', 'Set2', 'Set3', 'tab10', 'tab20'
        如果未提供，使用默认的鲜明配色。

    ylabel : str, default='Value'
        Y 轴标签文本。

    返回:
    ----
    None
        直接显示或保存图片，不返回任何值。

    示例:
    ----
    >>> data = {
    ...     "Model_A": [("Method_1", 10.5), ("Method_2", 20.3)],
    ...     "Model_B": [("Method_1", 15.2), ("Method_2", 18.7)],
    ... }
    >>> categories = ["Method_1", "Method_2"]
    >>> plot_grouped_bar_chart(data, categories, title="Comparison")
    """
    # 如果未提供颜色映射，使用色板自动生成颜色
    if category_colors is None:
        # 选择色板
        if color_palette is not None:
            try:
                cmap = plt.colormaps.get_cmap(color_palette)
            except (ValueError, KeyError):
                # 如果色板名称无效，使用默认色板
                cmap = plt.colormaps.get_cmap('Set2')
        else:
            # 使用 Set2 色板作为默认（提供 8 种区分度好的颜色）
            cmap = plt.colormaps.get_cmap('Set2')

        # 生成颜色字典
        n_colors = len(categories)
        category_colors = {
            category: cmap(i % cmap.N) if hasattr(cmap, 'N') else cmap(i % 8)
            for i, category in enumerate(categories)
        }

    # 设置默认显示名称
    if category_display_names is None:
        category_display_names = {cat: cat for cat in categories}

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)

    # 获取所有分组名称和排序
    group_names = list(data.keys())
    n_groups = len(group_names)
    n_categories = len(categories)

    # 计算每个分组的中心位置
    group_width = 1.0  # 每个分组的总宽度
    group_spacing = 0.4  # 组间间距
    x_positions = []  # 存储每个分组的中心位置

    # 绘制每个分组的柱状图
    for group_idx, group_name in enumerate(group_names):
        group_data = data[group_name]

        # 将数据转换为字典便于查找
        data_dict = {cat: value for cat, value in group_data}

        # 计算当前分组内所有柱子的 x 位置
        # 柱子在分组内均匀分布
        group_center = group_idx * (group_width + group_spacing) + group_width / 2
        x_positions.append(group_center)

        # 计算分组内柱子的起始位置（使柱子在分组内居中）
        start_offset = -(n_categories - 1) * bar_width / 2

        # 绘制该分组内的每个类别的柱子
        for cat_idx, category in enumerate(categories):
            value = data_dict.get(category, 0)
            x = group_center + start_offset + cat_idx * bar_width

            # 绘制柱体
            ax.bar(
                x, value, bar_width,
                color=category_colors.get(category, '#999999'),
                edgecolor='black',
                linewidth=0.5,
                label=category_display_names.get(category, category) if group_idx == 0 else None
            )

    # 设置坐标轴标签和标题
    ax.set_ylabel(ylabel, fontsize=fontsize)

    # 构建完整标题
    full_title = title if title else ''
    if statistic_value is not None and p_value is not None:
        if full_title:
            full_title += '\n'
        # 根据 P 值大小格式化显示
        if p_value < 0.001:
            p_str = f'P-value<0.001'
        elif p_value < 0.01:
            p_str = f'P-value={p_value:.3f}'
        else:
            p_str = f'P-value={p_value:.3f}'
        full_title += f'(Statistic: {statistic_value:.2f}, {p_str})'

    if full_title:
        ax.set_title(full_title, fontsize=fontsize, fontweight='bold')

    # 设置 X 轴刻度和标签
    ax.set_xticks(x_positions)
    ax.set_xticklabels(group_names, rotation=45, ha='right', fontsize=fontsize)

    # 设置 Y 轴从 0 开始
    ax.set_ylim(bottom=0)
    ax.tick_params(axis='y', labelsize=fontsize)

    # 设置坐标轴样式：仅保留左侧和底部边框
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    # 设置坐标轴线颜色和宽度
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # 添加图例（无边框，放置在图表右侧外部）
    # 使用 bbox_to_anchor 将图例锚定到坐标轴外部右侧
    # bbox_to_anchor 的坐标是相对于坐标轴的，(1, 1) 表示坐标轴右上角
    ax.legend(
        loc='upper left',  # 图例内部的左上角对齐锚点
        bbox_to_anchor=(1.02, 1),  # 锚点在坐标轴右侧外部
        bbox_transform=ax.transAxes,  # 使用坐标轴坐标系
        fontsize=fontsize,
        frameon=False,  # 无边框
        ncol=1
    )

    # 调整布局，为右侧图例预留空间
    # right=0.75 表示图表区域占宽度的 75%，右侧 25% 留给图例
    plt.subplots_adjust(right=0.75)

    # 保存或显示图片
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def generate_test_data(
    n_groups: int = 6,
    group_names: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    value_range: Tuple[float, float] = (1.0, 5.0),
    seed: Optional[int] = None,
) -> Dict[str, List[Tuple[str, float]]]:
    """
    生成用于测试的随机分组数据

    参数说明:
    --------
    n_groups : int, default=6
        分组数量。如果提供了 group_names，则忽略此参数。

    group_names : List[str], optional
        分组名称列表。如果未提供，将自动生成 "Group_1", "Group_2", ...

    categories : List[str], optional
        类别名称列表。如果未提供，将自动生成 "Category_1", "Category_2", ...

    value_range : Tuple[float, float], default=(1.0, 5.0)
        数值的范围（最小值，最大值）。

    seed : int, optional
        随机数种子，用于生成可重复的测试数据。

    返回:
    ----
    Dict[str, List[Tuple[str, float]]]
        生成的测试数据，格式与 plot_grouped_bar_chart 的 data 参数相同。

    示例:
    ----
    >>> data = generate_test_data(n_groups=4, seed=42)
    >>> print(list(data.keys()))
    ['Group_1', 'Group_2', 'Group_3', 'Group_4']
    """
    if seed is not None:
        np.random.seed(seed)

    # 设置默认类别名称
    if categories is None:
        categories = [f"Category_{i+1}" for i in range(5)]

    # 设置默认分组名称
    if group_names is None:
        group_names = [f"Group_{i+1}" for i in range(n_groups)]

    # 生成随机数据
    data = {}
    for group_name in group_names:
        # 为每个类别生成随机数值
        values = np.random.uniform(value_range[0], value_range[1], len(categories))
        # 添加一些变化，使数据更真实
        values = np.round(values, 2)
        data[group_name] = [(cat, float(val)) for cat, val in zip(categories, values)]

    return data


def calculate_friedman_p_value(ranking_data: List[List[float]]) -> Tuple[Optional[float], Optional[float]]:
    """
    计算 Friedman 检验统计量和 P 值

    参数说明:
    --------
    ranking_data : List[List[float]]
        二维列表，每行代表一个分组，每列代表一个类别的数值。
        示例: [[1.5, 3.2, 2.1, 4.0, 5.0], [2.1, 2.8, 3.5, 3.0, 4.2], ...]

    返回:
    ----
    Tuple[float, float]
        (统计量，P 值) 的元组。如果计算失败，返回 (None, None)。

    注意:
    ----
    此函数需要 scipy 库支持。
    """
    try:
        data = np.array(ranking_data)
        if data.ndim != 2 or data.size == 0:
            raise ValueError("输入数据必须是非空的二维数组")

        num_groups = data.shape[1]
        if num_groups < 2:
            print("警告：Friedman 检验需要至少 2 个组进行比较")
            return None, None

        statistic, p_value = scipy_stats.friedmanchisquare(*data.T)
        return float(statistic), float(p_value)

    except ImportError as e:
        print(f"错误：需要安装 scipy 库来计算 Friedman 检验 (pip install scipy): {e}")
        return None, None
    except Exception as e:
        print(f"错误：计算 Friedman 检验时发生异常：{e}")
        return None, None


# 主程序：测试绘图功能
if __name__ == "__main__":
    # 设置随机种子以确保可重复性
    np.random.seed(42)

    # 定义类别列表（保持固定顺序）
    categories = [
        "Method_A",
        "Method_B",
        "Method_C",
        "Method_D",
        "Method_E",
    ]

    # 生成测试数据
    group_names = [
        "Group_1",
        "Group_2",
        "Group_3",
        "Group_4",
        "Group_5",
        "Group_6",
    ]

    data = generate_test_data(
        group_names=group_names,
        categories=categories,
        value_range=(1.0, 5.0),
        seed=42,
    )

    # 准备用于 Friedman 检验的数据
    # 需要将数据转换为二维数组格式（每行一个分组，每列一个类别）
    ranking_data = []
    for group_name in group_names:
        group_data = data[group_name]
        # 按照 categories 的顺序提取数值
        values = [value for cat, value in group_data]
        ranking_data.append(values)

    # 计算 Friedman 检验统计量和 P 值
    statistic, p_val = calculate_friedman_p_value(ranking_data)

    # 生成图片保存路径
    save_path = "grouped_bar_llm_ranking_test.png"

    # 绘制分组柱状图
    plot_grouped_bar_chart(
        data=data,
        categories=categories,
        title="Grouped Bar Chart Test",
        statistic_value=statistic,
        p_value=p_val,
        figsize=(12, 7),
        fontsize=16,
        bar_width=0.15,
        legend_location='upper right',
        save_path=save_path,
        dpi=300,
        ylabel='Rank (Lower is Better)',
    )

    print(f"图片已生成：{save_path}")
    print(f"Friedman 检验统计量：{statistic:.2f}")
    print(f"P 值：{p_val:.6f}")
