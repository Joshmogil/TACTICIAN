"""Core data structures for the brain simulation."""
from dataclasses import dataclass, field
from typing import List, Optional

from config import V_R

@dataclass
class Synapse:
    """Synapse connecting two neurons with plasticity."""
    pre: int            # Index of presynaptic neuron
    post: int           # Index of postsynaptic neuron
    w: float            # Weight/strength of connection
    mask: int           # Context mask (which contexts this synapse is active in)
    elig: float = 0.0   # Eligibility trace for dopamine-based learning
    frozen: bool = False  # Whether this synapse is part of long-term memory
    above_since: int = -1  # When weight went above consolidation threshold

@dataclass
class Neuron:
    """Spiking neuron with leaky integrate-and-fire dynamics."""
    idx: int            # Unique neuron index
    excit: bool = True  # Whether the neuron is excitatory or inhibitory
    v: float = V_R      # Membrane potential
    ref: int = 0        # Refractory counter
    last: int = -10_000  # Last spike time
    out: List[Synapse] = field(default_factory=list)  # Outgoing synapses
    label: Optional[str] = None  # Optional label for this neuron