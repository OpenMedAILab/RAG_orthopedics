# 对比评分数据格式设计

## 概述

本文档描述了医学问答对比评分系统的数据格式设计。对比评分模式允许评分人员同时对比评估两个相关案例（通常是同一模型的 NoRAG 模式 vs RAG 模式）。

## 核心概念

### 评分对 (Rating Pair)

一个评分对包含两个需要对比评估的案例：
- **案例 A**: 通常为 NoRAG 模式（无检索增强生成）
- **案例 B**: 通常为 RAG 模式（有检索增强生成）

### 配对规则

| 案例 A | 案例 B | 说明 |
|--------|--------|------|
| Case1 GPT NoRAG | Case1 GPT RAG | 同一病例，同一模型，不同模式 |
| Case1 Gemini NoRAG | Case1 Gemini RAG | 同一病例，同一模型，不同模式 |
| CaseX ModelA NoRAG | CaseX ModelA RAG | 同一病例，同一模型，不同模式 |

## JSON 数据结构

### 整体结构

```json
{
  "ratingPairs": [
    {
      "pairId": "pair_001",
      "caseInfo": {
        "caseId": "case_001",
        "caseNumber": "病例号 001",
        "context": "患者基本信息和主诉",
        "physicalExamination": "体格检查结果",
        "imagingExamination": "影像学检查结果"
      },
      "model": "GPT-4",
      "sideA": {
        "sideId": "A",
        "mode": "NoRAG",
        "label": "无 RAG 模式",
        "qaPairs": [...],
        "ragContext": "",
        "evaluation": {...}
      },
      "sideB": {
        "sideId": "B",
        "mode": "RAG",
        "label": "RAG 模式",
        "qaPairs": [...],
        "ragContext": "...",
        "evaluation": {...}
      },
      "metadata": {
        "createdAt": "2026-02-22T10:00:00Z",
        "updatedAt": "2026-02-22T12:00:00Z"
      }
    }
  ]
}
```

### 详细字段说明

#### RatingPair 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pairId` | string | 是 | 评分对唯一标识符 |
| `caseInfo` | object | 是 | 病例基本信息 |
| `model` | string | 是 | AI 模型名称（如 GPT-4, Gemini, Grok） |
| `sideA` | object | 是 | A 侧数据（通常为 NoRAG） |
| `sideB` | object | 是 | B 侧数据（通常为 RAG） |
| `metadata` | object | 否 | 元数据信息 |

#### CaseInfo 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `caseId` | string | 是 | 病例唯一标识 |
| `caseNumber` | string | 是 | 病例编号/序号 |
| `context` | string | 是 | 患者情境描述 |
| `physicalExamination` | string | 是 | 体格检查结果 |
| `imagingExamination` | string | 是 | 影像学检查结果 |

#### Side 对象 (sideA/sideB)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sideId` | string | 是 | 侧标识（"A" 或 "B"） |
| `mode` | string | 是 | 评估模式（"NoRAG" 或 "RAG"） |
| `label` | string | 否 | 显示标签（如"无 RAG 模式"） |
| `qaPairs` | array | 是 | 问答对数组 |
| `ragContext` | string | 否 | RAG 检索的上下文（NoRAG 模式为空） |
| `evaluation` | object | 否 | 评估结果（评分时填充） |

#### QAPair 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | string | 是 | 问题文本 |
| `answer` | string | 是 | AI 生成的回答 |

#### Evaluation 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scores` | object | 是 | 三项评分 |
| `reasoning` | string | 否 | 评分理由/备注 |
| `ratedBy` | string | 是 | 评分人 ID |
| `ratedByName` | string | 是 | 评分人姓名 |
| `ratedAt` | string | 否 | 评分时间戳 |

#### Scores 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `medicalAccuracy` | number | 是 | 医学准确性（1-3 分） |
| `keyPointRecall` | number | 是 | 关键要点召回率（1-3 分） |
| `logicalCompleteness` | number | 是 | 逻辑完整性（1-3 分） |

## 评分维度说明

### 1. 医学准确性 (Medical Accuracy)
评估回答中的医学信息是否正确、精准，且无安全隐患。

| 分数 | 标准 |
|------|------|
| 3 分 | 医学信息完全正确，无错误或误导 |
| 2 分 | 基本正确，存在轻微不准确但不影响安全 |
| 1 分 | 存在明显错误或有潜在安全隐患 |

### 2. 关键要点召回率 (Key Point Recall)
评估回答是否全面覆盖了病例分析所必需的关键信息点。

| 分数 | 标准 |
|------|------|
| 3 分 | 覆盖所有关键要点，无遗漏 |
| 2 分 | 覆盖大部分要点，有少量遗漏 |
| 1 分 | 遗漏重要关键要点 |

### 3. 逻辑完整性 (Logical Completeness)
评估回答是否展现了清晰、连贯且符合临床实践的思维过程。

| 分数 | 标准 |
|------|------|
| 3 分 | 逻辑清晰，推理完整，符合临床思维 |
| 2 分 | 逻辑基本清晰，部分推理不够完整 |
| 1 分 | 逻辑混乱或推理缺失 |

## 示例数据

```json
{
  "ratingPairs": [
    {
      "pairId": "pair_001",
      "caseInfo": {
        "caseId": "case_001",
        "caseNumber": "病例 001",
        "context": "患者，男，65 岁，因'反复胸痛 3 个月，加重 1 周'入院。",
        "physicalExamination": "T 36.5℃, P 78 次/分，R 18 次/分，BP 140/90mmHg。",
        "imagingExamination": "心电图示 V3-V5导联 ST 段压低 0.1mV。"
      },
      "model": "GPT-4",
      "sideA": {
        "sideId": "A",
        "mode": "NoRAG",
        "label": "无 RAG 模式",
        "qaPairs": [
          {
            "question": "请分析该患者的可能诊断",
            "answer": "根据患者症状和检查结果，考虑冠心病可能性大..."
          }
        ],
        "ragContext": "",
        "evaluation": {
          "scores": {
            "medicalAccuracy": 2,
            "keyPointRecall": 2,
            "logicalCompleteness": 2
          },
          "reasoning": "回答基本正确，但缺少鉴别诊断",
          "ratedBy": "user_001",
          "ratedByName": "张医生",
          "ratedAt": "2026-02-22T10:30:00Z"
        }
      },
      "sideB": {
        "sideId": "B",
        "mode": "RAG",
        "label": "RAG 模式",
        "qaPairs": [
          {
            "question": "请分析该患者的可能诊断",
            "answer": "根据患者症状和检查结果，考虑冠心病可能性大。建议进一步行冠脉造影检查..."
          }
        ],
        "ragContext": "根据 2023 年 ESC 指南，对于疑似冠心病患者...",
        "evaluation": {
          "scores": {
            "medicalAccuracy": 3,
            "keyPointRecall": 3,
            "logicalCompleteness": 3
          },
          "reasoning": "RAG 模式提供了更详细的诊断依据和治疗建议",
          "ratedBy": "user_001",
          "ratedByName": "张医生",
          "ratedAt": "2026-02-22T10:35:00Z"
        }
      },
      "metadata": {
        "createdAt": "2026-02-22T09:00:00Z",
        "updatedAt": "2026-02-22T10:35:00Z"
      }
    }
  ]
}
```

## 数据迁移说明

### 从旧格式迁移

如果现有数据为单个案例格式，需要进行配对转换：

1. 按 `caseId` 和 `model` 分组
2. 将同一 `caseId` 和 `model` 的 NoRAG 和 RAG 案例配对
3. 合并共享的 `caseInfo` 字段
4. 保留各自的 `evaluation` 数据

### 兼容性考虑

- 系统应支持两种模式：单案例评分模式和对比评分模式
- 通过配置切换模式
- 对比评分模式下，进度统计以"评分对"为单位

## API 接口变更

### 获取评分对列表
```
GET /api/rating_pairs
```

### 获取单个评分对
```
GET /api/rating_pair/<pairId>
```

### 保存评分对
```
POST /api/save_rating_pair
{
  "pairId": "pair_001",
  "sideAEvaluation": {...},
  "sideBEvaluation": {...}
}
```

## 前端 UI 变更

### 布局设计
- 左右分栏显示 Side A 和 Side B
- 共享的病例信息置顶显示
- 两个侧边的评分区域并列显示
- 支持独立对每个侧边进行评分

### 交互设计
- 可切换查看不同侧边的详细内容
- 评分时可在两侧之间快速切换参考
- 进度显示以评分对为单位
