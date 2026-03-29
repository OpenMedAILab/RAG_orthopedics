"""API 路由模块

提供对比评分系统的 RESTful API 接口。
"""

import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

import jwt
from flask import Flask, jsonify, request, send_from_directory

from config import Config
from models.data_handler import DataHandler, NanConverter
from models.heartbeat_manager import get_heartbeat_manager

# 配置日志
logger = logging.getLogger(__name__)


def token_required(f: Callable) -> Callable:
    """JWT 令牌验证装饰器
    
    验证请求中的 JWT 令牌，将用户 ID 附加到请求对象。
    
    Args:
        f: 被装饰的视图函数
        
    Returns:
        Callable: 包装后的视图函数
        
    Raises:
        返回 401 错误如果令牌缺失、过期或无效
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = request.cookies.get('auth_token')

        if not token:
            logger.warning("请求缺少认证令牌")
            return jsonify({'message': 'Token is missing'}), Config.HTTP_UNAUTHORIZED

        try:
            data = jwt.decode(
                token, 
                Config.SECRET_KEY, 
                algorithms=[Config.JWT_ALGORITHM]
            )
            request.current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return jsonify({'message': 'Token has expired'}), Config.HTTP_UNAUTHORIZED
        except jwt.InvalidTokenError as e:
            logger.warning(f"令牌无效：{e}")
            return jsonify({'message': 'Token is invalid'}), Config.HTTP_UNAUTHORIZED

        return f(*args, **kwargs)

    return decorated


def register_routes(
    app: Flask, 
    data_handler: DataHandler, 
    user_manager: Any, 
    secret_key: str,
    socketio: Any = None
) -> None:
    """注册 API 路由
    
    Args:
        app: Flask 应用实例
        data_handler: 数据处理器实例
        user_manager: 用户管理器实例
        secret_key: JWT 密钥
        socketio: Socket.IO 实例（可选）
    """
    
    @app.route('/')
    def index() -> Any:
        """返回前端页面
        
        Returns:
            Any: 前端 HTML 页面
        """
        try:
            return app.send_static_file('index.html')
        except Exception:
            index_path = Path(__file__).parent.parent / 'index.html'
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return jsonify({'error': 'Frontend not found'}), Config.HTTP_NOT_FOUND

    @app.route('/api/rating_pair/<int:index>')
    @token_required
    def get_rating_pair(index: int) -> Tuple[Any, int]:
        """获取对比评分对数据
        
        Args:
            index: 评分对索引（从 1 开始）
            
        Returns:
            Tuple[Any, int]: (评分对数据，HTTP 状态码)
        """
        array_index = index - 1
        json_data = data_handler.data_manager.get_json_data()

        if not (0 <= array_index < len(json_data)):
            logger.warning(f"获取评分对失败：索引 {index} 超出范围")
            return jsonify({'error': 'Index out of range'}), Config.HTTP_NOT_FOUND

        pair_data = json_data[array_index]
        status_info = data_handler.rating_manager.rating_status.get(
            array_index, 
            {'status': Config.RATING_STATUS_IDLE, 'user_id': None, 'timestamp': None}
        )

        # 提取 Side A 评分
        side_a_eval = pair_data.get('sideA', {}).get('evaluation', {})
        side_a_scores = side_a_eval.get('scores', {})
        
        # 提取 Side B 评分
        side_b_eval = pair_data.get('sideB', {}).get('evaluation', {})
        side_b_scores = side_b_eval.get('scores', {})

        item = {
            'index': index,
            'pair_id': pair_data.get('pairId', ''),
            'model': pair_data.get('model', ''),
            'case_info': pair_data.get('caseInfo', {}),
            'side_a': {
                'side_id': pair_data.get('sideA', {}).get('sideId', Config.SIDE_A_ID),
                'mode': pair_data.get('sideA', {}).get('mode', Config.SIDE_A_MODE),
                'label': pair_data.get('sideA', {}).get('label', Config.SIDE_A_LABEL),
                'qa_pairs': pair_data.get('sideA', {}).get('qaPairs', []),
                'rag_context': pair_data.get('sideA', {}).get('ragContext', ''),
                'scores': {
                    'medical_accuracy': side_a_scores.get('medical_accuracy'),
                    'key_point_recall': side_a_scores.get('key_point_recall'),
                    'logical_completeness': side_a_scores.get('logical_completeness')
                },
                'comment': side_a_eval.get('reasoning', '')
            },
            'side_b': {
                'side_id': pair_data.get('sideB', {}).get('sideId', Config.SIDE_B_ID),
                'mode': pair_data.get('sideB', {}).get('mode', Config.SIDE_B_MODE),
                'label': pair_data.get('sideB', {}).get('label', Config.SIDE_B_LABEL),
                'qa_pairs': pair_data.get('sideB', {}).get('qaPairs', []),
                'rag_context': pair_data.get('sideB', {}).get('ragContext', ''),
                'scores': {
                    'medical_accuracy': side_b_scores.get('medical_accuracy'),
                    'key_point_recall': side_b_scores.get('key_point_recall'),
                    'logical_completeness': side_b_scores.get('logical_completeness')
                },
                'comment': side_b_eval.get('reasoning', '')
            },
            'status': status_info['status'],
            'status_user': status_info['user_id'],
        }

        return jsonify(NanConverter.convert(item)), Config.HTTP_OK

    @app.route('/api/all_ratings')
    @token_required
    def get_all_ratings() -> Tuple[Any, int]:
        """获取所有评分项列表
        
        Returns:
            Tuple[Any, int]: (评分项列表，HTTP 状态码)
        """
        try:
            all_items = data_handler.get_all_ratings()
            return jsonify(all_items), Config.HTTP_OK
        except Exception as e:
            logger.error(f"获取评分项列表失败：{e}")
            return jsonify({'error': str(e)}), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/save_rating', methods=['POST'])
    @token_required
    def save_rating() -> Tuple[Any, int]:
        """保存评分结果
        
        Returns:
            Tuple[Any, int]: (保存结果，HTTP 状态码)
        """
        try:
            data = request.json
            if not data:
                return jsonify({
                    'success': False, 
                    'error': '请求数据为空'
                }), Config.HTTP_BAD_REQUEST

            # 添加当前用户信息
            data['user_id'] = request.current_user_id
            
            # 获取用户信息
            user = user_manager.get_user_by_id(request.current_user_id)
            if user:
                data['rated_by_name'] = user.real_name
            
            result = data_handler.save_rating(data, app)
            
            if result.get('success'):
                return jsonify(result), Config.HTTP_OK
            else:
                return jsonify(result), Config.HTTP_BAD_REQUEST
                
        except Exception as e:
            logger.error(f"保存评分失败：{e}", exc_info=True)
            return jsonify({
                'success': False, 
                'error': f'保存失败：{str(e)}'
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/rating_last_modified/<int:index>')
    @token_required
    def get_rating_last_modified(index: int) -> Tuple[Any, int]:
        """获取评分项的最后修改信息

        Args:
            index: 评分项索引

        Returns:
            Tuple[Any, int]: (最后修改信息，HTTP 状态码)
        """
        result = data_handler.get_rating_last_modified(index)
        return jsonify(result if result else {}), Config.HTTP_OK

    @app.route('/api/heartbeat/start', methods=['POST'])
    @token_required
    def start_heartbeat() -> Tuple[Any, int]:
        """开始心跳（开始编辑评分项）

        Returns:
            Tuple[Any, int]: (结果，HTTP 状态码)
        """
        try:
            data = request.json or {}
            pair_index = data.get('pair_index')
            
            if pair_index is None:
                return jsonify({
                    'success': False,
                    'error': '缺少 pair_index 参数'
                }), Config.HTTP_BAD_REQUEST

            # 获取用户信息
            user = user_manager.get_user_by_id(request.current_user_id)
            username = user.real_name if user else request.current_user_id

            heartbeat_manager = get_heartbeat_manager()
            result = heartbeat_manager.start_heartbeat(
                pair_index, 
                request.current_user_id,
                username
            )

            if result.get('success'):
                return jsonify(result), Config.HTTP_OK
            else:
                return jsonify(result), Config.HTTP_CONFLICT

        except Exception as e:
            logger.error(f"开始心跳失败：{e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/heartbeat/stop', methods=['POST'])
    @token_required
    def stop_heartbeat() -> Tuple[Any, int]:
        """停止心跳（结束编辑）

        Returns:
            Tuple[Any, int]: (结果，HTTP 状态码)
        """
        try:
            data = request.json or {}
            pair_index = data.get('pair_index')
            
            if pair_index is None:
                return jsonify({
                    'success': False,
                    'error': '缺少 pair_index 参数'
                }), Config.HTTP_BAD_REQUEST

            heartbeat_manager = get_heartbeat_manager()
            result = heartbeat_manager.stop_heartbeat(
                pair_index, 
                request.current_user_id
            )

            return jsonify(result), Config.HTTP_OK

        except Exception as e:
            logger.error(f"停止心跳失败：{e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/rating_pair/<int:index>/status')
    @token_required
    def get_rating_pair_status(index: int) -> Tuple[Any, int]:
        """获取评分项状态（含锁信息）

        Args:
            index: 评分项索引

        Returns:
            Tuple[Any, int]: (状态信息，HTTP 状态码)
        """
        try:
            array_index = index - 1
            heartbeat_manager = get_heartbeat_manager()
            status = heartbeat_manager.get_status(array_index, request.current_user_id)
            return jsonify(status), Config.HTTP_OK
        except Exception as e:
            logger.error(f"获取状态失败：{e}")
            return jsonify({
                'error': str(e)
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/heartbeat/statistics')
    @token_required
    def get_heartbeat_statistics() -> Tuple[Any, int]:
        """获取心跳统计信息

        Returns:
            Tuple[Any, int]: (统计信息，HTTP 状态码)
        """
        try:
            heartbeat_manager = get_heartbeat_manager()
            stats = heartbeat_manager.get_statistics()
            return jsonify(stats), Config.HTTP_OK
        except Exception as e:
            logger.error(f"获取统计失败：{e}")
            return jsonify({
                'error': str(e)
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/rating_history/<int:index>')
    @token_required
    def get_rating_history(index: int) -> Tuple[Any, int]:
        """获取评分项的修改历史
        
        Args:
            index: 评分项索引
            
        Returns:
            Tuple[Any, int]: (修改历史列表，HTTP 状态码)
        """
        try:
            history = data_handler.get_rating_history(index)
            return jsonify(history), Config.HTTP_OK
        except Exception as e:
            logger.error(f"获取评分历史失败：{e}")
            return jsonify({'error': str(e)}), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/set_processing/<int:index>', methods=['POST'])
    @token_required
    def set_processing(index: int) -> Tuple[Any, int]:
        """设置评分项为处理中状态（兼容旧接口，推荐使用心跳接口）

        Args:
            index: 评分项索引

        Returns:
            Tuple[Any, int]: (设置结果，HTTP 状态码)
        """
        try:
            # 使用心跳管理器替代原来的逻辑
            array_index = index - 1
            
            # 获取用户信息
            user = user_manager.get_user_by_id(request.current_user_id)
            username = user.real_name if user else request.current_user_id

            heartbeat_manager = get_heartbeat_manager()
            result = heartbeat_manager.start_heartbeat(
                array_index, 
                request.current_user_id,
                username
            )

            if result.get('success'):
                return jsonify(result), Config.HTTP_OK
            else:
                return jsonify(result), Config.HTTP_CONFLICT
                
        except Exception as e:
            logger.error(f"设置处理状态失败：{e}")
            return jsonify({
                'success': False, 
                'error': str(e)
            }), Config.HTTP_INTERNAL_ERROR

    @app.route('/api/user/statistics')
    @token_required
    def get_user_statistics() -> Tuple[Any, int]:
        """获取当前用户的评分统计信息
        
        Returns:
            Tuple[Any, int]: (统计信息，HTTP 状态码)
        """
        try:
            user_id = request.current_user_id
            statistics = data_handler.get_user_statistics(user_id)
            return jsonify(statistics), Config.HTTP_OK
        except Exception as e:
            logger.error(f"获取用户统计失败：{e}")
            return jsonify({'error': str(e)}), Config.HTTP_INTERNAL_ERROR

    @app.route('/PDFs/<path:filename>')
    def serve_pdf(filename: str) -> Any:
        """提供 PDF 文件
        
        Args:
            filename: PDF 文件名
            
        Returns:
            Any: PDF 文件响应
        """
        return send_from_directory('PDFs', filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename: str) -> Any:
        """提供 JavaScript 文件
        
        Args:
            filename: JS 文件名
            
        Returns:
            Any: JS 文件响应
        """
        return send_from_directory('static/js', filename)

    @app.route('/static/<path:filename>')
    def serve_static_files(filename: str) -> Any:
        """提供静态文件
        
        Args:
            filename: 静态文件名
            
        Returns:
            Any: 静态文件响应
        """
        return send_from_directory('static', filename)
