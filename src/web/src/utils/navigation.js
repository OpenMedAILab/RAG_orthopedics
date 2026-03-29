/**
 * Navigation Utility
 * Implements navigation logic using the Utility pattern
 */

import { Events, eventManager } from '../utils/eventManager';

export class NavigationUtility {
  /**
   * Navigate to previous item
   */
  static navigatePrev(currentIndex, totalItems, onNavigate) {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      if (onNavigate) {
        onNavigate(newIndex);
      }
      eventManager.emit(Events.NAVIGATE_PREV, { fromIndex: currentIndex, toIndex: newIndex });
      return true;
    }
    return false;
  }

  /**
   * Navigate to next item
   */
  static navigateNext(currentIndex, totalItems, onNavigate) {
    if (currentIndex < totalItems - 1) {
      const newIndex = currentIndex + 1;
      if (onNavigate) {
        onNavigate(newIndex);
      }
      eventManager.emit(Events.NAVIGATE_NEXT, { fromIndex: currentIndex, toIndex: newIndex });
      return true;
    }
    return false;
  }

  /**
   * Check if previous navigation is possible
   */
  static canNavigatePrev(currentIndex) {
    return currentIndex > 0;
  }

  /**
   * Check if next navigation is possible
   */
  static canNavigateNext(currentIndex, totalItems) {
    return currentIndex < totalItems - 1;
  }

  /**
   * Handle navigation in a given direction
   */
  static handleNavigation(direction, currentIndex, totalItems, onNavigate) {
    if (direction === 'prev') {
      return NavigationUtility.navigatePrev(currentIndex, totalItems, onNavigate);
    } else if (direction === 'next') {
      return NavigationUtility.navigateNext(currentIndex, totalItems, onNavigate);
    }
    return false;
  }
}

export default NavigationUtility;