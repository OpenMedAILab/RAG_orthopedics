/**
 * Authentication Service
 * Implements the Service pattern for authentication logic
 */

import { ApiService } from '../services/apiService';
import { dispatch, AppActions } from '../utils/store';
import { Events, eventManager } from '../utils/eventManager';

export class AuthService {
  /**
   * Login user
   */
  static async login(username, password) {
    try {
      const result = await ApiService.login(username, password);
      
      if (result.success) {
        // Get full user profile after successful login
        const profileResult = await ApiService.getProfile();
        if (profileResult.success) {
          dispatch(AppActions.LOGIN_SUCCESS, { user: profileResult.user });
          eventManager.emit(Events.AUTH_LOGIN_SUCCESS, { user: profileResult.user });
          return { success: true, user: profileResult.user };
        } else {
          throw new Error(profileResult.message || '获取用户信息失败');
        }
      } else {
        throw new Error(result.message || '登录失败');
      }
    } catch (error) {
      console.error('Login error:', error);
      eventManager.emit(Events.AUTH_ERROR, { error: error.message });
      return { success: false, message: error.message };
    }
  }

  /**
   * Logout user
   */
  static async logout() {
    try {
      await ApiService.logout();
      dispatch(AppActions.LOGOUT);
      eventManager.emit(Events.AUTH_LOGOUT);
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      eventManager.emit(Events.AUTH_ERROR, { error: error.message });
      return { success: false, message: error.message };
    }
  }

  /**
   * Check authentication status
   */
  static async checkAuth() {
    try {
      const result = await ApiService.getProfile();
      if (result.success) {
        dispatch(AppActions.SET_AUTHENTICATION, { 
          isAuthenticated: true, 
          currentUser: result.user 
        });
        return { isAuthenticated: true, user: result.user };
      } else {
        dispatch(AppActions.SET_AUTHENTICATION, { 
          isAuthenticated: false, 
          currentUser: null 
        });
        return { isAuthenticated: false };
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      dispatch(AppActions.SET_AUTHENTICATION, { 
        isAuthenticated: false, 
        currentUser: null 
      });
      return { isAuthenticated: false, error: error.message };
    }
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated() {
    return dispatch.getState().isAuthenticated;
  }
}

export default AuthService;