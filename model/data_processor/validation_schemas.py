# data_processor/validation_schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime, date
from enum import Enum

# Enums
class Gender(str, Enum):
    MALE = "Nam"
    FEMALE = "Nữ"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"

class SeverityLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class ConditionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESOLVED = "resolved"

# Base Models
class Contact(BaseModel):
    phone: str
    address: str

    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('0') or not len(v) == 10 or not v.isdigit():
            raise ValueError('Invalid phone number format')
        return v

class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('0') or not len(v) == 10 or not v.isdigit():
            raise ValueError('Invalid phone number format')
        return v

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str

class Surgery(BaseModel):
    procedure: str
    date: str

class Lifestyle(BaseModel):
    smoking: str
    alcohol: str
    exercise: str
    diet: str


# Medical History Models
# class MedicalHistory(BaseModel):
#     chronic_conditions: Union[str, List[List[str]]]
#     allergies: Union[str, List[List[str]]]
#     past_surgeries: Union[str, List[Surgery]]
#     current_medications: Union[str, List[Medication]]

class MedicalHistory(BaseModel):
    chronic_conditions: List[str] 
    allergies: List[str] 
    past_surgeries: List[Surgery]
    current_medications: List[Medication]

class BasicInfo(BaseModel):
    name: str
    date_of_birth: str
    gender: str
    blood_type: str
    contact: Contact
    emergency_contact: EmergencyContact

# Patient Model

class Patient(BaseModel):
    patient_id: str
    basic_info: BasicInfo
    medical_history: MedicalHistory
    lifestyle: Lifestyle
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

    @validator('patient_id')
    def validate_patient_id(cls, v):
        if not v.startswith('P') or not len(v) >= 4:
            raise ValueError('Invalid patient ID format')
        return v

# Department Models

class Department(BaseModel):
    department_id: int
    department_name: str
    common_conditions: List[str]

# Symptom Models
class Symptom(BaseModel):
    symptom_id: int
    symptom_name: str
    priority_level: str
    related_conditions: List[str]
# class Symptom(BaseModel):
#     symptom_id: int
#     symptom_name: str
#     related_conditions: List[str]
#     severity_level: SeverityLevel

# Condition Models

class Condition(BaseModel):
    condition_id: int
    condition_name: str
    symptoms: List[str]
    department_name: str

# Visit Models
class PredictedCondition(BaseModel):
    condition_name: str
    confidence: float

class ChatbotAnalysis(BaseModel):
    predicted_conditions: List[PredictedCondition]
    recommended_department: str
    priority_level: SeverityLevel
    queue_number: int

class Visit(BaseModel):
    visit_id: str
    patient_id: str
    timestamp: datetime
    symptoms: List[str]
    chatbot_analysis: ChatbotAnalysis

    @validator('visit_id')
    def validate_visit_id(cls, v):
        if not v.startswith('V') or not len(v) >= 4:
            raise ValueError('Invalid visit ID format')
        return v

# Medical History Tracking Models
class ConditionTracking(BaseModel):
    diagnosed_date: str
    status: ConditionStatus
    last_followup: str

class HistoryTimeline(BaseModel):
    date: date
    type: str
    visit_id: str
    summary: str
    procedure: Optional[str] = None

class PatientHistory(BaseModel):
    patient_id: str
    history_timeline: List[HistoryTimeline]
    condition_tracking: Dict[str, Dict[str, ConditionTracking]]

# Routing Rules Models
class SeverityIndicator(BaseModel):
    symptoms: List[str]

class DepartmentRouting(BaseModel):
    department_id: str
    department_name: str
    severity_indicators: Dict[str, SeverityIndicator]
    capacity: Dict[str, int]

# Symptom Analysis Rules Models
class SeverityIndicators(BaseModel):
    mild: List[str]
    moderate: List[str]
    severe: List[str]

class AnalysisRule(BaseModel):
    symptoms: List[str]
    departments: List[str]
    follow_up_questions: List[str]
    severity_indicators: SeverityIndicators

# Complete Medical Data Model
class MedicalData(BaseModel):
    patients: List[Patient]
    departments: List[Department]
    symptoms: List[Symptom]
    conditions: List[Condition]
    visits: List[Visit]
    routing_rules: List[DepartmentRouting]
    analysis_rules: List[AnalysisRule]