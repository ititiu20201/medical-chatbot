from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SymptomAnalysisRequest(BaseModel):
    """Schema for symptom analysis request"""
    symptoms: str
    patientInfo: Optional[Dict] = None

    class Config:
        schema_extra = {
            "example": {
                "symptoms": "đau đầu và sốt nhẹ",
                "patientInfo": {
                    "age": 30,
                    "gender": "Nam"
                }
            }
        }

class SymptomAnalysisResponse(BaseModel):
    """Schema for symptom analysis response"""
    recommendedSpecialty: str
    needsMoreInfo: bool = False
    followUpQuestion: Optional[str] = None
    confidence: float
    recommendations: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "recommendedSpecialty": "Thần kinh",
                "needsMoreInfo": False,
                "confidence": 0.8,
                "recommendations": [
                    "Khám Thần kinh",
                    "Chuẩn bị các xét nghiệm cơ bản"
                ]
            }
        }

# Specialty mapping dictionary
SPECIALTY_MAPPING = {
    'đau đầu': 'Thần kinh',
    'đau dạ dày': 'Tiêu hóa',
    'đau ngực': 'Tim mạch',
    'ho': 'Hô hấp',
    'sốt': 'Nội tổng quát',
    'đau khớp': 'Cơ xương khớp',
    'đau răng': 'Răng hàm mặt',
    'rối loạn tiêu hóa': 'Tiêu hóa',
    'chóng mặt': 'Thần kinh',
    'khó thở': 'Hô hấp',
}

@router.post("/analyze-symptoms", response_model=SymptomAnalysisResponse, description="Analyze patient symptoms and recommend specialists")
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze patient symptoms and recommend medical specialists
    
    Args:
        request: SymptomAnalysisRequest object containing symptoms and optional patient info
        
    Returns:
        SymptomAnalysisResponse containing specialty recommendations and confidence score
    """
    try:
        logger.info(f"Analyzing symptoms: {request.symptoms}")
        
        # Clean and normalize the symptoms text
        symptoms = request.symptoms.lower().strip()
        
        # Find matching specialty
        matched_specialty = None
        max_confidence = 0.0
        
        for symptom, specialty in SPECIALTY_MAPPING.items():
            if symptom in symptoms:
                confidence = len(symptom.split()) / len(symptoms.split())
                if confidence > max_confidence:
                    matched_specialty = specialty
                    max_confidence = confidence

        if matched_specialty is None:
            return SymptomAnalysisResponse(
                recommendedSpecialty="Đang phân tích",
                needsMoreInfo=True,
                followUpQuestion="Vui lòng mô tả chi tiết hơn về triệu chứng của bạn. Ví dụ: vị trí đau, mức độ đau, thời gian kéo dài?",
                confidence=0.0
            )

        # Generate recommendations based on specialty
        recommendations = [
            f"Khám {matched_specialty}",
            "Chuẩn bị các xét nghiệm cơ bản",
            "Mang theo các kết quả xét nghiệm trước đây (nếu có)"
        ]
        
        # Add age-specific recommendations if available
        if request.patientInfo and "age" in request.patientInfo:
            age = request.patientInfo["age"]
            if age > 60:
                recommendations.append("Mang theo sổ theo dõi bệnh mãn tính (nếu có)")

        return SymptomAnalysisResponse(
            recommendedSpecialty=matched_specialty,
            needsMoreInfo=False,
            confidence=max_confidence,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Error analyzing symptoms: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi khi phân tích triệu chứng")