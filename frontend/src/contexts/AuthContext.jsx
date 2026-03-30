/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { clearAll, getUser, markJustLoggedIn, setUser } from '../utils/storage';

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUserState] = useState(() => getUser());

  const login = useCallback(
    (userData, redirectTo = '/dashboard') => {
      const payload = {
        ...userData,
        loggedAt: Date.now(),
      };

      setUserState(payload);
      setUser(payload);

      // Show disclaimer once immediately after login (not on refresh)
      markJustLoggedIn();

      navigate(redirectTo);
    },
    [navigate]
  );

  const logout = useCallback(() => {
    // Remove all user/session data when logging out
    clearAll();
    setUserState(null);
    navigate('/login');
  }, [navigate]);

  const value = useMemo(
    () => ({ user, login, logout, isAuthenticated: Boolean(user) }),
    [user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
