-- backend/db/schema.sql

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE gender_type AS ENUM ('Nam', 'Nữ');
CREATE TYPE blood_type AS ENUM ('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-');
CREATE TYPE severity_level AS ENUM ('mild', 'moderate', 'severe');
CREATE TYPE condition_status AS ENUM ('active', 'inactive', 'resolved');

-- Patients table
CREATE TABLE patients (
    patient_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_type NOT NULL,
    blood_type blood_type NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emergency contacts table
CREATE TABLE emergency_contacts (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    current_queue INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medical conditions table
CREATE TABLE medical_conditions (
    condition_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER REFERENCES departments(department_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Symptoms table
CREATE TABLE symptoms (
    symptom_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    priority_level severity_level NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Condition-Symptom mapping
CREATE TABLE condition_symptoms (
    condition_id INTEGER REFERENCES medical_conditions(condition_id),
    symptom_id INTEGER REFERENCES symptoms(symptom_id),
    PRIMARY KEY (condition_id, symptom_id)
);

-- Patient medical history
CREATE TABLE patient_conditions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    condition_id INTEGER REFERENCES medical_conditions(condition_id),
    diagnosed_date DATE,
    status condition_status NOT NULL,
    last_followup DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient allergies
CREATE TABLE patient_allergies (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    allergy_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Past surgeries
CREATE TABLE past_surgeries (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    procedure_name VARCHAR(200) NOT NULL,
    surgery_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Current medications
CREATE TABLE current_medications (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    medication_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient lifestyle
CREATE TABLE patient_lifestyle (
    patient_id VARCHAR(10) PRIMARY KEY REFERENCES patients(patient_id),
    smoking VARCHAR(50) NOT NULL,
    alcohol VARCHAR(50) NOT NULL,
    exercise VARCHAR(50) NOT NULL,
    diet VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visits
CREATE TABLE visits (
    visit_id VARCHAR(10) PRIMARY KEY,
    patient_id VARCHAR(10) REFERENCES patients(patient_id),
    visit_timestamp TIMESTAMP NOT NULL,
    symptoms TEXT[] NOT NULL,
    priority_level severity_level NOT NULL,
    department_id INTEGER REFERENCES departments(department_id),
    queue_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visit analysis
CREATE TABLE visit_analysis (
    visit_id VARCHAR(10) PRIMARY KEY REFERENCES visits(visit_id),
    predicted_conditions JSONB NOT NULL,
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices
CREATE INDEX idx_patient_id ON patients(patient_id);
CREATE INDEX idx_visit_timestamp ON visits(visit_timestamp);
CREATE INDEX idx_department_id ON medical_conditions(department_id);
CREATE INDEX idx_condition_symptoms ON condition_symptoms(condition_id, symptom_id);

-- Model versions
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    trained_date TIMESTAMP NOT NULL,
    performance_metrics JSONB NOT NULL,
    model_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);