/**
 * 认证模块
 * 负责处理用户认证相关功能
 */

export class AuthModule {
    constructor() {
        this.tokenKey = 'auth_token';
        this.userKey = 'current_user';
        // 缓存认证状态，避免重复检查
        this.cachedAuthStatus = null;
    }

    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise<Object>} 登录结果
     */
    async login(username, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password }),
                credentials: 'include'
            });

            const data = await response.json();

            if (data.success) {
                // Cookie 会自动设置，同时缓存认证状态
                this.cachedAuthStatus = true;
                return { success: true, user: data.user };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            return { success: false, message: '网络错误，请稍后重试' };
        }
    }

    /**
     * 用户登出
     */
    async logout() {
        try {
            await fetch('/api/logout', {
                method: 'POST',
                credentials: 'include'
            });
            // 清除缓存的认证状态
            this.cachedAuthStatus = null;
        } catch (error) {
            console.error('登出请求失败:', error);
        }
    }

    /**
     * 检查用户是否已认证
     * 通过向服务器发送请求来验证认证状态
     * 使用缓存避免重复请求
     * @returns {Promise<boolean>} 认证状态
     */
    async isAuthenticated() {
        // 如果已经有缓存的认证状态，直接返回
        if (this.cachedAuthStatus !== null) {
            return this.cachedAuthStatus;
        }

        // 向服务器验证认证状态
        try {
            const response = await fetch('/api/profile', {
                method: 'GET',
                credentials: 'include'  // 发送 Cookie（包括 HttpOnly Cookie）
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Token 有效，用户已认证
                    this.cachedAuthStatus = true;
                    return true;
                }
            } else if (response.status === 401) {
                // Token 已过期或无效，确认未认证
                this.cachedAuthStatus = false;
                return false;
            }

            // 服务器错误等其他情况，默认返回未认证
            this.cachedAuthStatus = false;
            return false;

        } catch (error) {
            // 网络错误时，返回 false
            console.warn('验证认证状态时网络错误:', error);
            this.cachedAuthStatus = false;
            return false;
        }
    }

    /**
     * 用户注册
     * @param {string} username - 用户名
     * @param {string} realname - 真实姓名
     * @param {string} password - 密码
     * @returns {Promise<Object>} 注册结果
     */
    async register(username, realname, password) {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, realname, password })
            });

            const data = await response.json();

            if (data.success) {
                return { success: true, user: data.user };
            } else {
                return { success: false, message: data.message };
            }
        } catch (error) {
            console.error('注册请求失败:', error);
            return { success: false, message: '网络错误，请稍后重试' };
        }
    }

    /**
     * 获取缓存的认证状态
     * @returns {boolean|null} 认证状态，null 表示未检查
     */
    getCachedAuthStatus() {
        return this.cachedAuthStatus;
    }
}
