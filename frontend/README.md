# Innocence Video Prediction (React + Vite)

A neon-style demo application that simulates a video analysis and generation workflow.

## Features

- **Authentication** (manual email login + Google sign in via `@react-oauth/google`).
- **Upload / Analyze**: Upload an image/video and simulate analysis.
- **Prediction options**: Choose a direction for the mock output.
- **Output preview**: See a mock preview with duration logic.
- **History**: Stores results in `localStorage` for 24 hours (automatic cleanup).
- **Session persistence**: Current workflow state is stored so the app can restore after refresh.

## Running the App

From the `frontend/` folder:

```bash
npm install
npm run dev
```

Open the URL shown in your terminal (usually http://localhost:5173).

## Optional: Google Sign-In

To enable Google login, create a `.env` file in `frontend/` with:

```env
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
```

Without it, manual login still works.

## Notes

- This is a demo: no real video processing is performed.
- All data stays in the browser; nothing is sent to a server.
