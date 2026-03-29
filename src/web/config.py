"""应用配置模块

提供统一的配置管理，包括文件路径、常量定义等。
"""

import os
from pathlib import Path
from typing import Final


class Config:
    """应用配置类
    
    集中管理应用的所有配置项，便于维护和扩展。
    """
    
    # ==================== 应用基础配置 ====================
    
    # Flask 配置
    SECRET_KEY: Final[str] = os.environ.get('SECRET_KEY', 'your-default-secret-key-for-jwt-must-be-32bytes')
    DEBUG: Final[bool] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST: Final[str] = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT: Final[int] = int(os.environ.get('FLASK_PORT', '5000'))
    
    # JWT 配置
    JWT_ALGORITHM: Final[str] = "HS256"
    JWT_EXPIRATION_HOURS: Final[int] = 24
    
    # ==================== 文件路径配置 ====================
    
    # 获取项目根目录
    BASE_DIR: Final[Path] = Path(__file__).parent
    
    # 数据文件路径
    JSON_DATA_FILE: Final[Path] = BASE_DIR / "评估结果_对比模式.json"
    JSON_DATA_FILE_BACKUP: Final[Path] = BASE_DIR / "评估结果.json"
    EXCEL_FILE: Final[Path] = BASE_DIR / "人工评分.xlsx"
    USERS_FILE: Final[Path] = BASE_DIR / "users.json"
    
    # 静态文件目录
    STATIC_DIR: Final[Path] = BASE_DIR / "static"
    PDFS_DIR: Final[Path] = BASE_DIR / "PDFs"
    
    # ==================== 评分配置 ====================
    
    # 评分维度
    RATING_DIMENSIONS: Final[list[str]] = [
        'medical_accuracy',      # 医学准确性
        'key_point_recall',      # 关键要点召回率
        'logical_completeness'   # 逻辑完整性
    ]
    
    # 评分范围
    RATING_MIN_SCORE: Final[int] = 1
    RATING_MAX_SCORE: Final[int] = 3
    
    # 评分状态
    RATING_STATUS_IDLE: Final[str] = 'idle'
    RATING_STATUS_PROCESSING: Final[str] = 'processing'
    RATING_STATUS_COMPLETED: Final[str] = 'completed'
    
    # ==================== 对比模式配置 ====================
    
    # 侧边标识
    SIDE_A_ID: Final[str] = 'A'
    SIDE_B_ID: Final[str] = 'B'
    SIDE_A_MODE: Final[str] = 'NoRAG'
    SIDE_B_MODE: Final[str] = 'RAG'
    SIDE_A_LABEL: Final[str] = '无 RAG 模式'
    SIDE_B_LABEL: Final[str] = 'RAG 模式'
    
    # ==================== API 响应配置 ====================
    
    # HTTP 状态码
    HTTP_OK: Final[int] = 200
    HTTP_CREATED: Final[int] = 201
    HTTP_BAD_REQUEST: Final[int] = 400
    HTTP_UNAUTHORIZED: Final[int] = 401
    HTTP_FORBIDDEN: Final[int] = 403
    HTTP_NOT_FOUND: Final[int] = 404
    HTTP_CONFLICT: Final[int] = 409
    HTTP_INTERNAL_ERROR: Final[int] = 500
    
    # 响应消息
    MSG_SUCCESS: Final[str] = "操作成功"
    MSG_UNAUTHORIZED: Final[str] = "未授权访问"
    MSG_INVALID_TOKEN: Final[str] = "令牌无效"
    MSG_TOKEN_EXPIRED: Final[str] = "令牌已过期"
    MSG_NOT_FOUND: Final[str] = "资源不存在"
    MSG_BAD_REQUEST: Final[str] = "请求参数错误"
    MSG_INTERNAL_ERROR: Final[str] = "服务器内部错误"
    
    # ==================== 验证规则 ====================
    
    # 用户名规则
    USERNAME_MIN_LENGTH: Final[int] = 3
    USERNAME_MAX_LENGTH: Final[int] = 20
    
    # 密码规则
    PASSWORD_MIN_LENGTH: Final[int] = 6
    
    # ==================== 类方法 ====================
    
    @classmethod
    def get_json_data_file(cls) -> Path:
        """获取 JSON 数据文件路径
        
        优先使用对比模式文件，如果不存在则使用备份文件。
        
        Returns:
            Path: JSON 数据文件路径
        """
        if cls.JSON_DATA_FILE.exists():
            return cls.JSON_DATA_FILE
        return cls.JSON_DATA_FILE_BACKUP
    
    @classmethod
    def validate_rating_score(cls, score: int) -> bool:
        """验证评分值是否在有效范围内
        
        Args:
            score: 评分值
            
        Returns:
            bool: 评分值是否有效
        """
        return cls.RATING_MIN_SCORE <= score <= cls.RATING_MAX_SCORE
