"""
Checkpoint Manager

This module handles saving and loading checkpoints during long-running downloads.
"""
import os
import pickle
from typing import Dict, List, Any
from pathlib import Path


class CheckpointManager:
    """Manages checkpointing for download progress."""
    
    def __init__(self, save_dir: Path):
        """
        Initialize the checkpoint manager.
        
        Args:
            save_dir: Directory to save checkpoint files
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(
        self,
        batch_index: int,
        num_batches: int,
        documents: Dict[str, Any],
        failed: List[str],
        multiple: Dict[str, List[str]]
    ) -> None:
        """
        Save progress checkpoint to disk.
        
        Args:
            batch_index: Current batch index
            num_batches: Total number of batches
            documents: Retrieved documents
            failed: Failed PMIDs
            multiple: PMIDs with multiple PMCIDs
        """
        checkpoint_files = {
            'documents': documents,
            'failed_pmids': failed,
            'multiple_pmcids': multiple
        }
        
        for name, data in checkpoint_files.items():
            filepath = self.save_dir / f'{name}_checkpoint_{batch_index}.pkl'
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        
        print(f'[Checkpoint] Saved at batch {batch_index + 1}/{num_batches} ({len(documents)} papers retrieved)')
    
    def save_final_results(
        self,
        documents: Dict[str, Any],
        failed: List[str],
        multiple: Dict[str, List[str]]
    ) -> None:
        """
        Save final results to disk.
        
        Args:
            documents: Retrieved documents
            failed: Failed PMIDs
            multiple: PMIDs with multiple PMCIDs
        """
        print("\nSaving final results...")
        
        final_files = {
            'documents_final.pkl': documents,
            'failed_pmids_final.pkl': failed,
            'multiple_pmcids_final.pkl': multiple
        }
        
        for filename, data in final_files.items():
            filepath = self.save_dir / filename
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        
        print('Final results saved successfully.')
    
    def load_checkpoint(self, batch_index: int) -> tuple:
        """
        Load checkpoint from disk.
        
        Args:
            batch_index: Checkpoint batch index to load
            
        Returns:
            Tuple of (documents, failed_pmids, multiple_pmcids)
        """
        documents_file = self.save_dir / f'documents_checkpoint_{batch_index}.pkl'
        failed_file = self.save_dir / f'failed_pmids_checkpoint_{batch_index}.pkl'
        multiple_file = self.save_dir / f'multiple_pmcids_checkpoint_{batch_index}.pkl'
        
        documents = {}
        failed = []
        multiple = {}
        
        if documents_file.exists():
            with open(documents_file, 'rb') as f:
                documents = pickle.load(f)
        
        if failed_file.exists():
            with open(failed_file, 'rb') as f:
                failed = pickle.load(f)
        
        if multiple_file.exists():
            with open(multiple_file, 'rb') as f:
                multiple = pickle.load(f)
        
        return documents, failed, multiple
    
    def list_checkpoints(self) -> List[int]:
        """
        List all available checkpoint indices.
        
        Returns:
            List of checkpoint indices
        """
        checkpoint_files = list(self.save_dir.glob('documents_checkpoint_*.pkl'))
        indices = []
        
        for filepath in checkpoint_files:
            try:
                index = int(filepath.stem.split('_')[-1])
                indices.append(index)
            except ValueError:
                continue
        
        return sorted(indices)
