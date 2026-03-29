/**
 * 评分管理模块
 * 负责处理评分相关功能（对比评分模式）
 */

export class RatingModule {
    constructor() {
        this.currentRatings = {
            side_a: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            },
            side_b: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            }
        };
    }

    /**
     * 选择评分（对比模式）
     * @param {string} side - 哪一侧 ('side_a' 或 'side_b')
     * @param {string} type - 评分类型
     * @param {number} value - 评分值
     */
    selectRating(side, type, value) {
        console.log('selectRating called:', side, type, value);
        console.log('currentRatings before:', JSON.stringify(this.currentRatings));

        // 将前端类型映射到后端类型
        const typeMapping = {
            'accuracy': 'medical_accuracy',
            'recall': 'key_point_recall',
            'logic': 'logical_completeness'
        };
        const mappedType = typeMapping[type] || type;

        if (side === 'side_a') {
            this.currentRatings.side_a[mappedType] = value;
        } else {
            this.currentRatings.side_b[mappedType] = value;
        }

        console.log('currentRatings after:', JSON.stringify(this.currentRatings));

        // 更新 UI - 使用 input 元素（name 属性使用下划线：side_a_accuracy）
        const input = document.querySelector(`input[name="${side}_${type}"][value="${value}"]`);
        if (input) {
            input.checked = true;
        }
    }

    /**
     * 检查是否有完整评分（对比模式）
     * @returns {boolean} 是否有完整评分
     */
    hasCompleteRatings() {
        const a = this.currentRatings.side_a;
        const b = this.currentRatings.side_b;
        console.log('hasCompleteRatings check - a.medical_accuracy:', a.medical_accuracy, 'type:', typeof a.medical_accuracy);
        console.log('hasCompleteRatings check - a.key_point_recall:', a.key_point_recall, 'type:', typeof a.key_point_recall);
        console.log('hasCompleteRatings check - a.logical_completeness:', a.logical_completeness, 'type:', typeof a.logical_completeness);
        console.log('hasCompleteRatings check - b.medical_accuracy:', b.medical_accuracy, 'type:', typeof b.medical_accuracy);
        console.log('hasCompleteRatings check - b.key_point_recall:', b.key_point_recall, 'type:', typeof b.key_point_recall);
        console.log('hasCompleteRatings check - b.logical_completeness:', b.logical_completeness, 'type:', typeof b.logical_completeness);
        const result = a.medical_accuracy != null &&
               a.key_point_recall != null &&
               a.logical_completeness != null &&
               b.medical_accuracy != null &&
               b.key_point_recall != null &&
               b.logical_completeness != null;
        console.log('hasCompleteRatings result:', result);
        return result;
    }

    /**
     * 保存评分到服务器（对比模式）
     * @param {Object} currentRatings - 当前评分对象
     * @param {Object} currentUser - 当前用户
     * @param {Function} updateSaveButtonState - 更新保存按钮状态函数
     * @param {Function} showNotification - 显示通知函数
     * @param {Object} dataManager - 数据管理器
     */
    async saveRatingToServer(currentRatings, currentUser, updateSaveButtonState, showNotification, dataManager) {
        // 检查是否有完整评分
        if (!this.hasCompleteRatings()) {
            showNotification('请为两侧所有维度选择评分！', false);
            return false;
        }

        // 设置评分项为处理中状态
        try {
            const result = await dataManager.setProcessing(currentRatings.index, currentUser.userId);
            if (!result.success) {
                showNotification('评分项正在被其他用户处理，无法编辑', false);
                return false;
            }
        } catch (error) {
            console.error('设置处理状态时出错:', error);
            showNotification('设置处理状态时出错', false);
            return false;
        }

        // 保存评分（对比模式）
        const sideAComment = document.getElementById('side-a-comment')?.value || '';
        const sideBComment = document.getElementById('side-b-comment')?.value || '';

        try {
            const result = await dataManager.saveRating({
                index: currentRatings.index,
                side_a_scores: {
                    medical_accuracy: this.currentRatings.side_a.medical_accuracy,
                    key_point_recall: this.currentRatings.side_a.key_point_recall,
                    logical_completeness: this.currentRatings.side_a.logical_completeness
                },
                side_b_scores: {
                    medical_accuracy: this.currentRatings.side_b.medical_accuracy,
                    key_point_recall: this.currentRatings.side_b.key_point_recall,
                    logical_completeness: this.currentRatings.side_b.logical_completeness
                },
                side_a_comment: sideAComment,
                side_b_comment: sideBComment,
                user_id: currentUser.userId,
                rated_by_name: currentUser.realName
            });

            if (result.success) {
                showNotification('评分已保存！', true);
                this.resetCurrentRatings();
                return true;
            } else {
                showNotification('保存失败：' + result.error, false);
                return false;
            }
        } catch (error) {
            console.error('Error saving rating:', error);
            showNotification('保存时发生错误！', false);
            return false;
        }
    }

    /**
     * 设置评分项为处理中状态
     * @param {number} index - 评分项索引
     * @param {Object} currentUser - 当前用户
     * @param {Function} showNotification - 显示通知函数
     * @param {Object} dataManager - 数据管理器
     * @returns {Promise<boolean>} 是否成功设置
     */
    async setItemProcessing(index, currentUser, showNotification, dataManager) {
        try {
            const result = await dataManager.setProcessing(index, currentUser.userId);
            
            if (result.success) {
                return true;
            } else if (result.locked_by) {
                // 被其他用户锁定
                const lockedBy = result.locked_by;
                showNotification(
                    `评分项正在被用户 ${lockedBy.username} 编辑，请稍后再试`,
                    false
                );
                return false;
            } else {
                showNotification(result.message || '评分项正在被其他用户处理，无法编辑', false);
                return false;
            }
        } catch (error) {
            console.error('设置处理状态时出错:', error);
            showNotification('设置处理状态时出错', false);
            return false;
        }
    }

    /**
     * 更新本地评分状态（对比模式）
     * @param {Array} allItems - 所有项目
     * @param {number} currentIndex - 当前索引
     */
    updateLocalRatingStatus(allItems, currentIndex) {
        const item = allItems[currentIndex];
        if (item) {
            item.side_a_rated = true;
            item.side_b_rated = true;
            item.status = 'completed';
        }
    }

    /**
     * 重置当前评分（保存后或离开时调用）
     */
    resetCurrentRatings() {
        // 重置数据
        this.currentRatings = {
            side_a: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            },
            side_b: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            }
        };

        // 清除 UI 上的活动状态（包括评论框）
        this.clearActiveStates(true);
    }

    /**
     * 清除 UI 上的活动状态
     * @param {boolean} clearComments - 是否清除评论框（默认 false）
     */
    clearActiveStates(clearComments = false) {
        // 对比模式 - 清除 radio 按钮的选中状态
        ['side_a', 'side_b'].forEach(side => {
            ['accuracy', 'recall', 'logic'].forEach(dimension => {
                const inputs = document.querySelectorAll(`input[name="${side}_${dimension}"]`);
                inputs.forEach(input => input.checked = false);
            });
        });

        // 只在明确要求时才清除评论框
        if (clearComments) {
            const sideAComment = document.getElementById('side-a-comment');
            const sideBComment = document.getElementById('side-b-comment');
            if (sideAComment) sideAComment.value = '';
            if (sideBComment) sideBComment.value = '';
        }
    }

    /**
     * 加载已保存的评分（对比模式）
     * @param {Object} ratingData - 评分数据（从 API 获取）
     */
    loadSavedRatings(ratingData) {
        console.log('加载已保存的评分:', ratingData);

        // 只清除 radio 按钮，不清除评论框（因为马上要加载新数据）
        this.clearActiveStates(false);

        // 重置内部数据
        this.currentRatings = {
            side_a: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            },
            side_b: {
                medical_accuracy: null,
                key_point_recall: null,
                logical_completeness: null,
                comment: ''
            }
        };

        // 加载 Side A 评分
        const sideA = ratingData.side_a || {};
        const sideAScores = sideA.scores || {};

        if (sideAScores.medical_accuracy) {
            this.selectRating('side_a', 'accuracy', sideAScores.medical_accuracy);
        }
        if (sideAScores.key_point_recall) {
            this.selectRating('side_a', 'recall', sideAScores.key_point_recall);
        }
        if (sideAScores.logical_completeness) {
            this.selectRating('side_a', 'logic', sideAScores.logical_completeness);
        }

        // 加载 Side B 评分
        const sideB = ratingData.side_b || {};
        const sideBScores = sideB.scores || {};

        if (sideBScores.medical_accuracy) {
            this.selectRating('side_b', 'accuracy', sideBScores.medical_accuracy);
        }
        if (sideBScores.key_point_recall) {
            this.selectRating('side_b', 'recall', sideBScores.key_point_recall);
        }
        if (sideBScores.logical_completeness) {
            this.selectRating('side_b', 'logic', sideBScores.logical_completeness);
        }

        // 加载评论（包括空字符串）
        const sideAComment = document.getElementById('side-a-comment');
        const sideBComment = document.getElementById('side-b-comment');
        if (sideAComment) sideAComment.value = sideA.comment !== undefined ? (sideA.comment || '') : '';
        if (sideBComment) sideBComment.value = sideB.comment !== undefined ? (sideB.comment || '') : '';

        console.log('已加载评分完成');
    }
}
