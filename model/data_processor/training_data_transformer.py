# data_processor/training_data_transformer.py
import json
import pandas as pd
from typing import List, Dict, Any, Union
import numpy as np
from sklearn.preprocessing import LabelEncoder
from model.data_processor.validation_schemas import Symptom, Condition, Department

class TrainingDataTransformer:
    def __init__(self):
        self.label_encoders = {}
        self.symptom_vectors = {}
        
    def transform_conversations(self, alpaca_data: List[Dict], chatdoctor_data: List[Dict]) -> List[Dict]:
        """Transform conversation data for training"""
        transformed_data = []
        
        # Transform general conversations
        for conv in alpaca_data:
            transformed_data.append({
                "instruction": conv["instruction"],
                "input": conv["input"],
                "output": conv["output"],
                "conversation_type": "general"
            })
            
        # Transform medical conversations
        for conv in chatdoctor_data:
            transformed_data.append({
                "instruction": conv["instruction"],
                "input": conv["input"],
                "output": conv["output"],
                "conversation_type": "medical"
            })
            
        return transformed_data

    def transform_medical_rules(self, 
                              symptoms_data: List[Symptom],
                              conditions_data: List[Condition],
                              departments_data: List[Department]) -> Dict:
        """Transform medical rules into training format"""
        symptom_vectors = {}
        
        # Process symptoms
        for symptom in symptoms_data:
            symptom_dict = symptom.dict()
            vectors = {
                "id": symptom_dict["symptom_id"],
                "name": symptom_dict["symptom_name"],
                "severity": symptom_dict["priority_level"],
                "conditions": symptom_dict["related_conditions"]
            }
            symptom_vectors[symptom_dict["symptom_name"]] = vectors

        # Process conditions
        condition_mappings = {}
        for condition in conditions_data:
            condition_dict = condition.dict()
            mapping = {
                "id": condition_dict["condition_id"],
                "name": condition_dict["condition_name"],
                "symptoms": condition_dict["symptoms"],
                "department": condition_dict["department_name"]
            }
            condition_mappings[condition_dict["condition_name"]] = mapping

        # Process departments
        department_mappings = {}
        for dept in departments_data:
            dept_dict = dept.dict()
            mapping = {
                "id": dept_dict["department_id"],
                "name": dept_dict["department_name"],
                "conditions": dept_dict["common_conditions"]
            }
            department_mappings[dept_dict["department_name"]] = mapping

        return {
            "symptoms": symptom_vectors,
            "conditions": condition_mappings,
            "departments": department_mappings
        }

    def create_symptom_embeddings(self, symptoms_data: List[Symptom]) -> Dict[str, Dict]:
        """Create numerical embeddings for symptoms"""
        self.label_encoders["severity"] = LabelEncoder()
        self.label_encoders["conditions"] = LabelEncoder()

        symptoms_dicts = [symptom.dict() for symptom in symptoms_data]
        
        # Prepare data for encoding
        severity_levels = [s["priority_level"] for s in symptoms_dicts]
        conditions = list(set([c for s in symptoms_dicts for c in s["related_conditions"]]))
        
        # Fit encoders
        self.label_encoders["severity"].fit(severity_levels)
        self.label_encoders["conditions"].fit(conditions)
        
        # Create embeddings
        embeddings = {}
        for symptom in symptoms_dicts:
            severity_encoded = self.label_encoders["severity"].transform([symptom["priority_level"]])[0]
            conditions_encoded = self.label_encoders["conditions"].transform(symptom["related_conditions"])
            
            embedding = {
                "id": symptom["symptom_id"],
                "name": symptom["symptom_name"],
                "severity_encoded": float(severity_encoded),
                "conditions_encoded": conditions_encoded.tolist(),
                "vector": np.concatenate([[severity_encoded], conditions_encoded]).tolist()
            }
            embeddings[symptom["symptom_name"]] = embedding
            
        return embeddings

    def prepare_training_data(self, 
                            conversation_data: List[Dict], 
                            medical_rules: Dict,
                            embeddings_data: Dict) -> Dict:
        """Prepare final training data"""
        try:
            # Prepare encoder information
            encoder_info = {}
            for name, encoder in self.label_encoders.items():
                encoder_info[name] = {
                    "classes": encoder.classes_.tolist(),
                    "n_classes": len(encoder.classes_)
                }

            # Construct training data structure
            training_data = {
                "conversations": conversation_data,
                "rules": medical_rules,
                "embeddings": embeddings_data,
                "encoders": encoder_info,
                "metadata": {
                    "n_conversations": len(conversation_data),
                    "n_symptoms": len(medical_rules["symptoms"]),
                    "n_conditions": len(medical_rules["conditions"]),
                    "n_departments": len(medical_rules["departments"])
                }
            }

            # Validate the structure
            required_keys = ["conversations", "rules", "embeddings", "encoders", "metadata"]
            for key in required_keys:
                if key not in training_data:
                    raise ValueError(f"Training data missing required key: {key}")

            return training_data

        except Exception as e:
            print(f"Error preparing training data: {str(e)}")
            raise