/**
 * 工具函数模块
 * 
 * 提供通用的工具函数，包括验证、格式化、错误处理等。
 */

import { Config } from './config.js';

/**
 * 工具函数集合
 */
export const Utils = {
    // ==================== 验证函数 ====================
    
    /**
     * 验证评分数据是否完整
     * @param {Object} ratings - 评分对象
     * @returns {{valid: boolean, missing: string[]}} 验证结果
     */
    validateRatings(ratings) {
        const missing = [];
        const dimensions = Object.values(Config.RATING_DIMENSIONS);
        
        for (const side of [Config.SIDES.A, Config.SIDES.B]) {
            const sideRatings = ratings[side] || {};
            for (const dim of dimensions) {
                if (sideRatings[dim] == null) {
                    missing.push(`${side}.${dim}`);
                }
            }
        }
        
        return {
            valid: missing.length === 0,
            missing
        };
    },
    
    /**
     * 验证用户登录信息
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {{valid: boolean, errors: string[]}} 验证结果
     */
    validateLogin(username, password) {
        const errors = [];
        
        if (!Config.isValidUsername(username)) {
            errors.push(`用户名长度应为 ${Config.USERNAME_MIN_LENGTH}-${Config.USERNAME_MAX_LENGTH} 位`);
        }
        
        if (!Config.isValidPassword(password)) {
            errors.push(`密码长度至少为 ${Config.PASSWORD_MIN_LENGTH} 位`);
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    /**
     * 验证用户注册信息
     * @param {Object} data - 注册数据
     * @returns {{valid: boolean, errors: string[]}} 验证结果
     */
    validateRegister(data) {
        const errors = [];
        const { username, realname, password, confirmPassword } = data;
        
        if (!Config.isValidUsername(username)) {
            errors.push(`用户名长度应为 ${Config.USERNAME_MIN_LENGTH}-${Config.USERNAME_MAX_LENGTH} 位`);
        }
        
        if (!realname || realname.trim().length === 0) {
            errors.push('真实姓名不能为空');
        }
        
        if (!Config.isValidPassword(password)) {
            errors.push(`密码长度至少为 ${Config.PASSWORD_MIN_LENGTH} 位`);
        }
        
        if (password !== confirmPassword) {
            errors.push('两次输入的密码不一致');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    // ==================== 格式化函数 ====================
    
    /**
     * 格式化日期时间
     * @param {string|Date} date - 日期对象或字符串
     * @param {string} format - 格式模板
     * @returns {string} 格式化后的日期字符串
     */
    formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        
        if (isNaN(d.getTime())) {
            return '-';
        }
        
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    /**
     * 格式化相对时间
     * @param {string|Date} date - 日期对象或字符串
     * @returns {string} 相对时间描述
     */
    formatRelativeTime(date) {
        const d = new Date(date);
        const now = new Date();
        const diffMs = now - d;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) {
            return '刚刚';
        } else if (diffMins < 60) {
            return `${diffMins}分钟前`;
        } else if (diffHours < 24) {
            return `${diffHours}小时前`;
        } else if (diffDays < 7) {
            return `${diffDays}天前`;
        } else {
            return this.formatDateTime(d, 'YYYY-MM-DD');
        }
    },
    
    /**
     * 格式化数字（添加千位分隔符）
     * @param {number} num - 数字
     * @returns {string} 格式化后的字符串
     */
    formatNumber(num) {
        if (num == null) return '-';
        return Number(num).toLocaleString('zh-CN');
    },
    
    /**
     * 计算百分比
     * @param {number} current - 当前值
     * @param {number} total - 总值
     * @returns {number} 百分比（0-100）
     */
    calculatePercentage(current, total) {
        if (!total || total === 0) return 0;
        return Math.round((current / total) * 100);
    },
    
    // ==================== 错误处理 ====================
    
    /**
     * 处理 API 响应错误
     * @param {Response} response - Fetch API 响应对象
     * @returns {Promise<any>} 响应数据
     * @throws {Error} 如果响应失败
     */
    async handleResponse(response) {
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            
            try {
                const data = await response.json();
                errorMessage = data.message || data.error || errorMessage;
            } catch {
                // 无法解析 JSON，使用默认错误消息
            }
            
            throw new Error(errorMessage);
        }
        
        // 检查响应类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('服务器返回了非 JSON 响应');
        }
        
        return response.json();
    },
    
    /**
     * 安全的异步操作包装器
     * @param {Promise} promise - 要执行的 Promise
     * @param {string} errorMessage - 错误消息
     * @returns {Promise<[any, Error|null]>} [结果，错误]
     */
    async wrapAsync(promise, errorMessage = '操作失败') {
        try {
            const result = await promise;
            return [result, null];
        } catch (error) {
            console.error(`${errorMessage}:`, error);
            return [null, error];
        }
    },
    
    // ==================== DOM 工具 ====================
    
    /**
     * 安全地获取元素
     * @param {string} selector - CSS 选择器
     * @param {Element} context - 搜索上下文
     * @returns {Element|null} 找到的元素或 null
     */
    getElement(selector, context = document) {
        return context.querySelector(selector);
    },
    
    /**
     * 安全地获取所有匹配元素
     * @param {string} selector - CSS 选择器
     * @param {Element} context - 搜索上下文
     * @returns {NodeList} 元素列表
     */
    getAllElements(selector, context = document) {
        return context.querySelectorAll(selector);
    },
    
    /**
     * 设置元素文本内容
     * @param {string} selector - CSS 选择器
     * @param {string} text - 文本内容
     * @param {Element} context - 搜索上下文
     */
    setText(selector, text, context = document) {
        const el = this.getElement(selector, context);
        if (el) {
            el.textContent = text || '-';
        }
    },
    
    /**
     * 设置元素 HTML 内容
     * @param {string} selector - CSS 选择器
     * @param {string} html - HTML 内容
     * @param {Element} context - 搜索上下文
     */
    setHTML(selector, html, context = document) {
        const el = this.getElement(selector, context);
        if (el) {
            el.innerHTML = html || '';
        }
    },
    
    /**
     * 切换元素可见性
     * @param {string} selector - CSS 选择器
     * @param {boolean} show - 是否显示
     * @param {Element} context - 搜索上下文
     */
    toggleVisibility(selector, show, context = document) {
        const el = this.getElement(selector, context);
        if (el) {
            el.style.display = show ? '' : 'none';
        }
    },
    
    /**
     * 添加 CSS 类
     * @param {string} selector - CSS 选择器
     * @param {string} className - 类名
     * @param {Element} context - 搜索上下文
     */
    addClass(selector, className, context = document) {
        const el = this.getElement(selector, context);
        if (el) {
            el.classList.add(className);
        }
    },
    
    /**
     * 移除 CSS 类
     * @param {string} selector - CSS 选择器
     * @param {string} className - 类名
     * @param {Element} context - 搜索上下文
     */
    removeClass(selector, className, context = document) {
        const el = this.getElement(selector, context);
        if (el) {
            el.classList.remove(className);
        }
    },
    
    // ==================== 存储工具 ====================
    
    /**
     * 安全地从 localStorage 获取数据
     * @param {string} key - 存储键
     * @returns {any|null} 存储的数据
     */
    getFromStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch {
            return null;
        }
    },
    
    /**
     * 安全地存储数据到 localStorage
     * @param {string} key - 存储键
     * @param {any} value - 存储值
     * @returns {boolean} 是否成功
     */
    setToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch {
            return false;
        }
    },
    
    /**
     * 从 localStorage 移除数据
     * @param {string} key - 存储键
     */
    removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch {
            // 忽略错误
        }
    }
};

// 冻结工具对象
Object.freeze(Utils);
