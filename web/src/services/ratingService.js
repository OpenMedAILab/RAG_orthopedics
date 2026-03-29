/**
 * Rating Service
 * Implements the Service pattern for business logic encapsulation
 */

import { ApiService } from '../services/apiService';
import { dispatch, AppActions } from '../utils/store';
import { Events, eventManager } from '../utils/eventManager';

export class RatingService {
  /**
   * Load all rating items
   */
  static async loadAllRatings() {
    try {
      dispatch(AppActions.SET_LOADING, { loading: true });
      
      const response = await ApiService.loadAllRatings();
      if (response && response.success !== false) {
        const items = response.data || response;
        dispatch(AppActions.SET_ALL_ITEMS, { items });
        eventManager.emit(Events.DATA_LOADED, { items });
        return items;
      } else {
        throw new Error(response.message || 'Failed to load ratings');
      }
    } catch (error) {
      console.error('Error loading ratings:', error);
      dispatch(AppActions.SET_ERROR, { error: error.message });
      eventManager.emit(Events.DATA_LOAD_ERROR, { error: error.message });
      
      if (error.message === 'Unauthorized') {
        eventManager.emit(Events.AUTH_ERROR, { error });
      }
      
      throw error;
    } finally {
      dispatch(AppActions.SET_LOADING, { loading: false });
    }
  }

  /**
   * Select a rating item
   */
  static async selectItem(index, items, currentUser) {
    try {
      const item = items[index];
      if (!item) {
        throw new Error('Invalid item index');
      }

      // Check if the item is already being processed by someone else
      if (item.status === 'processing' && item.status_user && item.status_user !== currentUser?.userId) {
        throw new Error(`此项目正在被用户 ${item.status_user} 处理`);
      }

      // Load the specific item
      const loadedItem = await ApiService.loadRating(item.index);
      
      dispatch(AppActions.SET_CURRENT_ITEM, { item: loadedItem, index });
      eventManager.emit(Events.ITEM_SELECTED, { item: loadedItem, index });
      return loadedItem;
    } catch (error) {
      console.error('Error selecting item:', error);
      eventManager.emit(Events.DATA_LOAD_ERROR, { error: error.message });
      throw error;
    }
  }

  /**
   * Save ratings to the server
   */
  static async saveRatings(currentItem, currentRatings, currentUser) {
    try {
      // First, set the item as processing for this user
      const setResult = await ApiService.setProcessing(currentItem.index, currentUser.userId);
      if (!setResult.success) {
        throw new Error(setResult.message || '此项目正在被其他用户处理，无法编辑');
      }

      // Prepare the data to save
      const saveData = {
        index: currentItem.index,
        accuracy: currentRatings.accuracy,
        recall: currentRatings.recall,
        logic: currentRatings.logic,
        comment: currentRatings.comment,
        user_id: currentUser.userId,
        rated_by_name: currentUser.realName
      };

      // Save the ratings
      const result = await ApiService.saveRating(saveData);

      if (result.success) {
        // Update the item status in the store
        dispatch(AppActions.UPDATE_ITEM_STATUS, {
          index: currentItem.index,
          updates: {
            ...currentItem,
            accuracy: currentRatings.accuracy,
            recall: currentRatings.recall,
            logic: currentRatings.logic,
            comment: currentRatings.comment,
            status: 'completed',
            rated_by: currentUser.userId,
            rated_by_name: currentUser.realName
          }
        });
        
        // Clear current ratings
        dispatch(AppActions.CLEAR_RATINGS);
        
        eventManager.emit(Events.RATING_SAVED, { 
          itemIndex: currentItem.index, 
          ratings: currentRatings 
        });
        
        // Show success notification
        eventManager.emit(Events.SHOW_NOTIFICATION, {
          message: '评分已保存！',
          severity: 'success'
        });
        
        return true;
      } else {
        throw new Error(result.message || '保存失败');
      }
    } catch (error) {
      console.error('Error saving ratings:', error);
      eventManager.emit(Events.RATING_SAVE_ERROR, { error: error.message });
      
      // Show error notification
      eventManager.emit(Events.SHOW_NOTIFICATION, {
        message: error.message || '保存评分时发生错误',
        severity: 'error'
      });
      
      throw error;
    }
  }

  /**
   * Update a rating dimension
   */
  static updateRating(dimension, value) {
    dispatch(AppActions.UPDATE_RATING, { dimension, value });
    eventManager.emit(Events.RATING_UPDATED, { dimension, value });
  }

  /**
   * Update the comment
   */
  static updateComment(comment) {
    dispatch(AppActions.UPDATE_COMMENT, { comment });
  }

  /**
   * Check if ratings are complete
   */
  static hasCompleteRatings(ratings) {
    return ratings.accuracy !== null &&
           ratings.recall !== null &&
           ratings.logic !== null;
  }
}

export default RatingService;