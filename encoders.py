"""Encoders for converting various inputs to neural activity patterns."""
import random
from abc import ABC, abstractmethod
from typing import List, Dict

from config import DIM, SPARSITY, POP_SIZE

class SensoryEncoder(ABC):
    """Abstract base class for sensory encoders."""
    
    @property
    @abstractmethod
    def required_neurons(self) -> int:
        """Return the number of neurons needed for this encoder."""
        pass
    
    @abstractmethod
    def encode(self, stimulus) -> List[int]:
        """
        Encode a stimulus into neuron activation indices.
        
        Args:
            stimulus: The stimulus to encode (specific to each encoder subclass)
            
        Returns:
            List of indices of neurons that should be activated
        """
        pass

class TextEncoder(SensoryEncoder):
    """Encoder for text input using semantic pointers and population codes."""
    
    def __init__(self, alphabet="abcdefghijklmnopqrstuvwxyz "):
        """Initialize with the given alphabet."""
        self.alphabet = alphabet
        self.pointers = {c: self._rand_pointer(c) for c in self.alphabet}
        
    @property
    def required_neurons(self) -> int:
        """Return the number of neurons needed for this encoder."""
        return len(self.alphabet) * POP_SIZE
    
    def encode(self, stimulus: str) -> List[int]:
        """
        Encode a character into neuron activation indices.
        
        Args:
            stimulus: A single character to encode
            
        Returns:
            List of indices (relative to this encoder's section) to activate
        """
        if stimulus not in self.pointers:
            return []
        
        return self._pointer_to_pop(self.pointers[stimulus])
    
    def get_neuron_label(self, char: str, idx: int) -> str:
        """Generate a label for a neuron representing a character."""
        return f"IN_{char}_{idx}"
    
    def _rand_pointer(self, seed=None) -> int:
        """Generate a random semantic pointer with the right sparsity."""
        rng = random.Random(seed)
        bits = 0
        need = int(DIM * SPARSITY)
        while bits.bit_count() < need:
            bits |= 1 << rng.randrange(DIM)
        return bits
    
    def _pointer_to_pop(self, bits: int) -> List[int]:
        """Convert a semantic pointer to population code indices."""
        out = []
        for i in range(POP_SIZE):
            # Hash 4 pointer bits into one index
            slice_bits = (bits >> (i * 4)) & 0xF
            if slice_bits & 0x1:
                out.append(i)
        # Guarantee at least one spike
        if not out:
            return [random.randrange(POP_SIZE)]
        return out

class VisualEncoder(SensoryEncoder):
    """Simple encoder for visual input (grayscale images)."""
    
    def __init__(self, width=28, height=28, sparsity=0.1):
        """Initialize with the given image dimensions."""
        self.width = width
        self.height = height
        self.sparsity = sparsity
        self.grid_size = 4  # Size of receptive fields
        
    @property
    def required_neurons(self) -> int:
        """Return the number of neurons needed for this encoder."""
        # We use multiple neurons per grid cell
        grid_w = self.width // self.grid_size
        grid_h = self.height // self.grid_size
        return grid_w * grid_h * 4  # 4 detectors per grid cell
    
    def encode(self, stimulus: List[List[float]]) -> List[int]:
        """
        Encode a grayscale image into neuron activation indices.
        
        Args:
            stimulus: 2D array of pixel values (0-1)
            
        Returns:
            List of indices (relative to this encoder's section) to activate
        """
        if not stimulus or len(stimulus) != self.height or len(stimulus[0]) != self.width:
            return []
        
        activations = []
        grid_w = self.width // self.grid_size
        grid_h = self.height // self.grid_size
        
        # For each grid cell
        for gy in range(grid_h):
            for gx in range(grid_w):
                # Extract the cell
                cell = [row[gx*self.grid_size:(gx+1)*self.grid_size] 
                        for row in stimulus[gy*self.grid_size:(gy+1)*self.grid_size]]
                
                # Compute features (simplified)
                avg = sum(sum(row) for row in cell) / (self.grid_size * self.grid_size)
                if avg > 0.5:  # Simple threshold
                    neuron_idx = (gy * grid_w + gx) * 4
                    activations.append(neuron_idx)
                
                # Additional features could be added here
        
        return activations
    
    def get_neuron_label(self, x: int, y: int, feature: int) -> str:
        """Generate a label for a visual neuron."""
        return f"VIS_{x}_{y}_{feature}"

class AudioEncoder(SensoryEncoder):
    """Simple encoder for audio input (frequency bands)."""
    
    def __init__(self, n_bands=64, sparsity=0.1):
        """Initialize with the given number of frequency bands."""
        self.n_bands = n_bands
        self.sparsity = sparsity
        
    @property
    def required_neurons(self) -> int:
        """Return the number of neurons needed for this encoder."""
        return self.n_bands
    
    def encode(self, stimulus: List[float]) -> List[int]:
        """
        Encode frequency bands into neuron activation indices.
        
        Args:
            stimulus: List of frequency band powers
            
        Returns:
            List of indices (relative to this encoder's section) to activate
        """
        if not stimulus or len(stimulus) != self.n_bands:
            return []
        
        # Activate the top N% of bands
        n_active = max(1, int(self.n_bands * self.sparsity))
        top_bands = sorted(range(len(stimulus)), key=lambda i: stimulus[i], reverse=True)[:n_active]
        return top_bands
    
    def get_neuron_label(self, band: int) -> str:
        """Generate a label for an audio neuron."""
        return f"AUD_{band}"