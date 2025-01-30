# data_processor/pipeline.py
import logging
from typing import Dict, List, Any, Union
from model.data_processor.text_standardization import TextStandardizer
from model.data_processor.validation_schemas import *
from model.data_processor.training_data_transformer import TrainingDataTransformer

class DataPipeline:
    def __init__(self):
        self.text_standardizer = TextStandardizer()
        self.transformer = TrainingDataTransformer()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _extract_list_data(self, data: Union[Dict, List], key: str = None) -> List:
        """Helper method to extract list data whether it's nested in a dict or direct list"""
        if isinstance(data, dict):
            # If key is provided, try to use it, otherwise try common keys
            if key and key in data:
                return data[key]
            # Try common plural keys (e.g., 'patients', 'symptoms')
            for possible_key in [key, f"{key}s" if key else None, 'data', 'items']:
                if possible_key and possible_key in data:
                    return data[possible_key]
            # If no matching key found, return first list value found
            for value in data.values():
                if isinstance(value, list):
                    return value
            raise ValueError(f"Could not find list data in dictionary: {data.keys()}")
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Input must be dict or list, got {type(data)}")

    def process_patient_data(self, raw_data: Dict) -> List[Patient]:
        """Process patient information"""
        try:
            processed_patients = []
            patients_data = self._extract_list_data(raw_data, 'patients')
            
            for patient_data in patients_data:
                try:
                    # Standardize basic info
                    patient_data["basic_info"]["name"] = self.text_standardizer.standardize_name(
                        patient_data["basic_info"]["name"]
                    )
                    patient_data["basic_info"]["contact"]["address"] = self.text_standardizer.standardize_address(
                        patient_data["basic_info"]["contact"]["address"]
                    )
                    patient_data["basic_info"]["emergency_contact"]["name"] = self.text_standardizer.standardize_name(
                        patient_data["basic_info"]["emergency_contact"]["name"]
                    )

                    # Standardize medical history
                    medical_history = patient_data["medical_history"]
                    
                    # Handle chronic conditions
                    if medical_history.get("chronic_conditions"):
                        if isinstance(medical_history["chronic_conditions"], list):
                            medical_history["chronic_conditions"] = [
                                self.text_standardizer.standardize_vietnamese(condition)
                                for condition in medical_history["chronic_conditions"]
                            ]
                        elif isinstance(medical_history["chronic_conditions"], str):
                            medical_history["chronic_conditions"] = [
                                self.text_standardizer.standardize_vietnamese(medical_history["chronic_conditions"])
                            ]

                    # Handle allergies
                    if medical_history.get("allergies"):
                        if isinstance(medical_history["allergies"], list):
                            medical_history["allergies"] = [
                                self.text_standardizer.standardize_vietnamese(allergy)
                                for allergy in medical_history["allergies"]
                            ]
                        elif isinstance(medical_history["allergies"], str):
                            medical_history["allergies"] = [
                                self.text_standardizer.standardize_vietnamese(medical_history["allergies"])
                            ]

                    # Handle medications
                    if medical_history.get("current_medications"):
                        if isinstance(medical_history["current_medications"], list):
                            for medication in medical_history["current_medications"]:
                                if isinstance(medication, dict):
                                    medication["name"] = self.text_standardizer.standardize_vietnamese(medication["name"])

                    # Handle surgeries
                    if medical_history.get("past_surgeries"):
                        if isinstance(medical_history["past_surgeries"], list):
                            for surgery in medical_history["past_surgeries"]:
                                if isinstance(surgery, dict):
                                    surgery["procedure"] = self.text_standardizer.standardize_vietnamese(surgery["procedure"])

                    # Validate using Pydantic model
                    patient = Patient(**patient_data)
                    processed_patients.append(patient)

                except Exception as e:
                    self.logger.error(f"Error processing individual patient: {str(e)}. Patient data: {patient_data}")
                    continue  # Skip this patient but continue processing others

            if not processed_patients:
                raise ValueError("No patients were successfully processed")

            return processed_patients

        except Exception as e:
            self.logger.error(f"Error processing patient data: {str(e)}")
            raise

    def process_medical_rules(self, symptoms_data: Dict, conditions_data: Dict, departments_data: Dict) -> Dict:
        """Process medical rules and symptoms"""
        try:
            # Transform symptoms
            symptoms = self._extract_list_data(symptoms_data, 'symptoms')
            processed_symptoms = []
            for symptom in symptoms:
                try:
                    # Standardize symptom name
                    symptom["symptom_name"] = self.text_standardizer.standardize_vietnamese(
                        symptom["symptom_name"]
                    )
                    # Standardize related conditions
                    if "related_conditions" in symptom:
                        symptom["related_conditions"] = [
                            self.text_standardizer.standardize_vietnamese(condition)
                            for condition in symptom["related_conditions"]
                        ]
                    processed_symptoms.append(Symptom(**symptom))
                except Exception as e:
                    self.logger.error(f"Error processing symptom: {str(e)}. Symptom: {symptom}")
                    continue

            # Transform conditions
            conditions = self._extract_list_data(conditions_data, 'conditions')
            processed_conditions = []
            for condition in conditions:
                try:
                    # Standardize condition name and symptoms
                    condition["condition_name"] = self.text_standardizer.standardize_vietnamese(
                        condition["condition_name"]
                    )
                    condition["symptoms"] = [
                        self.text_standardizer.standardize_vietnamese(s)
                        for s in condition["symptoms"]
                    ]
                    if "department_name" in condition:
                        condition["department_name"] = self.text_standardizer.standardize_vietnamese(
                            condition["department_name"]
                        )
                    processed_conditions.append(Condition(**condition))
                except Exception as e:
                    self.logger.error(f"Error processing condition: {str(e)}. Condition: {condition}")
                    continue

            # Transform departments
            departments = self._extract_list_data(departments_data, 'departments')
            processed_departments = []
            for department in departments:
                try:
                    # Standardize department name and common conditions
                    department["department_name"] = self.text_standardizer.standardize_vietnamese(
                        department["department_name"]
                    )
                    if "common_conditions" in department:
                        department["common_conditions"] = [
                            self.text_standardizer.standardize_vietnamese(condition)
                            for condition in department["common_conditions"]
                        ]
                    processed_departments.append(Department(**department))
                except Exception as e:
                    self.logger.error(f"Error processing department: {str(e)}. Department: {department}")
                    continue

            return {
                "symptoms": processed_symptoms,
                "conditions": processed_conditions,
                "departments": processed_departments
            }
        except Exception as e:
            self.logger.error(f"Error processing medical rules: {str(e)}")
            raise

    def process_training_data(self, alpaca_data: List[Dict], chatdoctor_data: List[Dict], medical_rules: Dict) -> Dict:
        """Process conversation training data"""
        try:
        # Transform conversations
            conversation_data = self.transformer.transform_conversations(
                alpaca_data,
                chatdoctor_data
        )

        # Create embeddings first
            embeddings = self.transformer.create_symptom_embeddings(
                medical_rules["symptoms"]
        )

        # Transform medical rules
            transformed_rules = self.transformer.transform_medical_rules(
                medical_rules["symptoms"],
                medical_rules["conditions"],
                medical_rules["departments"]
        )

        # Prepare final training data
            training_data = self.transformer.prepare_training_data(
                conversation_data,
                transformed_rules,
                embeddings  # Pass embeddings here
        )

            return training_data
        except Exception as e:
            self.logger.error(f"Error processing training data: {str(e)}. Medical rules: {medical_rules}")
            raise

    def run_pipeline(
        self, 
        patient_data: Dict, 
        symptoms_data: Dict, 
        conditions_data: Dict, 
        departments_data: Dict, 
        alpaca_data: List[Dict], 
        chatdoctor_data: List[Dict]
    ) -> Dict:
        """Run complete data processing pipeline"""
        try:
            # Process patient data
            self.logger.info("Processing patient data...")
            processed_patients = self.process_patient_data(patient_data)
            self.logger.info(f"Successfully processed {len(processed_patients)} patients")

            # Process medical rules
            self.logger.info("Processing medical rules...")
            processed_rules = self.process_medical_rules(
                symptoms_data,
                conditions_data,
                departments_data
            )
            self.logger.info(f"Successfully processed medical rules: {len(processed_rules['symptoms'])} symptoms, "
                           f"{len(processed_rules['conditions'])} conditions, "
                           f"{len(processed_rules['departments'])} departments")

            # Process training data
            self.logger.info("Processing training data...")
            training_data = self.process_training_data(
                alpaca_data,
                chatdoctor_data,
                processed_rules
            )
            self.logger.info("Successfully processed training data")

            # Validate final output
            if not processed_patients or not processed_rules or not training_data:
                raise ValueError("One or more pipeline components failed to produce output")

            return {
                "patients": processed_patients,
                "medical_rules": processed_rules,
                "training_data": training_data
            }

        except Exception as e:
            self.logger.error(f"Error in pipeline: {str(e)}")
            raise