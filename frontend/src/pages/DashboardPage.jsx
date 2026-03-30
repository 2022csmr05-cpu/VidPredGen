import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import DisclaimerModal from '../components/DisclaimerModal';
import { analyzeFile, getAnalysisStatus } from '../services/api';
import {
  cleanupExpiredHistory,
  getSession,
  setSession,
  removeSession,
  isDisclaimerAccepted,
  acceptDisclaimer,
  consumeJustLoggedIn,
} from '../utils/storage';

const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

export default function DashboardPage() {
  const navigate = useNavigate();
  const session = getSession();

  const [file, setFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [type, setType] = useState(() => session?.type || 'unknown');
  const [duration, setDuration] = useState(() => session?.duration || 0);
  const [fps, setFps] = useState(() => session?.fps || null);
  const [uploadInfo, setUploadInfo] = useState(
    () => session?.uploadInfo || 'No file selected yet.'
  );
  const [savedSummary, setSavedSummary] = useState(
    () => session?.summary || ''
  );
  const [savedPrediction, setSavedPrediction] = useState(
    () => session?.prediction || ''
  );
  const [futureOptions, setFutureOptions] = useState(
    () => session?.futureOptions || []
  );
  const [analysisId, setAnalysisId] = useState(() => session?.analysisId || null);
  const [analysisStatus, setAnalysisStatus] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const hasOutput = Boolean(savedPrediction);

  const videoFrameCallback = useRef(null);
  const previewVideoElement = useRef(null);

  const [accepted, setAccepted] = useState(() => isDisclaimerAccepted());
  const [showDisclaimer, setShowDisclaimer] = useState(() => consumeJustLoggedIn());

  const isMounted = useRef(true);

  useEffect(() => {
    cleanupExpiredHistory();

    const session = getSession();
    if (!session?.updatedAt) {
      removeSession();
    }

    return () => {
      isMounted.current = false;

      if (previewVideoElement.current) {
        if (typeof previewVideoElement.current.cancelVideoFrameCallback === 'function' &&
            videoFrameCallback.current?.callbackId) {
          previewVideoElement.current.cancelVideoFrameCallback(videoFrameCallback.current.callbackId);
        }
        previewVideoElement.current.src = '';
        previewVideoElement.current = null;
      }
    };
  }, []);

  useEffect(() => {
    setSession({
      type,
      uploadInfo,
      fileName: file?.name || null,
      duration,
      fps,
      analysisId,
      summary: savedSummary,
      prediction: savedPrediction,
      updatedAt: Date.now(),
    });
  }, [type, uploadInfo, file, duration, fps, analysisId, savedSummary, savedPrediction]);

  // ✅ FILE HANDLER WITH PREVIEW
  const handleFileSelection = (selected) => {
    if (!selected) return;

    if (selected.size > MAX_FILE_SIZE) {
      setUploadInfo('File too large. Maximum allowed size is 500MB.');
      return;
    }

    setFile(selected);
    setSavedSummary('');
    setSavedPrediction('');

    const url = URL.createObjectURL(selected);
    setPreviewURL(url);

    if (selected.type.startsWith('image/')) {
      setType('image');
      setDuration(0);
      setFps(null);
      setUploadInfo(`Selected: ${selected.name} (Image)`);

      if (previewVideoElement.current) {
        previewVideoElement.current = null;
      }
    } else if (selected.type.startsWith('video/')) {
      setType('video');
      setUploadInfo(`Selected: ${selected.name} (Video)`);

      const vid = document.createElement('video');
      vid.muted = true;
      vid.playsInline = true;
      vid.src = url;

      // Force metadata load to ensure duration is available.
      vid.load();

      previewVideoElement.current = vid;

      vid.onloadedmetadata = () => {
        if (!isMounted.current) return;

        const videoDuration = vid.duration && !Number.isNaN(vid.duration) ? Math.floor(vid.duration) : 0;
        setDuration(videoDuration);

        const measureFps = (now, metadata) => {
          if (!isMounted.current) return;
          const last = videoFrameCallback.current?.lastMeta;
          if (last) {
            const deltaFrames = metadata.presentedFrames - last.presentedFrames;
            const deltaTime = metadata.mediaTime - last.mediaTime;
            if (deltaTime > 0 && deltaFrames > 0) {
              const estimate = Math.round(deltaFrames / deltaTime);
              setFps(estimate);
              return;
            }
          }

          videoFrameCallback.current = { lastMeta: metadata, callbackId: null };
          if (typeof vid.requestVideoFrameCallback === 'function') {
            const callbackId = vid.requestVideoFrameCallback(measureFps);
            videoFrameCallback.current.callbackId = callbackId;
          }
        };

        if (typeof vid.requestVideoFrameCallback === 'function') {
          const callbackId = vid.requestVideoFrameCallback(measureFps);
          videoFrameCallback.current = { lastMeta: null, callbackId };
        }
      };
    } else {
      setType('unknown');
      setUploadInfo('Unsupported file type.');
    }
  };

  const startAnalysis = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setError('');
    setAnalysisStatus({ status: 'running', progress: 10 });

    try {
      const result = await analyzeFile(file);

      setAnalysisId(result.analysisId);
      setFps(result.fps ?? fps);

      setSession({
        type,
        uploadInfo,
        fileName: file?.name || null,
        duration,
        fps: result.fps ?? fps,
        analysisId: result.analysisId,
        summary: session?.summary || '',
        prediction: savedPrediction,
        updatedAt: Date.now(),
      });

      const pollStatus = async () => {
        try {
          const statusResult = await getAnalysisStatus(result.analysisId);
          setAnalysisStatus(statusResult);
          setFps(statusResult.fps ?? fps);

          if (statusResult.status === 'done') {
            const opts = statusResult.futureOptions || [];
            setSavedSummary(statusResult.summary || '');
            setFutureOptions(opts);
            setSession((prev) => ({
              ...prev,
              summary: statusResult.summary || '',
              futureOptions: opts,
              analysisId: result.analysisId,
            }));
            navigate('/summarise');
            return;
          }

          if (statusResult.status === 'error') {
            setError(statusResult.error || 'Analysis failed.');
            setIsAnalyzing(false);
            return;
          }

          setTimeout(pollStatus, 1200);
        } catch (pollError) {
          setError(pollError?.message || 'Status polling failed.');
          setIsAnalyzing(false);
        }
      };

      pollStatus();
    } catch (err) {
      setError(err?.message || 'Failed to start analysis.');
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="dashboard">
      <Header />

      <div className="container">
        <div className="card">
          <h2>Upload Video / Image</h2>

          <div className="upload-area">
            <div
              className="upload-box"
              onClick={() => document.getElementById('file-input')?.click()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files?.[0];
                if (file) handleFileSelection(file);
              }}
              onDragOver={(e) => e.preventDefault()}
            >
              {previewURL ? (
                <div className="preview-wrapper">
                  {type === 'video' ? (
                    <video
                      src={previewURL}
                      controls
                      className="preview-media"
                      onLoadedMetadata={(e) => {
                        const dur = e.target.duration;
                        if (dur && !Number.isNaN(dur) && dur > 0) {
                          setDuration(Math.floor(dur));
                        }
                      }}
                    />
                  ) : (
                    <img
                      src={previewURL}
                      alt="preview"
                      className="preview-media"
                    />
                  )}

                  <div className="preview-meta">
                    <div className="preview-line">
                      <span className="preview-label">File:</span> {file?.name}
                    </div>
                    <div className="preview-line">
                      <span className="preview-label">Duration:</span>{' '}
                      {type === 'image' ? 2 : duration} seconds
                    </div>
                    {type === 'video' && (
                      <div className="preview-line">
                        <span className="preview-label">FPS:</span> {fps ?? '—'}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <>
                  Click or Drop File
                  <div className="hint">Max size: 500MB</div>
                </>
              )}
            </div>

            <input
              id="file-input"
              type="file"
              accept="video/*,image/*"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelection(e.target.files[0])}
            />

            <button
              className="btn"
              onClick={startAnalysis}
              disabled={!file || isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing…' : 'Analyze'}
            </button>

            <div className="meta">
              {uploadInfo}
              {analysisStatus && (
                <div style={{ marginTop: 8 }}>
                  Status: {analysisStatus.status} • {analysisStatus.progress}%
                  {analysisStatus.fps && ` • FPS: ${analysisStatus.fps}`}
                </div>
              )}
              {error && (
                <div style={{ color: '#ff6b6b', marginTop: 8 }}>
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>

        {hasOutput && (
          <div className="card">
            <h2>Last Output</h2>
            <div className="output-box">
              <p>{savedPrediction}</p>
            </div>

            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button className="btn" onClick={() => navigate('/output')}>
                View Output
              </button>
              <button
                className="btn"
                style={{ background: 'rgba(255,255,255,0.12)' }}
                onClick={() => setSavedPrediction('')}
              >
                Clear Output
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ================= DISCLAIMER ================= */}
      {showDisclaimer && !accepted && (
        <DisclaimerModal
          onAccept={() => {
            acceptDisclaimer();
            setAccepted(true);
            setShowDisclaimer(false);
          }}
        />
      )}
    </div>
  );
}