import { useEffect, useMemo, useRef, useState } from 'react';
import Header from '../components/Header';
import DisclaimerModal from '../components/DisclaimerModal';
import {
  cleanupExpiredHistory,
  addHistory,
  getHistory,
  formatTimestamp,
  getSession,
  setSession,
  removeSession,
} from '../utils/storage';
import { simulateAnalysis, simulatePrediction } from '../services/mockAnalysis';

const STEP = {
  UPLOAD: 'upload',
  PROCESSING: 'processing',
  SUMMARY: 'summary',
  OPTIONS: 'options',
  OUTPUT: 'output',
};

const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500MB

export default function DashboardPage() {
  const [step, setStep] = useState(STEP.UPLOAD);
  const [file, setFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [type, setType] = useState('unknown');
  const [duration, setDuration] = useState(0);
  const [summary, setSummary] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);
  const [prediction, setPrediction] = useState('');
  const [history, setHistory] = useState([]);
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadInfo, setUploadInfo] = useState('No file selected yet.');
  const [restoredSession, setRestoredSession] = useState(false);

  const [accepted, setAccepted] = useState(
    localStorage.getItem('acceptedDisclaimer') === 'true'
  );

  const isMounted = useRef(true);

  useEffect(() => {
    cleanupExpiredHistory();
    setHistory(getHistory());

    const session = getSession();
    if (session?.updatedAt) {
      setStep(session.step || STEP.UPLOAD);
      setType(session.type || 'unknown');
      setUploadInfo(session.uploadInfo || '');
      setSummary(session.summary || '');
      setSelectedOption(session.selectedOption || null);
      setPrediction(session.prediction || '');
      setRestoredSession(true);
    } else {
      removeSession();
    }

    return () => {
      isMounted.current = false;
    };
  }, []);

  const computedDuration = useMemo(() => {
    if (type === 'image') return 2;
    return Math.max(2, Math.round(duration + 2));
  }, [type, duration]);

  useEffect(() => {
    setSession({
      step,
      type,
      uploadInfo,
      summary,
      selectedOption,
      prediction,
      fileName: file?.name || null,
    });
  }, [step, type, uploadInfo, summary, selectedOption, prediction, file]);

  // ✅ FILE HANDLER WITH PREVIEW
  const handleFileSelection = (selected) => {
    if (!selected) return;

    if (selected.size > MAX_FILE_SIZE) {
      setUploadInfo('File too large. Maximum allowed size is 500MB.');
      return;
    }

    setFile(selected);

    const url = URL.createObjectURL(selected);
    setPreviewURL(url);

    if (selected.type.startsWith('image/')) {
      setType('image');
      setDuration(0);
      setUploadInfo(`Selected: ${selected.name} (Image)`);
    } 
    else if (selected.type.startsWith('video/')) {
      setType('video');
      setUploadInfo(`Selected: ${selected.name} (Video)`);

      const vid = document.createElement('video');
      vid.src = url;

      vid.onloadedmetadata = () => {
        if (!isMounted.current) return;
        setDuration(Math.floor(vid.duration || 0));
      };
    } 
    else {
      setType('unknown');
      setUploadInfo('Unsupported file type.');
    }
  };

  const startAnalysis = () => {
    if (!file) return;

    setStep(STEP.PROCESSING);
    setProgress(0);
    setIsProcessing(true);

    const interval = setInterval(() => {
      setProgress((p) => Math.min(100, p + 10));
    }, 300);

    simulateAnalysis({ type }).then(({ summary }) => {
      clearInterval(interval);
      setSummary(summary);
      setStep(STEP.SUMMARY);
      setIsProcessing(false);
    });
  };

  const handleGenerate = () => {
    if (!selectedOption) return;

    setStep(STEP.OUTPUT);

    simulatePrediction({ option: selectedOption }).then(({ prediction }) => {
      setPrediction(prediction);

      addHistory({
        id: Date.now(),
        createdAt: Date.now(),
        inputName: file?.name,
        option: selectedOption,
        prediction,
        outputDuration: computedDuration,
      });

      setHistory(getHistory());
    });
  };

  return (
    <div className="dashboard">
      <Header />

      <div className="container">

        {/* ================= UPLOAD ================= */}
        {step === STEP.UPLOAD && (
          <div className="card">
            <h2>Upload Video / Image</h2>

            {/* 🔥 PREVIEW */}
            {previewURL && (
              <div className="preview-container">
                {type === 'video' ? (
                  <video src={previewURL} controls className="preview-media" />
                ) : (
                  <img src={previewURL} alt="preview" className="preview-media" />
                )}

                <div className="preview-info">
                  Duration: {type === 'image' ? 2 : duration} seconds
                </div>
              </div>
            )}

            <div
              className="upload-box"
              onClick={() => document.getElementById('file-input')?.click()}
            >
              Click or Drop File
              <div className="hint">Max size: 500MB</div>
            </div>

            <input
              id="file-input"
              type="file"
              accept="video/*,image/*"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelection(e.target.files[0])}
            />

            <button className="btn" onClick={startAnalysis} disabled={!file}>
              Analyze
            </button>

            <div className="meta">{uploadInfo}</div>
          </div>
        )}

        {/* ================= PROCESSING ================= */}
        {step === STEP.PROCESSING && (
          <div className="card">
            <h2>Processing...</h2>
            <p>{progress}% completed</p>
          </div>
        )}

        {/* ================= SUMMARY ================= */}
        {step === STEP.SUMMARY && (
          <div className="card">
            <h2>Summary</h2>
            <p>{summary}</p>

            <button className="btn" onClick={() => setStep(STEP.OPTIONS)}>
              Continue
            </button>
          </div>
        )}

        {/* ================= OPTIONS ================= */}
        {step === STEP.OPTIONS && (
          <div className="card">
            <h2>Choose Future</h2>

            <div className="option-buttons">
              <button className="btn" onClick={() => setSelectedOption('continue')}>
                Continue
              </button>
              <button className="btn" onClick={handleGenerate}>
                Generate
              </button>
            </div>
          </div>
        )}

        {/* ================= OUTPUT ================= */}
        {step === STEP.OUTPUT && (
          <div className="card">
            <h2>Output</h2>
            <p>{prediction}</p>
          </div>
        )}
      </div>

      {/* ================= DISCLAIMER ================= */}
      {!accepted && (
        <DisclaimerModal
          onAccept={() => {
            localStorage.setItem('acceptedDisclaimer', 'true');
            setAccepted(true);
          }}
        />
      )}
    </div>
  );
}