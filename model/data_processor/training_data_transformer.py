# data_processor/training_data_transformer.py
import json
import pandas as pd
from typing import List, Dict, Any
import numpy as np
from sklearn.preprocessing import LabelEncoder

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
                              symptoms_data: Dict,
                              conditions_data: Dict,
                              departments_data: Dict) -> Dict:
        """Transform medical rules into training format"""
        # Create symptom embeddings
        symptom_vectors = {}
        for symptom in symptoms_data["symptoms"]:
            vector = {
                "symptom_id": symptom["symptom_id"],
                "name": symptom["symptom_name"],
                "severity": symptom["severity_level"],
                "conditions": symptom["related_conditions"]
            }
            symptom_vectors[symptom["symptom_name"]] = vector
            
        # Create condition mappings
        condition_mappings = {}
        for condition in conditions_data["conditions"]:
            mapping = {
                "condition_id": condition["condition_id"],
                "name": condition["condition_name"],
                "symptoms": condition["symptoms"],
                "department": condition["department_name"]
            }
            condition_mappings[condition["condition_name"]] = mapping
            
        # Create department rules
        department_rules = {}
        for dept in departments_data["departments"]:
            rules = {
                "department_id": dept["department_id"],
                "name": dept["department_name"],
                "conditions": dept["common_conditions"]
            }
            department_rules[dept["department_name"]] = rules
            
        return {
            "symptom_vectors": symptom_vectors,
            "condition_mappings": condition_mappings,
            "department_rules": department_rules
        }

    def create_symptom_embeddings(self, symptoms_data: Dict) -> Dict:
        """Create numerical embeddings for symptoms"""
        # Create label encoders
        self.label_encoders["severity"] = LabelEncoder()
        self.label_encoders["conditions"] = LabelEncoder()
        
        # Transform symptom data
        symptoms = symptoms_data["symptoms"]
        severity_levels = [s["severity_level"] for s in symptoms]
        conditions = [c for s in symptoms for c in s["related_conditions"]]
        
        # Fit label encoders
        self.label_encoders["severity"].fit(severity_levels)
        self.label_encoders["conditions"].fit(conditions)
        
        # Create embeddings
        embeddings = {}
        for symptom in symptoms:
            severity_encoded = self.label_encoders["severity"].transform([symptom["severity_level"]])[0]
            conditions_encoded = self.label_encoders["conditions"].transform(symptom["related_conditions"])
            
            embedding = {
                "symptom_id": symptom["symptom_id"],
                "name": symptom["symptom_name"],
                "severity_encoded": severity_encoded,
                "conditions_encoded": conditions_encoded.tolist(),
                "vector": np.concatenate([[severity_encoded], conditions_encoded])
            }
            embeddings[symptom["symptom_name"]] = embedding
            
        return embeddings

    def prepare_training_data(self, 
                            conversation_data: List[Dict], 
                            medical_rules: Dict,
                            symptom_embeddings: Dict) -> Dict:
        """Prepare final training data"""
        return {
            "conversations": conversation_data,
            "medical_rules": medical_rules,
            "symptom_embeddings": symptom_embeddings,
            "label_encoders": self.label_encoders
        }