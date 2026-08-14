/**
 * Frontend Authentication Context & JWT State Management (T062).
 *
 * Provides reactive user authentication state, token persistence in localStorage,
 * login, register, logout, and automatic session restoration on app launch.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import apiClient from '../services/api';

export interface UserProfile {
  id: str;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchProfile = async () => {
    try {
      const res = await apiClient.get<UserProfile>('/auth/me');
      setUser(res.data);
    } catch (err) {
      console.warn('Failed to fetch user profile, clearing session.', err);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (email: string, pass: string) => {
    const res = await apiClient.post<{ access_token: string }>('/auth/login', {
      username: email,
      password: pass,
    });
    const newToken = res.data.access_token;
    localStorage.setItem('access_token', newToken);
    setToken(newToken);
    const profileRes = await apiClient.get<UserProfile>('/auth/me', {
      headers: { Authorization: `Bearer ${newToken}` },
    });
    setUser(profileRes.data);
  };

  const register = async (email: string, pass: string, fullName: string) => {
    await apiClient.post('/auth/register', {
      email,
      password: pass,
      full_name: fullName,
    });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
