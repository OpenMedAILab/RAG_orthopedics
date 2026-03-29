"""认证路由模块

该模块定义了与用户认证相关的API路由，包括登录、注册、登出等功能。
"""

from flask import Blueprint, request, jsonify
import jwt
from models.user_model import UserManager
from utils.auth_utils import verify_password, generate_token, validate_username, validate_password
from functools import wraps


def token_required(f):
    """装饰器：验证JWT令牌

    用于保护需要认证的路由，验证请求中的JWT令牌
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 从Cookie中获取认证令牌
        token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # 使用Flask的current_app来获取配置
            from flask import current_app
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401

        # 将当前用户信息附加到请求对象上
        request.current_user_id = current_user_id
        return f(*args, **kwargs)

    return decorated


def register_auth_routes(app, user_manager, secret_key):
    """注册认证相关的路由
    
    Args:
        app: Flask应用实例
        user_manager: 用户管理器实例
        secret_key: 服务器密钥
    """
    @app.route('/api/login', methods=['POST'])
    def login_route():
        """登录路由处理函数
        
        处理用户登录请求，验证用户名和密码，返回JWT令牌
        """
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        user = user_manager.authenticate_user(username, password)
        if user:
            token = generate_token(user.user_id, secret_key)
            response_data = {
                'success': True,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'role': user.role
                }
            }
            # 创建响应对象并设置Cookie
            response = jsonify(response_data)
            # 设置认证cookie
            response.set_cookie(
                'auth_token', 
                token, 
                httponly=True, 
                secure=False,  # 在开发环境中设为False，生产环境应设为True
                samesite='Lax',
                max_age=86400  # 设置Cookie有效期为24小时
            )
            return response, 200
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    @app.route('/api/register', methods=['POST'])
    def register_route():
        """注册路由处理函数

        处理用户注册请求，创建新用户账户
        """
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # 前端可能发送 'realname' 或 'real_name'，都应处理
        real_name = data.get('realname') or data.get('real_name')

        if not username or not password or not real_name:
            return jsonify({'success': False, 'message': '用户名、密码和真实姓名不能为空'}), 400

        if not validate_username(username):
            return jsonify({'success': False, 'message': '用户名格式不合法'}), 400

        if not validate_password(password):
            return jsonify({'success': False, 'message': '密码强度不够'}), 400

        if user_manager.create_user(username, password, real_name):
            user = user_manager.get_user_by_username(username)
            return jsonify({'success': True, 'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'role': user.role
                }, 'message': '注册成功'}), 201
        else:
            return jsonify({'success': False, 'message': '用户名已存在'}), 409
    
    @app.route('/api/logout', methods=['POST'])
    @token_required
    def logout_route():
        """登出路由处理函数
        
        处理用户登出请求，使当前会话失效
        """
        response = jsonify({'success': True, 'message': '登出成功'})
        # 清除认证cookie
        response.set_cookie('auth_token', '', expires=0)
        return response, 200
    
    @app.route('/api/profile', methods=['GET'])
    @token_required
    def get_profile_route():
        """获取用户资料路由处理函数
        
        返回当前认证用户的信息
        """
        user_id = request.current_user_id
        user = user_manager.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'role': user.role,
                    'created_time': user.created_time.isoformat() if user.created_time else None
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 404