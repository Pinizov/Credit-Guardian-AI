import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

/**
 * JWT Token utilities
 */
const TOKEN_KEY = 'cg_auth_token';
const USER_KEY = 'cg_user';

/**
 * Decode JWT token payload
 */
function decodeToken(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

/**
 * Check if token is expired
 */
function isTokenExpired(token) {
  if (!token) return true;
  
  const payload = decodeToken(token);
  if (!payload?.exp) return true;
  
  // Add 60 second buffer
  return Date.now() >= (payload.exp * 1000) - 60000;
}

/**
 * Get stored token
 */
function getStoredToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

/**
 * Get stored user
 */
function getStoredUser() {
  try {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
}

// Create context
const AuthContext = createContext(null);

// API instance
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Auth Provider Component
 */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken);
  const [user, setUser] = useState(getStoredUser);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Clear auth state (logout)
   */
  const clearAuth = useCallback(() => {
    setToken(null);
    setUser(null);
    setError(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    delete api.defaults.headers.common['Authorization'];
  }, []);

  /**
   * Set auth state
   */
  const setAuth = useCallback((newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USER_KEY, JSON.stringify(newUser));
    api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
  }, []);

  /**
   * Login
   */
  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/auth/login', { email, password });
      const { token: newToken, user: newUser } = response.data;
      
      setAuth(newToken, newUser);
      return { success: true, user: newUser };
    } catch (err) {
      const message = err.response?.data?.error || err.response?.data?.message || 'Грешка при вход';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, [setAuth]);

  /**
   * Register
   */
  const register = useCallback(async (name, email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/auth/register', { name, email, password });
      const { token: newToken, user: newUser } = response.data;
      
      setAuth(newToken, newUser);
      return { success: true, user: newUser };
    } catch (err) {
      const message = err.response?.data?.error || err.response?.data?.message || 'Грешка при регистрация';
      setError(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, [setAuth]);

  /**
   * Logout
   */
  const logout = useCallback(() => {
    clearAuth();
    // Redirect to home or login page
    window.location.href = '/';
  }, [clearAuth]);

  /**
   * Refresh user data
   */
  const refreshUser = useCallback(async () => {
    if (!token) return null;
    
    try {
      const response = await api.get('/users/me');
      const newUser = response.data;
      setUser(newUser);
      localStorage.setItem(USER_KEY, JSON.stringify(newUser));
      return newUser;
    } catch (err) {
      // If 401, token is invalid
      if (err.response?.status === 401) {
        clearAuth();
      }
      return null;
    }
  }, [token, clearAuth]);

  /**
   * Check if user has premium subscription
   */
  const isPremium = useCallback(() => {
    return user?.subscription_status === 'active';
  }, [user]);

  /**
   * Initialize auth on mount
   */
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = getStoredToken();
      
      if (storedToken) {
        // Check if token is expired
        if (isTokenExpired(storedToken)) {
          console.log('Token expired, logging out');
          clearAuth();
        } else {
          // Set token in axios
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          
          // Optionally refresh user data
          // await refreshUser();
        }
      }
      
      setLoading(false);
    };
    
    initAuth();
  }, [clearAuth]);

  /**
   * Set up axios interceptors for 401 handling
   */
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        // Auto-logout on 401
        if (error.response?.status === 401) {
          clearAuth();
          // Show message to user
          console.log('Session expired, please login again');
        }
        return Promise.reject(error);
      }
    );
    
    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [clearAuth]);

  /**
   * Token expiration checker (runs every minute)
   */
  useEffect(() => {
    if (!token) return;
    
    const checkExpiration = () => {
      if (isTokenExpired(token)) {
        console.log('Token expired, logging out');
        clearAuth();
      }
    };
    
    // Check every minute
    const interval = setInterval(checkExpiration, 60000);
    
    return () => clearInterval(interval);
  }, [token, clearAuth]);

  const value = {
    // State
    user,
    token,
    loading,
    error,
    isAuthenticated: !!token && !!user,
    
    // Actions
    login,
    register,
    logout,
    refreshUser,
    clearError: () => setError(null),
    
    // Helpers
    isPremium,
    
    // API instance (for authenticated requests)
    api,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Protected Route component
 */
export function ProtectedRoute({ children, requirePremium = false }) {
  const { isAuthenticated, isPremium, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    // Redirect to login
    window.location.href = '/login';
    return null;
  }
  
  if (requirePremium && !isPremium()) {
    // Redirect to pricing/upgrade
    window.location.href = '/pricing';
    return null;
  }
  
  return children;
}

export default AuthContext;

