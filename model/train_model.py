# model/train_model.py
import logging
from pathlib import Path
import json
import torch
from sklearn.model_selection import train_test_split
from transformers import PhobertTokenizer
import numpy as np
import random
import os
import psutil
from typing import Dict, Any

from training.dataset import MedicalDataset
from training.model import MedicalPhoBERT
from training.trainer import MedicalChatbotTrainer
from training.utils import prepare_training_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def set_seed(seed: int = 42) -> None:
    """Set all random seeds for reproducibility"""
    try:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = True
    except Exception as e:
        logger.error(f"Error setting random seeds: {str(e)}")
        raise

def setup_gpu() -> None:
    """Setup GPU and display information"""
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA must be available for A100 training")
        
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        logger.info(f"Found {gpu_count} GPU(s)")
        logger.info(f"Using GPU: {gpu_name}")
        logger.info(f"GPU Memory: {gpu_memory:.2f}GB")
        
        torch.cuda.set_device(0)
        torch.cuda.empty_cache()
    except Exception as e:
        logger.error(f"Error setting up GPU: {str(e)}")
        raise

def get_system_info() -> None:
    """Get system information"""
    try:
        memory = psutil.virtual_memory()
        logger.info(f"System Memory: {memory.total / 1024**3:.2f}GB")
        logger.info(f"Available Memory: {memory.available / 1024**3:.2f}GB")
        logger.info(f"CPU Count: {psutil.cpu_count()}")
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise

def load_training_data(data_path: Path) -> Dict:
    """Load and validate the processed training data"""
    try:
        with open(data_path / "training_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        required_keys = ["conversations", "rules"]
        if not all(key in data for key in required_keys):
            raise ValueError(f"Missing required keys in training data. Required: {required_keys}")
        
        return data
    except Exception as e:
        logger.error(f"Error loading training data: {str(e)}")
        raise

def main():
    try:
        # Set random seeds
        set_seed(42)
        
        # Setup GPU
        setup_gpu()
        
        # Get system information
        get_system_info()
        
        # Create output directories
        output_dir = Path("model/saved_models")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load processed data
        data_dir = Path("data/processed")
        training_data = load_training_data(data_dir)
        
        # Initialize tokenizer
        tokenizer = PhobertTokenizer.from_pretrained(
            "vinai/phobert-base",
            use_fast=True
        )
        
        # Split conversations
        train_convs, val_convs = train_test_split(
            training_data["conversations"],
            test_size=0.1,
            random_state=42,
            shuffle=True
        )
        
        logger.info(f"Training samples: {len(train_convs)}")
        logger.info(f"Validation samples: {len(val_convs)}")
        
        # Create datasets
        max_length = 256
        
        train_dataset = MedicalDataset(
            conversations=train_convs,
            rules=training_data["rules"],
            tokenizer=tokenizer,
            max_length=max_length
        )
        
        val_dataset = MedicalDataset(
            conversations=val_convs,
            rules=training_data["rules"],
            tokenizer=tokenizer,
            max_length=max_length
        )
        
        # Initialize model
        model = MedicalPhoBERT()
        
        # Prepare training configuration
        base_config = {
    'output_dir': str(output_dir),
    'num_train_epochs': 10,
    'train_batch_size': 16,          # Reduced batch size
    'eval_batch_size': 32,           # Reduced eval batch size
    'learning_rate': 1e-5,           # Lower learning rate
    'adam_epsilon': 1e-8,
    'adam_beta1': 0.9,
    'adam_beta2': 0.999,
    'warmup_ratio': 0.1,             # Increased warmup
    'max_grad_norm': 0.5,            # Lower gradient clipping
    'weight_decay': 0.01,
    'early_stopping_patience': 3,
    'num_workers': 8,
    'max_length': max_length,
    'gradient_accumulation_steps': 4, # Increased accumulation
    'fp16': True,
    'logging_steps': 50,
    'save_total_limit': 3,
    'evaluation_strategy': 'steps',
    'metric_for_best_model': 'loss',
    'greater_is_better': False,
    'load_best_model_at_end': True,
    'save_strategy': 'steps',
    'save_steps': 200,
    'logging_first_step': True
}
        
        # Calculate training steps
        num_training_samples = len(train_dataset)
        effective_batch_size = base_config['train_batch_size'] * base_config['gradient_accumulation_steps']
        steps_per_epoch = num_training_samples // effective_batch_size
        total_training_steps = steps_per_epoch * base_config['num_train_epochs']
        
        # Calculate warmup steps
        base_config['warmup_steps'] = int(total_training_steps * base_config['warmup_ratio'])
        
        logger.info(f"Training configuration:")
        logger.info(f"Total training steps: {total_training_steps}")
        logger.info(f"Steps per epoch: {steps_per_epoch}")
        logger.info(f"Effective batch size: {effective_batch_size}")
        logger.info(f"Warmup steps: {base_config['warmup_steps']}")
        
        config = prepare_training_config(base_config)
        
        # Initialize trainer
        trainer = MedicalChatbotTrainer(
            model=model,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            config=config
        )
        
        # Train model
        logger.info("Starting training...")
        trainer.train()
        logger.info("Training completed successfully!")
        
        # Save final model
        final_model_path = output_dir / 'final_model'
        trainer.model.save_model(final_model_path)
        logger.info(f"Final model saved to {final_model_path}")

    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        try:
            interrupt_path = output_dir / 'interrupt_checkpoint'
            trainer.save_model()
            logger.info(f"Interrupt checkpoint saved to {interrupt_path}")
        except Exception as e:
            logger.error(f"Error saving interrupt checkpoint: {str(e)}")

    except Exception as e:
        logger.error(f"Training failed with error: {str(e)}", exc_info=True)
        raise

    finally:
        # Cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            memory_used = torch.cuda.max_memory_allocated() / 1024**3
            logger.info(f"Peak GPU memory usage: {memory_used:.2f}GB")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        raise