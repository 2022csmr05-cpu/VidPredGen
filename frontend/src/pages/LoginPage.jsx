import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import './LoginPage.css';

// ✅ safer JWT decode
function decodeJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export default function LoginPage() {
  const location = useLocation();
  const fromPath = location.state?.from?.pathname || '/dashboard';

  const { login } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Ensure we don't keep any lingering fade-out classes from prior navigations
  useEffect(() => {
    document.body.classList.remove('fade-out');
  }, []);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  // ✅ Manual Login
  const handleManualLogin = (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !email.trim()) {
      setError('Please enter both name and email.');
      return;
    }

    setIsSubmitting(true);

    login(
      {
        name: name.trim(),
        email: email.trim(),
        type: 'manual',
      },
      fromPath
    );
  };

  // ✅ Google Login Success
  const handleGoogleSuccess = (credentialResponse) => {
    const decoded = decodeJwt(credentialResponse.credential);

    if (!decoded) {
      setError('Google login failed.');
      return;
    }

    setIsSubmitting(true);

    login(
      {
        name: decoded.name || decoded.given_name || 'Google User',
        email: decoded.email,
        picture: decoded.picture,
        type: 'google',
      },
      fromPath
    );
  };

  const handleGoogleError = () => {
    setError('Google Sign-In failed. Try again.');
  };


  return (
    <div className="page login-page">
      <div className="login-card">
        <h2>Welcome back</h2>
        <p className="lead">
          Sign in to continue to Innocence Video Lab
        </p>

        {/* 🔹 Manual Login */}
        <form className="login-form" onSubmit={handleManualLogin}>
          <label>
            <span>Name</span>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              required
            />
          </label>

          <label>
            <span>Email</span>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              type="email"
              required
            />
          </label>

          {error && <div className="error">{error}</div>}

          <button className="btn" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Continue'}
          </button>
        </form>

        <div className="divider">or</div>

        {/* 🔹 Google Login */}
        {googleClientId ? (
          <div className="google-login">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
            />
          </div>
        ) : (
          <div className="meta" style={{ marginTop: 12 }}>
            Google sign-in is not configured.
          </div>
        )}

        {/* 🔹 Note */}
        <div className="disclaimer" style={{ marginTop: 12 }}>
          This demo stores login data locally. All data is cleared on logout.
        </div>
      </div>
    </div>
  );
}