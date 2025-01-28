# data_processor/utils/db_utils.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Dict, Any
from ..config import DB_CONFIG
import json

logger = logging.getLogger(__name__)

class DatabaseUtils:
    def __init__(self):
        # Create database URL from config
        self.db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        try:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    def save_processed_data(self, data: Dict[str, Any]) -> bool:
        """Save processed data to database"""
        session = self.Session()
        try:
            # Save patients
            if 'patients' in data:
                for patient in data['patients']:
                    session.execute(
                        text("""
                        INSERT INTO patients (
                            patient_id, name, date_of_birth, gender, blood_type
                        ) VALUES (:patient_id, :name, :date_of_birth, :gender, :blood_type)
                        ON CONFLICT (patient_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            date_of_birth = EXCLUDED.date_of_birth,
                            gender = EXCLUDED.gender,
                            blood_type = EXCLUDED.blood_type
                        """),
                        {
                            'patient_id': patient.patient_id,
                            'name': patient.basic_info.name,
                            'date_of_birth': patient.basic_info.date_of_birth,
                            'gender': patient.basic_info.gender,
                            'blood_type': patient.basic_info.blood_type
                        }
                    )

            # Save symptoms
            if 'symptoms' in data:
                for symptom in data['symptoms']:
                    session.execute(
                        text("""
                        INSERT INTO symptoms (
                            symptom_id, name, priority_level
                        ) VALUES (:symptom_id, :name, :priority_level)
                        ON CONFLICT (symptom_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            priority_level = EXCLUDED.priority_level
                        """),
                        symptom
                    )

            # Save departments
            if 'departments' in data:
                for dept in data['departments']:
                    session.execute(
                        text("""
                        INSERT INTO departments (
                            department_id, name
                        ) VALUES (:department_id, :name)
                        ON CONFLICT (department_id) DO UPDATE SET
                            name = EXCLUDED.name
                        """),
                        dept
                    )

            # Save visits
            if 'visits' in data:
                for visit in data['visits']:
                    session.execute(
                        text("""
                        INSERT INTO visits (
                            visit_id, patient_id, visit_timestamp, symptoms,
                            priority_level, department_id, queue_number
                        ) VALUES (
                            :visit_id, :patient_id, :visit_timestamp, :symptoms,
                            :priority_level, :department_id, :queue_number
                        )
                        """),
                        {
                            'visit_id': visit.visit_id,
                            'patient_id': visit.patient_id,
                            'visit_timestamp': visit.timestamp,
                            'symptoms': json.dumps(visit.symptoms),
                            'priority_level': visit.chatbot_analysis.priority_level,
                            'department_id': visit.chatbot_analysis.recommended_department,
                            'queue_number': visit.chatbot_analysis.queue_number
                        }
                    )

            session.commit()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while saving processed data: {str(e)}")
            session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error while saving processed data: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()

    def load_training_data(self) -> Dict[str, Any]:
        """Load data for training from database"""
        session = self.Session()
        try:
            # Load conversations
            conversations = session.execute(
                text("SELECT * FROM training_conversations")
            ).fetchall()

            # Load symptoms
            symptoms = session.execute(
                text("SELECT * FROM symptoms")
            ).fetchall()

            # Load symptom embeddings
            embeddings = session.execute(
                text("SELECT * FROM symptom_embeddings")
            ).fetchall()

            return {
                'conversations': conversations,
                'symptoms': symptoms,
                'embeddings': embeddings
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error while loading training data: {str(e)}")
            raise
        finally:
            session.close()

    def update_symptom_mappings(self, mappings: Dict[str, Any]) -> bool:
        """Update symptom mappings in database"""
        session = self.Session()
        try:
            for symptom_id, mapping in mappings.items():
                session.execute(
                    text("""
                    UPDATE symptoms
                    SET related_conditions = :conditions,
                        severity_level = :severity
                    WHERE symptom_id = :symptom_id
                    """),
                    {
                        'symptom_id': symptom_id,
                        'conditions': json.dumps(mapping['conditions']),
                        'severity': mapping['severity']
                    }
                )
            
            session.commit()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating symptom mappings: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_patient_history(self, patient_id: str) -> Dict[str, Any]:
        """Get patient history from database"""
        session = self.Session()
        try:
            # Get basic patient info
            patient = session.execute(
                text("SELECT * FROM patients WHERE patient_id = :patient_id"),
                {'patient_id': patient_id}
            ).fetchone()

            # Get visit history
            visits = session.execute(
                text("SELECT * FROM visits WHERE patient_id = :patient_id ORDER BY visit_timestamp DESC"),
                {'patient_id': patient_id}
            ).fetchall()

            # Get medical conditions
            conditions = session.execute(
                text("SELECT * FROM patient_conditions WHERE patient_id = :patient_id"),
                {'patient_id': patient_id}
            ).fetchall()

            return {
                'patient': patient,
                'visits': visits,
                'conditions': conditions
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching patient history: {str(e)}")
            raise
        finally:
            session.close()