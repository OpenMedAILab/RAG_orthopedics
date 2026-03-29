"""主处理器模块"""

import pandas as pd
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config_manager import ConfigManager
from .model_manager import ModelManager
from .rag_processor import RAGProcessor
from .evaluator import MedicalEvaluator
from .query_rewriter import QueryRewriter


class StreamableRAGComparisonProcessor:
    """支持流式输出的 RAG 对比处理器"""

    def __init__(self, config_path="config/models_config.json", thread_safe=False):
        self.model_manager = ModelManager(config_path)
        self.rag_processor = RAGProcessor()
        self.evaluator = MedicalEvaluator(config_path)
        self.config_manager = ConfigManager(config_path)
        self.models = self.config_manager.get_models()
        self.thread_safe = thread_safe

    def get_single_question_answer(
        self,
        model_name: str,
        context_info: str,
        physical_exam: str,
        imaging: str,
        rag_results: str,
        question: str,
        question_num: str,
        use_rag: bool = True,
    ) -> str:
        """获取指定模型对单个问题的回答"""
        # DEBUG: Hook 掉 AI 调用，返回固定字符串
        return (
            f"推理过程：这是{model_name}模型对{question_num}的测试回答。\n"
            f"最终结果：测试答案 - {question[:20]}..."
        )

        model_info, client = self.model_manager.get_client(model_name)

        if use_rag:
            system_prompt = self._get_rag_system_prompt()
            user_content = (
                f"请回答以下问题：\n"
                f"问题{question_num}：{question}\n\n"
                f"=============== 情景 ===============\n{context_info}\n"
                f"=============== 体格检查 ===============\n{physical_exam}\n"
                f"=============== 影像学检查 ===============\n{imaging}\n"
                f"=============== 知识库搜索 ===============\n{rag_results}\n\n"
                f"请务必参考知识库搜索结果中的信息来回答问题。"
            )
        else:
            system_prompt = self._get_no_rag_system_prompt()
            user_content = (
                f"请回答以下问题：\n"
                f"问题{question_num}：{question}\n\n"
                f"=============== 情景 ===============\n{context_info}\n"
                f"=============== 体格检查 ===============\n{physical_exam}\n"
                f"=============== 影像学检查 ===============\n{imaging}\n"
            )

        chat_completion = client.chat.completions.create(
            model=model_info["model_id"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )

        full_response = ""
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content

        return full_response

    def _get_rag_system_prompt(self) -> str:
        """获取 RAG 模式的系统提示词"""
        return """
你是一个专业的医学助手，需要综合患者信息和检索到的医学知识来回答问题。请特别注意并优先使用"知识库搜索"部分提供的信息。

回答要求：
1. 优先参考知识库搜索结果中的信息
2. 将检索到的知识与患者具体情况相结合
3. 严格按照以下格式输出：
```
推理过程：{{基于检索知识和患者信息的推理过程}}
最终结果：{{最终结论}}
```
4. 如果使用了检索到的信息，请在推理过程中明确标注来源，使用`[检索结果 X]`格式
禁止使用 Markdown 语法，请保证逻辑清晰，术语明确，并给出简短、明确的回答
"""

    def _get_no_rag_system_prompt(self) -> str:
        """获取 No-RAG 模式的系统提示词"""
        return """
你是一个专业的医学助手，根据提供的上下文信息和患者信息回答医学相关问题。

请严格按照以下格式输出：
```
推理过程：{{推理过程}}
最终结果：{{最终结果}}
```
如果有引用依据，请在推理过程中明确展示推理依据。
禁止使用 Markdown 语法，请保证逻辑清晰，术语明确，并给出简短、明确的回答
"""

    def get_answer_streaming(
        self,
        model_name: str,
        context_info: str,
        physical_exam: str,
        imaging: str,
        rag_results: str,
        question1: str,
        question2: str,
        question3: str,
        use_rag: bool = True,
    ) -> str:
        """获取指定模型对所有问题的回答"""
        patient_info = (
            f"# 患者信息\n\n## 情境\n{context_info}\n\n"
            f"## 体格检查\n{physical_exam}\n\n## 影像学检查\n{imaging}\n\n"
        )

        all_answers = []

        if question1 and question1.lower() != "nan":
            answer1 = self.get_single_question_answer(
                model_name,
                context_info,
                physical_exam,
                imaging,
                rag_results,
                question1,
                "问题 1",
                use_rag,
            )
            all_answers.append(f"# 问题 1 回答:\n{answer1}")

        if question2 and question2.lower() != "nan":
            answer2 = self.get_single_question_answer(
                model_name,
                context_info,
                physical_exam,
                imaging,
                rag_results,
                question2,
                "问题 2",
                use_rag,
            )
            all_answers.append(f"\n# 问题 2 回答:\n{answer2}")

        if question3 and question3.lower() != "nan":
            answer3 = self.get_single_question_answer(
                model_name,
                context_info,
                physical_exam,
                imaging,
                rag_results,
                question3,
                "问题 3",
                use_rag,
            )
            all_answers.append(f"\n# 问题 3 回答:\n{answer3}")

        return patient_info + "\n---\n".join(all_answers) + "\n---\n"

    def evaluate_output(
        self, model_name: str, output_text: str, case_info: str
    ) -> Dict[str, Any]:
        """对输出进行评估"""
        return self.evaluator.evaluate_output(model_name, output_text, case_info)

    def _determine_medical_specialty(
        self, context_info: str, physical_exam: str, imaging: str, questions: str
    ) -> str:
        """确定病例所属的医学专业领域"""
        all_text = f"{context_info} {physical_exam} {imaging} {questions}".lower()

        specialties = {
            "orthopedic_spine": [
                "脊髓型颈椎病",
                "颈椎病",
                "腰椎病",
                "椎间盘突出",
                "椎管狭窄",
                "脊柱侧弯",
                "颈椎手术",
                "腰椎手术",
                "脊髓压迫",
                "颈髓",
                "腰髓",
            ],
            "orthopedics": [
                "骨科",
                "骨折",
                "关节",
                "脊柱",
                "椎间盘",
                "颈椎",
                "腰椎",
                "骨关节炎",
                "韧带",
                "软骨",
            ],
            "neurosurgery": [
                "神经外科",
                "脑部",
                "脊髓",
                "颅内",
                "神经",
                "脑血管",
                "脑肿瘤",
            ],
            "cardiology": [
                "心脏",
                "心血管",
                "冠心病",
                "心律",
                "心肌",
                "瓣膜",
                "心电图",
            ],
            "ophthalmology": [
                "眼科",
                "眼睛",
                "视力",
                "白内障",
                "青光眼",
                "视网膜",
                "角膜",
                "晶状体",
            ],
            "internal_medicine": [
                "内科",
                "呼吸",
                "消化",
                "内分泌",
                "泌尿",
                "血液",
                "免疫",
            ],
            "general_surgery": [
                "普外科",
                "腹部",
                "阑尾",
                "胆囊",
                "疝气",
                "甲状腺",
                "乳腺",
            ],
            "urology": ["泌尿", "肾脏", "膀胱", "前列腺", "输尿管", "尿道"],
        }

        scores = {}
        for specialty, keywords in specialties.items():
            score = 0
            for keyword in keywords:
                if len(keyword) >= 4:
                    score += all_text.count(keyword.lower()) * 2
                else:
                    score += all_text.count(keyword.lower())
            scores[specialty] = score

        best_specialty = max(scores, key=scores.get)
        if scores[best_specialty] > 0:
            return best_specialty
        return "general"

    def process_case(
        self, case_data: pd.Series, case_num: int
    ) -> List[Dict[str, Any]]:
        """处理单个案例"""
        results = []

        context_info = (
            str(case_data.get("情境", "")).strip()
            if pd.notna(case_data.get("情境", ""))
            else ""
        )
        physical_exam = (
            str(case_data.get("体格检查", "")).strip()
            if pd.notna(case_data.get("体格检查", ""))
            else ""
        )
        imaging = (
            str(case_data.get("影像学检查", "")).strip()
            if pd.notna(case_data.get("影像学检查", ""))
            else ""
        )

        question1 = (
            str(case_data.get("问题 1", "")).strip()
            if pd.notna(case_data.get("问题 1", ""))
            else ""
        )
        question2 = (
            str(case_data.get("问题 2", "")).strip()
            if pd.notna(case_data.get("问题 2", ""))
            else ""
        )
        question3 = (
            str(case_data.get("问题 3", "")).strip()
            if pd.notna(case_data.get("问题 3", ""))
            else ""
        )

        questions = []
        if question1 and question1.lower() != "nan":
            questions.append(("问题 1", question1))
        if question2 and question2.lower() != "nan":
            questions.append(("问题 2", question2))
        if question3 and question3.lower() != "nan":
            questions.append(("问题 3", question3))

        if not questions:
            return results

        rag_context = ""
        if self.rag_processor.rag_pipeline:
            all_questions_text = " ".join([q[1] for q in questions])
            rewritten_query = QueryRewriter.rewrite_query(
                original_query=all_questions_text,
                context_info=context_info,
                physical_exam=physical_exam,
                imaging=imaging,
            )
            medical_specialty = self._determine_medical_specialty(
                context_info, physical_exam, imaging, all_questions_text
            )
            rag_context = self.rag_processor.get_rag_results(
                rewritten_query, medical_specialty
            )

        all_outputs = []

        def process_model_and_mode(use_rag, model_info):
            model_name = model_info["name"]
            rag_status = "RAG" if use_rag else "No-RAG"

            try:
                q1 = next((q[1] for q in questions if q[0] == "问题 1"), "")
                q2 = next((q[1] for q in questions if q[0] == "问题 2"), "")
                q3 = next((q[1] for q in questions if q[0] == "问题 3"), "")

                answer = self.get_answer_streaming(
                    model_name=model_name,
                    context_info=context_info,
                    physical_exam=physical_exam,
                    imaging=imaging,
                    rag_results=rag_context if use_rag else "",
                    question1=q1,
                    question2=q2,
                    question3=q3,
                    use_rag=use_rag,
                )

                return {
                    "case_num": case_num,
                    "model": model_name,
                    "use_rag": use_rag,
                    "rag_status": rag_status,
                    "questions": [q for _, q in questions],
                    "answer": answer,
                    "rag_results": rag_context if use_rag else "",
                    "case_data": case_data,
                    "type": "output",
                }
            except Exception as ex:
                error_content = f"错误：{str(ex)}\n\n原始问题：{q1}, {q2}, {q3}"
                return {
                    "case_num": case_num,
                    "model": model_name,
                    "use_rag": use_rag,
                    "rag_status": rag_status,
                    "questions": [q for _, q in questions],
                    "answer": error_content,
                    "case_data": case_data,
                    "type": "output",
                }

        with ThreadPoolExecutor(
            max_workers=min(8, len(self.model_manager.models) * 2)
        ) as executor1:
            futures = []
            for use_rag in [True, False]:
                for model_info in self.model_manager.models:
                    future = executor1.submit(process_model_and_mode, use_rag, model_info)
                    futures.append(future)

            for future in as_completed(futures):
                result_entry = future.result()
                results.append(result_entry)
                all_outputs.append(result_entry)

        for model_info in self.model_manager.models:
            model_name = model_info["name"]
            try:

                def process_evaluation(output):
                    case_info_str = (
                        f"Case {output['case_num']} - "
                        f"{output['model']} - {output['rag_status']}"
                    )
                    evaluation_result = self.evaluate_output(
                        model_name=model_name,
                        output_text=output["answer"],
                        case_info=case_info_str,
                    )

                    return {
                        "case_num": output["case_num"],
                        "evaluated_model": output["model"],
                        "evaluated_rag_status": output["rag_status"],
                        "evaluator_model": model_name,
                        "medical_accuracy": evaluation_result["medical_accuracy"],
                        "key_point_recall": evaluation_result["key_point_recall"],
                        "logical_completeness": evaluation_result["logical_completeness"],
                        "evaluation_reasoning": evaluation_result["evaluation_reasoning"],
                        "type": "evaluation",
                    }

                with ThreadPoolExecutor(
                    max_workers=min(8, len(all_outputs))
                ) as executor2:
                    eval_futures = [
                        executor2.submit(process_evaluation, output)
                        for output in all_outputs
                    ]

                    for eval_future in as_completed(eval_futures):
                        eval_entry = eval_future.result()
                        results.append(eval_entry)
            except Exception:
                pass

        return results
