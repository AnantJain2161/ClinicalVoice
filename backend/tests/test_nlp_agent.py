from app.agents.nlp_agent import MedicalNLPAgent, MockNLPBackend


def test_mock_backend_extracts_known_symptom_and_medication() -> None:
    agent = MedicalNLPAgent(backend=MockNLPBackend())
    entities = agent.extract("Patient has fever for 3 days, took paracetamol yesterday.")
    names = {s.name for s in entities.symptoms}
    assert "fever" in names
    assert entities.symptoms[0].duration is not None
    med_names = {m.name for m in entities.medications}
    assert "paracetamol" in med_names


def test_mock_backend_returns_empty_lists_for_no_matches() -> None:
    agent = MedicalNLPAgent(backend=MockNLPBackend())
    entities = agent.extract("Routine checkup, patient feels fine.")
    assert entities.symptoms == []
    assert entities.medications == []
