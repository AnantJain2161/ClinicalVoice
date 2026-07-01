"""Clinical scenario matrix (brief section 5, step 1): parameterized cases
covering common ASHA/ANM consultation topics, including high-risk obstetrics.

Each scenario is clean/canonical clinical data. `colloquial_templates.py`
renders it into code-switched Hinglish/dialect phrasing; the structured
fields here become the ground-truth labels for the NLP eval set.
"""

SCENARIOS = [
    {
        "id": "fever_chills",
        "symptoms": [{"name": "fever", "duration": "3 days", "severity": "moderate"}],
        "medications": [{"name": "paracetamol", "dosage": "500mg", "frequency": "twice daily"}],
        "diagnoses": [{"name": "fever with chills", "snomed_code": "386661006"}],
    },
    {
        "id": "cough_cold",
        "symptoms": [{"name": "cough", "duration": "5 days", "severity": "mild"},
                     {"name": "headache", "duration": "2 days", "severity": "mild"}],
        "medications": [],
        "diagnoses": [{"name": "upper respiratory infection", "snomed_code": "54150009"}],
    },
    {
        "id": "diarrhea_dehydration",
        "symptoms": [{"name": "vomiting", "duration": "1 day", "severity": "severe"},
                     {"name": "diarrhea", "duration": "1 day", "severity": "severe"}],
        "medications": [{"name": "ORS", "dosage": None, "frequency": "after every loose motion"}],
        "diagnoses": [{"name": "acute gastroenteritis", "snomed_code": "25374005"}],
    },
    {
        "id": "pregnancy_swelling",
        "symptoms": [{"name": "swelling in legs", "duration": "1 week", "severity": "moderate"},
                     {"name": "headache", "duration": "2 days", "severity": "severe"}],
        "medications": [],
        "diagnoses": [{"name": "pre-eclampsia risk", "snomed_code": "398254007"}],
    },
    {
        "id": "pregnancy_bleeding",
        "symptoms": [{"name": "vaginal bleeding", "duration": "few hours", "severity": "severe"}],
        "medications": [],
        "diagnoses": [{"name": "antepartum hemorrhage risk", "snomed_code": "417981005"}],
    },
    {
        "id": "child_fever_rash",
        "symptoms": [{"name": "fever", "duration": "2 days", "severity": "moderate"},
                     {"name": "rash", "duration": "1 day", "severity": "mild"}],
        "medications": [{"name": "paracetamol", "dosage": "250mg", "frequency": "as needed"}],
        "diagnoses": [{"name": "viral exanthem", "snomed_code": "271807003"}],
    },
    {
        "id": "joint_pain_elderly",
        "symptoms": [{"name": "joint pain", "duration": "3 weeks", "severity": "moderate"}],
        "medications": [{"name": "ibuprofen", "dosage": "400mg", "frequency": "twice daily"}],
        "diagnoses": [{"name": "osteoarthritis", "snomed_code": "396275006"}],
    },
    {
        "id": "chest_infection",
        "symptoms": [{"name": "cough", "duration": "1 week", "severity": "severe"},
                     {"name": "fever", "duration": "4 days", "severity": "moderate"}],
        "medications": [{"name": "azithromycin", "dosage": "500mg", "frequency": "once daily"}],
        "diagnoses": [{"name": "lower respiratory tract infection", "snomed_code": "50417007"}],
    },
]
