/**
 * 主应用模块
 * 负责协调各个模块的工作（支持对比评分模式）
 */

import { AuthModule } from './modules/auth.js';
import { DataModule } from './modules/data.js';
import { UIModule } from './modules/ui.js';
import { RatingModule } from './modules/rating.js';
import { NavigationModule } from './modules/navigation.js';
import { AppStateModule } from './modules/app-state.js';

class App {
    constructor() {
        this.appState = new AppStateModule();
        this.auth = new AuthModule();
        this.data = new DataModule();
        this.ui = new UIModule();
        this.rating = new RatingModule();
        this.navigation = new NavigationModule();

        this.initializeEventListeners();
    }

    /**
     * 初始化应用
     */
    async init() {
        try {
            // 检查认证状态
            const isAuthenticated = await this.auth.isAuthenticated();
            this.appState.set('isAuthenticated', isAuthenticated);

            if (isAuthenticated) {
                // 获取用户信息
                try {
                    const response = await fetch('/api/profile', {
                        credentials: 'include'
                    });
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            // 后端返回的字段是 user_id 和 real_name，需要转换为 userId 和 realName
                            const user = data.user;
                            const currentUser = {
                                userId: user.user_id,
                                username: user.username,
                                realName: user.real_name,
                                role: user.role
                            };
                            this.appState.set('currentUser', currentUser);
                        } else {
                            this.appState.set('isAuthenticated', false);
                            this.appState.set('currentUser', {
                                userId: null,
                                username: null,
                                realName: null
                            });
                        }
                    } else if (response.status === 401) {
                        this.appState.set('isAuthenticated', false);
                        this.appState.set('currentUser', {
                            userId: null,
                            username: null,
                            realName: null
                        });
                    }
                } catch (error) {
                    console.error('获取用户信息失败:', error);
                }
            } else {
                this.appState.set('currentUser', {
                    userId: null,
                    username: null,
                    realName: null
                });
            }

            // 更新用户界面
            if (this.ui) {
                this.ui.updateUserDisplay(this.appState.get('currentUser'));
                this.ui.updateAuthButtons(this.appState.get('isAuthenticated'));
            }

            // 只有在确认用户已认证的情况下才尝试加载数据
            if (this.appState.get('isAuthenticated')) {
                try {
                    const items = await this.data.loadAllItems();
                    this.appState.set('allItems', items);
                    this.appState.set('totalItems', items.length);

                    if (this.appState.get('totalItems') > 0) {
                        if (this.ui) {
                            this.renderApp();
                        }
                        // 加载第一个项目
                        await this.loadItemAtIndex(0);
                    } else {
                        if (this.ui) {
                            this.ui.showLoadingMessage('没有找到评分项');
                        }
                    }
                } catch (error) {
                    if (error.message && error.message.includes('401')) {
                        this.appState.set('isAuthenticated', false);
                        this.appState.set('currentUser', {
                            userId: null,
                            username: null,
                            realName: null
                        });

                        if (this.ui) {
                            this.ui.updateUserDisplay(this.appState.get('currentUser'));
                            this.ui.updateAuthButtons(this.appState.get('isAuthenticated'));
                            this.ui.showLoadingMessage('登录已过期，请重新登录');
                        }
                    } else {
                        console.error('Error loading items:', error);
                        if (this.ui) {
                            this.ui.showErrorWithReload('加载评分项时出错：' + error.message);
                        }
                    }
                }
            } else {
                if (this.ui) {
                    this.ui.showLoadingMessage('请先登录以查看评分数据');
                }
            }

        } catch (error) {
            console.error('Initialization error:', error);
            if (this.ui) {
                if (error.message && error.message.includes('401')) {
                    this.appState.set('isAuthenticated', false);
                    this.appState.set('currentUser', {
                        userId: null,
                        username: null,
                        realName: null
                    });

                    this.ui.updateUserDisplay(this.appState.get('currentUser'));
                    this.ui.updateAuthButtons(this.appState.get('isAuthenticated'));
                    this.ui.showLoadingMessage('登录已过期，请重新登录');
                } else {
                    this.ui.showErrorWithReload('加载评分项时出错：' + error.message);
                }
            }
        } finally {
            try {
                this.bindEventListeners();
            } catch (bindingError) {
                console.error('Error binding event listeners:', bindingError);
            }
        }
    }

    /**
     * 渲染应用界面
     */
    renderApp() {
        this.ui.renderItemsGrid(
            this.appState.get('allItems'),
            this.appState.get('currentIndex'),
            (index) => this.handleItemClick(index)
        );
        this.ui.updateProgressInfo(
            this.appState.get('allItems'),
            this.appState.get('totalItems')
        );
        this.ui.hideLoading();
    }

    /**
     * 加载指定索引的项目
     * @param {number} index - 项目索引（数组索引，从 0 开始）
     */
    async loadItemAtIndex(index) {
        if (index < 0 || index >= this.appState.get('totalItems')) return;

        console.log(`[loadItemAtIndex] 开始加载项目 ${index + 1}`);

        // 先更新当前索引
        this.appState.set('currentIndex', index);

        // 使用数组索引 + 1 作为 API 期望的 index 参数
        const apiIndex = index + 1;

        try {
            // 设置项目为处理中状态
            const currentUser = this.appState.get('currentUser');
            if (currentUser && currentUser.userId) {
                const isSetProcessing = await this.rating.setItemProcessing(
                    apiIndex,
                    currentUser,
                    (msg, success) => this.ui.showNotification(msg, success),
                    this.data
                );

                if (!isSetProcessing) {
                    console.log(`[loadItemAtIndex] 设置处理中状态失败，项目 ${index + 1}`);
                    return;
                }
            }

            // 从 API 加载最新数据
            console.log(`[loadItemAtIndex] 加载详细数据，项目 ${index + 1}`);
            const currentItem = await this.data.loadItem(apiIndex);

            // 同步所有项目的状态（确保侧边栏显示最新状态）
            console.log(`[loadItemAtIndex] 同步所有项目状态，项目 ${index + 1}`);
            const allItems = await this.data.loadAllItems();
            this.appState.set('allItems', allItems);
            this.appState.set('totalItems', allItems.length);

            // 找到当前项目在同步后的索引（可能与之前相同）
            const syncedItem = allItems.find(item => item.index === apiIndex);
            if (syncedItem) {
                // 合并详细数据和状态数据
                // 注意：必须显式保留状态字段，防止被 currentItem 覆盖
                const mergedItem = {
                    ...syncedItem,           // 基础：状态数据（来自 all_ratings）
                    ...currentItem,          // 覆盖：详细数据（来自 rating_pair）
                    // 显式保留状态字段（优先级最高，防止被 undefined 覆盖）
                    status: syncedItem.status,
                    side_a_rated: syncedItem.side_a_rated,
                    side_b_rated: syncedItem.side_b_rated,
                    rated: syncedItem.rated,
                    status_user: syncedItem.status_user
                };
                allItems[index] = mergedItem;
                this.appState.set('allItems', allItems);
                console.log(`[loadItemAtIndex] 合并完成，项目 ${index + 1}`, mergedItem);
            }

            // 显示当前项目，并重新渲染项目网格（显示最新状态）
            console.log(`[loadItemAtIndex] 显示项目 ${index + 1}`);
            this.displayCurrentItem();
            
            // 重新渲染项目网格，确保状态正确显示
            console.log(`[loadItemAtIndex] 重新渲染项目网格，项目 ${index + 1}`);
            this.renderApp();
        } catch (error) {
            console.error(`[loadItemAtIndex] 加载项目 ${index + 1} 时出错:`, error);
            this.ui.showNotification(`加载项目 ${index + 1} 时出错：${error.message}`, false);
        }
    }

    /**
     * 显示当前项目
     */
    displayCurrentItem() {
        const currentIndex = this.appState.get('currentIndex');
        const currentItem = this.appState.get('allItems')[currentIndex];

        // 更新病例信息
        this.ui.updateCaseInfo(currentItem);

        // 更新病例内容
        this.ui.updateCaseContent(currentItem);

        // 对比模式：加载已保存的评分
        this.rating.loadSavedRatings(currentItem);

        // 更新状态显示
        this.ui.updateStatusDisplay(currentItem);

        // 更新导航按钮状态
        this.ui.updateNavigationButtons(
            this.appState.get('currentIndex'),
            this.appState.get('totalItems')
        );

        // 更新保存按钮状态
        this.ui.updateSaveButtonState();

        // 只更新项目网格的选中状态，不重新渲染整个网格
        this.ui.updateItemGridSelection(currentIndex);
    }

    /**
     * 处理项目点击事件
     * @param {number} index - 项目索引
     */
    async handleItemClick(index) {
        const item = this.appState.get('allItems')[index];

        // 检查项目状态
        if (item.status === 'processing' && item.status_user !== this.appState.get('currentUser').userId) {
            this.ui.showNotification(`此项目正在被用户 ${item.status_user} 处理`, false);
            return;
        }

        await this.loadItemAtIndex(index);
    }

    /**
     * 处理保存按钮点击
     */
    async handleSaveButtonClick() {
        const currentRatings = {
            index: this.appState.get('allItems')[this.appState.get('currentIndex')].index
        };

        const success = await this.rating.saveRatingToServer(
            currentRatings,
            this.appState.get('currentUser'),
            () => this.ui.updateSaveButtonState(),
            (msg, success) => this.ui.showNotification(msg, success),
            this.data
        );

        if (success) {
            // 重新从 API 加载最新数据以更新评分状态
            const apiIndex = this.appState.get('currentIndex') + 1;
            try {
                const updatedItem = await this.data.loadItem(apiIndex);
                const allItems = this.appState.get('allItems');
                allItems[this.appState.get('currentIndex')] = updatedItem;
                this.appState.set('allItems', allItems);
                
                // 重新显示当前项目（加载已保存的评分）
                this.displayCurrentItem();
                
                this.ui.showNotification('评分已保存！', true);
            } catch (error) {
                console.error('刷新评分数据失败:', error);
                this.ui.showNotification('保存成功，但刷新数据失败', false);
            }
        }
    }

    /**
     * 初始化事件监听器
     */
    initializeEventListeners() {
        // 保存 this 引用以便在闭包中使用
        const app = this;

        // 选择评分事件（对比模式）
        // 使用 bind 确保 this 上下文正确
        window.RatingManager = {
            selectRating: function(side, type, value) {
                app.rating.selectRating(side, type, value);
                app.ui.updateSaveButtonState();
            }
        };
    }

    /**
     * 绑定事件监听器
     */
    bindEventListeners() {
        // 保存 this 引用以便在闭包中使用
        const app = this;

        // 监听认证失效事件
        window.addEventListener('auth:invalid', (event) => {
            const message = event.detail?.message || '登录已过期，请重新登录';
            this.appState.set('isAuthenticated', false);
            this.appState.set('currentUser', {
                userId: null,
                username: null,
                realName: null
            });

            this.ui.updateUserDisplay(this.appState.get('currentUser'));
            this.ui.updateAuthButtons(false);
            this.ui.showNotification(message, false);
        });

        // 上一页按钮
        const prevBtn = document.getElementById('prev-btn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.navigation.handleNavigation(
                    'prev',
                    this.appState.get('currentIndex'),
                    this.appState.get('totalItems'),
                    (index) => this.loadItemAtIndex(index)
                );
            });
        }

        // 下一页按钮
        const nextBtn = document.getElementById('next-btn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.navigation.handleNavigation(
                    'next',
                    this.appState.get('currentIndex'),
                    this.appState.get('totalItems'),
                    (index) => this.loadItemAtIndex(index)
                );
            });
        }

        // 保存按钮
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.handleSaveButtonClick();
            });
        }

        // 登录按钮
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => {
                this.ui.showLoginModal();
            });
        }

        // 对比模式 Side A 评分事件
        ['accuracy', 'recall', 'logic'].forEach(dimension => {
            const inputs = document.querySelectorAll(`input[name="side_a_${dimension}"]`);
            inputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        const value = parseInt(e.target.value);
                        app.rating.selectRating('side_a', dimension, value);
                        app.ui.updateSaveButtonState();
                    }
                });
            });
        });

        // 对比模式 Side B 评分事件
        ['accuracy', 'recall', 'logic'].forEach(dimension => {
            const inputs = document.querySelectorAll(`input[name="side_b_${dimension}"]`);
            inputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        const value = parseInt(e.target.value);
                        app.rating.selectRating('side_b', dimension, value);
                        app.ui.updateSaveButtonState();
                    }
                });
            });
        });

        // 登出按钮
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                await this.auth.logout();
                this.appState.set('isAuthenticated', false);
                this.appState.set('currentUser', {
                    userId: null,
                    username: null,
                    realName: null
                });
                this.ui.updateUserDisplay(this.appState.get('currentUser'));
                this.ui.updateAuthButtons(false);
                this.ui.showNotification('已登出', true);
            });
        }

        // 登录表单提交
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;

                const result = await this.auth.login(username, password);

                if (result.success) {
                    // 后端返回的字段是 user_id 和 real_name，需要转换为 userId 和 realName
                    const user = result.user;
                    const currentUser = {
                        userId: user.user_id,
                        username: user.username,
                        realName: user.real_name,
                        role: user.role
                    };

                    this.appState.set('isAuthenticated', true);
                    this.appState.set('currentUser', currentUser);

                    this.ui.hideLoginModal();
                    this.ui.updateUserDisplay(currentUser);
                    this.ui.updateAuthButtons(true);
                    this.ui.showNotification('登录成功！', true);

                    try {
                        const items = await this.data.loadAllItems();
                        this.appState.set('allItems', items);
                        this.appState.set('totalItems', items.length);

                        if (this.appState.get('totalItems') > 0) {
                            if (this.ui) {
                                this.renderApp();
                            }
                            await this.loadItemAtIndex(0);
                        } else {
                            if (this.ui) {
                                this.ui.showLoadingMessage('没有找到评分项');
                            }
                        }
                    } catch (error) {
                        console.error('加载评分项失败:', error);
                        if (error.message && error.message.includes('401')) {
                            this.appState.set('isAuthenticated', false);
                            this.appState.set('currentUser', {
                                userId: null,
                                username: null,
                                realName: null
                            });

                            this.ui.updateUserDisplay(this.appState.get('currentUser'));
                            this.ui.updateAuthButtons(this.appState.get('isAuthenticated'));
                            this.ui.showLoadingMessage('登录已过期，请重新登录');
                        } else {
                            this.ui.showErrorWithReload('加载评分项时出错：' + error.message);
                        }
                    }
                } else {
                    this.ui.showNotification(result.message || '登录失败', false);
                }
            });
        }

        // 关闭登录模态框
        const loginCloseBtn = document.querySelector('#login-modal .modal-close');
        if (loginCloseBtn) {
            loginCloseBtn.addEventListener('click', () => {
                this.ui.hideLoginModal();
            });
        }

        // 点击登录模态框外部关闭
        window.addEventListener('click', (event) => {
            const loginModal = document.getElementById('login-modal');
            const registerModal = document.getElementById('register-modal');

            if (loginModal && event.target === loginModal) {
                this.ui.hideLoginModal();
            }

            if (registerModal && event.target === registerModal) {
                this.ui.hideRegisterModal();
            }
        });

        // 显示注册模态框
        const showRegisterLink = document.getElementById('show-register-link');
        if (showRegisterLink) {
            showRegisterLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.ui.hideLoginModal();
                this.ui.showRegisterModal();
            });
        }

        // 显示登录模态框（从注册页面）
        const showLoginLink = document.getElementById('show-login-link');
        if (showLoginLink) {
            showLoginLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.ui.hideRegisterModal();
                this.ui.showLoginModal();
            });
        }

        // 注册表单提交
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                const username = document.getElementById('register-username').value;
                const realname = document.getElementById('register-realname').value;
                const password = document.getElementById('register-password').value;
                const confirmPassword = document.getElementById('register-confirm-password').value;

                if (password !== confirmPassword) {
                    this.ui.showNotification('两次输入的密码不一致', false);
                    return;
                }

                if (password.length < 6) {
                    this.ui.showNotification('密码长度至少为 6 位', false);
                    return;
                }

                const result = await this.auth.register(username, realname, password);

                if (result.success) {
                    this.ui.hideRegisterModal();
                    this.ui.showNotification('注册成功！请登录', true);
                    registerForm.reset();
                } else {
                    this.ui.showNotification(result.message || '注册失败', false);
                }
            });
        }

        // 注册模态框关闭按钮
        const registerCloseBtn = document.querySelector('#register-modal .modal-close');
        if (registerCloseBtn) {
            registerCloseBtn.addEventListener('click', () => {
                this.ui.hideRegisterModal();
            });
        }

        // 模式选择器
        const modeSelect = document.getElementById('mode-select');
        if (modeSelect) {
            modeSelect.addEventListener('change', async (e) => {
                const newMode = e.target.value;
                try {
                    // 重新加载数据
                    const items = await this.data.loadAllItems();
                    this.appState.set('allItems', items);
                    this.appState.set('totalItems', items.length);

                    this.rating.resetCurrentRatings();

                    if (this.appState.get('totalItems') > 0) {
                        this.renderApp();
                        await this.loadItemAtIndex(0);
                    }

                    this.ui.showNotification('已切换到对比评分模式', true);
                } catch (error) {
                    console.error('切换模式失败:', error);
                    this.ui.showNotification('切换模式失败', false);
                }
            });
        }
    }

    /**
     * 开始定期刷新列表
     */
    startPeriodicRefresh() {
        setInterval(async () => {
            if (this.appState.get('isAuthenticated')) {
                try {
                    const refreshedItems = await this.data.refreshAllItems();
                    this.appState.set('allItems', refreshedItems);
                    this.renderApp();
                    console.log('列表已刷新');
                } catch (error) {
                    console.error('刷新列表失败:', error);
                }
            }
        }, 10000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', async () => {
    const app = new App();
    await app.init();
    app.startPeriodicRefresh();
});
