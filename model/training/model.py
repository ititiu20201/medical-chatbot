# model/training/model.py
import torch
from torch import nn
from transformers import AutoModel, AutoConfig
import os

class MedicalPhoBERT(nn.Module):
    def __init__(self, model_name="vinai/phobert-base", dropout_rate=0.1):
        super().__init__()
        self.config = AutoConfig.from_pretrained(model_name)
        self.phobert = AutoModel.from_pretrained(model_name)
        
        # Add dropout
        self.dropout = nn.Dropout(dropout_rate)
        
        # Add classification head for sequence generation
        self.classifier = nn.Linear(self.config.hidden_size, self.config.vocab_size)

    def forward(self, input_ids, attention_mask, labels=None):
        # Get PhoBERT outputs
        outputs = self.phobert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )

        sequence_output = outputs.last_hidden_state
        
        # Apply dropout and get logits
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)

        outputs = {'logits': logits}

        if labels is not None:
            # Calculate loss
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            # Reshape logits and labels for loss calculation
            # logits: (batch_size, sequence_length, vocab_size)
            # labels: (batch_size, sequence_length)
            loss = loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))
            outputs['loss'] = loss

        return outputs

    def save_model(self, path):
        """Save the model to a directory"""
        os.makedirs(path, exist_ok=True)
        
        # Save the base PhoBERT model
        self.phobert.save_pretrained(os.path.join(path, "phobert"))
        
        # Save the custom components
        torch.save({
            'classifier_state_dict': self.classifier.state_dict(),
            'dropout_state_dict': self.dropout.state_dict(),
            'config': self.config
        }, os.path.join(path, "medical_components.pt"))

    @classmethod
    def load_model(cls, path):
        """Load the model from a directory"""
        # Create a new instance
        model = cls()
        
        # Load the base PhoBERT model
        model.phobert = AutoModel.from_pretrained(os.path.join(path, "phobert"))
        
        # Load the custom components
        custom_components = torch.load(os.path.join(path, "medical_components.pt"))
        model.classifier.load_state_dict(custom_components['classifier_state_dict'])
        model.dropout.load_state_dict(custom_components['dropout_state_dict'])
        model.config = custom_components['config']
        
        return model