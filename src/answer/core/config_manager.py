"""配置管理模块"""

import json
from typing import Dict, List, Any


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config/models_config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_models(self) -> List[Dict[str, Any]]:
        """获取模型配置列表"""
        return self.config["models"]

    def get_model_by_name(self, model_name: str) -> Dict[str, Any]:
        """根据名称获取特定模型配置"""
        for model in self.config["models"]:
            if model["name"] == model_name:
                return model
        raise ValueError(f"未找到模型：{model_name}")

    def get_thread_count(self) -> int:
        """获取线程数配置，默认为 16"""
        return self.config.get("thread_count", 16)
