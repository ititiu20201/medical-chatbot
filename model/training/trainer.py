# model/training/trainer.py
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from tqdm import tqdm
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MedicalChatbotTrainer:
    def __init__(
        self,
        model,
        train_dataset,
        val_dataset,
        config: Dict[str, Any]
    ):
        self.model = model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.config = config
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Setup optimizer
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in model.named_parameters() 
                          if not any(nd in n for nd in no_decay)],
                'weight_decay': config['weight_decay']
            },
            {
                'params': [p for n, p in model.named_parameters() 
                          if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0
            }
        ]
        
        self.optimizer = AdamW(
            optimizer_grouped_parameters,
            lr=config['learning_rate'],
            eps=config['adam_epsilon']
        )
        
        # Setup data loaders
        self.train_dataloader = DataLoader(
            train_dataset,
            batch_size=config['train_batch_size'],
            shuffle=True,
            num_workers=config['num_workers']
        )
        
        self.val_dataloader = DataLoader(
            val_dataset,
            batch_size=config['eval_batch_size'],
            num_workers=config['num_workers']
        )
        
        # Create scheduler
        num_training_steps = len(self.train_dataloader) * config['num_train_epochs']
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config['warmup_steps'],
            num_training_steps=num_training_steps
        )

        # Initialize tracking variables
        self.best_val_loss = float('inf')
        self.current_epoch = 0
        self.global_step = 0

    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(self.train_dataloader, desc='Training')
        
        for step, batch in enumerate(progress_bar):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Reset gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(**batch)
            loss = outputs['loss']

            # Backward pass
            if self.config.get('gradient_accumulation_steps', 1) > 1:
                loss = loss / self.config['gradient_accumulation_steps']
            
            loss.backward()
            
            total_loss += loss.item()
            
            # Update weights if gradient accumulation is complete
            if (step + 1) % self.config.get('gradient_accumulation_steps', 1) == 0:
                # Clip gradients
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config['max_grad_norm']
                )
                
                # Update weights and learning rate
                self.optimizer.step()
                self.scheduler.step()
                
                # Update progress bar
                progress_bar.set_postfix({
                    'loss': loss.item() * self.config.get('gradient_accumulation_steps', 1),
                    'avg_loss': total_loss / (step + 1),
                    'lr': self.scheduler.get_last_lr()[0]
                })
                
                self.global_step += 1
        
        return total_loss / len(self.train_dataloader)

    def evaluate(self):
        """Evaluate the model on the validation set"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in tqdm(self.val_dataloader, desc='Evaluating'):
                # Move batch to device
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Forward pass
                outputs = self.model(**batch)
                loss = outputs['loss']
                
                total_loss += loss.item()
        
        return total_loss / len(self.val_dataloader)

    def save_checkpoint(self, val_loss: float):
        """Save a training checkpoint"""
        checkpoint_path = os.path.join(self.config['output_dir'], 'checkpoint')
        os.makedirs(checkpoint_path, exist_ok=True)
        
        # Save model
        self.model.save_model(os.path.join(checkpoint_path, 'model'))
        
        # Save optimizer and scheduler states
        torch.save({
            'epoch': self.current_epoch,
            'global_step': self.global_step,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss,
            'best_val_loss': self.best_val_loss,
            'config': self.config
        }, os.path.join(checkpoint_path, 'training_state.pt'))
        
        logger.info(f"Checkpoint saved to {checkpoint_path}")

    def load_checkpoint(self, checkpoint_path: str):
        """Load a training checkpoint"""
        # Load model
        self.model = self.model.load_model(os.path.join(checkpoint_path, 'model'))
        self.model.to(self.device)
        
        # Load training state
        training_state = torch.load(os.path.join(checkpoint_path, 'training_state.pt'))
        
        self.current_epoch = training_state['epoch']
        self.global_step = training_state['global_step']
        self.optimizer.load_state_dict(training_state['optimizer_state_dict'])
        self.scheduler.load_state_dict(training_state['scheduler_state_dict'])
        self.best_val_loss = training_state['best_val_loss']
        
        logger.info(f"Checkpoint loaded from {checkpoint_path}")

    def save_model(self):
        """Save the best model"""
        model_path = os.path.join(self.config['output_dir'], 'best_model')
        self.model.save_model(model_path)
        logger.info(f"Best model saved to {model_path}")

    def train(self):
        """Complete training process"""
        # Create output directory
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        for epoch in range(self.current_epoch, self.config['num_train_epochs']):
            self.current_epoch = epoch
            logger.info(f"\nEpoch {epoch + 1}/{self.config['num_train_epochs']}")
            
            # Training
            train_loss = self.train_epoch()
            logger.info(f"Average training loss: {train_loss:.4f}")
            
            # Validation
            val_loss = self.evaluate()
            logger.info(f"Validation loss: {val_loss:.4f}")
            
            # Save checkpoint
            self.save_checkpoint(val_loss)
            
            # Save best model
            if val_loss < self.best_val_loss:
                logger.info(f"Validation loss improved from {self.best_val_loss:.4f} to {val_loss:.4f}")
                self.best_val_loss = val_loss
                self.save_model()
            else:
                # Early stopping
                if self.config.get('early_stopping_patience'):
                    if epoch - self.last_improvement >= self.config['early_stopping_patience']:
                        logger.info("Early stopping triggered")
                        break
            
            # Update last improvement epoch
            if val_loss < self.best_val_loss:
                self.last_improvement = epoch