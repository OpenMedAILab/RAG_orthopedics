"""
数据处理模块

用于处理 RAG 评估结果 Excel 文件，提取和计算统计数据。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def load_evaluation_data(excel_path: str) -> pd.DataFrame:
    """加载评估结果 Excel 文件"""
    return pd.read_excel(excel_path)


def calculate_avg_score(row: pd.Series, evaluator: str) -> float:
    """计算指定评估者的平均分数（三个维度的平均）"""
    # 列名格式：Gemini-医学准确性 [1-10 分] (无空格)
    # 动态查找列名
    suffixes = ['-医学准确性 [1-10 分]', '-关键要点召回率 [1-10 分]', '-逻辑完整性 [1-10 分]']
    scores = []
    for suffix in suffixes:
        col_name = f'{evaluator}{suffix}'
        if col_name in row.index:
            scores.append(row[col_name])
        else:
            # 尝试其他可能的格式
            for col in row.index:
                if col.startswith(evaluator) and suffix.replace(' [', '[').replace(']', ']') in col:
                    scores.append(row[col])
                    break
    return sum(scores) / len(scores) if scores else 0.0


def extract_ranks_by_mode(df: pd.DataFrame) -> Dict[str, List[float]]:
    """
    从评估数据中提取 RAG 和 No-RAG 模式下的排名数据
    
    排名计算方式：
    - 对每个病例号，根据被评估模型的对应评估者分数计算平均排名
    - 使用被评估模型对应的评估者分数
    
    返回:
        {'RAG': [排名列表], 'No-RAG': [排名列表]}
    """
    mode_ranks = {'RAG': [], 'No-RAG': []}
    
    # 按病例号分组
    for case_id, case_df in df.groupby('病例号'):
        # 对每个病例中的每个回答计算排名
        ranks_in_case = []
        for idx, row in case_df.iterrows():
            model = row['被评估模型']
            mode = row['模式']
            # 使用对应评估者的分数
            score = calculate_avg_score(row, model)
            ranks_in_case.append({
                'model': model,
                'mode': mode,
                'score': score
            })
        
        # 按分数排序，分数越高排名越靠前（排名数值越小）
        ranks_in_case.sort(key=lambda x: -x['score'])
        
        # 分配排名（1-6）
        for rank, item in enumerate(ranks_in_case, 1):
            mode_ranks[item['mode']].append(rank)
    
    return mode_ranks


def extract_ranked_first_rate(df: pd.DataFrame) -> Dict[str, List[int]]:
    """
    从评估数据中提取 RAG 和 No-RAG 模式下的首选率数据
    
    首选率计算方式：
    - 对每个病例号，比较 RAG 和 No-RAG 的平均分数
    - 分数高的模式获得 1 分（排名第一），否则为 0
    
    返回:
        {'RAG': [0/1 列表], 'No-RAG': [0/1 列表]}
    """
    mode_first_counts = {'RAG': [], 'No-RAG': []}
    
    # 按病例号分组
    for case_id, case_df in df.groupby('病例号'):
        # 计算 RAG 和 No-RAG 的平均分数
        rag_scores = []
        norag_scores = []
        
        for idx, row in case_df.iterrows():
            model = row['被评估模型']
            mode = row['模式']
            score = calculate_avg_score(row, model)
            
            if mode == 'RAG':
                rag_scores.append(score)
            else:
                norag_scores.append(score)
        
        rag_avg = np.mean(rag_scores) if rag_scores else 0
        norag_avg = np.mean(norag_scores) if norag_scores else 0
        
        # 分配第一名
        if rag_avg >= norag_avg:
            # RAG 第一
            for _ in range(len(rag_scores)):
                mode_first_counts['RAG'].append(1)
            for _ in range(len(norag_scores)):
                mode_first_counts['No-RAG'].append(0)
        else:
            # No-RAG 第一
            for _ in range(len(rag_scores)):
                mode_first_counts['RAG'].append(0)
            for _ in range(len(norag_scores)):
                mode_first_counts['No-RAG'].append(1)
    
    return mode_first_counts


def extract_ranks_by_model_and_mode(df: pd.DataFrame) -> Dict[str, Dict[str, List[int]]]:
    """
    从评估数据中提取每个模型在 RAG 和 No-RAG 模式下的排名数据
    
    排名计算逻辑：
    - 对每个病例号，每个模型有 2 个回答（RAG 和 No-RAG）
    - 对每个模型内的 2 个回答进行排名（1 或 2），1 为最好
    
    返回:
        {
            'Gemini': {'RAG': [ranks], 'No-RAG': [ranks]},
            'GPT': {'RAG': [ranks], 'No-RAG': [ranks]},
            ...
        }
    """
    model_mode_ranks = {}
    
    # 按病例号分组
    for case_id, case_df in df.groupby('病例号'):
        # 按模型分组
        for model, model_df in case_df.groupby('被评估模型'):
            if model not in model_mode_ranks:
                model_mode_ranks[model] = {'RAG': [], 'No-RAG': []}
            
            # 计算该模型内 RAG 和 No-RAG 的分数
            rag_score = None
            norag_score = None
            
            for idx, row in model_df.iterrows():
                mode = row['模式']
                score = calculate_avg_score(row, model)
                
                if mode == 'RAG':
                    rag_score = score
                else:
                    norag_score = score
            
            # 分配排名（1=最好，2=较差）
            if rag_score is not None and norag_score is not None:
                if rag_score >= norag_score:
                    rag_rank = 1
                    norag_rank = 2
                else:
                    rag_rank = 2
                    norag_rank = 1
                
                # 找到对应的行并添加排名
                for idx, row in model_df.iterrows():
                    mode = row['模式']
                    if mode == 'RAG':
                        model_mode_ranks[model]['RAG'].append(rag_rank)
                    else:
                        model_mode_ranks[model]['No-RAG'].append(norag_rank)
    
    return model_mode_ranks


def calculate_statistics(values: List[float]) -> Tuple[float, float]:
    """计算平均值和标准差"""
    if not values:
        return 0.0, 0.0
    arr = np.array(values)
    return float(np.mean(arr)), float(np.std(arr))


def calculate_ranked_first_rate(values: List[int]) -> Tuple[float, float]:
    """计算首选率（百分比形式）"""
    if not values:
        return 0.0, 0.0
    arr = np.array(values)
    rate = np.mean(arr) * 100
    std = np.std(arr) * 100
    return float(rate), float(std)


def process_rag_comparison(df: pd.DataFrame) -> dict:
    """
    处理 RAG vs Vanilla LLM 对比数据（平均排名）
    
    排名计算方式：
    - 对每个病例，计算 RAG 和 Vanilla LLM 的总分（三个维度之和）
    - 根据总分对每个病例内的 RAG 和 Vanilla LLM 进行排名
    - 最后计算所有病例中 RAG 和 Vanilla LLM 的平均排名和标准差
    
    返回:
        {
            'labels': ['RAG', 'Vanilla LLM'],
            'data': [rag_mean_rank, norag_mean_rank],
            'errors': [rag_std, norag_std],
            'sample_sizes': [rag_n, norag_n]
        }
    """
    mode_ranks = {'RAG': [], 'Vanilla LLM': []}
    
    # 维度关键词
    dim_keywords = ['医学准确性', '关键要点召回率', '逻辑完整性']
    
    # 按病例号分组
    for case_id, case_df in df.groupby('病例号'):
        # 计算每个模式的总分
        mode_scores = {'RAG': [], 'Vanilla LLM': []}
        
        for idx, row in case_df.iterrows():
            model = row['被评估模型']
            mode = row['模式']
            
            # 将 No-RAG 映射为 Vanilla LLM
            if mode == 'No-RAG':
                mode = 'Vanilla LLM'
            
            if mode not in mode_scores:
                continue
            
            # 计算该回答的总分（三个维度之和）
            total_score = 0
            for keyword in dim_keywords:
                for col in row.index:
                    if col.startswith(model) and keyword in col:
                        total_score += row[col]
                        break
            
            mode_scores[mode].append(total_score)
        
        # 计算每个模式的平均总分
        rag_total = np.mean(mode_scores['RAG']) if mode_scores['RAG'] else 0
        norag_total = np.mean(mode_scores['Vanilla LLM']) if mode_scores['Vanilla LLM'] else 0
        
        # 分配排名（总分高的排名为 1，低的为 2）
        if rag_total >= norag_total:
            rag_rank = 1
            norag_rank = 2
        else:
            rag_rank = 2
            norag_rank = 1
        
        # 为该病例的每个回答分配排名
        for _ in mode_scores['RAG']:
            mode_ranks['RAG'].append(rag_rank)
        for _ in mode_scores['Vanilla LLM']:
            mode_ranks['Vanilla LLM'].append(norag_rank)
    
    rag_mean, rag_std = calculate_statistics(mode_ranks['RAG'])
    norag_mean, norag_std = calculate_statistics(mode_ranks['Vanilla LLM'])
    
    return {
        'labels': ['RAG', 'Vanilla LLM'],
        'data': [rag_mean, norag_mean],
        'errors': [rag_std, norag_std],
        'sample_sizes': [len(mode_ranks['RAG']), len(mode_ranks['Vanilla LLM'])],
        'raw_data': mode_ranks
    }


def process_ranked_first_rate(df: pd.DataFrame) -> dict:
    """
    处理 Ranked First Rate 对比数据
    
    计算方式：
    - 对每个病例，计算 RAG 和 Vanilla LLM 的总分
    - 总分高的模式获得第 1 名
    - 统计所有病例中每个模式获得第 1 名的频率（百分比）
    
    返回:
        {
            'labels': ['RAG', 'Vanilla LLM'],
            'data': [rag_first_rate, norag_first_rate],  # 百分比
            'errors': [rag_std, norag_std],  # 百分比标准差
            'sample_sizes': [rag_n, norag_n]
        }
    """
    # 维度关键词
    dim_keywords = ['医学准确性', '关键要点召回率', '逻辑完整性']
    
    # 统计每个模式获得第 1 名的次数
    rag_first_count = 0
    norag_first_count = 0
    total_cases = 0
    
    # 按病例号分组
    for case_id, case_df in df.groupby('病例号'):
        # 计算每个模式的总分
        mode_scores = {'RAG': [], 'Vanilla LLM': []}
        
        for idx, row in case_df.iterrows():
            model = row['被评估模型']
            mode = row['模式']
            
            # 将 No-RAG 映射为 Vanilla LLM
            if mode == 'No-RAG':
                mode = 'Vanilla LLM'
            
            if mode not in mode_scores:
                continue
            
            # 计算该回答的总分
            total_score = 0
            for keyword in dim_keywords:
                for col in row.index:
                    if col.startswith(model) and keyword in col:
                        total_score += row[col]
                        break
            
            mode_scores[mode].append(total_score)
        
        # 计算每个模式的平均总分
        rag_total = np.mean(mode_scores['RAG']) if mode_scores['RAG'] else 0
        norag_total = np.mean(mode_scores['Vanilla LLM']) if mode_scores['Vanilla LLM'] else 0
        
        # 分配第 1 名
        if rag_total >= norag_total:
            rag_first_count += 1
        else:
            norag_first_count += 1
        
        total_cases += 1
    
    # 计算频率（百分比）
    rag_rate = (rag_first_count / total_cases) * 100 if total_cases > 0 else 0
    norag_rate = (norag_first_count / total_cases) * 100 if total_cases > 0 else 0
    
    # 计算标准差（二项分布）
    rag_std = np.sqrt(rag_rate * (100 - rag_rate) / total_cases) if total_cases > 0 else 0
    norag_std = np.sqrt(norag_rate * (100 - norag_rate) / total_cases) if total_cases > 0 else 0
    
    return {
        'labels': ['RAG', 'Vanilla LLM'],
        'data': [rag_rate, norag_rate],
        'errors': [rag_std, norag_std],
        'sample_sizes': [total_cases, total_cases],
        'raw_data': {'rag_first_count': rag_first_count, 'norag_first_count': norag_first_count, 'total_cases': total_cases}
    }


def process_llm_ranking(df: pd.DataFrame) -> dict:
    """
    处理每个模型的 RAG 和 Vanilla LLM 排名数据
    
    排名规则：
    - 对每一行，计算 9 个打分列的平均分（3 个评估者 × 3 个维度）
    - 对每个病例的每个模型，比较 RAG 和 Vanilla LLM 的平均分
    - 分数高的排名为 1，低的为 2
    - 统计每个模型在所有病例中的排名均值和标准差
    
    返回:
        {
            'models': ['GPT-4o Mini', 'Grok 4 Fast', 'Gemini 3 Flash'],
            'data': {
                'GPT-4o Mini': {'RAG': mean_rank, 'Vanilla LLM': mean_rank},
                ...
            },
            'errors': {
                'GPT-4o Mini': {'RAG': std, 'Vanilla LLM': std},
                ...
            }
        }
    """
    # 9 个打分列的关键词
    score_keywords = [
        '医学准确性', '关键要点召回率', '逻辑完整性'
    ]
    evaluators = ['GPT', 'Gemini', 'Grok']
    
    # 模型名称映射
    model_name_map = {
        'GPT': 'GPT-4o Mini',
        'Gemini': 'Gemini 3 Flash',
        'Grok': 'Grok 4 Fast'
    }
    
    # 按模型收集排名
    model_ranks = {
        'GPT-4o Mini': {'RAG': [], 'Vanilla LLM': []},
        'Gemini 3 Flash': {'RAG': [], 'Vanilla LLM': []},
        'Grok 4 Fast': {'RAG': [], 'Vanilla LLM': []}
    }
    
    # 按病例号和模型分组
    for (case_id, model), group_df in df.groupby(['病例号', '被评估模型']):
        # 映射模型名称
        mapped_model = model_name_map.get(model, model)
        
        if mapped_model not in model_ranks:
            continue
        
        # 计算该模型在该病例中 RAG 和 Vanilla LLM 的平均分
        rag_scores = []
        norag_scores = []
        
        for idx, row in group_df.iterrows():
            mode = row['模式']
            
            # 将 No-RAG 映射为 Vanilla LLM
            if mode == 'No-RAG':
                mode = 'Vanilla LLM'
            
            # 计算 9 个打分的平均分
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
                    rag_scores.append(avg_score)
                elif mode == 'Vanilla LLM':
                    norag_scores.append(avg_score)
        
        # 计算 RAG 和 Vanilla LLM 的总分/平均分
        rag_total = np.mean(rag_scores) if rag_scores else 0
        norag_total = np.mean(norag_scores) if norag_scores else 0
        
        # 分配排名（分数高的排名为 1，低的为 2）
        if rag_total >= norag_total:
            rag_rank = 1
            norag_rank = 2
        else:
            rag_rank = 2
            norag_rank = 1
        
        model_ranks[mapped_model]['RAG'].append(rag_rank)
        model_ranks[mapped_model]['Vanilla LLM'].append(norag_rank)
    
    # 计算每个模型的均值和标准差
    result_data = {}
    result_errors = {}
    
    for model, modes in model_ranks.items():
        result_data[model] = {}
        result_errors[model] = {}
        for mode, ranks in modes.items():
            if ranks:
                result_data[model][mode] = float(np.mean(ranks))
                result_errors[model][mode] = float(np.std(ranks))
            else:
                result_data[model][mode] = 0.0
                result_errors[model][mode] = 0.0
    
    return {
        'models': sorted(result_data.keys()),
        'data': result_data,
        'errors': result_errors,
        'raw_data': model_ranks
    }


def process_model_first_rate(df: pd.DataFrame) -> dict:
    """
    处理每个模型 RAG 获得第一名的百分比统计
    
    计算方式：
    - 对每个模型，统计在 40 个病例中 RAG 获得第 1 名的次数
    - 计算每个模型的 RAG 第一名百分比
    - 返回每个模型的独立百分比（不计算平均）
    
    返回:
        {
            'labels': ['GPT-4o Mini', 'Grok 4 Fast', 'Gemini 3 Flash'],
            'data': [rag_rate_gpt, rag_rate_grok, rag_rate_gemini],
            'errors': [0, 0, 0]  # 占位，每个模型独立统计无误差
        }
    """
    # 9 个打分列的关键词
    score_keywords = [
        '医学准确性', '关键要点召回率', '逻辑完整性'
    ]
    evaluators = ['GPT', 'Gemini', 'Grok']

    # 模型名称映射
    model_name_map = {
        'GPT': 'GPT-4o Mini',
        'Gemini': 'Gemini 3 Flash',
        'Grok': 'Grok 4 Fast'
    }

    # 按模型统计 RAG 获得第 1 名的次数
    model_first_counts = {
        'GPT-4o Mini': {'RAG': 0, 'Vanilla LLM': 0},
        'Grok 4 Fast': {'RAG': 0, 'Vanilla LLM': 0},
        'Gemini 3 Flash': {'RAG': 0, 'Vanilla LLM': 0}
    }
    
    # 按病例号和模型分组
    for (case_id, model), group_df in df.groupby(['病例号', '被评估模型']):
        # 映射模型名称
        mapped_model = model_name_map.get(model, model)
        
        # 计算该模型在该病例中 RAG 和 Vanilla LLM 的平均分
        rag_score = None
        vanilla_score = None
        
        for idx, row in group_df.iterrows():
            mode = row['模式']
            
            # 计算 9 个打分的平均分
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
        
        # 分配第 1 名（每个模型在每个病例中独立比较）
        if rag_score is not None and vanilla_score is not None:
            if rag_score >= vanilla_score:
                model_first_counts[mapped_model]['RAG'] += 1
            else:
                model_first_counts[mapped_model]['Vanilla LLM'] += 1
    
    # 计算每个模型的 RAG 第一名百分比（40 个病例）
    total_cases = 40
    labels = []
    data = []
    errors = []

    for model in ['GPT-4o Mini', 'Grok 4 Fast', 'Gemini 3 Flash']:
        counts = model_first_counts[model]
        rag_rate = (counts['RAG'] / total_cases) * 100

        # 计算二项分布标准差：sqrt(p*(100-p)/n)
        p = rag_rate / 100
        rag_std = np.sqrt(p * (1 - p) / total_cases) * 100

        labels.append(model)
        data.append(rag_rate)
        errors.append(rag_std)

    return {
        'labels': labels,
        'data': data,
        'errors': errors,  # 每个模型的二项分布标准差
        'raw_data': model_first_counts
    }


def process_three_dimension_ranks(df: pd.DataFrame) -> dict:
    """
    处理三个评估维度的排名数据（用于雷达图）
    
    展示 2 条线：RAG 和 Vanilla LLM
    每个维度的分数 = 该维度下所有模型和所有评估者评分的平均值
    
    三个维度：
    - medical_accuracy: 医学准确性
    - key_point_recall: 关键要点召回率
    - logical_completeness: 逻辑完整性
    
    返回:
        {
            'dimensions': ['Medical Accuracy', 'Key Point Recall', 'Logical Completeness'],
            'data': {
                'RAG': [score1, score2, score3],
                'Vanilla LLM': [score1, score2, score3]
            }
        }
    """
    # 维度关键词
    dim_keywords = [
        ('medical_accuracy', '医学准确性'),
        ('key_point_recall', '关键要点召回率'),
        ('logical_completeness', '逻辑完整性')
    ]
    
    # 评估者
    evaluators = ['GPT', 'Gemini', 'Grok']
    
    # 按模式收集分数
    mode_scores = {
        'RAG': {dim: [] for dim, _ in dim_keywords},
        'Vanilla LLM': {dim: [] for dim, _ in dim_keywords}
    }
    
    # 遍历每一行数据
    for idx, row in df.iterrows():
        model = row['被评估模型']
        mode = row['模式']
        
        # 将 No-RAG 映射为 Vanilla LLM
        if mode == 'No-RAG':
            mode = 'Vanilla LLM'
        
        if mode not in mode_scores:
            continue
        
        # 计算每个维度的分数（所有评估者的平均）
        for dim_en, dim_cn in dim_keywords:
            scores = []
            for evaluator in evaluators:
                for col in row.index:
                    if col.startswith(evaluator) and dim_cn in col:
                        scores.append(row[col])
                        break
            
            if scores:
                mode_scores[mode][dim_en].append(np.mean(scores))
    
    # 计算每个维度的最终平均分
    dimension_names = ['Medical\nAccuracy', 'Key Point\nRecall', 'Logical\nCompleteness']
    data = {}
    
    for mode in ['RAG', 'Vanilla LLM']:
        data[mode] = []
        for dim_en, dim_cn in dim_keywords:
            if mode_scores[mode][dim_en]:
                data[mode].append(np.mean(mode_scores[mode][dim_en]))
            else:
                data[mode].append(0)
    
    return {
        'dimensions': dimension_names,
        'data': data,
    }


if __name__ == '__main__':
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    excel_path = os.path.join(project_root, '模型评分.xlsx')
    
    df = load_evaluation_data(excel_path)
    print(f"加载数据：{len(df)} 行")
    
    print("\n=== RAG vs No-RAG Comparison (Average Rank) ===")
    result = process_rag_comparison(df)
    print(f"  RAG:    mean={result['data'][0]:.2f}, std={result['errors'][0]:.2f}, n={result['sample_sizes'][0]}")
    print(f"  No-RAG: mean={result['data'][1]:.2f}, std={result['errors'][1]:.2f}, n={result['sample_sizes'][1]}")
    
    print("\n=== Ranked First Rate Comparison ===")
    result_rate = process_ranked_first_rate(df)
    print(f"  RAG:    rate={result_rate['data'][0]:.1f}%")
    print(f"  No-RAG: rate={result_rate['data'][1]:.1f}%")
    
    print("\n=== LLM Ranking by Model ===")
    result_llm = process_llm_ranking(df)
    for model, data in result_llm['data'].items():
        print(f"  {model}: RAG={data['RAG']} (first: {data['rag_first_count']}), No-RAG={data['No-RAG']} (first: {data['norag_first_count']})")
