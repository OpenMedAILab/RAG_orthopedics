/**
 * 数据管理模块
 * 负责处理数据加载和 API 请求（对比评分模式）
 */

export class DataModule {
    constructor() {
        this.mode = 'comparison';
    }

    /**
     * 获取当前模式
     * @returns {string} 当前模式
     */
    getMode() {
        return this.mode;
    }

    /**
     * 加载所有评分项
     * @returns {Promise<Array>} 评分项列表
     */
    async loadAllItems() {
        try {
            const response = await this.fetchData('/api/all_ratings');
            console.log('列表已刷新');
            return response;
        } catch (error) {
            console.error('Error loading items:', error);
            throw error;
        }
    }

    /**
     * 加载特定评分项（对比模式）
     * @param {number} index - 评分项索引
     */
    async loadItem(index) {
        try {
            const response = await this.fetchData(`/api/rating_pair/${index}`);
            return response;
        } catch (error) {
            console.error('Error loading item:', error);
            throw error;
        }
    }

    /**
     * 保存评分（支持对比模式）
     * @param {Object} data - 评分数据
     */
    async saveRating(data) {
        try {
            const response = await fetch('/api/save_rating', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error saving rating:', error);
            throw error;
        }
    }

    /**
     * 设置评分项为处理中状态
     * @param {number} index - 评分项索引
     * @param {string} userId - 用户 ID
     * @returns {Promise<{success: boolean, message?: string, locked_by?: Object}>} 结果
     */
    async setProcessing(index, userId) {
        try {
            const response = await fetch(`/api/set_processing/${index}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId }),
                credentials: 'include'
            });

            // 409 Conflict 表示被其他用户锁定，这是正常情况，不是错误
            if (response.status === 409) {
                const result = await response.json();
                return result;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('设置处理状态失败:', error);
            throw error;
        }
    }

    /**
     * 刷新评分项列表
     */
    async refreshAllItems() {
        try {
            const response = await this.fetchData('/api/all_ratings');
            return response;
        } catch (error) {
            console.error('Error refreshing items:', error);
            throw error;
        }
    }

    /**
     * 数据获取辅助函数
     * @param {string} url - 请求 URL
     */
    async fetchData(url) {
        const response = await fetch(url, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error(`HTTP error! status: ${response.status} (Unauthorized)`);
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await response.text();
            console.error("Response is not JSON:", text);
            throw new Error("Response is not JSON");
        }

        return await response.json();
    }
}
