"""评估器模块"""

import json
import re
from pathlib import Path
from typing import Dict, Any
from .model_manager import ModelManager

# 获取 core 模块所在目录的父目录（即 answer 项目根目录）
PROJECT_ROOT = Path(__file__).parent.parent


class MedicalEvaluator:
    """医疗评估器"""

    PROMPT_EVALUATION = """
你是一个严格的医学评估专家，需要对以下医学回答进行评估。请按照以下三个维度进行评分，每个维度评分范围为 1-10 分：

1. 医学准确性（权重 40%）：
   - 10-9 分：完全准确，所有医学信息符合循证医学标准
   - 8-7 分：基本准确，有少量非关键性偏差
   - 6-5 分：部分准确，存在明显错误
   - 4-1 分：存在严重医学错误

2. 关键要点召回率（权重 30%）：
   - 10-9 分：完全覆盖所有关键要点
   - 8-7 分：覆盖大部分关键要点
   - 6-5 分：覆盖部分关键要点
   - 4-1 分：严重遗漏关键要点

3. 逻辑完整性（权重 30%）：
   - 10-9 分：逻辑链完整，思路清晰
   - 8-7 分：逻辑基本完整，有轻微跳跃
   - 6-5 分：逻辑有缺陷
   - 4-1 分：逻辑混乱

请严格按照以下 JSON 格式输出评分结果：
{
    "medical_accuracy": X,
    "key_point_recall": X,
    "logical_completeness": X,
    "evaluation_reasoning": "详细的评估理由"
}

其中 X 为 1-10 之间的整数。
"""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = PROJECT_ROOT.parent / "config" / "models_config.json"
        self.model_manager = ModelManager(str(config_path))

    def evaluate_output(
        self, model_name: str, output_text: str, case_info: str
    ) -> Dict[str, Any]:
        """对输出进行评估，返回 JSON 格式的评分"""
        # DEBUG: Hook 掉 AI 调用，返回固定评分
        return {
            "medical_accuracy": 8,
            "key_point_recall": 7,
            "logical_completeness": 8,
            "evaluation_reasoning": "测试模式：这是固定评分",
        }

        # 以下为原有逻辑
        model_info, client = self.model_manager.get_client(model_name)

        evaluation_prompt = (
            f"请评估以下医学回答的质量：\n\n"
            f"病例信息：{case_info}\n\n"
            f"回答：{output_text}\n\n"
            f"{self.PROMPT_EVALUATION}"
        )

        try:
            chat_completion = client.chat.completions.create(
                model=model_info["model_id"],
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的医学评估专家，严格按照 JSON 格式输出评估结果。",
                    },
                    {"role": "user", "content": evaluation_prompt},
                ],
            )

            response_text = chat_completion.choices[0].message.content.strip()

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return {
                        "medical_accuracy": 5,
                        "key_point_recall": 5,
                        "logical_completeness": 5,
                        "evaluation_reasoning": "解析错误",
                    }
            else:
                return {
                    "medical_accuracy": 5,
                    "key_point_recall": 5,
                    "logical_completeness": 5,
                    "evaluation_reasoning": "格式错误",
                }
        except Exception as e:
            return {
                "medical_accuracy": 3,
                "key_point_recall": 3,
                "logical_completeness": 3,
                "evaluation_reasoning": f"评估错误：{str(e)}",
            }
