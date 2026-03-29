/**
 * 导航管理模块
 * 负责处理页面导航功能
 */

export class NavigationModule {
    /**
     * 处理导航
     * @param {string} direction - 导航方向 ('prev' 或 'next')
     * @param {number} currentIndex - 当前索引
     * @param {number} totalItems - 总项目数
     * @param {Function} loadItemAtIndex - 加载项目函数
     */
    handleNavigation(direction, currentIndex, totalItems, loadItemAtIndex) {
        let newIndex = currentIndex;
        
        if (direction === 'prev' && currentIndex > 0) {
            newIndex = currentIndex - 1;
        } else if (direction === 'next' && currentIndex < totalItems - 1) {
            newIndex = currentIndex + 1;
        }
        
        if (newIndex !== currentIndex) {
            loadItemAtIndex(newIndex);
        }
    }
}