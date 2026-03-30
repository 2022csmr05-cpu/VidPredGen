import { Routes, Route, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SummarisationPage from './pages/SummarisationPage';
import OutputPage from './pages/OutputPage';
import ProfilePage from './pages/ProfilePage'; // ✅ NEW
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

export default function App() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  return (
    <GoogleOAuthProvider clientId={googleClientId || ''}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/summarise"
            element={
              <ProtectedRoute>
                <SummarisationPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/output"
            element={
              <ProtectedRoute>
                <OutputPage />
              </ProtectedRoute>
            }
          />

          {/* ✅ PROFILE ROUTE */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}