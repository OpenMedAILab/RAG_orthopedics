"""主应用入口

医学问答对比评分系统 - Flask 应用启动入口
"""

import atexit
import logging
import os
import sys
from pathlib import Path

from flask import Flask

from config import Config
from models.data_handler import DataHandler
from models.user_model import UserManager
from models.heartbeat_manager import stop_heartbeat_manager
from routes.api import register_routes
from routes.auth import register_auth_routes


def setup_logging() -> None:
    """配置日志系统
    
    设置日志格式和级别，输出到控制台和文件。
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建日志目录
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / 'app.log', encoding='utf-8')
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('openpyxl').setLevel(logging.WARNING)


def cleanup_on_exit() -> None:
    """应用退出时的清理函数"""
    logger = logging.getLogger(__name__)
    logger.info("应用正在退出...")
    stop_heartbeat_manager()


def create_app() -> Flask:
    """创建并配置 Flask 应用
    
    使用工厂模式创建应用实例，便于测试和扩展。
    
    Returns:
        Flask: 配置好的 Flask 应用实例
    """
    app = Flask(
        __name__, 
        static_folder='.', 
        template_folder='.'
    )
    
    # 配置应用
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    
    # 配置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 注册退出清理函数
    atexit.register(cleanup_on_exit)
    
    try:
        # 创建组件实例
        user_manager = UserManager()
        data_handler = DataHandler(user_manager)
        
        # 加载数据
        data_handler.load_json_data(app)
        logger.info("数据加载成功")
        
        # 注册路由
        register_auth_routes(app, user_manager, Config.SECRET_KEY)
        register_routes(app, data_handler, user_manager, Config.SECRET_KEY)
        logger.info("路由注册成功")
        
        logger.info(f"应用初始化完成，运行模式：{'DEBUG' if Config.DEBUG else 'PRODUCTION'}")
        
    except Exception as e:
        logger.error(f"应用初始化失败：{e}", exc_info=True)
        raise
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info(f"启动服务器：http://{Config.HOST}:{Config.PORT}")
    
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
