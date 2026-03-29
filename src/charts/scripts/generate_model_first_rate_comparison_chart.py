"""
模型首选率对比图表生成脚本（RAG vs Vanilla LLM）

展示每个模型 RAG 和 Vanilla LLM 获得第一名的百分比
X 轴：3 个模型名称
Y 轴：First Place Rate (%)
每个模型有两个柱体：RAG 和 Vanilla LLM
"""

import os
import sys

# 添加 charts 根目录到路径以便导入模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from viz.grouped_bar_with_errors import plot_grouped_bar_with_errors
from modules.data_processor import load_evaluation_data


def process_model_first_rate_comparison(df):
    """处理每个模型 RAG 和 Vanilla LLM 获得第一名的百分比统计"""
    import numpy as np
    
    score_keywords = ['医学准确性', '关键要点召回率', '逻辑完整性']
    evaluators = ['GPT', 'Gemini', 'Grok']
    
    model_name_map = {
        'GPT': 'GPT-4o Mini',
        'Gemini': 'Gemini 3 Flash',
        'Grok': 'Grok 4 Fast'
    }

    model_first_counts = {
        'GPT-4o Mini': {'RAG': 0, 'Vanilla LLM': 0},
        'Grok 4 Fast': {'RAG': 0, 'Vanilla LLM': 0},
        'Gemini 3 Flash': {'RAG': 0, 'Vanilla LLM': 0}
    }
    
    total_cases = 40
    
    for (case_id, model), group_df in df.groupby(['病例号', '被评估模型']):
        mapped_model = model_name_map.get(model, model)
        
        rag_score = None
        vanilla_score = None
        
        for idx, row in group_df.iterrows():
            mode = row['模式']
            
            all_scores = []
            for evaluator in evaluators:
                for keyword in score_keywords:
                    for col in row.index:
                        if col.startswith(evaluator) and keyword in col:
                            all_scores.append(row[col])
                            break
            
            if all_scores:
                avg_score = np.mean(all_scores)
                if mode == 'RAG':
                    rag_score = avg_score
                elif mode == 'No-RAG':
                    vanilla_score = avg_score
        
        if rag_score is not None and vanilla_score is not None:
            if rag_score >= vanilla_score:
                model_first_counts[mapped_model]['RAG'] += 1
            else:
                model_first_counts[mapped_model]['Vanilla LLM'] += 1
    
    models = ['GPT-4o Mini', 'Grok 4 Fast', 'Gemini 3 Flash']
    result_data = {}
    result_errors = {}
    
    for model in models:
        counts = model_first_counts[model]
        
        rag_rate = (counts['RAG'] / total_cases) * 100
        p_rag = rag_rate / 100
        rag_std = np.sqrt(p_rag * (1 - p_rag) / total_cases) * 100
        
        vanilla_rate = (counts['Vanilla LLM'] / total_cases) * 100
        p_vanilla = vanilla_rate / 100
        vanilla_std = np.sqrt(p_vanilla * (1 - p_vanilla) / total_cases) * 100
        
        result_data[model] = {'RAG': rag_rate, 'Vanilla LLM': vanilla_rate}
        result_errors[model] = {'RAG': rag_std, 'Vanilla LLM': vanilla_std}
    
    return {
        'models': models,
        'data': result_data,
        'errors': result_errors,
        'raw_data': model_first_counts
    }


def main():
    excel_path = os.path.join(project_root, '模型评分.xlsx')
    output_dir = os.path.join(project_root, 'outputs')
    output_path = os.path.join(output_dir, 'bar_chart_model_first_rate_comparison.tif')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading data from: {excel_path}")
    df = load_evaluation_data(excel_path)
    
    result = process_model_first_rate_comparison(df)

    # 使用固定模型顺序：GPT, Grok, Gemini
    sorted_models = ['GPT-4o Mini', 'Grok 4 Fast', 'Gemini 3 Flash']

    print(f"\nModel First Rate Comparison Summary:")
    for model in sorted_models:
        rag_rate = result['data'][model]['RAG']
        rag_std = result['errors'][model]['RAG']
        vanilla_rate = result['data'][model]['Vanilla LLM']
        vanilla_std = result['errors'][model]['Vanilla LLM']
        print(f"  {model}: RAG={rag_rate:.1f}%±{rag_std:.1f}%, Vanilla LLM={vanilla_rate:.1f}%±{vanilla_std:.1f}%")
    
    print(f"\nGenerating chart...")
    
    # 创建排序后的数据字典
    sorted_data = {m: result['data'][m] for m in sorted_models}
    sorted_errors = {m: result['errors'][m] for m in sorted_models}
    
    fig, ax = plot_grouped_bar_with_errors(
        data=sorted_data,
        errors=sorted_errors,
        categories=['RAG', 'Vanilla LLM'],
        title='Ranking LLM: GPT-4o Mini, Grok 4 Fast, Gemini 3 Flash',
        y_label='Ranked First Rate',
        category_colors={
            'RAG': '#1a9988',
            'Vanilla LLM': '#a8b8d8',
        },
        figsize=(12, 9),  # 增加高度避免图例重叠
        fontsize=16,
        bar_width=0.33,  # 柱状图宽度再加 10%
        save_path=output_path,
        dpi=300,
        y_max=100,
        y_min=0,
        show_value_labels=True,
    )
    
    print(f"Chart saved to: {output_path}")


if __name__ == '__main__':
    main()
