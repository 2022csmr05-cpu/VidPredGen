const BASE_URL = import.meta.env.VITE_API_BASE || "";

export async function analyzeFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to analyze file.");
  }

  return res.json();
}

export async function getAnalysisStatus(analysisId) {
  const res = await fetch(`${BASE_URL}/api/status/${analysisId}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to fetch analysis status.");
  }

  return res.json();
}

export async function generateVideo({ analysisId, optionId }) {
  const res = await fetch(`${BASE_URL}/api/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ analysisId, optionId }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to generate video.");
  }

  return res.json();
}
