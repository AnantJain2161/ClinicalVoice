import { useState } from "react";
import VoiceRecorder from "./components/VoiceRecorder";
import "./App.css";

function App() {
  const [lastRecordingSize, setLastRecordingSize] = useState<number | null>(null);

  return (
    <div className="app">
      <h1>ClinicalVoice</h1>
      <p>Speak a consultation. Transcript, extraction, and record generation wire in during Phase 2.</p>

      <VoiceRecorder onRecordingComplete={(blob) => setLastRecordingSize(blob.size)} />

      {lastRecordingSize !== null && <p>Captured {lastRecordingSize} bytes of audio.</p>}
    </div>
  );
}

export default App;
