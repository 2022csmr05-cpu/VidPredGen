import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Header.css';

export default function Header() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="app-header">
      <div className="app-title">
        <div className="title-main">Innocence Video Lab</div>
        <div className="title-sub">Frame Prediction & Generation</div>
      </div>

      {user && (
        <div
          className="profile-icon"
          onClick={() => navigate('/profile')}
          title="Profile"
        >
          {user.picture ? (
            <img src={user.picture} alt="Profile" />
          ) : (
            <span>{user.name?.[0]?.toUpperCase() || 'A'}</span>
          )}
        </div>
      )}
    </header>
  );
}