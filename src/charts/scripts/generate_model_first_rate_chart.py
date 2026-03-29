"""
模型首选率对比图表生成脚本

展示每个模型 RAG 获得第一名的百分比
X 轴：3 个模型名称
Y 轴：RAG First Place Rate (%)
"""

import os
import sys

# 添加父目录到路径以便导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

from visualization.bar_chart_with_errors import plot_bar_chart_with_errors
from data_processor import load_evaluation_data, process_model_first_rate


def main():
    # 文件路径
    excel_path = os.path.join(project_root, '模型评分.xlsx')
    output_dir = os.path.join(project_root, 'outputs')
    output_path = os.path.join(output_dir, 'bar_chart_model_first_rate.tif')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    print(f"Loading data from: {excel_path}")
    df = load_evaluation_data(excel_path)
    
    # 处理数据
    result = process_model_first_rate(df)
    
    print(f"\nModel First Rate Summary:")
    for i, model in enumerate(result['labels']):
        print(f"  {model}: {result['data'][i]:.1f}% ± {result['errors'][i]:.1f}%")
    
    print(f"\nRaw counts:")
    for model, counts in result['raw_data'].items():
        print(f"  {model}: RAG first={counts['RAG']}, Vanilla LLM first={counts['Vanilla LLM']}")
    
    # 生成图表
    print(f"\nGenerating chart...")
    
    fig, ax = plot_bar_chart_with_errors(
        data=result['data'],
        errors=result['errors'],
        labels=result['labels'],
        title='Ranking LLM: GPT-4o Mini, Grok 4 Fast, Gemini 3 Flash',
        y_label='Ranked First Rate',
        stat_annotation=None,
        value_labels=[f'{v:.1f}±{e:.1f}%' for v, e in zip(result['data'], result['errors'])],
        figsize=(12, 7),
        dpi=300,
        save_path=output_path,
        y_max=100,
        y_min=0,
    )


if __name__ == '__main__':
    main()
