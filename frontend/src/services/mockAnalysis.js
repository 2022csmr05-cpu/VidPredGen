export function simulateAnalysis({ type, fileName }) {
  // Returns a Promise that resolves with a mock summary.
  return new Promise((resolve) => {
    const baseText =
      type === 'image'
        ? 'This image was treated as a single-frame video. Key visual elements were identified.'
        : 'This video was analyzed across frames and key motion patterns were detected.';

    const extras = [
      'Bright highlights and contrast were noted.',
      'Motion patterns suggest dynamic movement.',
      'The scene shows a clear focal subject.',
      'Color grading suggests a high-energy segment.',
      'Transitions appear smooth and consistent.'
    ];

    const random = extras[Math.floor(Math.random() * extras.length)];

    const summary = `${baseText} ${random}`;
    const delay = 1500 + Math.random() * 1500;

    setTimeout(() => resolve({ summary, analysisId: `${Date.now()}` }), delay);
  });
}

export function simulatePrediction({ option }) {
  return new Promise((resolve) => {
    const predictions = {
      continue: 'The scene continues, with the main subject moving forward and new elements appearing.',
      obstacle: 'An obstacle appears, forcing a rapid change in direction and pace.',
      shift: 'The camera refocuses on a different subject, revealing new context.',
      new: 'A new character enters, changing the dynamics of the scene.',
      slowdown: 'Time slows down; the atmosphere feels more dramatic and detailed.',
    };

    const delay = 1100 + Math.random() * 1200;
    setTimeout(() => {
      resolve({ prediction: predictions[option] || predictions.continue });
    }, delay);
  });
}
