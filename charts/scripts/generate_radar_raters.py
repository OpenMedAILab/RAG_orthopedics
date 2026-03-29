#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成雷达图：每个医生一个（Vanilla LLM vs RAG），外加一个汇总图

注意：排除第 4 个医生（数据存在错误），仅使用前 3 个医生

输出:
- outputs/radar_rater1.tif (300 DPI)
- outputs/radar_rater2.tif (300 DPI)
- outputs/radar_rater3.tif (300 DPI)
- outputs/radar_aggregated.tif (300 DPI)
"""

import openpyxl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import pearsonr, spearmanr
import warnings
import os

warnings.filterwarnings('ignore')

os.chdir('/home/kali/文档/实习/RAGAnswer_Graph')

# ── Load data ──────────────────────────────────────────────────────────────────
wb = openpyxl.load_workbook('人工评分.xlsx')
# 仅使用前 3 个医生（排除第 4 个）
sheets = ['人工评分-1', '人工评分-2', '人工评分-3']
rater_data = []

for sheet in sheets:
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))[1:]
    data = []
    for r in rows:
        if r[1] is None:
            continue
        data.append({
            'case': r[1],
            'model': r[2],
            'mode': r[3],
            'accuracy': r[5],
            'recall': r[6],
            'logic': r[7],
        })
    rater_data.append(data)

# ── Constants ──────────────────────────────────────────────────────────────────
DIMS = ['Medical Accuracy', 'Key Point Recall', 'Logical Completeness']
DIM_KEYS = ['accuracy', 'recall', 'logic']
MODES = ['RAG', 'Vanilla LLM']
MODE_COLORS = {'RAG': '#DD8452', 'Vanilla LLM': '#4C72B0'}
RATER_COLORS = ['#2196F3', '#E91E63', '#4CAF50']
RATER_NAMES = ['Rater 1', 'Rater 2', 'Rater 3']

# ── Helper Functions ───────────────────────────────────────────────────────────
def get_rater_dim_scores(rdata, mode):
    """
    计算单个医生在指定模式下的三维度平均分
    支持 'Vanilla LLM' 和 'No-RAG' 两种模式名称（向后兼容）
    """
    # 支持 No-RAG 和 Vanilla LLM 两种名称
    mode_match = 'Vanilla LLM' if mode == 'Vanilla LLM' else mode
    if mode == 'Vanilla LLM':
        mode_match = ['Vanilla LLM', 'No-RAG']
    
    scores = {k: [] for k in DIM_KEYS}
    for row in rdata:
        row_mode = row['mode']
        # 支持两种模式名称的匹配
        if isinstance(mode_match, list):
            if row_mode not in mode_match:
                continue
        else:
            if row_mode != mode_match:
                continue
        for k in DIM_KEYS:
            if row[k] is not None:
                scores[k].append(row[k])
    return [np.mean(scores[k]) for k in DIM_KEYS]


def get_aggregated_scores(rater_data_list, mode):
    """
    计算 3 个医生在指定模式下的三维度平均分（汇总平均）
    支持 'Vanilla LLM' 和 'No-RAG' 两种模式名称（向后兼容）
    """
    # 支持 No-RAG 和 Vanilla LLM 两种名称
    mode_match = 'Vanilla LLM' if mode == 'Vanilla LLM' else mode
    if mode == 'Vanilla LLM':
        mode_match = ['Vanilla LLM', 'No-RAG']
    
    all_scores = {k: [] for k in DIM_KEYS}
    for rdata in rater_data_list:
        for row in rdata:
            row_mode = row['mode']
            # 支持两种模式名称的匹配
            if isinstance(mode_match, list):
                if row_mode not in mode_match:
                    continue
            else:
                if row_mode != mode_match:
                    continue
            for k in DIM_KEYS:
                if row[k] is not None:
                    all_scores[k].append(row[k])
    return [np.mean(all_scores[k]) for k in DIM_KEYS]


# ── Radar plot helper ──────────────────────────────────────────────────────────
def radar(ax, values_list, labels, colors, legend_labels, title, max_val=3.0):
    """
    绘制雷达图
    """
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=14, fontweight='bold')

    # Grid
    for r in [1, 1.5, 2, 2.5, 3]:
        ax.plot(angles, [r] * (N + 1), color='grey', linewidth=0.4, linestyle='--', alpha=0.5)
    ax.set_ylim(0, max_val)
    ax.set_yticks([1, 1.5, 2, 2.5, 3])
    ax.set_yticklabels(['1', '1.5', '2', '2.5', '3'], fontsize=12, color='grey')

    for vals, color, lbl in zip(values_list, colors, legend_labels):
        v = vals + vals[:1]
        ax.plot(angles, v, color=color, linewidth=2.2, linestyle='solid', label=lbl)
        ax.fill(angles, v, alpha=0.18, color=color)
        # Mark points
        for a, val in zip(angles[:-1], vals):
            ax.plot(a, val, 'o', color=color, markersize=5)

    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    
    # 图例放在右上角
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=14)
    ax.spines['polar'].set_visible(False)


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1-3: Per-rater radar plots (Vanilla LLM vs RAG)
# ═══════════════════════════════════════════════════════════════════════════════

for i, (rdata, rname, rcolor) in enumerate(zip(rater_data, RATER_NAMES, RATER_COLORS), 1):
    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))

    # 计算该医生在两种模式下的三维度分数
    norag_scores = get_rater_dim_scores(rdata, 'Vanilla LLM')
    rag_scores = get_rater_dim_scores(rdata, 'RAG')

    # 绘制雷达图（2 条线：RAG 和 Vanilla LLM）
    radar(ax,
          [rag_scores, norag_scores],
          DIMS,
          [MODE_COLORS['RAG'], MODE_COLORS['Vanilla LLM']],
          ['RAG', 'Vanilla LLM'],
          f'Rater {i}')
    
    plt.tight_layout()
    save_path = f'outputs/radar_rater{i}.tif'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {save_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Aggregated radar plot (3 raters average)
# ═══════════════════════════════════════════════════════════════════════════════

fig4, ax4 = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))

# 计算 3 个医生汇总的三维度分数
norag_agg = get_aggregated_scores(rater_data, 'Vanilla LLM')
rag_agg = get_aggregated_scores(rater_data, 'RAG')

# 绘制雷达图（2 条线：RAG 和 Vanilla LLM）
radar(ax4,
      [rag_agg, norag_agg],
      DIMS,
      [MODE_COLORS['RAG'], MODE_COLORS['Vanilla LLM']],
      ['RAG', 'Vanilla LLM'],
      'Aggregated Raters (n=3)')

plt.tight_layout()
plt.savefig('outputs/radar_aggregated.tif', dpi=300, bbox_inches='tight')
plt.close()
print("Saved outputs/radar_aggregated.tif")

# ── Print Summary Statistics ────────────────────────────────────────────────────
print("\n" + "="*60)
print("Per-Rater Dimension Scores (RAG vs Vanilla LLM)")
print("="*60)
for i, rdata in enumerate(rater_data, 1):
    norag = get_rater_dim_scores(rdata, 'Vanilla LLM')
    rag = get_rater_dim_scores(rdata, 'RAG')
    print(f"\n{RATER_NAMES[i-1]}:")
    print(f"  RAG:         Accuracy={rag[0]:.2f}, Recall={rag[1]:.2f}, Logic={rag[2]:.2f}")
    print(f"  Vanilla LLM: Accuracy={norag[0]:.2f}, Recall={norag[1]:.2f}, Logic={norag[2]:.2f}")

print("\n" + "="*60)
print("Aggregated Scores (3 Raters Average)")
print("="*60)
norag_agg = get_aggregated_scores(rater_data, 'Vanilla LLM')
rag_agg = get_aggregated_scores(rater_data, 'RAG')
print(f"\nRAG:         Accuracy={rag_agg[0]:.2f}, Recall={rag_agg[1]:.2f}, Logic={rag_agg[2]:.2f}")
print(f"Vanilla LLM: Accuracy={norag_agg[0]:.2f}, Recall={norag_agg[1]:.2f}, Logic={norag_agg[2]:.2f}")
