/**
 * 应用状态管理模块
 * 负责管理应用的整体状态
 */

export class AppStateModule {
    constructor() {
        this.state = {
            currentIndex: 0,
            totalItems: 0,
            allItems: [],
            // 用户认证相关信息
            isAuthenticated: false,
            currentUser: {
                userId: null,
                username: null,
                realName: null
            },
            authToken: null,
            // 评分相关信息
            currentRatings: {
                accuracy: null,
                recall: null,
                logic: null,
                comment: '',
                index: null,
                ratedBy: null,  // 评分人ID
                ratedByName: null  // 评分人姓名
            }
        };
    }

    /**
     * 获取状态
     * @param {string} key - 状态键
     * @returns {*} 状态值
     */
    get(key) {
        return this.state[key];
    }

    /**
     * 设置状态
     * @param {string} key - 状态键
     * @param {*} value - 状态值
     */
    set(key, value) {
        this.state[key] = value;
    }

    /**
     * 获取嵌套状态
     * @param {string} path - 状态路径，例如 'currentUser.username'
     * @returns {*} 状态值
     */
    getNested(path) {
        return path.split('.').reduce((obj, prop) => obj && obj[prop], this.state);
    }

    /**
     * 设置嵌套状态
     * @param {string} path - 状态路径，例如 'currentUser.username'
     * @param {*} value - 状态值
     */
    setNested(path, value) {
        const parts = path.split('.');
        const lastPart = parts.pop();
        const target = parts.reduce((obj, part) => obj[part], this.state);
        target[lastPart] = value;
    }

    /**
     * 重置评分状态
     */
    resetRatings() {
        this.state.currentRatings = {
            accuracy: null,
            recall: null,
            logic: null,
            comment: '',
            index: null,
            ratedBy: null,
            ratedByName: null
        };
    }
}