import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';
import {
  getHistory,
  cleanupExpiredHistory,
  formatTimestamp,
  clearHistory,
} from '../utils/storage';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [history, setHistory] = useState(() => {
    cleanupExpiredHistory();
    return getHistory();
  });

  useEffect(() => {
    // History is initialized on mount via lazy initializer
  }, []);

  return (
    <div className="dashboard fade-in">
      <Header />

      <div className="container">

        {/* 🔹 PROFILE CARD */}
        <div className="card profile-card">
          <h2 style={{ marginBottom: 20 }}>Profile</h2>

          <div className="profile-info">
            {/* GOOGLE IMAGE */}
            {user?.picture ? (
              <img
                src={user.picture}
                alt="profile"
                className="profile-img-large"
              />
            ) : (
              /* MANUAL AVATAR */
              <div className="profile-avatar-large">
                {user?.name?.[0]?.toUpperCase() || 'A'}
              </div>
            )}

            <div>
              <h3>{user?.name}</h3>
              <p className="meta">{user?.email}</p>

              {/* LOGIN TYPE */}
              <p className="meta">
                Login Type: {user?.type === 'google' ? 'Google' : 'Manual'}
              </p>
            </div>
          </div>

          {/* 🔹 ACTIONS */}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button className="btn" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </button>

            <button className="btn logout-btn" onClick={logout}>
              Logout
            </button>
          </div>
        </div>

        {/* 🔹 HISTORY SECTION */}
        <div className="history-card card">
          <h2>History (24h retention)</h2>

          <p className="meta" style={{ marginBottom: 12 }}>
            All inputs and outputs are stored temporarily and will be automatically deleted at midnight (00:00).
          </p>

          {history.length === 0 ? (
            <p className="meta">No history available.</p>
          ) : (
            <ul className="history-list">
              {history.map((item) => (
                <li key={item.id} className="history-item">
                  <div className="history-row">
                    <span className="history-title">{item.inputName}</span>
                    <span className="history-time">
                      {formatTimestamp(item.createdAt)}
                    </span>
                  </div>

                  <div className="history-meta">
                    {item.option} · {item.outputDuration}s
                  </div>

                  <div className="history-summary">
                    {item.prediction}
                  </div>
                </li>
              ))}
            </ul>
          )}

          {/* 🔹 CLEAR BUTTON */}
          {history.length > 0 && (
            <button
              className="btn"
              style={{ marginTop: 15 }}
              onClick={() => {
                clearHistory();
                setHistory([]);
              }}
            >
              Clear History
            </button>
          )}
        </div>

      </div>
    </div>
  );
}