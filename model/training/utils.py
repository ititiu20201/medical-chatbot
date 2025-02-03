# model/training/utils.py
import torch
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, f1_score
from typing import Dict, List, Any, Union, Tuple

def compute_metrics(predictions: Dict[str, np.ndarray], 
                   labels: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """Compute metrics for all tasks"""
    metrics = {}
    
    # Symptom metrics (multi-label)
    if 'symptoms' in predictions:
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels['symptoms'],
            predictions['symptoms'],
            average='weighted'
        )
        metrics['symptoms'] = {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    # Other tasks (multi-class)
    for task in ['conditions', 'departments', 'severity']:
        if task in predictions:
            accuracy = accuracy_score(labels[task], predictions[task])
            f1 = f1_score(labels[task], predictions[task], average='weighted')
            metrics[task] = {
                'accuracy': accuracy,
                'f1': f1
            }
    
    return metrics

def prepare_training_config(base_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Prepare training configuration with defaults"""
    default_config = {
        'output_dir': 'model/saved_models',
        'num_train_epochs': 5,
        'train_batch_size': 16,
        'eval_batch_size': 32,
        'learning_rate': 2e-5,
        'adam_epsilon': 1e-8,
        'warmup_steps': 0,
        'max_grad_norm': 1.0,
        'weight_decay': 0.01,
        'early_stopping_patience': 3,
        'num_workers': 4,
        'max_length': 512,
        'loss_weights': {
            'symptoms': 1.0,
            'conditions': 1.0,
            'departments': 1.0,
            'severity': 1.0
        },
        'scheduler_type': 'linear',  # ['linear', 'cosine', 'constant']
        'gradient_accumulation_steps': 1,
        'fp16': False,  # Mixed precision training
        'evaluation_strategy': 'epoch'  # ['epoch', 'steps']
    }
    
    if base_config:
        default_config.update(base_config)
    
    return default_config

def save_checkpoint(model: torch.nn.Module,
                   optimizer: torch.optim.Optimizer,
                   scheduler: Any,
                   epoch: int,
                   loss: float,
                   metrics: Dict[str, Any],
                   path: str) -> None:
    """Save training checkpoint"""
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
        'loss': loss,
        'metrics': metrics
    }, path)

def load_checkpoint(model: torch.nn.Module,
                   optimizer: torch.optim.Optimizer,
                   scheduler: Any,
                   path: str) -> Tuple[int, float, Dict[str, Any]]:
    """Load training checkpoint"""
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    if scheduler and checkpoint['scheduler_state_dict']:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    return checkpoint['epoch'], checkpoint['loss'], checkpoint['metrics']

def create_department_mapping(departments: List[str]) -> Dict[str, int]:
    """Create department ID mapping"""
    return {dept: idx for idx, dept in enumerate(sorted(departments))}

def create_symptom_mapping(symptoms: List[str]) -> Dict[str, int]:
    """Create symptom ID mapping"""
    return {symptom: idx for idx, symptom in enumerate(sorted(symptoms))}

def format_time(seconds: float) -> str:
    """Format time in human readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_class_weights(labels: np.ndarray) -> torch.Tensor:
    """Calculate class weights for imbalanced datasets"""
    class_counts = np.bincount(labels)
    total = len(labels)
    weights = total / (len(class_counts) * class_counts)
    return torch.FloatTensor(weights)

def get_learning_rate(optimizer: torch.optim.Optimizer) -> float:
    """Get current learning rate from optimizer"""
    for param_group in optimizer.param_groups:
        return param_group['lr']

def move_to_device(batch: Dict[str, Any], device: torch.device) -> Dict[str, Any]:
    """Recursively move batch to device"""
    for key, value in batch.items():
        if isinstance(value, torch.Tensor):
            batch[key] = value.to(device)
        elif isinstance(value, dict):
            batch[key] = move_to_device(value, device)
    return batch