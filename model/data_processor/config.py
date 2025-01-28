# data_processor/config.py
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # One more parent to reach project root
DATA_DIR = BASE_DIR / 'model' / 'data'  # Add 'model' to the path

# Data paths
DATA_CONFIG = {
    'raw_data_path': str(DATA_DIR / 'raw'),
    'processed_data_path': str(DATA_DIR / 'processed'),
    'model_path': str(BASE_DIR / 'model' / 'saved_models')
}

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'medical_chatbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Training configuration
TRAINING_CONFIG = {
    'batch_size': 32,
    'epochs': 10,
    'learning_rate': 1e-5,
    'max_length': 512
}

# Validation configuration
VALIDATION_CONFIG = {
    'min_confidence_threshold': 0.7,
    'max_symptoms_per_visit': 10,
    'required_fields': ['patient_id', 'symptoms', 'timestamp']
}