/**
 * Event Manager
 * Implements the Observer pattern for event handling
 */

class EventManager {
  constructor() {
    this.events = {};
  }

  /**
   * Subscribe to an event
   */
  subscribe(eventName, callback) {
    if (!this.events[eventName]) {
      this.events[eventName] = [];
    }
    
    this.events[eventName].push(callback);
    
    // Return unsubscribe function
    return () => {
      this.events[eventName] = this.events[eventName].filter(cb => cb !== callback);
    };
  }

  /**
   * Emit an event
   */
  emit(eventName, data) {
    if (this.events[eventName]) {
      this.events[eventName].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${eventName}:`, error);
        }
      });
    }
  }

  /**
   * Unsubscribe all callbacks from an event
   */
  unsubscribeAll(eventName) {
    if (this.events[eventName]) {
      delete this.events[eventName];
    }
  }
}

// Create a global event manager instance
const eventManager = new EventManager();

export default eventManager;

// Define event constants
export const Events = {
  // Authentication events
  AUTH_LOGIN_SUCCESS: 'AUTH_LOGIN_SUCCESS',
  AUTH_LOGOUT: 'AUTH_LOGOUT',
  AUTH_ERROR: 'AUTH_ERROR',
  
  // Data events
  DATA_LOADED: 'DATA_LOADED',
  DATA_LOAD_ERROR: 'DATA_LOAD_ERROR',
  ITEM_SELECTED: 'ITEM_SELECTED',
  
  // Rating events
  RATING_UPDATED: 'RATING_UPDATED',
  RATING_SAVED: 'RATING_SAVED',
  RATING_SAVE_ERROR: 'RATING_SAVE_ERROR',
  
  // UI events
  SHOW_NOTIFICATION: 'SHOW_NOTIFICATION',
  HIDE_NOTIFICATION: 'HIDE_NOTIFICATION',
  
  // Progress events
  PROGRESS_UPDATED: 'PROGRESS_UPDATED',
  
  // Navigation events
  NAVIGATE_PREV: 'NAVIGATE_PREV',
  NAVIGATE_NEXT: 'NAVIGATE_NEXT'
};