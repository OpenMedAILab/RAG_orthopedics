#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Table 1: Statistical Evaluation Results

计算逻辑：
1. 对每个病例内，每个评估者对 6 个方法（3 模型×2 模式）进行排名
2. 计算每个评估者对每个方法的平均排名（跨 40 个病例）
3. 基于这些平均排名计算 Friedman 统计量和 Kendall's W

注意：排除第 4 个医生（数据存在错误），仅使用前 3 个医生

输出:
- outputs/table1_statistical_results.tif (300 DPI, 学术论文风格图片)
- outputs/table1_statistical_results.md (Markdown 格式表格)
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os

os.chdir('/home/kali/文档/实习/RAGAnswer_Graph')

# ============================================================
# 1. 读取数据
# ============================================================

llm_df = pd.read_excel('模型评分.xlsx', sheet_name='模型评分')
expert1_df = pd.read_excel('人工评分.xlsx', sheet_name='人工评分-1')
expert2_df = pd.read_excel('人工评分.xlsx', sheet_name='人工评分-2')
expert3_df = pd.read_excel('人工评分.xlsx', sheet_name='人工评分-3')
# 排除 expert4（数据存在错误）

# ============================================================
# 2. 计算综合分数
# ============================================================

llm_df['GPT_score'] = (llm_df['GPT-医学准确性[1-10分]'] +
                        llm_df['GPT-关键要点召回率[1-10分]'] +
                        llm_df['GPT-逻辑完整性[1-10分]']) / 3
llm_df['Gemini_score'] = (llm_df['Gemini-医学准确性[1-10分]'] +
                          llm_df['Gemini-关键要点召回率[1-10分]'] +
                          llm_df['Gemini-逻辑完整性[1-10分]']) / 3
llm_df['Grok_score'] = (llm_df['Grok-医学准确性[1-10分]'] +
                        llm_df['Grok-关键要点召回率[1-10分]'] +
                        llm_df['Grok-逻辑完整性[1-10分]']) / 3

# 仅使用前 3 个医生
for exp_df in [expert1_df, expert2_df, expert3_df]:
    exp_df['avg_score'] = (exp_df['医学准确性[1-3分]'] +
                           exp_df['关键要点召回率[1-3分]'] +
                           exp_df['逻辑完整性[1-3分]']) / 3

# ============================================================
# 3. 创建方法标识
# ============================================================

llm_df['method'] = llm_df['被评估模型'] + '_' + llm_df['模式']

for exp_df in [expert1_df, expert2_df, expert3_df]:
    exp_df['method'] = exp_df['被评估模型'] + '_' + exp_df['模式']

print("="*60)
print("第一步：计算每个评估者对 6 个方法的平均排名")
print("="*60)

# ── LLM-as-a-judge (n=3): 计算每个 LLM 对 6 个方法的平均排名 ──────
print("\n--- LLM-as-a-judge (n=3) ---")

# 对每个病例，计算每个 LLM 对 6 个方法的排名
llm_ranks_by_case = []

for case in llm_df['病例号'].unique():
    case_data = llm_df[llm_df['病例号'] == case]
    
    # 对每个 LLM，计算其对 6 个方法的排名
    for evaluator in ['GPT', 'Gemini', 'Grok']:
        score_col = f'{evaluator}_score'
        
        # 获取该 LLM 对 6 个方法的评分
        method_scores = case_data.groupby('method')[score_col].mean()
        
        # 对 6 个方法进行排名
        ranks = stats.rankdata(method_scores.values, method='average')
        
        for method, rank in zip(method_scores.index, ranks):
            llm_ranks_by_case.append({
                '病例号': case,
                '评估者': evaluator,
                '方法': method,
                '排名': rank
            })

llm_ranks_df = pd.DataFrame(llm_ranks_by_case)

# 计算每个 LLM 对每个方法的平均排名（跨 40 个病例）
llm_avg_ranks = llm_ranks_df.groupby(['评估者', '方法'])['排名'].mean().reset_index()
llm_avg_ranks_pivot = llm_avg_ranks.pivot(index='评估者', columns='方法', values='排名')

print("\n每个 LLM 对 6 个方法的平均排名:")
print(llm_avg_ranks_pivot)

# ── Expert Evaluators (n=3): 计算每个专家对 6 个方法的平均排名 ──────
print("\n--- Expert Evaluators (n=3) ---")

expert_ranks_by_case = []

for exp_idx, exp_df in enumerate([expert1_df, expert2_df, expert3_df], 1):
    for case in exp_df['病例号'].unique():
        case_data = exp_df[exp_df['病例号'] == case]
        
        # 获取该专家对 6 个方法的评分
        method_scores = case_data.groupby('method')['avg_score'].mean()
        
        # 对 6 个方法进行排名
        ranks = stats.rankdata(method_scores.values, method='average')
        
        for method, rank in zip(method_scores.index, ranks):
            expert_ranks_by_case.append({
                '病例号': case,
                '评估者': f'expert{exp_idx}',
                '方法': method,
                '排名': rank
            })

expert_ranks_df = pd.DataFrame(expert_ranks_by_case)

# 计算每个专家对每个方法的平均排名（跨 40 个病例）
expert_avg_ranks = expert_ranks_df.groupby(['评估者', '方法'])['排名'].mean().reset_index()
expert_avg_ranks_pivot = expert_avg_ranks.pivot(index='评估者', columns='方法', values='排名')

print("\n每个专家对 6 个方法的平均排名:")
print(expert_avg_ranks_pivot)

# ============================================================
# 4. 基于平均排名计算 Friedman 统计量和 Kendall's W
# ============================================================

print("\n" + "="*60)
print("第二步：基于平均排名计算 Friedman 统计量和 Kendall's W")
print("="*60)

def friedman_kendall_from_ranks(rank_matrix):
    """
    从排名矩阵计算 Friedman 统计量和 Kendall's W
    
    参数:
        rank_matrix: 行=评估者，列=方法，值=平均排名（已经是排名数据，不需要再排名）
    
    返回:
        Q, p_value, W
    """
    k, n = rank_matrix.shape  # k=评估者数，n=方法数
    
    # 计算每个方法的秩和（直接对列求和，因为输入已经是排名）
    rank_sums = rank_matrix.sum(axis=0)
    
    # 计算秩和的离差平方和 S
    mean_rank_sum = np.mean(rank_sums)
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    
    # Kendall's W: W = 12S / (k^2 * n * (n^2 - 1))
    # k=评估者数，n=方法数
    W = (12 * S) / (k**2 * n * (n**2 - 1))
    W = max(0, min(1, W))
    
    # Friedman Q: Q = W * k * (n - 1)
    # 或者从原始公式: Q = [12 / (k*n*(n+1))] * ΣRj² - 3k(n+1)
    Q = W * k * (n - 1)
    
    # P 值（卡方分布）
    p_value = 1 - stats.chi2.cdf(Q, k - 1)
    
    return Q, p_value, W

# ── LLM-as-a-judge (n=3) ──────
llm_rank_matrix = llm_avg_ranks_pivot.values  # 行=评估者，列=方法
llm_Q, llm_p, llm_W = friedman_kendall_from_ranks(llm_rank_matrix)

print(f"\nLLM-as-a-judge (n=3):")
print(f"  评估者数 (k) = {llm_avg_ranks_pivot.shape[0]}, 方法数 (n) = {llm_avg_ranks_pivot.shape[1]}")
print(f"  Friedman Q = {llm_Q:.3f}")
print(f"  P-value = {llm_p:.4f}")
print(f"  Kendall's W = {llm_W:.3f}")

# ── Expert Evaluators (n=3) ──────
expert_rank_matrix = expert_avg_ranks_pivot.values
expert_Q, expert_p, expert_W = friedman_kendall_from_ranks(expert_rank_matrix)

print(f"\nExpert Evaluators (n=3):")
print(f"  评估者数 (k) = {expert_avg_ranks_pivot.shape[0]}, 方法数 (n) = {expert_avg_ranks_pivot.shape[1]}")
print(f"  Friedman Q = {expert_Q:.3f}")
print(f"  P-value = {expert_p:.4f}")
print(f"  Kendall's W = {expert_W:.3f}")

# ============================================================
# 5. Cross-method Correlation (n=6): 3 个 LLM + 3 个专家
# ============================================================

print("\n" + "="*60)
print("Cross-method Correlation (n=6)")
print("="*60)

# 合并 LLM 和专家的排名数据
llm_ranks_df['评估者'] = 'LLM_' + llm_ranks_df['评估者']
expert_ranks_df['评估者'] = 'Expert_' + expert_ranks_df['评估者']

combined_ranks = pd.concat([llm_ranks_df, expert_ranks_df], ignore_index=True)

# 计算每个评估者对每个方法的平均排名
combined_avg_ranks = combined_ranks.groupby(['评估者', '方法'])['排名'].mean().reset_index()
combined_avg_ranks_pivot = combined_avg_ranks.pivot(index='评估者', columns='方法', values='排名')

print("\n6 个评估者对 6 个方法的平均排名:")
print(combined_avg_ranks_pivot)

# 基于平均排名计算 Friedman 和 Kendall's W
combined_rank_matrix = combined_avg_ranks_pivot.values
combined_Q, combined_p, combined_W = friedman_kendall_from_ranks(combined_rank_matrix)

print(f"\nExpert vs. LLM-as-a-judge (n=6):")
print(f"  评估者数 (k) = {combined_avg_ranks_pivot.shape[0]}, 方法数 (n) = {combined_avg_ranks_pivot.shape[1]}")
print(f"  Friedman Q = {combined_Q:.3f}")
print(f"  P-value = {combined_p:.4f}")
print(f"  Kendall's W = {combined_W:.3f}")

# ============================================================
# 6. 格式化 P 值
# ============================================================

def format_p_value(p):
    if p < 0.001:
        return '<0.001'
    elif p < 0.01:
        return f'{p:.3f}'
    else:
        return f'{p:.3f}'

# ============================================================
# 7. 生成表格图片
# ============================================================

fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
ax.axis('off')

table_data = [
    ['Evaluation Comparison', 'Friedman Test\nStatistics', 'Friedman Test\nP-value', "Kendall's W"],
    ['Inter-rater Reliability', '', '', ''],
    [f'LLM-as-a-judge (n=3)', f'{llm_Q:.3f}', format_p_value(llm_p), f'{llm_W:.3f}'],
    [f'Expert Evaluators (n=3)', f'{expert_Q:.3f}', format_p_value(expert_p), f'{expert_W:.3f}'],
    ['Cross-method Correlation', '', '', ''],
    [f'Expert vs. LLM-as-a-judge (n=6)', f'{combined_Q:.3f}', format_p_value(combined_p), f'{combined_W:.3f}'],
]

table = ax.table(
    cellText=table_data[1:],
    colLabels=table_data[0],
    cellLoc='left',
    loc='center',
    colWidths=[0.38, 0.22, 0.20, 0.15]
)

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.8)

for key, cell in table.get_celld().items():
    cell.set_edgecolor('white')
    cell.set_linewidth(0)
    cell.set_text_props(fontfamily='serif', color='black')
    if key[1] == 0:
        cell.set_text_props(weight='bold')

fig.suptitle(
    'Table 1. Statistical Evaluation Results. Summary of ranking correlations and\nperformance metrics across different evaluation methods.',
    fontsize=11, fontfamily='serif', y=0.95, weight='bold'
)

ax.axhline(y=0.90, color='black', linewidth=1.2, xmin=0.02, xmax=0.98)
ax.axhline(y=0.70, color='black', linewidth=0.8, xmin=0.02, xmax=0.98)
ax.axhline(y=0.42, color='black', linewidth=0.8, xmin=0.02, xmax=0.98)
ax.axhline(y=0.10, color='black', linewidth=1.2, xmin=0.02, xmax=0.98)

plt.tight_layout()
save_path = 'outputs/table1_statistical_results.tif'
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print(f'\nTable 1 图片已保存至：{save_path}')

# ============================================================
# 8. 生成 Markdown 表格
# ============================================================

md_content = f'''# Table 1. Statistical Evaluation Results

Summary of ranking correlations and performance metrics across different evaluation methods.

## Statistical Evaluation Results

| Evaluation Comparison | Friedman Test Statistics | Friedman Test P-value | Kendall's W |
|:----------------------|:------------------------:|:---------------------:|:-----------:|
| **Inter-rater Reliability** | | | |
| LLM-as-a-judge (n=3) | {llm_Q:.3f} | {format_p_value(llm_p)} | {llm_W:.3f} |
| Expert Evaluators (n=3) | {expert_Q:.3f} | {format_p_value(expert_p)} | {expert_W:.3f} |
| **Cross-method Correlation** | | | |
| Expert vs. LLM-as-a-judge (n=6) | {combined_Q:.3f} | {format_p_value(combined_p)} | {combined_W:.3f} |

---

## Calculation Method

1. **Within-case ranking**: For each case, each evaluator ranks the 6 methods (3 models × 2 modes)
2. **Average ranking**: Calculate the average rank for each evaluator-method pair across 40 cases
3. **Friedman test & Kendall's W**: Computed from the average ranking matrix

## Notes

- **Friedman Test**: Non-parametric statistical test used to detect differences in treatments across multiple test attempts.
- **Kendall's W**: Coefficient of concordance, measuring agreement among raters (range: 0 to 1, where 1 indicates perfect agreement).
- **Note**: Rater 4 was excluded from analysis due to data quality issues.

## Data Sources

- **LLM-as-a-judge (n=3)**: 3 LLM evaluators (GPT, Gemini, Grok) ranking 6 methods across 40 cases
- **Expert Evaluators (n=3)**: 3 expert evaluators (physicians) ranking 6 methods across 40 cases
- **Cross-method (n=6)**: Combined 6 evaluators (3 LLMs + 3 experts)

---

*Generated on: 2026-03-04*
'''

md_save_path = 'outputs/table1_statistical_results.md'
with open(md_save_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f'Markdown 表格已保存至：{md_save_path}')

# ============================================================
# 9. 打印预览
# ============================================================

print('\n' + '='*80)
print('Table 1. Statistical Evaluation Results')
print('='*80)
print("Evaluation Comparison                      Friedman     P-value      Kendall's W ")
print("                                           Statistics                            ")
print('-'*80)
print('Inter-rater Reliability')
print(f"LLM-as-a-judge (n=3)                       {llm_Q:<12.3f} {format_p_value(llm_p):<12} {llm_W:<12.3f}")
print(f"Expert Evaluators (n=3)                    {expert_Q:<12.3f} {format_p_value(expert_p):<12} {expert_W:<12.3f}")
print('-'*80)
print('Cross-method Correlation')
print(f"Expert vs. LLM-as-a-judge (n=6)            {combined_Q:<12.3f} {format_p_value(combined_p):<12} {combined_W:<12.3f}")
print('='*80)

# ============================================================
# 10. 保存中间数据（每个评估者的平均排名）
# ============================================================

llm_avg_ranks.to_csv('outputs/llm_avg_ranks.csv', index=False)
expert_avg_ranks.to_csv('outputs/expert_avg_ranks.csv', index=False)
combined_avg_ranks.to_csv('outputs/combined_avg_ranks.csv', index=False)

print("\n平均排名数据已保存至:")
print("  - outputs/llm_avg_ranks.csv")
print("  - outputs/expert_avg_ranks.csv")
print("  - outputs/combined_avg_ranks.csv")

# ============================================================
# 11. 生成 Excel 文件
# ============================================================

excel_save_path = 'outputs/table1_statistical_results.xlsx'
with pd.ExcelWriter(excel_save_path, engine='openpyxl') as writer:
    # Sheet 1: 主要统计结果
    summary_data = {
        'Evaluation Comparison': [
            'Inter-rater Reliability',
            'LLM-as-a-judge (n=3)',
            'Expert Evaluators (n=3)',
            'Cross-method Correlation',
            'Expert vs. LLM-as-a-judge (n=6)'
        ],
        'Friedman Q': [np.nan, llm_Q, expert_Q, np.nan, combined_Q],
        'P-value': [np.nan, format_p_value(llm_p), format_p_value(expert_p), np.nan, format_p_value(combined_p)],
        "Kendall's W": [np.nan, llm_W, expert_W, np.nan, combined_W]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Sheet 2: LLM 评估者平均排名
    llm_avg_ranks_pivot.to_excel(writer, sheet_name='LLM_Avg_Ranks')
    
    # Sheet 3: 专家评估者平均排名
    expert_avg_ranks_pivot.to_excel(writer, sheet_name='Expert_Avg_Ranks')
    
    # Sheet 4: 合并评估者平均排名
    combined_avg_ranks_pivot.to_excel(writer, sheet_name='Combined_Avg_Ranks')
    
    # Sheet 5: 原始排名数据
    llm_ranks_df.to_excel(writer, sheet_name='LLM_Raw_Ranks', index=False)
    expert_ranks_df.to_excel(writer, sheet_name='Expert_Raw_Ranks', index=False)

print(f'\nExcel 表格已保存至：{excel_save_path}')
