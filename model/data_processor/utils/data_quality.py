# model/data_processor/utils/data_quality.py
class DataQualityChecker:
    def __init__(self):
        self.error_logs = []
        
    def check_data_completeness(self, data):
        """Check if all required data types are present"""
        self.error_logs = []
        
        # Update required data types to match your actual data structure
        required_data = {
            'alpaca_data': lambda x: isinstance(x, list),
            'chatdoctor_data': lambda x: isinstance(x, list),
            'disease_details': lambda x: isinstance(x, dict) and 'conditions' in x,
            'departments': lambda x: isinstance(x, dict) and 'departments' in x,
            'patient_info': lambda x: isinstance(x, dict) and 'patients' in x,
            'symptoms': lambda x: isinstance(x, dict) and 'symptoms' in x
        }
        
        for data_type, validator in required_data.items():
            if data_type not in data or not validator(data[data_type]):
                self.error_logs.append(f"Invalid or missing data type: {data_type}")
                return False
        return True
    
    def check_data_consistency(self, data):
        """Check if data is consistent across different components"""
        self.error_logs = []
        
        try:
            # Check patient data structure
            if not data['patient_info'].get('patients'):
                self.error_logs.append("Patient data is empty")
                return False
            
            # Check symptoms data structure
            if not data['symptoms'].get('symptoms'):
                self.error_logs.append("Symptoms data is empty")
                return False
            
            # Check departments data structure
            if not data['departments'].get('departments'):
                self.error_logs.append("Departments data is empty")
                return False
            
            # Check disease details data structure
            if not data['disease_details'].get('conditions'):
                self.error_logs.append("Disease conditions data is empty")
                return False
            
            # Check training data
            if not data['alpaca_data'] or not data['chatdoctor_data']:
                self.error_logs.append("Training data is empty")
                return False
            
            return True
            
        except Exception as e:
            self.error_logs.append(f"Data consistency check error: {str(e)}")
            return False
    
    def get_error_logs(self):
        """Return all error logs"""
        return self.error_logs