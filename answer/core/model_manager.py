"""模型管理模块"""

import os
from typing import Tuple, Dict, Any
from openai import OpenAI
from .config_manager import ConfigManager


class ModelManager:
    """模型管理器"""

    def __init__(self, config_path: str = "config/models_config.json"):
        self.config_manager = ConfigManager(config_path)
        self.clients = {}
        self.models = self.config_manager.get_models()

        for model_info in self.models:
            api_key = os.getenv(model_info["api_key_env"])
            if not api_key:
                raise ValueError(f"{model_info['api_key_env']} 环境变量未设置")

            self.clients[model_info["name"]] = {
                "client": None,
                "model_info": model_info,
            }

    def get_client(self, model_name: str) -> Tuple[Dict[str, Any], OpenAI]:
        """获取指定模型的客户端"""
        model_entry = self.clients.get(model_name)
        if not model_entry:
            raise ValueError(f"未找到模型：{model_name}")

        if model_entry["client"] is None:
            api_key = os.getenv(model_entry["model_info"]["api_key_env"])
            model_entry["client"] = OpenAI(
                api_key=api_key,
                base_url=model_entry["model_info"]["base_url"],
            )

        return model_entry["model_info"], model_entry["client"]
