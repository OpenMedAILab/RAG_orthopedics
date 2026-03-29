/**
 * 心跳管理模块
 * 
 * 管理评分项编辑状态的心跳机制，实现并发控制。
 * 只有在用户实际编辑评分时才发送心跳，查看不会触发锁定。
 */

import { Config } from './config.js';
import { Utils } from './utils.js';

/**
 * 心跳管理器类
 * 
 * 使用示例：
 * const heartbeat = new HeartbeatManager();
 * 
 * // 开始编辑
 * await heartbeat.startEditing(0);
 * 
 * // 停止编辑
 * await heartbeat.stopEditing(0);
 * 
 * // 页面卸载时自动清理
 * window.addEventListener('beforeunload', () => heartbeat.cleanup());
 */
export class HeartbeatManager {
    /**
     * 创建心跳管理器
     */
    constructor() {
        /** @type {Map<number, HeartbeatSession>} 活跃的心跳会话 */
        this.sessions = new Map();
        
        /** @type {number} 心跳间隔（毫秒） */
        this.interval = Config.HEARTBEAT_INTERVAL || 15000;
        
        /** @type {number} 超时时间（毫秒） */
        this.timeout = Config.HEARTBEAT_TIMEOUT || 30000;
        
        /** @type {Map<number, number>} 心跳定时器 */
        this.timers = new Map();
        
        /** @type {string|null} 当前用户 ID */
        this.currentUserId = null;
        
        /** @type {string|null} 当前用户名 */
        this.currentUserName = null;
    }
    
    /**
     * 设置当前用户信息
     * @param {string} userId - 用户 ID
     * @param {string} userName - 用户名
     */
    setCurrentUser(userId, userName) {
        this.currentUserId = userId;
        this.currentUserName = userName;
    }
    
    /**
     * 开始编辑评分项（启动心跳）
     * @param {number} pairIndex - 评分项索引（从 0 开始）
     * @returns {Promise<{success: boolean, message: string}>} 结果
     */
    async startEditing(pairIndex) {
        if (!this.currentUserId) {
            return { success: false, message: '用户未登录' };
        }
        
        // 如果已经在编辑中，刷新心跳
        if (this.sessions.has(pairIndex)) {
            return { success: true, message: '心跳已刷新' };
        }
        
        try {
            const response = await fetch(Config.API_ENDPOINTS.HEARTBEAT_START, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ pair_index: pairIndex })
            });
            
            const result = await Utils.handleResponse(response);
            
            if (result.success) {
                // 创建会话
                const session = new HeartbeatSession(
                    pairIndex,
                    this.currentUserId,
                    this.currentUserName,
                    result.interval || this.interval
                );
                this.sessions.set(pairIndex, session);
                
                // 启动心跳定时器
                this._startTimer(pairIndex);
                
                console.log(`[心跳开始] 评分项 ${pairIndex}`);
                return { success: true, message: '已开始编辑' };
            } else {
                return result;
            }
        } catch (error) {
            console.error('[Heartbeat] 开始编辑失败:', error);
            return { success: false, message: '网络错误' };
        }
    }
    
    /**
     * 停止编辑评分项（停止心跳）
     * @param {number} pairIndex - 评分项索引
     * @returns {Promise<{success: boolean, message: string}>} 结果
     */
    async stopEditing(pairIndex) {
        if (!this.sessions.has(pairIndex)) {
            return { success: true, message: '未在编辑中' };
        }
        
        try {
            // 停止定时器
            this._stopTimer(pairIndex);
            
            // 发送停止请求
            const response = await fetch(Config.API_ENDPOINTS.HEARTBEAT_STOP, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ pair_index: pairIndex })
            });
            
            await Utils.handleResponse(response);
            
            // 移除会话
            this.sessions.delete(pairIndex);
            
            console.log(`[心跳结束] 评分项 ${pairIndex}`);
            return { success: true, message: '已停止编辑' };
        } catch (error) {
            console.error('[Heartbeat] 停止编辑失败:', error);
            // 即使请求失败也移除会话
            this.sessions.delete(pairIndex);
            return { success: false, message: '停止失败' };
        }
    }
    
    /**
     * 检查是否可以编辑评分项
     * @param {number} pairIndex - 评分项索引
     * @returns {Promise<{canEdit: boolean, lockedBy?: Object}>} 检查结果
     */
    async canEdit(pairIndex) {
        try {
            const response = await fetch(
                Config.API_ENDPOINTS.RATING_PAIR_STATUS(pairIndex + 1)
            );
            
            const status = await Utils.handleResponse(response);
            return {
                canEdit: status.can_edit,
                lockedBy: status.locked_by || null,
                isMine: status.is_mine || false
            };
        } catch (error) {
            console.error('[Heartbeat] 检查编辑状态失败:', error);
            return { canEdit: true, lockedBy: null }; // 默认可以编辑
        }
    }
    
    /**
     * 启动心跳定时器
     * @param {number} pairIndex - 评分项索引
     * @private
     */
    _startTimer(pairIndex) {
        this._stopTimer(pairIndex); // 先停止已有的定时器
        
        const timer = setInterval(async () => {
            const session = this.sessions.get(pairIndex);
            if (!session) {
                this._stopTimer(pairIndex);
                return;
            }
            
            try {
                // 发送带序列号的心跳
                const sequence = session.nextSequence();
                await fetch(Config.API_ENDPOINTS.HEARTBEAT_START, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ 
                        pair_index: pairIndex,
                        heartbeat: true,
                        sequence: sequence
                    })
                });
                session.lastBeat = Date.now();
                // 中间心跳不输出日志
            } catch (error) {
                // 心跳失败不输出错误，避免日志过多
            }
        }, this.interval);
        
        this.timers.set(pairIndex, timer);
    }
    
    /**
     * 停止心跳定时器
     * @param {number} pairIndex - 评分项索引
     * @private
     */
    _stopTimer(pairIndex) {
        const timer = this.timers.get(pairIndex);
        if (timer) {
            clearInterval(timer);
            this.timers.delete(pairIndex);
        }
    }
    
    /**
     * 获取活跃的编辑会话
     * @returns {Map<number, HeartbeatSession>} 会话映射
     */
    getActiveSessions() {
        return new Map(this.sessions);
    }
    
    /**
     * 清理所有会话（页面卸载时调用）
     */
    async cleanup() {
        // 停止所有定时器
        for (const [pairIndex] of this.timers) {
            this._stopTimer(pairIndex);
        }
        
        // 停止所有心跳（异步，不等待）
        const promises = [];
        for (const [pairIndex] of this.sessions) {
            promises.push(
                fetch(Config.API_ENDPOINTS.HEARTBEAT_STOP, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ pair_index: pairIndex })
                }).catch(() => {}) // 忽略错误
            );
        }
        
        // 等待所有停止请求（最多 2 秒）
        await Promise.race([
            Promise.all(promises),
            new Promise(resolve => setTimeout(resolve, 2000))
        ]);
        
        this.sessions.clear();
    }
    
    /**
     * 获取统计信息
     * @returns {Object} 统计信息
     */
    getStatistics() {
        return {
            activeSessions: this.sessions.size,
            interval: this.interval,
            timeout: this.timeout,
            currentUserId: this.currentUserId
        };
    }
}

/**
 * 心跳会话类
 * 
 * 跟踪单个评分项的编辑会话状态。
 */
class HeartbeatSession {
    /**
     * 创建心跳会话
     * @param {number} pairIndex - 评分项索引
     * @param {string} userId - 用户 ID
     * @param {string} userName - 用户名
     * @param {number} interval - 心跳间隔（毫秒）
     */
    constructor(pairIndex, userId, userName, interval) {
        /** @type {number} */
        this.pairIndex = pairIndex;
        
        /** @type {string} */
        this.userId = userId;
        
        /** @type {string} */
        this.userName = userName;
        
        /** @type {number} */
        this.interval = interval;
        
        /** @type {number} 最后心跳时间戳 */
        this.lastBeat = Date.now();
        
        /** @type {number} 开始时间戳 */
        this.startedAt = Date.now();
        
        /** @type {number} 心跳序列号 */
        this.sequence = 0;
    }
    
    /**
     * 获取下一个序列号
     * @returns {number} 序列号
     */
    nextSequence() {
        return ++this.sequence;
    }
    
    /**
     * 获取会话信息
     * @returns {Object} 会话信息对象
     */
    getInfo() {
        return {
            pairIndex: this.pairIndex,
            userId: this.userId,
            userName: this.userName,
            lastBeat: this.lastBeat,
            startedAt: this.startedAt,
            sequence: this.sequence,
            duration: Date.now() - this.startedAt
        };
    }
}
