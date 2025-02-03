import torch
import torch.nn as nn
import torch.nn.functional as F

class MedicalLoss(nn.Module):
    def __init__(self, loss_weights=None):
        super().__init__()
        self.loss_weights = loss_weights or {
            'symptoms': 1.0,
            'conditions': 1.0,
            'departments': 1.0,
            'severity': 1.0
        }
        
        # BCE loss for multi-label symptom classification
        self.symptoms_criterion = nn.BCELoss()
        # CE loss for multi-class classification tasks
        self.classification_criterion = nn.CrossEntropyLoss()
        
    def forward(self, predictions, targets):
        total_loss = 0
        losses = {}
        
        # Symptom prediction loss (multi-label)
        if 'symptoms' in predictions and 'symptoms' in targets:
            symptoms_loss = self.symptoms_criterion(
                predictions['symptoms'],
                targets['symptoms']
            )
            losses['symptoms'] = symptoms_loss
            total_loss += self.loss_weights['symptoms'] * symptoms_loss
            
        # Condition prediction loss (multi-class)
        if 'conditions' in predictions and 'conditions' in targets:
            conditions_loss = self.classification_criterion(
                predictions['conditions'],
                targets['conditions']
            )
            losses['conditions'] = conditions_loss
            total_loss += self.loss_weights['conditions'] * conditions_loss
            
        # Department prediction loss (multi-class)
        if 'departments' in predictions and 'departments' in targets:
            departments_loss = self.classification_criterion(
                predictions['departments'],
                targets['departments']
            )
            losses['departments'] = departments_loss
            total_loss += self.loss_weights['departments'] * departments_loss
            
        # Severity prediction loss (multi-class)
        if 'severity' in predictions and 'severity' in targets:
            severity_loss = self.classification_criterion(
                predictions['severity'],
                targets['severity']
            )
            losses['severity'] = severity_loss
            total_loss += self.loss_weights['severity'] * severity_loss
            
        return total_loss, losses