#!/usr/bin/env python3
import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from model.data_processor.pipeline import DataPipeline
from model.data_processor.config import DATA_CONFIG
from model.data_processor.utils.data_quality import DataQualityChecker
from model.data_processor.utils.db_utils import DatabaseUtils
import pprint

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.pipeline = DataPipeline()
        self.quality_checker = DataQualityChecker()
        self.db_utils = DatabaseUtils()
        
    def print_data_structure(self, data: Dict[str, Any], title: str = "Data Structure") -> None:
        """Print the structure and first items of each data component"""
        logger.info(f"\n{'='*50}\n{title}\n{'='*50}")
        for key, value in data.items():
            logger.info(f"\nComponent: {key}")
            if isinstance(value, dict):
                logger.info(f"Keys: {list(value.keys())}")
                first_key = next(iter(value))
                logger.info(f"Sample of first item: \n{pprint.pformat(value[first_key], indent=2)[:500]}...")
            elif isinstance(value, list):
                logger.info(f"Length: {len(value)}")
                if value:
                    logger.info(f"Sample of first item: \n{pprint.pformat(value[0], indent=2)[:500]}...")
            else:
                logger.info(f"Type: {type(value)}")

    def load_json_file(self, file_path: str) -> dict:
        """Load and parse a JSON file"""
        try:
            logger.info(f"Loading file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {file_path}")
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            raise

    def load_raw_data(self) -> Dict[str, Any]:
        """Load all raw data files"""
        raw_data_path = Path(DATA_CONFIG['raw_data_path'])
        logger.info(f"\nLoading data from: {raw_data_path}")
        
        required_files = {
            'alpaca_data': 'alpaca_data.json',
            'chatdoctor_data': 'chatdoctor5k.json',
            'disease_details': 'Disease_Details_Data.json',
            'departments': 'Medical_Departments.json',
            'patient_info': 'PatientInformation.json',
            'symptoms': 'Symptoms_MedicalConditions.json'
        }
        
        data = {}
        for key, filename in required_files.items():
            try:
                data[key] = self.load_json_file(raw_data_path / filename)
            except Exception as e:
                logger.error(f"Failed to load {key} from {filename}")
                raise
                
        return data

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data quality and consistency"""
        logger.info("\nValidating data...")
        
        # Check data completeness
        if not self.quality_checker.check_data_completeness(data):
            logger.error("Data completeness check failed")
            logger.error("Error logs:")
            logger.error("\n".join(self.quality_checker.get_error_logs()))
            return False
            
        # Check data consistency
        if not self.quality_checker.check_data_consistency(data):
            logger.error("Data consistency check failed")
            logger.error("Error logs:")
            logger.error("\n".join(self.quality_checker.get_error_logs()))
            return False
            
        logger.info("Data validation successful")
        return True

    def process_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process the data through the pipeline"""
        try:
            logger.info("\nProcessing data through pipeline...")
            processed_data = self.pipeline.run_pipeline(
                patient_data=data['patient_info'],
                symptoms_data=data['symptoms'],
                conditions_data=data['disease_details'],
                departments_data=data['departments'],
                alpaca_data=data['alpaca_data'],
                chatdoctor_data=data['chatdoctor_data']
            )
            logger.info("Data processing completed successfully")
            return processed_data
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return None

    def save_processed_data(self, processed_data: Dict[str, Any]) -> bool:
        """Save processed data to files and database"""
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        def convert_to_dict(item):
            """Recursively convert Pydantic models and datetime objects in nested structures"""
            if hasattr(item, 'dict'):  # Check if it's a Pydantic model
                return convert_to_dict(item.dict())
            elif isinstance(item, dict):
                return {key: convert_to_dict(value) for key, value in item.items()}
            elif isinstance(item, list):
                return [convert_to_dict(element) for element in item]
            elif isinstance(item, datetime):
                return item.isoformat()
            return item

        try:
        # Convert all data to JSON-serializable format
            logger.info("Converting data to JSON-serializable format...")
            processed_data_json = convert_to_dict(processed_data)
            
        # Save to files
            processed_data_path = Path(DATA_CONFIG['processed_data_path'])
            processed_data_path.mkdir(parents=True, exist_ok=True)
        
            logger.info("\nSaving processed data to files...")
            for data_type, data_content in processed_data_json.items():
                output_file = processed_data_path / f"{data_type}.json"
                logger.info(f"Saving {data_type} to {output_file}")
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data_content, f, 
                                ensure_ascii=False, 
                                indent=2, 
                                cls=DateTimeEncoder)
                    logger.info(f"Successfully saved {data_type}")
                except Exception as e:
                    logger.error(f"Error saving {data_type}: {str(e)}")
                    raise
        
        # Save to database
            logger.info("\nSaving processed data to database...")
            self.db_utils.save_processed_data(processed_data_json)
        
            logger.info("All data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")
            return False
    

    def create_backup(self, data: Dict[str, Any]) -> None:
        """Create a backup of the processed data"""
        try:
            backup_dir = Path(DATA_CONFIG['processed_data_path']).parent / 'backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"processed_data_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Backup created at: {backup_file}")
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")

def main():
    processor = DataProcessor()
    success = False
    
    try:
        # Log system information
        logger.info("="*50)
        logger.info("Starting data processing")
        logger.info(f"Current working directory: {Path.cwd()}")
        logger.info(f"Raw data path: {Path(DATA_CONFIG['raw_data_path']).absolute()}")
        logger.info(f"Processed data path: {Path(DATA_CONFIG['processed_data_path']).absolute()}")
        logger.info("="*50)

        # Load raw data
        data = processor.load_raw_data()
        processor.print_data_structure(data, "Initial Data Structure")

        # Validate data
        if not processor.validate_data(data):
            logger.error("Data validation failed. Exiting...")
            return

        # Process data
        processed_data = processor.process_data(data)
        if processed_data is None:
            logger.error("Data processing failed. Exiting...")
            return

        # Print processed data structure
        processor.print_data_structure(processed_data, "Processed Data Structure")

        # Save processed data
        if not processor.save_processed_data(processed_data):
            logger.error("Failed to save processed data. Exiting...")
            return

        # Create backup
        processor.create_backup(processed_data)

        success = True
        logger.info("\nData processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        raise
    finally:
        if not success:
            logger.warning("Data processing did not complete successfully")
        logger.info("="*50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
        sys.exit(1)
