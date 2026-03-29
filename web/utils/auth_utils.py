"""认证工具函数模块

该模块提供了密码加密、令牌生成和验证等认证相关的工具函数。
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """对密码进行哈希加密

    Args:
        password: 明文密码
        salt: 盐值，如果不提供则自动生成

    Returns:
        tuple: (哈希后的密码, 盐值)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return password_hash.hex(), salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """验证密码是否匹配哈希值
    
    Args:
        password: 明文密码
        hashed_password: 哈希后的密码
        salt: 盐值
        
    Returns:
        bool: 密码匹配返回True，否则返回False
    """
    password_hash, _ = hash_password(password, salt)
    return password_hash == hashed_password


def generate_token(user_id: str, secret_key: str, expires_delta: Optional[timedelta] = None) -> str:
    """生成JWT令牌
    
    Args:
        user_id: 用户ID
        secret_key: 服务器密钥
        expires_delta: 过期时间间隔
        
    Returns:
        str: JWT令牌字符串
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_delta
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def verify_token(token: str, secret_key: str) -> Optional[dict]:
    """验证JWT令牌
    
    Args:
        token: JWT令牌
        secret_key: 服务器密钥
        
    Returns:
        Optional[dict]: 解码后的令牌信息，验证失败返回None
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_salt() -> str:
    """生成随机盐值
    
    Returns:
        str: 随机生成的盐值
    """
    return secrets.token_hex(16)


def validate_username(username: str) -> bool:
    """验证用户名格式是否合法
    
    Args:
        username: 待验证的用户名
        
    Returns:
        bool: 合法返回True，否则返回False
    """
    if not username:
        return False
    if len(username) < 3 or len(username) > 20:
        return False
    return username.isalnum() or '_' in username


def validate_password(password: str) -> bool:
    """验证密码强度是否足够
    
    Args:
        password: 待验证的密码
        
    Returns:
        bool: 符合要求返回True，否则返回False
    """
    if not password:
        return False
    if len(password) < 6:
        return False
    return True