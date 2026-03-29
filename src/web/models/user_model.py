"""用户数据模型模块

该模块定义了用户数据模型及相关操作方法，包括用户注册、登录验证等功能。
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from utils.auth_utils import hash_password, verify_password


class User:
    """用户数据模型类
    
    该类表示系统中的一个用户，包含用户的基本信息和操作方法
    """
    
    def __init__(self, user_id, username, password_hash, real_name, role='user', created_time=None, last_login=None):
        """初始化用户对象
        
        Args:
            user_id: 用户唯一标识符
            username: 用户名
            password_hash: 密码哈希值
            real_name: 用户真实姓名
            role: 用户角色，默认为'user'
            created_time: 账户创建时间
            last_login: 最后登录时间
        """
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.real_name = real_name
        self.role = role
        self.created_time = created_time or datetime.now()
        self.last_login = last_login
    
    def to_dict(self):
        """将用户对象转换为字典格式
        
        Returns:
            dict: 包含用户信息的字典
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'real_name': self.real_name,
            'role': self.role,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class UserManager:
    """用户管理类
    
    该类负责管理所有用户数据，包括用户的增删改查、登录验证等操作
    """
    
    def __init__(self, users_file='users.json'):
        """初始化用户管理器
        
        Args:
            users_file: 存储用户数据的文件路径
        """
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self):
        """从文件加载用户数据
        
        Returns:
            dict: 用户数据字典，键为用户名，值为User对象
        """
        if Path(self.users_file).exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            users = {}
            for user_data in data.values():
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    real_name=user_data['real_name'],
                    role=user_data['role'],
                    created_time=datetime.fromisoformat(user_data['created_time']) if user_data['created_time'] else None,
                    last_login=datetime.fromisoformat(user_data['last_login']) if user_data['last_login'] else None
                )
                users[user.username] = user
            return users
        else:
            return {}
    
    def _save_users(self):
        """将用户数据保存到文件"""
        data = {username: user.to_dict() for username, user in self.users.items()}
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_user(self, username, password, real_name, role='user'):
        """创建新用户

        Args:
            username: 用户名
            password: 明文密码
            real_name: 用户真实姓名
            role: 用户角色

        Returns:
            bool: 创建成功返回True，否则返回False
        """
        if username in self.users:
            return False

        password_hash, salt = hash_password(password)
        # 将哈希值和盐值组合存储
        combined_hash = f"{password_hash}:{salt}"
        user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5((username + str(datetime.now())).encode()).hexdigest()[:8]}"
        user = User(
            user_id=user_id,
            username=username,
            password_hash=combined_hash,
            real_name=real_name,
            role=role
        )
        self.users[username] = user
        self._save_users()
        return True
    
    def authenticate_user(self, username, password):
        """验证用户登录信息

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            User or None: 验证成功返回User对象，否则返回None
        """
        if username not in self.users:
            return None

        user = self.users[username]
        # 由于hash_password函数会生成新的salt，我们需要从存储的密码中提取salt来验证
        # 这里假设密码哈希格式为 "hash:salt"
        stored_hash_parts = user.password_hash.split(':')
        if len(stored_hash_parts) != 2:
            return None

        stored_hash, stored_salt = stored_hash_parts
        # 直接比较计算出的哈希值与存储的哈希值
        input_password_hash, _ = hash_password(password, stored_salt)

        if input_password_hash == stored_hash:
            self.update_last_login(username)
            self._save_users()
            return user
        return None
    
    def get_user_by_username(self, username):
        """根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            User or None: 找到返回User对象，否则返回None
        """
        return self.users.get(username)
    
    def get_user_by_id(self, user_id):
        """根据用户ID获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            User or None: 找到返回User对象，否则返回None
        """
        for user in self.users.values():
            if user.user_id == user_id:
                return user
        return None
    
    def update_last_login(self, username):
        """更新用户的最后登录时间
        
        Args:
            username: 用户名
        """
        if username in self.users:
            self.users[username].last_login = datetime.now()
    
    def change_password(self, username, old_password, new_password):
        """修改用户密码

        Args:
            username: 用户名
            old_password: 旧密码
            new_password: 新密码

        Returns:
            bool: 修改成功返回True，否则返回False
        """
        user = self.get_user_by_username(username)
        if not user:
            return False

        # 验证旧密码
        stored_hash_parts = user.password_hash.split(':')
        if len(stored_hash_parts) != 2:
            return False

        stored_hash, stored_salt = stored_hash_parts
        # 验证用户输入的旧密码是否正确
        input_old_password_hash, _ = hash_password(old_password, stored_salt)
        if input_old_password_hash != stored_hash:
            return False

        # 设置新密码
        new_password_hash, new_salt = hash_password(new_password)
        user.password_hash = f"{new_password_hash}:{new_salt}"
        self._save_users()
        return True