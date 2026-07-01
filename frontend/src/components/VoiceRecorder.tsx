import { useRef, useState } from "react";

interface VoiceRecorderProps {
  onRecordingComplete?: (blob: Blob) => void;
}

type RecorderState = "idle" | "recording" | "recorded";

export default function VoiceRecorder({ onRecordingComplete }: VoiceRecorderProps) {
  const [state, setState] = useState<RecorderState>("idle");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        setAudioUrl(URL.createObjectURL(blob));
        setState("recorded");
        stream.getTracks().forEach((track) => track.stop());
        onRecordingComplete?.(blob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setState("recording");
    } catch {
      setError("Microphone access denied or unavailable.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
  }

  function resetRecording() {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setState("idle");
  }

  return (
    <div className="voice-recorder">
      <div className="voice-recorder-controls">
        {state !== "recording" ? (
          <button onClick={startRecording}>{state === "recorded" ? "Record again" : "Start recording"}</button>
        ) : (
          <button onClick={stopRecording}>Stop recording</button>
        )}
        {state === "recorded" && <button onClick={resetRecording}>Clear</button>}
      </div>

      {state === "recording" && <p>Recording…</p>}
      {error && <p role="alert">{error}</p>}
      {audioUrl && (
        <audio controls src={audioUrl}>
          Your browser does not support audio playback.
        </audio>
      )}
    </div>
  );
}
