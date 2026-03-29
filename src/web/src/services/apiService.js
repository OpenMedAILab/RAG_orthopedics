/**
 * API Service Module
 * Handles all communication with the Flask backend API
 */

export const ApiService = {
  /**
   * Get user profile
   */
  async getProfile() {
    try {
      const response = await fetch('/api/profile', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  },

  /**
   * User login
   */
  async login(username, password) {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  /**
   * User logout
   */
  async logout() {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  /**
   * Load all ratings
   */
  async loadAllRatings() {
    try {
      const response = await fetch('/api/all_ratings', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error loading ratings:', error);
      throw error;
    }
  },

  /**
   * Load specific rating
   */
  async loadRating(index) {
    try {
      const response = await fetch(`/api/rating/${index}`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error loading rating:', error);
      throw error;
    }
  },

  /**
   * Save rating
   */
  async saveRating(data) {
    try {
      const response = await fetch('/api/save_rating', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving rating:', error);
      throw error;
    }
  },

  /**
   * Set item as processing
   */
  async setProcessing(index, userId) {
    try {
      const response = await fetch(`/api/set_processing/${index}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId }),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error setting processing status:', error);
      throw error;
    }
  },
  
  /**
   * Refresh all ratings
   */
  async refreshAllRatings() {
    try {
      const response = await fetch('/api/all_ratings', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error refreshing ratings:', error);
      throw error;
    }
  }
};