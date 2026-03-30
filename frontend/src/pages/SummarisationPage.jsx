import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getSession, setSession } from '../utils/storage';
import { getAnalysisStatus } from '../services/api';

export default function SummarisationPage() {
  const navigate = useNavigate();
  const session = getSession();

  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(session?.summary || '');
  const [futureOptions, setFutureOptions] = useState(session?.futureOptions || []);
  const [error, setError] = useState('');

  const missingData = useMemo(() => {
    return !session?.fileName || !session?.type;
  }, [session]);

  useEffect(() => {
    if (missingData) {
      navigate('/dashboard', { replace: true });
      return;
    }

    if (summary && futureOptions.length > 0) {
      setLoading(false);
      setProgress(100);
      return;
    }

    if (!session?.analysisId) {
      setError('No analysis job available. Please try again from Dashboard.');
      return;
    }

    setLoading(true);
    setProgress(20);

    const poll = async () => {
      try {
        const statusResult = await getAnalysisStatus(session.analysisId);

        setProgress(Math.max(20, statusResult.progress || 0));

        if (statusResult.status === 'done') {
          setSummary(statusResult.summary || '');
          setFutureOptions(statusResult.futureOptions || []);
          setSession({
            ...session,
            summary: statusResult.summary || '',
            futureOptions: statusResult.futureOptions || [],
          });
          setLoading(false);
          setProgress(100);
          return;
        }

        if (statusResult.status === 'error') {
          setError(statusResult.error || 'Analysis failed during summary retrieval.');
          setLoading(false);
          return;
        }

        setTimeout(poll, 1200);
      } catch (err) {
        setError(err?.message || 'Failed to check analysis status.');
        setLoading(false);
      }
    };

    poll();
  }, [missingData, navigate, session, summary, futureOptions.length]);

  const selectOption = (option) => {
    setSession({ ...session, selectedOption: option });
    navigate('/output');
  };

  return (
    <div className="dashboard">
      <Header />
      <div className="container">
        <div className="card">
          <h2>Summarisation</h2>

          {loading ? (
            <>
              <p>Loading summary and options…</p>
              <p className="meta">{progress}% completed</p>
            </>
          ) : error ? (
            <p className="meta" style={{ color: '#ff6b6b' }}>
              {error}
            </p>
          ) : (
            <>
              <p>{summary || 'No summary available yet.'}</p>

              {futureOptions.length > 0 ? (
                <>
                  <h3>Future prediction options</h3>
                  <div className="option-buttons" style={{ gap: 8, flexWrap: 'wrap' }}>
                    {futureOptions.map((option) => (
                      <button
                        key={option.id}
                        className="btn"
                        onClick={() => selectOption(option)}
                      >
                        {option.text || option.title || option.label || `Option ${option.id}`}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <p className="meta">No future options available; proceed to output.</p>
              )}
            </>
          )}

          <button
            className="btn"
            style={{ marginTop: 8, background: 'rgba(255,255,255,0.12)' }}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
