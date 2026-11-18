import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/axiosClient';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('foodflow_user');
    const token = localStorage.getItem('foodflow_token');
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('foodflow_user');
        localStorage.removeItem('foodflow_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    if (res.data && res.data.success) {
      const data = res.data.data;
      const userData = {
        userId: data.user_id,
        email: data.email,
        role: data.role,
        fullName: data.full_name,
        profileId: data.profile_id,
        organizationName: data.organization_name,
        token: data.token
      };
      localStorage.setItem('foodflow_token', data.token);
      localStorage.setItem('foodflow_user', JSON.stringify(userData));
      setUser(userData);
      return userData;
    }
    throw new Error(res.data.message || 'Login failed');
  };

  const registerDonor = async (formData) => {
    const res = await api.post('/auth/register/donor', formData);
    if (res.data && res.data.success) {
      const data = res.data.data;
      const userData = {
        userId: data.user_id,
        email: data.email,
        role: data.role,
        fullName: data.full_name,
        profileId: data.profile_id,
        organizationName: data.organization_name,
        token: data.token
      };
      localStorage.setItem('foodflow_token', data.token);
      localStorage.setItem('foodflow_user', JSON.stringify(userData));
      setUser(userData);
      return userData;
    }
    throw new Error(res.data.message || 'Registration failed');
  };

  const registerReceiver = async (formData) => {
    const res = await api.post('/auth/register/receiver', formData);
    if (res.data && res.data.success) {
      const data = res.data.data;
      const userData = {
        userId: data.user_id,
        email: data.email,
        role: data.role,
        fullName: data.full_name,
        profileId: data.profile_id,
        organizationName: data.organization_name,
        token: data.token
      };
      localStorage.setItem('foodflow_token', data.token);
      localStorage.setItem('foodflow_user', JSON.stringify(userData));
      setUser(userData);
      return userData;
    }
    throw new Error(res.data.message || 'Registration failed');
  };

  const logout = () => {
    localStorage.removeItem('foodflow_token');
    localStorage.removeItem('foodflow_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, registerDonor, registerReceiver }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

