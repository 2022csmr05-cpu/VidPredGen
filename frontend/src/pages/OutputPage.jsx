import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getSession, setSession } from '../utils/storage';
import { generateVideo } from '../services/api';

export default function OutputPage() {
  const navigate = useNavigate();
  const session = getSession();

  const [prediction, setPrediction] = useState(session?.prediction || '');
  const [outputUrl, setOutputUrl] = useState(session?.outputUrl || '');
  const [selectedOption, setSelectedOption] = useState(session?.selectedOption || null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  const missingData = useMemo(() => {
    return !session?.summary || !session?.fileName;
  }, [session]);

  useEffect(() => {
    if (missingData) {
      navigate('/summarise', { replace: true });
    }
  }, [missingData, navigate]);

  const handleGenerate = async (option) => {
    if (!option && !selectedOption) return;

    const optionToUse = option || selectedOption;

    if (!session?.analysisId || !optionToUse?.id) {
      setError('No valid selection or analysis ID available.');
      return;
    }

    setIsGenerating(true);
    setError('');

    setSelectedOption(optionToUse);
    setSession({ ...session, selectedOption: optionToUse });

    try {
      const result = await generateVideo({
        analysisId: session.analysisId,
        optionId: optionToUse.id,
      });
      const outputPath = result.outputUrl;
      setOutputUrl(outputPath);
      setPrediction(result.prompt || 'Video generation complete.');
      setSession({ ...session, selectedOption: optionToUse, prediction: result.prompt || '', outputUrl: outputPath });
    } catch (err) {
      setError(err?.message || 'Failed to generate output.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!prediction) return;

    const blob = new Blob([prediction], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `output-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="dashboard">
      <Header />

      <div className="container">
        <div className="card">
          <h2>Output</h2>

          {missingData ? (
            <p className="meta">No summary available. Returning to summarisation.</p>
          ) : (
            <>
              {(isGenerating || !outputUrl) && (
                <div style={{ marginBottom: 12 }}>
                  <p>Selected option: {selectedOption?.text || selectedOption?.title || selectedOption?.label || (selectedOption && selectedOption.id) || 'None'}</p>
                </div>
              )}

              {outputUrl ? (
                <>
                  <div className="output-box">
                    <p>Video generated successfully!</p>
                    <p>Prompt: {prediction}</p>
                    <video controls src={outputUrl} style={{ width: '100%' }} />
                  </div>

                  <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    <a className="btn" href={outputUrl} target="_blank" rel="noopener noreferrer">
                      View / Download Video
                    </a>
                    <button
                      className="btn"
                      style={{ background: 'rgba(255,255,255,0.12)' }}
                      onClick={() => navigate('/dashboard')}
                    >
                      Upload More
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <p className="meta">No output video yet. Click generate to create one.</p>

                  <div className="option-buttons" style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    <button
                      className="btn"
                      onClick={() => handleGenerate(null)}
                      disabled={isGenerating || !selectedOption}
                    >
                      Generate Video
                    </button>
                    <button
                      className="btn"
                      style={{ background: 'rgba(255,255,255,0.12)' }}
                      onClick={() => navigate('/summarise')}
                    >
                      Choose Option
                    </button>
                  </div>

                  {isGenerating && (
                    <p className="meta" style={{ marginTop: 10 }}>
                      Generating output…
                    </p>
                  )}

                  {error && (
                    <p className="meta" style={{ marginTop: 10, color: '#ff6b6b' }}>
                      {error}
                    </p>
                  )}

                  <button
                    className="btn"
                    style={{ marginTop: 12, background: 'rgba(255,255,255,0.12)' }}
                    onClick={() => navigate('/dashboard')}
                  >
                    Back to Dashboard
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
