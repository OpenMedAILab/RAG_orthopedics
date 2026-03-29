/**
 * UI 管理模块
 * 负责处理用户界面更新和交互（对比评分模式）
 */

export class UIModule {
    constructor() {
        this.mode = 'comparison';
    }

    /**
     * 显示通知
     * @param {string} message - 通知消息
     * @param {boolean} isSuccess - 是否成功状态
     */
    showNotification(message, isSuccess = true) {
        const snackbar = document.getElementById('snackbar');
        const snackbarMessage = document.getElementById('snackbar-message');

        if (snackbar && snackbarMessage) {
            snackbarMessage.textContent = message;
            snackbar.className = 'snackbar show';

            // 更新图标
            const snackbarIcon = snackbar.querySelector('.snackbar-icon');
            if (snackbarIcon) {
                snackbarIcon.textContent = isSuccess ? '✓' : '✕';
            }

            setTimeout(() => {
                snackbar.className = 'snackbar';
            }, 3000);
        }
    }

    /**
     * 显示加载消息
     * @param {string} message - 加载消息
     */
    showLoadingMessage(message) {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.textContent = message;
        }
    }

    /**
     * 隐藏加载提示并显示内容
     */
    hideLoading() {
        const loadingElement = document.getElementById('loading');
        const contentElement = document.getElementById('content');

        if (loadingElement) {
            loadingElement.style.display = 'none';
        }

        if (contentElement) {
            contentElement.style.display = 'block';
        }
    }

    /**
     * 渲染项目网格
     * @param {Array} items - 项目列表
     * @param {number} currentIndex - 当前选中索引
     * @param {Function} onItemClick - 项目点击回调
     */
    renderItemsGrid(items, currentIndex, onItemClick) {
        const itemsGrid = document.getElementById('items-grid');
        if (itemsGrid) {
            itemsGrid.innerHTML = '';

            items.forEach((item, index) => {
                const itemBtn = this.createItemButton(item, index, onItemClick);
                if (index === currentIndex) {
                    itemBtn.classList.add('active');
                }
                itemsGrid.appendChild(itemBtn);
            });
        }
    }

    /**
     * 创建项目按钮
     * @param {Object} item - 项目数据
     * @param {number} index - 项目索引
     * @param {Function} onItemClick - 点击回调
     */
    createItemButton(item, index, onItemClick) {
        const itemBtn = document.createElement('button');
        itemBtn.className = 'item-btn';
        itemBtn.textContent = item.index;
        itemBtn.onclick = () => onItemClick(index);

        // 对比模式：检查两侧是否都已评分
        let isCompleted = false;
        if (item.side_a_rated !== undefined && item.side_b_rated !== undefined) {
            isCompleted = item.side_a_rated && item.side_b_rated;
        } else {
            isCompleted = item.rated || item.status === 'completed';
        }

        // 调试日志：查看状态数据
        console.log(`[createItemButton] 项目 ${item.index}: status=${item.status}, side_a_rated=${item.side_a_rated}, side_b_rated=${item.side_b_rated}, rated=${item.rated}, isCompleted=${isCompleted}`);

        // 根据状态添加样式类
        if (isCompleted) {
            // 已完成：绿色
            itemBtn.classList.add('completed');
        } else if (item.status === 'processing') {
            // 处理中：黄色
            itemBtn.classList.add('processing');
        } else {
            // 未评分：无背景色（默认样式）
            itemBtn.classList.add('available');
        }

        return itemBtn;
    }

    /**
     * 更新项目网格的选中状态
     * @param {number} currentIndex - 当前选中索引
     */
    updateItemGridSelection(currentIndex) {
        const itemsGrid = document.getElementById('items-grid');
        if (itemsGrid) {
            const buttons = itemsGrid.querySelectorAll('.item-btn');
            buttons.forEach((btn, index) => {
                if (index === currentIndex) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
    }

    /**
     * 更新病例信息（支持对比模式）
     * @param {Object} item - 病例数据
     */
    updateCaseInfo(item) {
        // 对比模式
        if (this.mode === 'comparison') {
            const caseInfo = item.case_info || {};
            
            const contextValue = document.getElementById('context-value');
            if (contextValue) contextValue.textContent = caseInfo.context || 'N/A';

            const examValue = document.getElementById('exam-value');
            if (examValue) examValue.textContent = caseInfo.physicalExamination || 'N/A';

            const imagingValue = document.getElementById('imaging-value');
            if (imagingValue) imagingValue.textContent = caseInfo.imagingExamination || 'N/A';

            const caseNumber = document.getElementById('case-number');
            if (caseNumber) caseNumber.textContent = caseInfo.caseNumber || '-';

            const modelName = document.getElementById('model-name');
            if (modelName) modelName.textContent = item.model || '-';

            const pairId = document.getElementById('pair-id');
            if (pairId) pairId.textContent = item.pair_id || '-';

            const caseTitle = document.getElementById('case-title');
            if (caseTitle) {
                caseTitle.textContent = `评分对 ${item.pair_id || item.index} - ${item.model || '-'} (NoRAG vs RAG)`;
            }

            // 更新侧边标签
            const sideABadge = document.getElementById('side-a-badge');
            const sideBBadge = document.getElementById('side-b-badge');
            const sideAModeLabel = document.getElementById('side-a-mode-label');
            const sideBModeLabel = document.getElementById('side-b-mode-label');

            if (sideABadge) {
                sideABadge.textContent = item.side_a?.mode || 'NoRAG';
                sideABadge.className = `side-mode-badge ${item.side_a?.mode === 'NoRAG' ? 'norag' : 'rag'}`;
            }
            if (sideBBadge) {
                sideBBadge.textContent = item.side_b?.mode || 'RAG';
                sideBBadge.className = `side-mode-badge ${item.side_b?.mode === 'RAG' ? 'rag' : 'norag'}`;
            }
            if (sideAModeLabel) sideAModeLabel.textContent = item.side_a?.label || '无 RAG 模式';
            if (sideBModeLabel) sideBModeLabel.textContent = item.side_b?.label || 'RAG 模式';
        }
    }

    /**
     * 更新进度信息
     * @param {Array} allItems - 所有项目
     * @param {number} totalItems - 总项目数
     */
    updateProgressInfo(allItems, totalItems) {
        // 对比模式：计算两侧都已评分的项目数
        let completedCount = 0;
        allItems.forEach(item => {
            if (item.side_a_rated !== undefined && item.side_b_rated !== undefined) {
                if (item.side_a_rated && item.side_b_rated) {
                    completedCount++;
                }
            } else if (item.rated || item.status === 'completed') {
                completedCount++;
            }
        });

        const currentIndexElement = document.getElementById('current-index');
        if (currentIndexElement) currentIndexElement.textContent = completedCount;

        const totalCountElement = document.getElementById('total-count');
        if (totalCountElement) totalCountElement.textContent = totalItems;

        const progressPercent = totalItems > 0 ? Math.round((completedCount / totalItems) * 100) : 0;

        const progressPercentElement = document.getElementById('progress-percent');
        if (progressPercentElement) progressPercentElement.textContent = progressPercent;

        const progressBarElement = document.getElementById('progress-bar');
        if (progressBarElement) progressBarElement.style.width = progressPercent + '%';
    }

    /**
     * 更新病例内容（对比模式）
     * @param {Object} item - 病例数据
     */
    updateCaseContent(item) {
        // Side A 内容
        const sideAContainer = document.getElementById('side-a-qa-pairs');
        if (sideAContainer && item.side_a) {
            sideAContainer.innerHTML = '';
            this.renderQAPairs(sideAContainer, item.side_a.qa_pairs || []);
        }

        // Side A RAG 上下文
        const sideARagContext = document.getElementById('side-a-rag-context');
        const sideARagContent = document.getElementById('side-a-rag-context-content');
        if (sideARagContext && sideARagContent && item.side_a) {
            if (item.side_a.rag_context && item.side_a.rag_context.trim()) {
                if (window.updateRagContext) {
                    window.updateRagContext('side-a', item.side_a.rag_context);
                } else {
                    sideARagContent.textContent = item.side_a.rag_context;
                    sideARagContext.style.display = 'block';
                }
            } else {
                sideARagContext.style.display = 'none';
            }
        }

        // Side B 内容
        const sideBContainer = document.getElementById('side-b-qa-pairs');
        if (sideBContainer && item.side_b) {
            sideBContainer.innerHTML = '';
            this.renderQAPairs(sideBContainer, item.side_b.qa_pairs || []);
        }

        // Side B RAG 上下文
        const sideBRagContext = document.getElementById('side-b-rag-context');
        if (sideBRagContext && item.side_b) {
            if (item.side_b.rag_context && item.side_b.rag_context.trim()) {
                if (window.updateRagContext) {
                    window.updateRagContext('side-b', item.side_b.rag_context);
                } else {
                    const sideBRagContent = document.getElementById('side-b-rag-context-content');
                    sideBRagContent.textContent = item.side_b.rag_context;
                    sideBRagContext.style.display = 'block';
                }
            } else {
                sideBRagContext.style.display = 'none';
            }
        }
    }

    /**
     * 渲染问答对
     * @param {HTMLElement} container - 容器元素
     * @param {Array} qaPairs - 问答对数组
     */
    renderQAPairs(container, qaPairs) {
        if (!qaPairs || qaPairs.length === 0) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-tertiary); padding: var(--space-8);">暂无问答内容</div>';
            return;
        }

        qaPairs.forEach((pair, index) => {
            const qaCard = document.createElement('div');
            qaCard.className = 'qa-card';

            // Question Section
            const questionSection = document.createElement('div');
            questionSection.className = 'qa-section';

            const questionLabel = document.createElement('div');
            questionLabel.className = 'qa-label question';
            questionLabel.innerHTML = '<span>❓</span> 问题 ' + (index + 1);

            const questionContent = document.createElement('div');
            questionContent.className = 'qa-content';
            questionContent.textContent = pair.question;

            questionSection.appendChild(questionLabel);
            questionSection.appendChild(questionContent);

            // Answer Section
            const answerSection = document.createElement('div');
            answerSection.className = 'qa-section';

            const answerLabel = document.createElement('div');
            answerLabel.className = 'qa-label answer';
            answerLabel.innerHTML = '<span>✓</span> 回答';

            const answerContent = document.createElement('div');
            answerContent.className = 'qa-content';
            answerContent.innerHTML = pair.answer.replace(/\n/g, '<br>');

            answerSection.appendChild(answerLabel);
            answerSection.appendChild(answerContent);

            qaCard.appendChild(questionSection);
            qaCard.appendChild(answerSection);
            container.appendChild(qaCard);
        });
    }

    /**
     * 更新状态显示
     * @param {Object} item - 项目数据
     */
    updateStatusDisplay(item) {
        const statusBadge = document.getElementById('case-status');
        const statusText = document.getElementById('status-text');
        const statusDot = statusBadge ? statusBadge.querySelector('.status-dot') : null;

        // 对比模式：检查两侧是否都已评分
        let isCompleted = false;
        if (item.side_a_rated !== undefined && item.side_b_rated !== undefined) {
            isCompleted = item.side_a_rated && item.side_b_rated;
        } else {
            isCompleted = item.rated || item.status === 'completed';
        }

        let status = isCompleted ? 'completed' : (item.status || 'idle');

        if (statusBadge && statusText) {
            // 移除所有现有状态类
            statusBadge.classList.remove('available', 'processing', 'completed');

            switch(status) {
                case 'processing':
                    statusBadge.classList.add('processing');
                    statusText.textContent = '处理中';
                    break;
                case 'completed':
                    statusBadge.classList.add('completed');
                    statusText.textContent = '已完成';
                    break;
                default:
                    statusBadge.classList.add('available');
                    statusText.textContent = '可用';
                    break;
            }
        }
    }

    /**
     * 更新导航按钮状态
     * @param {number} currentIndex - 当前索引
     * @param {number} totalItems - 总项目数
     */
    updateNavigationButtons(currentIndex, totalItems) {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (prevBtn) prevBtn.disabled = (currentIndex <= 0);
        if (nextBtn) nextBtn.disabled = (currentIndex >= totalItems - 1);
    }

    /**
     * 更新保存按钮状态
     */
    updateSaveButtonState() {
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            // 对比模式：检查两侧是否都有评分
            // 注意：input 的 name 属性使用下划线（side_a_accuracy），而非连字符
            const aAccuracy = document.querySelector('input[name="side_a_accuracy"]:checked');
            const aRecall = document.querySelector('input[name="side_a_recall"]:checked');
            const aLogic = document.querySelector('input[name="side_a_logic"]:checked');
            const bAccuracy = document.querySelector('input[name="side_b_accuracy"]:checked');
            const bRecall = document.querySelector('input[name="side_b_recall"]:checked');
            const bLogic = document.querySelector('input[name="side_b_logic"]:checked');

            const hasSideA = aAccuracy && aRecall && aLogic;
            const hasSideB = bAccuracy && bRecall && bLogic;

            saveBtn.disabled = !(hasSideA && hasSideB);
        }
    }

    /**
     * 清除所有活动状态
     */
    clearAllActiveStates() {
        // 对比模式
        ['side-a', 'side-b'].forEach(side => {
            ['accuracy', 'recall', 'logic'].forEach(dimension => {
                const inputs = document.querySelectorAll(`input[name="${side}-${dimension}"]`);
                inputs.forEach(input => input.checked = false);
            });
        });
    }

    /**
     * 加载评分到 UI（对比模式）
     * @param {Object} item - 项目数据
     */
    loadRatingsForComparison(item) {
        // Side A 评分
        if (item.side_a?.scores) {
            const scores = item.side_a.scores;
            if (scores.medical_accuracy) {
                const input = document.querySelector(`input[name="side-a-accuracy"][value="${scores.medical_accuracy}"]`);
                if (input) input.checked = true;
            }
            if (scores.key_point_recall) {
                const input = document.querySelector(`input[name="side-a-recall"][value="${scores.key_point_recall}"]`);
                if (input) input.checked = true;
            }
            if (scores.logical_completeness) {
                const input = document.querySelector(`input[name="side-a-logic"][value="${scores.logical_completeness}"]`);
                if (input) input.checked = true;
            }
        }

        // Side B 评分
        if (item.side_b?.scores) {
            const scores = item.side_b.scores;
            if (scores.medical_accuracy) {
                const input = document.querySelector(`input[name="side-b-accuracy"][value="${scores.medical_accuracy}"]`);
                if (input) input.checked = true;
            }
            if (scores.key_point_recall) {
                const input = document.querySelector(`input[name="side-b-recall"][value="${scores.key_point_recall}"]`);
                if (input) input.checked = true;
            }
            if (scores.logical_completeness) {
                const input = document.querySelector(`input[name="side-b-logic"][value="${scores.logical_completeness}"]`);
                if (input) input.checked = true;
            }
        }

        // 评论
        const sideAComment = document.getElementById('side-a-comment');
        if (sideAComment && item.side_a?.comment) {
            sideAComment.value = item.side_a.comment;
        }

        const sideBComment = document.getElementById('side-b-comment');
        if (sideBComment && item.side_b?.comment) {
            sideBComment.value = item.side_b.comment;
        }
    }

    /**
     * 选择评分（辅助方法）
     * @param {string} side - 哪一侧
     * @param {string} dimension - 维度
     * @param {number} value - 值
     */
    selectRating(side, dimension, value) {
        const input = document.querySelector(`input[name="${side}-${dimension}"][value="${value}"]`);
        if (input) input.checked = true;
    }

    /**
     * 更新用户信息显示
     * @param {Object} currentUser - 当前用户信息
     */
    updateUserDisplay(currentUser) {
        const userIdDisplay = document.getElementById('user-id');
        const userNameDisplay = document.getElementById('user-name');

        if (!userIdDisplay || !userNameDisplay) {
            return;
        }

        if (currentUser && currentUser.username) {
            userIdDisplay.textContent = currentUser.userId || '未知 ID';
            userNameDisplay.textContent = currentUser.realName || currentUser.username || '未知用户';
        } else {
            userIdDisplay.textContent = '未登录';
            userNameDisplay.textContent = '未登录';
        }
    }

    /**
     * 切换登录/登出按钮显示
     * @param {boolean} isAuthenticated - 认证状态
     */
    updateAuthButtons(isAuthenticated) {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');

        if (isAuthenticated) {
            if (loginBtn) loginBtn.classList.add('hidden');
            if (logoutBtn) logoutBtn.classList.remove('hidden');
        } else {
            if (loginBtn) loginBtn.classList.remove('hidden');
            if (logoutBtn) logoutBtn.classList.add('hidden');
        }
    }

    /**
     * 显示登录模态框
     */
    showLoginModal() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.add('active');
        }
    }

    /**
     * 隐藏登录模态框
     */
    hideLoginModal() {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * 显示注册模态框
     */
    showRegisterModal() {
        const modal = document.getElementById('register-modal');
        if (modal) {
            modal.classList.add('active');
        }
    }

    /**
     * 隐藏注册模态框
     */
    hideRegisterModal() {
        const modal = document.getElementById('register-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * 显示错误信息和重载按钮
     * @param {string} message - 错误消息
     */
    showErrorWithReload(message) {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div style="color: #f44336; font-size: 18px; margin-bottom: 20px;">${message}</div>
                    <button id="reload-btn" class="mui-button mui-primary-button" style="padding: 10px 20px; font-size: 16px;">重载数据</button>
                </div>
            `;
            loadingDiv.style.display = 'flex';
            loadingDiv.style.alignItems = 'center';
            loadingDiv.style.justifyContent = 'center';
        }
    }
}
