"""
三维度排名雷达图生成脚本

展示 2 条线：RAG 和 Vanilla LLM
每个维度的分数 = 该维度下所有模型和所有评估者评分的平均值

三个维度：
- Medical Accuracy (医学准确性)
- Key Point Recall (关键要点召回率)
- Logical Completeness (逻辑完整性)
"""

import os
import sys
import numpy as np

# 添加 charts 根目录到路径以便导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from viz.radar_chart_average_rank import plot_radar_chart_average_rank
from modules.data_processor import load_evaluation_data, process_three_dimension_ranks


def main():
    # 文件路径
    excel_path = os.path.join(project_root, '模型评分.xlsx')
    output_dir = os.path.join(project_root, 'outputs')
    output_path = os.path.join(output_dir, 'radar_chart_average_rank.tif')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    print(f"Loading data from: {excel_path}")
    df = load_evaluation_data(excel_path)
    
    # 处理数据
    result = process_three_dimension_ranks(df)
    
    print(f"\nDimensions: {result['dimensions']}")
    print(f"\nScores by Mode:")
    for key, scores in result['data'].items():
        print(f"  {key}: {scores}")
    
    # 计算 Y 轴范围：固定 0-9
    y_min = 0
    y_max = 9

    # 生成刻度（整数刻度：0, 1, 2, ..., 9）
    y_ticks = list(range(int(y_min), int(y_max) + 1))
    
    print(f"\nY-axis range: {y_min:.1f}-{y_max:.1f}, ticks: {y_ticks}")
    
    # 生成图表
    print(f"\nGenerating chart...")
    
    # 定义 2 种颜色
    colors = [
        '#1a9988',  # RAG: 深青绿色
        '#a8b8d8',  # Vanilla LLM: 淡蓝紫色
    ]
    
    fig, ax = plot_radar_chart_average_rank(
        data=result['data'],
        dimensions=result['dimensions'],
        title='Ranking LLM: GPT-4o Mini, Grok 4 Fast, Gemini 3 Flash',
        save_path=output_path,
        figsize=(10, 10),
        colors=colors,
        line_width=2.5,
        alpha_fill=0.15,
        alpha_line=0.9,
        show_legend=True,
        legend_ncol=2,
        legend_fontsize=16,
        dimension_fontsize=16,
        tick_fontsize=16,
        title_fontsize=18,
        y_min=y_min,
        y_max=y_max,
        y_ticks=y_ticks,
        grid_alpha=0.25,
        grid_linewidth=1.5,
        radial_grid_linewidth=1.0,
        dpi=300,
    )
    
    print(f"Chart saved to: {output_path}")


if __name__ == '__main__':
    main()
