# model/tests/test_validation.py
import pytest
from data_processor.validation_schemas import Patient, Visit, Symptom

def test_patient_validation():
    # Valid patient data
    patient_data = {
        "patient_id": "P001",
        "basic_info": {
            "name": "Nguyen Van A",
            "date_of_birth": "1990-01-01",
            "gender": "Nam",
            "blood_type": "A+"
        }
    }
    patient = Patient(**patient_data)
    assert patient.patient_id == "P001"

def test_invalid_patient():
    # Invalid patient data
    with pytest.raises(ValueError):
        Patient(patient_id="invalid", basic_info={})