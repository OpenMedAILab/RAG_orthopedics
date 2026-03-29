"""心跳管理模块

提供基于心跳的并发控制机制，管理评分项的锁定状态。
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from config import Config

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class HeartbeatInfo:
    """心跳信息数据类
    
    Attributes:
        user_id: 用户 ID
        username: 用户名
        last_heartbeat: 最后心跳时间
        started_at: 开始编辑时间
        sequence: 心跳序列号（防止旧心跳覆盖新状态）
    """
    user_id: str
    username: str = ""
    last_heartbeat: datetime = field(default_factory=datetime.now)
    started_at: datetime = field(default_factory=datetime.now)
    sequence: int = 0  # 心跳序列号
    
    def is_active(self, timeout_seconds: int = 60) -> bool:
        """检查心跳是否仍然活跃
        
        Args:
            timeout_seconds: 超时时间（秒）
            
        Returns:
            bool: 是否活跃
        """
        timeout = timedelta(seconds=timeout_seconds)
        return datetime.now() - self.last_heartbeat < timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'started_at': self.started_at.isoformat(),
            'sequence': self.sequence,
            'is_active': True
        }


class HeartbeatManager:
    """心跳管理器
    
    管理所有评分项的心跳状态，提供锁定、释放和超时检测功能。
    
    并发安全设计：
    1. 超时时间 (60s) >> 心跳间隔 (15s)，提供 4 倍安全边际
    2. 心跳序列号机制，防止旧心跳覆盖新状态
    3. 后台线程定期清理，避免竞态条件
    
    使用示例：
        manager = HeartbeatManager()
        
        # 开始心跳
        manager.start_heartbeat(0, 'user_001', '张三')
        
        # 检查是否可编辑
        if manager.can_edit(0, 'user_002'):
            # 可以编辑
            pass
        else:
            # 被其他用户锁定
            locked_by = manager.get_lock_info(0)
            
        # 停止心跳
        manager.stop_heartbeat(0, 'user_001')
        
        # 清理超时锁
        manager.cleanup_stale_locks()
    """
    
    # 默认超时时间（秒）- 心跳间隔的 4 倍，提供安全边际
    DEFAULT_TIMEOUT = 60
    
    # 心跳间隔建议（秒）
    RECOMMENDED_INTERVAL = 15
    
    # 清理间隔（秒）
    CLEANUP_INTERVAL = 30
    
    def __init__(self, timeout_seconds: int = None) -> None:
        """初始化心跳管理器
        
        Args:
            timeout_seconds: 超时时间（秒），默认 30 秒
        """
        self._timeout = timeout_seconds or self.DEFAULT_TIMEOUT
        # 评分项索引 -> 心跳信息
        self._heartbeats: Dict[int, HeartbeatInfo] = {}
        logger.info(f"心跳管理器已初始化，超时时间：{self._timeout}秒")
    
    def start_heartbeat(
        self, 
        pair_index: int, 
        user_id: str, 
        username: str = "",
        sequence: int = None
    ) -> Dict[str, Any]:
        """开始或更新心跳
        
        Args:
            pair_index: 评分项索引（从 0 开始）
            user_id: 用户 ID
            username: 用户名
            sequence: 心跳序列号（可选，用于防止旧心跳覆盖）
            
        Returns:
            Dict[str, Any]: 结果 {'success': bool, 'message': str}
        """
        now = datetime.now()
        is_new_lock = False
        
        # 检查是否已被其他用户锁定
        if pair_index in self._heartbeats:
            existing = self._heartbeats[pair_index]
            
            if existing.user_id == user_id:
                # 同一用户的心跳更新
                if sequence is not None and sequence <= existing.sequence:
                    # 旧的心跳包，忽略（防止网络延迟导致的乱序）
                    logger.debug(
                        f"[心跳忽略] 评分项 {pair_index}, "
                        f"收到旧序列号 {sequence} <= 当前 {existing.sequence}"
                    )
                    return {
                        'success': True,
                        'message': '旧心跳，已忽略',
                        'ignored': True
                    }
                
                # 更新心跳
                existing.last_heartbeat = now
                if sequence is not None:
                    existing.sequence = sequence
                return {
                    'success': True,
                    'message': '心跳已更新',
                    'timeout': self._timeout,
                    'interval': self.RECOMMENDED_INTERVAL
                }
            
            # 被其他用户锁定
            if existing.is_active(self._timeout):
                return {
                    'success': False,
                    'message': f'评分项正在被用户 {existing.username} 编辑',
                    'locked_by': existing.to_dict()
                }
            else:
                # 原用户已超时，自动释放
                logger.info(
                    f"[心跳开始] 评分项 {pair_index} 检测到超时锁，"
                    f"原用户 {existing.user_id}，自动释放"
                )
                is_new_lock = True
        
        else:
            is_new_lock = True
        
        # 创建新的心跳
        self._heartbeats[pair_index] = HeartbeatInfo(
            user_id=user_id,
            username=username,
            last_heartbeat=now,
            started_at=now,
            sequence=sequence or 0
        )
        
        if is_new_lock:
            logger.info(f"[心跳开始] 评分项 {pair_index}, 用户：{user_id} ({username})")
        
        return {
            'success': True,
            'message': '心跳已更新',
            'timeout': self._timeout,
            'interval': self.RECOMMENDED_INTERVAL
        }
    
    def get_status(self, pair_index: int, user_id: str) -> Dict[str, Any]:
        """获取评分项的状态（含锁信息）
        
        Args:
            pair_index: 评分项索引（从 0 开始）
            user_id: 用户 ID
            
        Returns:
            Dict[str, Any]: 状态信息
        """
        if pair_index not in self._heartbeats:
            return {
                'status': Config.RATING_STATUS_IDLE,
                'can_edit': True,
                'is_mine': False
            }
        
        heartbeat = self._heartbeats[pair_index]
        
        # 检查是否超时
        if not heartbeat.is_active(self._timeout):
            return {
                'status': Config.RATING_STATUS_IDLE,
                'can_edit': True,
                'is_mine': False
            }
        
        # 活跃锁定
        is_mine = heartbeat.user_id == user_id
        return {
            'status': Config.RATING_STATUS_PROCESSING,
            'can_edit': is_mine,
            'is_mine': is_mine,
            'locked_by': heartbeat.to_dict() if not is_mine else None
        }
    
    def get_all_statuses(self, user_id: str) -> Dict[int, Dict[str, Any]]:
        """获取所有评分项的状态
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Dict[int, Dict[str, Any]]: 索引 -> 状态映射
        """
        # 先清理超时锁
        self.cleanup_stale_locks()
        
        statuses = {}
        for index, heartbeat in self._heartbeats.items():
            statuses[index] = self.get_status(index, user_id)
        
        return statuses
    
    def stop_heartbeat(self, pair_index: int, user_id: str) -> Dict[str, Any]:
        """停止心跳（用户主动释放锁）
        
        Args:
            pair_index: 评分项索引
            user_id: 用户 ID
            
        Returns:
            Dict[str, Any]: 结果
        """
        if pair_index not in self._heartbeats:
            return {'success': True, 'message': '评分项未被锁定'}
        
        heartbeat = self._heartbeats[pair_index]
        if heartbeat.user_id != user_id:
            return {
                'success': False,
                'message': '无权释放其他用户的锁'
            }
        
        username = heartbeat.username
        del self._heartbeats[pair_index]
        logger.info(f"[心跳结束] 评分项 {pair_index}, 用户：{user_id} ({username})")
        return {'success': True, 'message': '锁已释放'}
    
    def can_edit(self, pair_index: int, user_id: str) -> bool:
        """检查用户是否可以编辑评分项
        
        Args:
            pair_index: 评分项索引
            user_id: 用户 ID
            
        Returns:
            bool: 是否可以编辑
        """
        if pair_index not in self._heartbeats:
            return True
        
        heartbeat = self._heartbeats[pair_index]
        
        # 如果是自己的锁，可以编辑
        if heartbeat.user_id == user_id:
            return True
        
        # 检查是否超时
        if not heartbeat.is_active(self._timeout):
            # 超时，自动释放
            del self._heartbeats[pair_index]
            return True
        
        # 被其他活跃用户锁定
        return False
    
    def get_lock_info(self, pair_index: int) -> Optional[Dict[str, Any]]:
        """获取评分项的锁定信息
        
        Args:
            pair_index: 评分项索引
            
        Returns:
            Optional[Dict[str, Any]]: 锁定信息，未锁定返回 None
        """
        if pair_index not in self._heartbeats:
            return None
        
        heartbeat = self._heartbeats[pair_index]
        
        # 检查是否超时
        if not heartbeat.is_active(self._timeout):
            del self._heartbeats[pair_index]
            return None
        
        return heartbeat.to_dict()
    
    def get_status(self, pair_index: int, user_id: str) -> Dict[str, Any]:
        """获取评分项状态
        
        Args:
            pair_index: 评分项索引
            user_id: 用户 ID
            
        Returns:
            Dict[str, Any]: 状态信息
        """
        lock_info = self.get_lock_info(pair_index)
        
        if lock_info is None:
            return {
                'status': Config.RATING_STATUS_IDLE,
                'can_edit': True
            }
        
        if lock_info['user_id'] == user_id:
            return {
                'status': Config.RATING_STATUS_PROCESSING,
                'can_edit': True,
                'is_mine': True,
                'lock_info': lock_info
            }
        
        return {
            'status': Config.RATING_STATUS_PROCESSING,
            'can_edit': False,
            'is_mine': False,
            'locked_by': lock_info
        }
    
    def cleanup_stale_locks(self) -> int:
        """清理超时的锁
        
        Returns:
            int: 清理的锁数量
        """
        stale_keys = []
        
        for key, heartbeat in self._heartbeats.items():
            if not heartbeat.is_active(self._timeout):
                stale_keys.append(key)
        
        for key in stale_keys:
            heartbeat = self._heartbeats[key]
            logger.info(
                f"[心跳超时] 评分项 {key}, 用户：{heartbeat.user_id} ({heartbeat.username}), "
                f"超时 {self._timeout}秒"
            )
            del self._heartbeats[key]
        
        return len(stale_keys)
    
    def get_all_statuses(self, user_id: str) -> Dict[int, Dict[str, Any]]:
        """获取所有评分项的状态
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Dict[int, Dict[str, Any]]: 索引 -> 状态映射
        """
        # 先清理超时锁
        self.cleanup_stale_locks()
        
        statuses = {}
        for index in range(len(self._heartbeats) + 100):  # 估算范围
            statuses[index] = self.get_status(index, user_id)
        
        return statuses
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取心跳统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        active_locks = sum(
            1 for hb in self._heartbeats.values() 
            if hb.is_active(self._timeout)
        )
        
        return {
            'total_locks': len(self._heartbeats),
            'active_locks': active_locks,
            'timeout_seconds': self._timeout,
            'recommended_interval': self.RECOMMENDED_INTERVAL
        }


# 全局心跳管理器实例
_heartbeat_manager: Optional[HeartbeatManager] = None

# 后台清理线程
_cleanup_thread: Optional[threading.Thread] = None
_cleanup_stop_event = threading.Event()


def _cleanup_worker() -> None:
    """后台清理工作线程
    
    每隔一定时间清理超时的锁。
    """
    manager = get_heartbeat_manager()
    while not _cleanup_stop_event.is_set():
        # 等待清理间隔或停止信号
        if _cleanup_stop_event.wait(timeout=manager.CLEANUP_INTERVAL):
            break
        # 执行清理
        cleaned_count = manager.cleanup_stale_locks()
        if cleaned_count > 0:
            logger.info(f"[心跳清理] 清理了 {cleaned_count} 个超时锁")


def get_heartbeat_manager() -> HeartbeatManager:
    """获取全局心跳管理器实例
    
    Returns:
        HeartbeatManager: 心跳管理器单例
    """
    global _heartbeat_manager, _cleanup_thread
    if _heartbeat_manager is None:
        _heartbeat_manager = HeartbeatManager()
        
        # 启动后台清理线程
        _cleanup_thread = threading.Thread(target=_cleanup_worker, daemon=True)
        _cleanup_thread.start()
        logger.info("[心跳清理] 后台清理线程已启动")
    
    return _heartbeat_manager


def stop_heartbeat_manager() -> None:
    """停止心跳管理器（应用关闭时调用）"""
    global _cleanup_thread, _heartbeat_manager
    
    if _cleanup_thread:
        _cleanup_stop_event.set()
        _cleanup_thread.join(timeout=5)
        _cleanup_thread = None
    
    if _heartbeat_manager:
        _heartbeat_manager = None
    
    logger.info("[心跳清理] 心跳管理器已停止")
