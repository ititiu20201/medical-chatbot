import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Tuple
from underthesea import word_tokenize
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalDataPreprocessor:
    def __init__(self, raw_data_path: str = 'data/raw'):
        """Initialize the preprocessor with path to raw data"""
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path('data/processed')
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

    def load_json_file(self, file_path: Path) -> Dict:
        """Load JSON file and return data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return {}

    def preprocess_text(self, text: str) -> str:
        """Preprocess Vietnamese text"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Vietnamese word tokenization
        text = word_tokenize(text, format="text")
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text

    def create_training_data(self) -> pd.DataFrame:
        """Create training dataset"""
        try:
            # Load disease-symptom data
            with open(self.raw_data_path / 'disease_symptom.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # Skip header

            training_data = []
            specialties = set()

            # Process disease-symptom data
            for line in lines:
                parts = line.strip().split(';', 2)
                if len(parts) == 3:
                    specialty, disease, symptoms = parts
                    specialties.add(specialty.strip())
                    try:
                        symptom_list = eval(symptoms.strip())
                        training_data.append({
                            'input': ' '.join(symptom_list),
                            'specialty': specialty.strip(),
                            'output_type': 'specialty'
                        })
                    except:
                        continue

            # Load conversation data
            alpaca_path = self.raw_data_path / 'alpaca_data.json'
            chatdoctor_path = self.raw_data_path / 'chatdoctor5k.json'
            
            # Add conversation data
            if alpaca_path.exists():
                with open(alpaca_path, 'r', encoding='utf-8') as f:
                    alpaca_data = json.load(f)
                    for item in alpaca_data:
                        if 'input' in item and 'output' in item:
                            training_data.append({
                                'input': item['input'],
                                'output': item['output'],
                                'output_type': 'conversation'
                            })

            if chatdoctor_path.exists():
                with open(chatdoctor_path, 'r', encoding='utf-8') as f:
                    chatdoctor_data = json.load(f)
                    for item in chatdoctor_data:
                        if 'input' in item and 'output' in item:
                            training_data.append({
                                'input': item['input'],
                                'output': item['output'],
                                'output_type': 'conversation'
                            })

            # Create DataFrame
            df = pd.DataFrame(training_data)
            
            # Save specialty mapping
            specialty_map = {spec: idx for idx, spec in enumerate(sorted(specialties))}
            with open(self.processed_data_path / 'specialty_map.json', 'w', encoding='utf-8') as f:
                json.dump(specialty_map, f, ensure_ascii=False, indent=2)

            logger.info(f"Created dataset with {len(df)} samples")
            logger.info(f"Found {len(specialties)} unique specialties: {specialties}")
            
            return df

        except Exception as e:
            logger.error(f"Error creating training data: {str(e)}")
            raise

    def save_processed_data(self, output_path: str = 'data/processed'):
        """Save processed data to files"""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        training_data = self.create_training_data()
        
        # Split into train/val/test
        train_size = int(0.8 * len(training_data))
        val_size = int(0.1 * len(training_data))
        
        indices = np.random.permutation(len(training_data))
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        # Save splits
        training_data.iloc[train_indices].to_csv(
            output_path / 'train.csv', index=False, encoding='utf-8'
        )
        training_data.iloc[val_indices].to_csv(
            output_path / 'val.csv', index=False, encoding='utf-8'
        )
        training_data.iloc[test_indices].to_csv(
            output_path / 'test.csv', index=False, encoding='utf-8'
        )
        
        logger.info(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    preprocessor = MedicalDataPreprocessor()
    preprocessor.save_processed_data()