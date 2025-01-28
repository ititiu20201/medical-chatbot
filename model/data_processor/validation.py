# data_processor/validation_schemas.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class PatientInfo(BaseModel):
    patient_id: str
    name: str
    date_of_birth: str
    gender: str
    blood_type: str
    
class MedicalHistory(BaseModel):
    chronic_conditions: List[str]
    allergies: List[str]
    past_surgeries: List[dict]
    current_medications: List[dict]

class VisitRecord(BaseModel):
    visit_id: str
    patient_id: str
    timestamp: datetime
    symptoms: List[str]
    chatbot_analysis: dict