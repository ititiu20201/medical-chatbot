# data_processor/pipeline.py
import logging
from typing import Dict, List, Any
from model.data_processor.text_standardization import TextStandardizer
from model.data_processor.validation_schemas import *
from model.data_processor.training_data_transformer import TrainingDataTransformer

class DataPipeline:
    def __init__(self):
        self.text_standardizer = TextStandardizer()
        self.transformer = TrainingDataTransformer()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # def process_patient_data(self, raw_data: Dict) -> List[Patient]:
    #     """Process patient information"""
    #     try:
    #         processed_patients = []
    #         for patient_data in raw_data["patients"]:
    #             # Standardize text fields
    #             patient_data["basic_info"]["name"] = self.text_standardizer.standardize_name(
    #                 patient_data["basic_info"]["name"]
    #             )
    #             patient_data["basic_info"]["contact"]["address"] = self.text_standardizer.standardize_address(
    #                 patient_data["basic_info"]["contact"]["address"]
    #             )
    #             patient_data["basic_info"]["emergency_contact"]["name"] = self.text_standardizer.standardize_name(
    #                 patient_data["basic_info"]["emergency_contact"]["name"]
    #             )

    #             # Standardize medical history fields
    #             if isinstance(patient_data["medical_history"]["chronic_conditions"], list):
    #                 patient_data["medical_history"]["chronic_conditions"] = [
    #                     self.text_standardizer.standardize_vietnamese(condition)
    #                     for condition in patient_data["medical_history"]["chronic_conditions"]
    #                 ]
    #             if isinstance(patient_data["medical_history"]["allergies"], list):
    #                 patient_data["medical_history"]["allergies"] = [
    #                     self.text_standardizer.standardize_vietnamese(allergy)
    #                     for allergy in patient_data["medical_history"]["allergies"]
    #                 ]
    #             if isinstance(patient_data["medical_history"]["current_medications"], list):
    #                 for medication in patient_data["medical_history"]["current_medications"]:
    #                     medication["name"] = self.text_standardizer.standardize_vietnamese(medication["name"])

    #             # Validate using Pydantic model
    #             patient = Patient(**patient_data)
    #             processed_patients.append(patient)

    #         return processed_patients
        # except Exception as e:
        #     self.logger.error(f"Error processing patient data: {str(e)}. Data: {patient_data}")
        #     raise

    def process_patient_data(self, raw_data: Dict) -> List[Patient]:
        """Process patient information"""
        try:
            processed_patients = []
            for patient_data in raw_data["patients"]:
            # Standardize text fields
                patient_data["basic_info"]["name"] = self.text_standardizer.standardize_name(
                    patient_data["basic_info"]["name"]
                )
                patient_data["basic_info"]["contact"]["address"] = self.text_standardizer.standardize_address(
                    patient_data["basic_info"]["contact"]["address"]
                )
                patient_data["basic_info"]["emergency_contact"]["name"] = self.text_standardizer.standardize_name(
                    patient_data["basic_info"]["emergency_contact"]["name"]
                )

            # Standardize medical history fields
                if isinstance(patient_data["medical_history"]["chronic_conditions"], list):
                    patient_data["medical_history"]["chronic_conditions"] = [
                        self.text_standardizer.standardize_vietnamese(condition)
                        for condition in patient_data["medical_history"]["chronic_conditions"]
                ]
                if isinstance(patient_data["medical_history"]["allergies"], list):
                    patient_data["medical_history"]["allergies"] = [
                        self.text_standardizer.standardize_vietnamese(allergy)
                        for allergy in patient_data["medical_history"]["allergies"]
                    ]
                if isinstance(patient_data["medical_history"]["current_medications"], list) and len(patient_data["medical_history"]["current_medications"]) > 0:
                    for medication in patient_data["medical_history"]["current_medications"]:
                        medication["name"] = self.text_standardizer.standardize_vietnamese(medication["name"])

            # Validate using Pydantic model
                patient = Patient(**patient_data)
                processed_patients.append(patient)

            return processed_patients
        except Exception as e:
            self.logger.error(f"Error processing patient data: {str(e)}. Data: {patient_data}")
            raise



    def process_medical_rules(self, symptoms_data: Dict, conditions_data: Dict, departments_data: Dict) -> Dict:
        """Process medical rules and symptoms"""
        try:
            # Transform symptoms
            processed_symptoms = []
            for symptom in symptoms_data["symptoms"]:
                symptom["symptom_name"] = self.text_standardizer.standardize_vietnamese(
                    symptom["symptom_name"]
                )
                processed_symptoms.append(Symptom(**symptom))

            # Transform conditions
            processed_conditions = []
            for condition in conditions_data["conditions"]:
                condition["symptoms"] = [
                    self.text_standardizer.standardize_vietnamese(s)
                    for s in condition["symptoms"]
                ]
                processed_conditions.append(Condition(**condition))

            # Transform departments
            processed_departments = []
            for department in departments_data["departments"]:
                processed_departments.append(Department(**department))

            return {
                "symptoms": processed_symptoms,
                "conditions": processed_conditions,
                "departments": processed_departments
            }
        except Exception as e:
            self.logger.error(f"Error processing medical rules: {str(e)}. Symptoms data: {symptoms_data}")
            raise

    def process_training_data(self, alpaca_data: List[Dict], chatdoctor_data: List[Dict], medical_rules: Dict) -> Dict:
        """Process conversation training data"""
        try:
            # Transform conversations
            conversation_data = self.transformer.transform_conversations(
                alpaca_data, chatdoctor_data
            )

            # Transform medical rules
            transformed_rules = self.transformer.transform_medical_rules(
                medical_rules["symptoms"],
                medical_rules["conditions"],
                medical_rules["departments"]
            )

            # Create symptom embeddings
            symptom_embeddings = self.transformer.create_symptom_embeddings(
                medical_rules["symptoms"]
            )

            # Prepare final training data
            training_data = self.transformer.prepare_training_data(
                conversation_data,
                transformed_rules,
                symptom_embeddings
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
            processed_patients = self.process_patient_data(patient_data)

            # Process medical rules
            processed_rules = self.process_medical_rules(
                symptoms_data,
                conditions_data,
                departments_data
            )

            # Process training data
            training_data = self.process_training_data(
                alpaca_data,
                chatdoctor_data,
                processed_rules
            )

            return {
                "patients": processed_patients,
                "medical_rules": processed_rules,
                "training_data": training_data
            }
        except Exception as e:
            self.logger.error(f"Error in pipeline: {str(e)}")
            raise

   