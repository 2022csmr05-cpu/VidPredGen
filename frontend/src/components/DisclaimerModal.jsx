import { useState } from 'react';

export default function DisclaimerModal({ onAccept }) {
  const [checked, setChecked] = useState(false);

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2 style={{ marginBottom: 10 }}>⚠️ Disclaimer & Usage Guide</h2>

        <div style={{ fontSize: 14, lineHeight: 1.6, color: '#ccc' }}>
          <p>
            • All uploaded content is stored locally and automatically deleted after 24 hours or at midnight (00:00).
          </p>

          <p>
            • Logging out will remove all stored data including login and history.
          </p>

          <p>
            • Do NOT upload explicit, illegal, or harmful content. Violations may lead to restrictions.
          </p>

          <p>
            • This system is currently in testing mode. Results may vary.
          </p>

          <hr style={{ margin: '12px 0', opacity: 0.3 }} />

          <strong>How it works:</strong>
          <ul>
            <li>Upload image/video (image treated as single-frame video)</li>
            <li>System analyzes and generates summary</li>
            <li>Select future prediction option</li>
            <li>Final output video is generated</li>
          </ul>
        </div>

        <div className="checkbox-row">
          <input
            type="checkbox"
            id="accept"
            checked={checked}
            onChange={() => setChecked(!checked)}
          />
          <label htmlFor="accept">
            I understand and accept the terms
          </label>
        </div>

        <button
          className="btn"
          style={{ marginTop: 15, width: '100%' }}
          disabled={!checked}
          onClick={onAccept}
        >
          Accept & Continue
        </button>
      </div>
    </div>
  );
}