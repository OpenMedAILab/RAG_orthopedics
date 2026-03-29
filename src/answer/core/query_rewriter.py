"""查询重写模块"""

import os
import json
import re
from .config_manager import ConfigManager


class QueryRewriter:
    """查询重写器"""

    @staticmethod
    def rewrite_query(
        original_query: str,
        context_info: str,
        physical_exam: str,
        imaging: str,
        rewrite_model_name: str = "Gemini",
    ) -> str:
        """重写查询语句，使其更适合 RAG 检索"""
        # DEBUG: Hook 掉 AI 调用，返回原始查询
        return original_query

        # 以下为原有逻辑
        config_manager = ConfigManager()
        config_data = config_manager.load_config()

        model_info = next(
            (m for m in config_data["models"] if m["name"] == rewrite_model_name),
            config_data["models"][0],
        )

        api_key = os.getenv(model_info["api_key_env"])
        if not api_key:
            return original_query

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=model_info["base_url"],
        )

        rewrite_prompt = (
            f"请将以下医学问题转化为更适合知识库检索的查询语句。\n\n"
            f"原始问题：{original_query}\n\n"
            f"病例背景信息：\n"
            f"- 情境：{context_info}\n"
            f"- 体格检查：{physical_exam}\n"
            f"- 影像学检查：{imaging}\n\n"
            f'请返回一个适合向量检索的查询语句，格式：{{"rewritten_query": "重写的查询语句"}}'
        )

        try:
            chat_completion = client.chat.completions.create(
                model=model_info["model_id"],
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.1,
            )

            response_text = chat_completion.choices[0].message.content.strip()

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result.get("rewritten_query", original_query)
                except json.JSONDecodeError:
                    return original_query
            return original_query
        except Exception:
            return original_query
