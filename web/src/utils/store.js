/**
 * State Management Store
 * Implements the Store pattern for centralized state management
 */

class Store {
  constructor(initialState = {}) {
    this.state = { ...initialState };
    this.subscribers = [];
  }

  /**
   * Get current state
   */
  getState() {
    return this.state;
  }

  /**
   * Update state and notify subscribers
   */
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.notifySubscribers();
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback) {
    this.subscribers.push(callback);

    // Return unsubscribe function
    return () => {
      this.subscribers = this.subscribers.filter(subscriber => subscriber !== callback);
    };
  }

  /**
   * Notify all subscribers of state change
   */
  notifySubscribers() {
    this.subscribers.forEach(callback => callback(this.state));
  }

  /**
   * Reset state to initial values
   */
  reset() {
    this.state = { ...this.initialState };
    this.notifySubscribers();
  }
}

// Create the main application store
const initialState = {
  // Authentication state
  isAuthenticated: false,
  currentUser: null,
  
  // Data state
  allItems: [],
  currentItem: null,
  currentIndex: 0,
  
  // Rating state
  currentRatings: {
    accuracy: null,
    recall: null,
    logic: null,
    comment: ''
  },
  
  // UI state
  loading: true,
  error: null,
  progress: 0
};

const appStore = new Store(initialState);

// Export the store instance
export default appStore;

// Also export action creators for consistent state updates
export const AppActions = {
  // Authentication actions
  SET_AUTHENTICATION: 'SET_AUTHENTICATION',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGOUT: 'LOGOUT',
  
  // Data actions
  SET_ALL_ITEMS: 'SET_ALL_ITEMS',
  SET_CURRENT_ITEM: 'SET_CURRENT_ITEM',
  UPDATE_ITEM_STATUS: 'UPDATE_ITEM_STATUS',
  
  // Rating actions
  UPDATE_RATING: 'UPDATE_RATING',
  UPDATE_COMMENT: 'UPDATE_COMMENT',
  CLEAR_RATINGS: 'CLEAR_RATINGS',
  
  // UI actions
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  UPDATE_PROGRESS: 'UPDATE_PROGRESS'
};

// Dispatch function to update store
export const dispatch = (action, payload) => {
  switch(action) {
    case AppActions.SET_AUTHENTICATION:
      appStore.setState({
        isAuthenticated: payload.isAuthenticated,
        currentUser: payload.currentUser
      });
      break;
      
    case AppActions.LOGIN_SUCCESS:
      appStore.setState({
        isAuthenticated: true,
        currentUser: payload.user
      });
      break;
      
    case AppActions.LOGOUT:
      appStore.setState({
        isAuthenticated: false,
        currentUser: null,
        allItems: [],
        currentItem: null,
        currentRatings: {
          accuracy: null,
          recall: null,
          logic: null,
          comment: ''
        }
      });
      break;
      
    case AppActions.SET_ALL_ITEMS:
      appStore.setState({
        allItems: payload.items,
        loading: false
      });
      // Also update progress
      const completedCount = payload.items.filter(item => item.status === 'completed').length;
      const totalCount = payload.items.length;
      const progress = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
      dispatch(AppActions.UPDATE_PROGRESS, { progress });
      break;
      
    case AppActions.SET_CURRENT_ITEM:
      appStore.setState({
        currentItem: payload.item,
        currentIndex: payload.index
      });
      break;
      
    case AppActions.UPDATE_ITEM_STATUS:
      const updatedItems = appStore.getState().allItems.map(item => 
        item.index === payload.index ? { ...item, ...payload.updates } : item
      );
      appStore.setState({ allItems: updatedItems });
      break;
      
    case AppActions.UPDATE_RATING:
      appStore.setState({
        currentRatings: {
          ...appStore.getState().currentRatings,
          [payload.dimension]: payload.value
        }
      });
      break;
      
    case AppActions.UPDATE_COMMENT:
      appStore.setState({
        currentRatings: {
          ...appStore.getState().currentRatings,
          comment: payload.comment
        }
      });
      break;
      
    case AppActions.CLEAR_RATINGS:
      appStore.setState({
        currentRatings: {
          accuracy: null,
          recall: null,
          logic: null,
          comment: ''
        }
      });
      break;
      
    case AppActions.SET_LOADING:
      appStore.setState({
        loading: payload.loading
      });
      break;
      
    case AppActions.SET_ERROR:
      appStore.setState({
        error: payload.error
      });
      break;
      
    case AppActions.UPDATE_PROGRESS:
      appStore.setState({
        progress: payload.progress
      });
      break;
      
    default:
      console.warn(`Unknown action: ${action}`);
  }
};