"""
RAG vs Vanilla LLM Ranked First Rate 对比图表生成脚本

X 轴：RAG, Vanilla LLM
Y 轴：Ranked First Rate (%)
计算每个模式获得排名第一的频率
"""

import os
import sys

# 添加 charts 根目录到路径以便导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from viz.bar_chart_ranked_first_rate import plot_ranked_first_rate
from modules.data_processor import load_evaluation_data, process_ranked_first_rate


def main():
    # 文件路径
    excel_path = os.path.join(project_root, '模型评分.xlsx')
    output_dir = os.path.join(project_root, 'outputs')
    output_path = os.path.join(output_dir, 'bar_chart_ranked_first_rate.tif')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    print(f"Loading data from: {excel_path}")
    df = load_evaluation_data(excel_path)
    
    # 处理数据
    result = process_ranked_first_rate(df)
    
    print(f"\nRanked First Rate Summary:")
    print(f"  RAG:    {result['data'][0]:.1f}%")
    print(f"  Vanilla LLM: {result['data'][1]:.1f}%")
    
    # 生成图表
    print(f"\nGenerating chart...")
    
    fig, ax = plot_ranked_first_rate(
        data=result['data'],
        labels=result['labels'],
        title='Ranking LLM: GPT-4o Mini, Grok 4 Fast, Gemini 3 Flash',
        ylabel='Ranked First Rate',
        colors=['#1a9988', '#a8b8d8'],
        y_max=100,
        show_value_labels=True,
        value_label_fontsize_offset=-2,
        label_rotation=0,
        figsize=(10, 7),
        dpi=300,
        save_path=output_path,
    )
    
    print(f"\nRanked First Rate Summary:")
    print(f"  RAG:    {result['data'][0]:.1f}% ± {result['errors'][0]:.1f}%")
    print(f"  Vanilla LLM: {result['data'][1]:.1f}% ± {result['errors'][1]:.1f}%")
    print(f"  Total cases: {result['sample_sizes'][0]}")


if __name__ == '__main__':
    main()
