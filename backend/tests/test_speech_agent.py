from app.agents.speech_agent import MockASRBackend, SpeechAgent


def test_mock_backend_returns_transcript() -> None:
    agent = SpeechAgent(backend=MockASRBackend())
    transcript = agent.transcribe(audio_bytes=b"fake-audio-bytes", language_hint="hi-en")
    assert transcript.text
    assert transcript.language == "hi-en"


def test_unknown_backend_raises() -> None:
    from app.agents.speech_agent import _build_backend

    try:
        _build_backend("nemo")
        assert False, "expected ValueError"
    except ValueError:
        pass
