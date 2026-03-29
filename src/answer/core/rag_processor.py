"""RAG 处理器模块"""

from pathlib import Path


class RAGProcessor:
    """RAG 处理器 - 管理 RAG 检索逻辑"""

    def __init__(
        self,
        rag_config_path="NaiveRag/rag_index.faiss",
        rag_meta_path="NaiveRag/rag_meta.json",
    ):
        self.rag_config_path = rag_config_path
        self.rag_meta_path = rag_meta_path
        self.rag_pipeline = None
        self._initialize_rag()

    def _initialize_rag(self):
        """初始化 RAG 管道"""
        try:
            from NaiveRag.rag.rag_pipeline import RAGPipeline
            from NaiveRag.rag.config import RAGConfig

            config = RAGConfig(
                index_path=Path(self.rag_config_path),
                meta_path=Path(self.rag_meta_path),
                embed_provider="modelscope",
                embed_model="BAAI/bge-m3",
            )
            self.rag_pipeline = RAGPipeline(config=config)
        except Exception as e:
            print(f"RAG 初始化失败：{str(e)}")
            self.rag_pipeline = None

    def get_rag_results(self, query_text: str, medical_specialty: str = "general"):
        """获取 RAG 检索结果"""
        if not self.rag_pipeline:
            return ""

        try:
            results_retrieved = self.rag_pipeline.query(
                query_text=query_text,
                top_k=3,
                retrieve_k=10,
                rerank=True,
            )

            specialty_keywords = {
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

            selected_keywords = specialty_keywords.get(medical_specialty, [])

            context_parts = []
            for result in results_retrieved:
                content = result.get("content", "")
                if content:
                    if selected_keywords:
                        content_lower = content.lower()
                        is_relevant = any(
                            keyword.lower() in content_lower
                            for keyword in selected_keywords
                        )
                        if is_relevant:
                            context_parts.append(content)
                    else:
                        context_parts.append(content)

            return "\n\n".join(context_parts) if context_parts else ""

        except Exception as e:
            print(f"RAG 检索失败：{str(e)}")
            return ""
