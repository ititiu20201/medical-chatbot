# model/tests/test_text_standardization.py
import pytest
from data_processor.text_standardization import TextStandardizer

def test_vietnamese_standardization():
    standardizer = TextStandardizer()
    test_cases = [
        ("Đau Đầu", "đau đầu"),
        ("SỐTTCAO", "sốt cao"),
        ("Khó Thở", "khó thở")
    ]
    
    for input_text, expected in test_cases:
        assert standardizer.standardize_vietnamese(input_text) == expected

def test_symptom_standardization():
    standardizer = TextStandardizer()
    test_symptoms = [
        "Đau Đầu",
        "nhuc dau",
        "đau_đầu"
    ]
    result = standardizer.standardize_symptoms(test_symptoms)
    assert "đau đầu" in result