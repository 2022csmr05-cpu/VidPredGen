import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUser, removeUser, removeSession, setUser } from '../utils/storage';

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUserState] = useState(() => getUser());

  useEffect(() => {
    if (user) {
      setUser(user);
    }
  }, [user]);

  const login = (userData) => {
    const payload = {
      ...userData,
      loggedAt: Date.now(),
    };
    setUserState(payload);
    setUser(payload);
    navigate('/dashboard');
  };

  const logout = () => {
    removeUser();
    removeSession();
    setUserState(null);
    navigate('/login');
  };

  const value = useMemo(
    () => ({ user, login, logout, isAuthenticated: Boolean(user) }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
