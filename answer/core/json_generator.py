"""JSON 生成器模块"""

import json
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict


class JSONGenerator:
    """JSON 生成器 - 将处理结果转换为对比评分 JSON 格式"""

    @staticmethod
    def generate_json_output(
        all_results: List[Dict[str, Any]], output_path: str
    ) -> List[Dict[str, Any]]:
        """生成对比评分模式的 JSON 文件"""
        case_groups = defaultdict(lambda: {
            "case_data": None,
            "outputs": [],
            "evaluations": [],
        })

        for result in all_results:
            case_key = result["case_num"]

            if result["type"] == "output":
                case_groups[case_key]["outputs"].append(result)
                if case_groups[case_key]["case_data"] is None:
                    case_groups[case_key]["case_data"] = result.get("case_data")

            elif result["type"] == "evaluation":
                case_groups[case_key]["evaluations"].append(result)

        rating_pairs = []

        for case_num, case_data in case_groups.items():
            case_info = case_data["case_data"]
            if case_info is not None and hasattr(case_info, "get"):
                context = case_info.get("情境", "")
                physical_examination = case_info.get("体格检查", "")
                imaging_examination = case_info.get("影像学检查", "")
            else:
                context = ""
                physical_examination = ""
                imaging_examination = ""

            outputs_by_model_mode = defaultdict(list)
            for output in case_data["outputs"]:
                key = (output["model"], output["rag_status"])
                outputs_by_model_mode[key].append(output)

            for model_name, outputs in outputs_by_model_mode.items():
                norag_output = next(
                    (o for o in outputs if o["rag_status"] == "No-RAG"), None
                )
                rag_output = next(
                    (o for o in outputs if o["rag_status"] == "RAG"), None
                )

                if not norag_output or not rag_output:
                    continue

                side_a_qa_pairs = JSONGenerator._extract_qa_pairs(norag_output)
                side_b_qa_pairs = JSONGenerator._extract_qa_pairs(rag_output)

                side_a_eval = JSONGenerator._find_evaluation(
                    case_data["evaluations"], "No-RAG", model_name
                )
                side_b_eval = JSONGenerator._find_evaluation(
                    case_data["evaluations"], "RAG", model_name
                )

                pair_id = f"pair_{case_num:03d}_{model_name}"
                timestamp = datetime.now().isoformat()

                rating_pair = {
                    "pairId": pair_id,
                    "caseInfo": {
                        "caseId": f"case_{case_num:03d}",
                        "caseNumber": f"病例 {case_num:03d}",
                        "context": context,
                        "physicalExamination": physical_examination,
                        "imagingExamination": imaging_examination,
                    },
                    "model": model_name,
                    "sideA": {
                        "sideId": "A",
                        "mode": "NoRAG",
                        "label": "无 RAG 模式",
                        "qaPairs": side_a_qa_pairs,
                        "ragContext": "",
                    },
                    "sideB": {
                        "sideId": "B",
                        "mode": "RAG",
                        "label": "RAG 模式",
                        "qaPairs": side_b_qa_pairs,
                        "ragContext": rag_output.get("rag_results", ""),
                    },
                    "metadata": {
                        "createdAt": timestamp,
                        "updatedAt": timestamp,
                    },
                }

                if side_a_eval:
                    rating_pair["sideA"]["evaluation"] = side_a_eval

                if side_b_eval:
                    rating_pair["sideB"]["evaluation"] = side_b_eval

                rating_pairs.append(rating_pair)

        output_data = {"ratingPairs": rating_pairs}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return rating_pairs

    @staticmethod
    def _extract_qa_pairs(output: Dict[str, Any]) -> List[Dict[str, str]]:
        """从输出中提取问答对"""
        qa_pairs = []
        answer_text = output["answer"]
        questions = output["questions"]

        for i, question in enumerate(questions, 1):
            question_header = f"# 问题{i}回答:"
            if question_header in answer_text:
                start_pos = answer_text.find(question_header)
                end_pos = len(answer_text)

                next_q_start = f"# 问题{i+1}回答:"
                if next_q_start in answer_text[start_pos:]:
                    end_pos = answer_text.find(next_q_start, start_pos)

                if end_pos > start_pos:
                    answer_part = answer_text[start_pos:end_pos].replace(
                        question_header, ""
                    ).strip()
                else:
                    answer_part = answer_text[start_pos:].replace(
                        question_header, ""
                    ).strip()

                qa_pairs.append({"question": question, "answer": answer_part})
            else:
                qa_pairs.append({"question": question, "answer": ""})

        return qa_pairs

    @staticmethod
    def _find_evaluation(
        evaluations: List[Dict[str, Any]],
        rag_status: str,
        evaluator_model: str,
    ) -> Dict[str, Any]:
        """查找对应的评估结果"""
        for eval_data in evaluations:
            if (
                eval_data["evaluated_rag_status"] == rag_status
                and eval_data["evaluator_model"] == evaluator_model
            ):
                return {
                    "scores": {
                        "medical_accuracy": eval_data["medical_accuracy"],
                        "key_point_recall": eval_data["key_point_recall"],
                        "logical_completeness": eval_data["logical_completeness"],
                    },
                    "reasoning": eval_data.get("evaluation_reasoning", ""),
                    "ratedBy": "auto_eval",
                    "ratedByName": evaluator_model,
                    "ratedAt": datetime.now().isoformat(),
                }
        return {}
