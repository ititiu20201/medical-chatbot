# model/training/dataset.py
import torch
from torch.utils.data import Dataset
from transformers import PhobertTokenizer
import json
from typing import List, Dict, Any

class MedicalDataset(Dataset):
    def __init__(
        self,
        conversations: List[Dict[str, Any]],
        rules: Dict[str, Any],
        tokenizer: PhobertTokenizer,
        max_length: int = 256
    ):
        self.conversations = conversations
        self.rules = rules
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Filter medical conversations
        self.medical_conversations = [
            conv for conv in conversations
            if conv['conversation_type'] == 'medical'
        ]

    def __len__(self):
        return len(self.medical_conversations)

    def __getitem__(self, idx):
        conversation = self.medical_conversations[idx]
        
        # Combine instruction and input for the full context
        input_text = conversation['instruction']
        if conversation['input']:
            input_text += '\n' + conversation['input']
        
        # Tokenize input
        encoding = self.tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # Get expected output
        output_text = conversation['output']
        output_encoding = self.tokenizer.encode_plus(
            output_text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_token_type_ids=False,
            return_attention_mask=True,
            return_tensors='pt'
        )

        # Remove the batch dimension since DataLoader will add it
        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)
        labels = output_encoding['input_ids'].squeeze(0)
        
        # Create the output dictionary
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }