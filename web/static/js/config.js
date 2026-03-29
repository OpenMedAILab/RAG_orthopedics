/**
 * 应用常量配置
 * 
 * 集中管理应用的所有常量，便于维护和统一修改。
 */

export const Config = {
    // ==================== 应用配置 ====================
    
    /** 应用名称 */
    APP_NAME: '医学问答对比评分系统',
    
    /** 应用副标题 */
    APP_SUBTITLE: 'Medical Q&A Evaluation Platform',
    
    // ==================== API 配置 ====================
    
    /** API 基础路径 */
    API_BASE: '',
    
    /** API 端点 */
    API_ENDPOINTS: {
        // 认证相关
        LOGIN: '/api/login',
        REGISTER: '/api/register',
        LOGOUT: '/api/logout',
        PROFILE: '/api/profile',
        
        // 评分相关
        ALL_RATINGS: '/api/all_ratings',
        RATING_PAIR: (index) => `/api/rating_pair/${index}`,
        SAVE_RATING: '/api/save_rating',
        SET_PROCESSING: (index) => `/api/set_processing/${index}`,
        RATING_LAST_MODIFIED: (index) => `/api/rating_last_modified/${index}`,
        RATING_HISTORY: (index) => `/api/rating_history/${index}`,
        
        // 心跳相关
        HEARTBEAT_START: '/api/heartbeat/start',
        HEARTBEAT_STOP: '/api/heartbeat/stop',
        RATING_PAIR_STATUS: (index) => `/api/rating_pair/${index}/status`,
        
        // 用户统计
        USER_STATISTICS: '/api/user/statistics'
    },
    
    // ==================== 评分配置 ====================
    
    /** 评分维度 */
    RATING_DIMENSIONS: {
        ACCURACY: 'medical_accuracy',      // 医学准确性
        RECALL: 'key_point_recall',         // 关键要点召回率
        LOGIC: 'logical_completeness'       // 逻辑完整性
    },
    
    /** 评分维度显示名称 */
    RATING_DIMENSION_LABELS: {
        medical_accuracy: '医学准确性',
        key_point_recall: '关键要点召回率',
        logical_completeness: '逻辑完整性'
    },
    
    /** 评分范围 */
    RATING_MIN: 1,
    RATING_MAX: 3,
    
    /** 评分描述 */
    RATING_LABELS: {
        1: '差',
        2: '中',
        3: '好'
    },
    
    // ==================== 侧边配置 ====================
    
    /** 侧边标识 */
    SIDES: {
        A: 'side_a',
        B: 'side_b'
    },
    
    /** 侧边显示名称 */
    SIDE_LABELS: {
        side_a: 'A 侧',
        side_b: 'B 侧'
    },
    
    /** 模式标识 */
    MODES: {
        NORAG: 'NoRAG',
        RAG: 'RAG'
    },
    
    /** 模式显示名称 */
    MODE_LABELS: {
        NoRAG: '无 RAG 模式',
        RAG: 'RAG 模式'
    },
    
    // ==================== 状态配置 ====================
    
    /** 评分状态 */
    STATUS: {
        IDLE: 'idle',           // 空闲
        PROCESSING: 'processing',  // 处理中
        COMPLETED: 'completed'   // 已完成
    },
    
    /** 状态显示名称 */
    STATUS_LABELS: {
        idle: '未评分',
        processing: '进行中',
        completed: '已完成'
    },
    
    // ==================== 验证规则 ====================
    
    /** 用户名最小长度 */
    USERNAME_MIN_LENGTH: 3,
    
    /** 用户名最大长度 */
    USERNAME_MAX_LENGTH: 20,
    
    /** 密码最小长度 */
    PASSWORD_MIN_LENGTH: 6,
    
    // ==================== UI 配置 ====================
    
    /** 通知显示时间（毫秒） */
    NOTIFICATION_DURATION: 3000,
    
    /** 列表自动刷新间隔（毫秒） */
    REFRESH_INTERVAL: 10000,
    
    // ==================== 心跳配置 ====================
    
    /** 心跳间隔（毫秒） */
    HEARTBEAT_INTERVAL: 15000,
    
    /** 心跳超时时间（毫秒）- 心跳间隔的 4 倍，提供安全边际 */
    HEARTBEAT_TIMEOUT: 60000,
    
    // ==================== 消息配置 ====================
    
    /** 成功消息前缀 */
    MSG_SUCCESS: '✓',
    
    /** 错误消息前缀 */
    MSG_ERROR: '✕',
    
    /** 默认成功消息 */
    DEFAULT_SUCCESS_MESSAGE: '操作成功',
    
    /** 默认错误消息 */
    DEFAULT_ERROR_MESSAGE: '操作失败',
    
    // ==================== 辅助方法 ====================
    
    /**
     * 获取评分维度标签
     * @param {string} dimension - 评分维度
     * @returns {string} 维度标签
     */
    getDimensionLabel(dimension) {
        return this.RATING_DIMENSION_LABELS[dimension] || dimension;
    },
    
    /**
     * 获取状态标签
     * @param {string} status - 状态值
     * @returns {string} 状态标签
     */
    getStatusLabel(status) {
        return this.STATUS_LABELS[status] || status;
    },
    
    /**
     * 验证评分值是否有效
     * @param {number} score - 评分值
     * @returns {boolean} 是否有效
     */
    isValidRating(score) {
        return Number.isInteger(score) && 
               score >= this.RATING_MIN && 
               score <= this.RATING_MAX;
    },
    
    /**
     * 验证用户名是否有效
     * @param {string} username - 用户名
     * @returns {boolean} 是否有效
     */
    isValidUsername(username) {
        if (!username) return false;
        const len = username.length;
        return len >= this.USERNAME_MIN_LENGTH && len <= this.USERNAME_MAX_LENGTH;
    },
    
    /**
     * 验证密码是否有效
     * @param {string} password - 密码
     * @returns {boolean} 是否有效
     */
    isValidPassword(password) {
        return password && password.length >= this.PASSWORD_MIN_LENGTH;
    }
};

// 冻结配置对象，防止意外修改
Object.freeze(Config);
