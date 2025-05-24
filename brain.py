"""Core brain model implementing a spiking neural network."""
import random
from typing import Dict, List, Optional, Any, Type

from config import *
from models import Neuron, Synapse
from encoders import SensoryEncoder, TextEncoder
from logger import logger
import learning

class Brain:
    """Spiking neural network with plasticity and reservoir computing."""
    
    def __init__(self):
        """Initialize the brain network."""
        logger.info("🧠 Initializing Brain...")
        
        # Initialize neuron list
        self.N: List[Neuron] = []
        for _ in range(N_INT_EXC):
            self.N.append(Neuron(len(self.N), True))
        for _ in range(N_INT_INH):
            self.N.append(Neuron(len(self.N), False))
        logger.info(f"Created {N_INT_EXC} excitatory + {N_INT_INH} inhibitory neurons")
        
        # Initialize synapse list and buffers
        self.S: List[Synapse] = []
        self._inc: List[List[Synapse]] = [[] for _ in range(len(self.N))]
        self._buf: List[List[float]] = [[] for _ in range(len(self.N))]
        
        # IO mappings
        self.encoders: Dict[str, SensoryEncoder] = {}
        self.sensory_maps: Dict[str, Dict[Any, List[int]]] = {}
        self.pred_map: Dict[str, Dict[Any, int]] = {}
        self.speakers: Dict[str, Dict[Any, int]] = {}
        
        # Reservoir (temporal memory)
        self.reservoir: List[int] = [
            self.add_neuron(f"RES_{i}") for i in range(RESERVOIR_LEN)
        ]
        logger.info(f"Created {RESERVOIR_LEN} reservoir neurons")
        
        # State variables
        self._t = 0
        self.context = 1
        self.dopamine, self.dop_base = 0.0, 0.0
        self.spontaneous_rate = SPONTANEOUS_RATE
        
        # Logging/stats variables
        self.spike_count = 0
        self.frozen_synapses = 0
        
        # Wire up the core network
        self._wire_random_sparse()
        
        # Setup default text encoder if none provided
        self.setup_encoder("text", TextEncoder())
        
        logger.info(f"🎯 Brain initialized with {len(self.N)} neurons, {len(self.S)} synapses")
    
    def setup_encoder(self, modality: str, encoder: SensoryEncoder):
        """
        Set up input/output neurons for a sensory modality.
        
        Args:
            modality: Name of the sensory modality
            encoder: Encoder for this modality
        """
        logger.info(f"Setting up {modality} encoder...")
        self.encoders[modality] = encoder
        self.sensory_maps[modality] = {}
        self.pred_map[modality] = {}
        self.speakers[modality] = {}
        
        # For text encoder, build specific input infrastructure
        if modality == "text" and hasattr(encoder, "alphabet"):
            text_encoder = encoder
            for ch in text_encoder.alphabet:
                pop_indices = encoder.encode(ch)
                pop_neurons = []
                
                # Create input neurons for this character
                for idx in pop_indices:
                    neuron_idx = self.add_neuron(text_encoder.get_neuron_label(ch, idx))
                    pop_neurons.append(neuron_idx)
                    # Wire to reservoir for temporal dynamics
                    self.connect(neuron_idx, self.reservoir[idx % RESERVOIR_LEN], w=0.9)
                
                self.sensory_maps[modality][ch] = pop_neurons
                
                # Create predictor and speaker neurons
                pred = self.add_neuron(f"PRED_{ch}")
                speak = self.add_neuron(f"SPEAK_{ch}", excit=True)
                self.pred_map[modality][ch] = pred
                self.speakers[modality][ch] = speak
                
                # Wire predictor to reservoir
                for _ in range(12):
                    self.connect(random.choice(self.reservoir), pred, w=0.6)
                
                # Predictor excites speaker
                self.connect(pred, speak, w=0.8)
                
                # Speaker feeds back to reservoir
                for _ in range(6):
                    self.connect(speak, random.choice(self.reservoir), w=0.5)
        
        # For other encoders, create more generic infrastructure
        else:
            num_neurons = encoder.required_neurons
            logger.info(f"Creating {num_neurons} input neurons for {modality}")
            
            # Create generic input layer
            for i in range(num_neurons):
                neuron_idx = self.add_neuron(f"{modality.upper()}_{i}")
                self.connect(neuron_idx, self.reservoir[i % RESERVOIR_LEN], w=0.7)
        
        logger.info(f"Completed setup for {modality} encoder")
    
    def add_neuron(self, label="", excit=True) -> int:
        """Add a new neuron to the network."""
        idx = len(self.N)
        self.N.append(Neuron(idx, excit, label=label))
        self._inc.append([])
        self._buf.append([])
        return idx
    
    def connect(self, pre, post, w=None):
        """Connect two neurons with a synapse."""
        if w is None:
            sign = 1 if self.N[pre].excit else -1
            w = sign * random.uniform(0.01, 0.05)
        syn = Synapse(pre, post, w, mask=random.getrandbits(CTX_BITS))
        self.S.append(syn)
        self._inc[post].append(syn)
        self.N[pre].out.append(syn)
    
    def _wire_random_sparse(self):
        """Create sparse random connections in the core network."""
        n_total = len(self.N)
        connections = 0
        for pre in range(n_total):
            targets = random.sample(range(n_total), int(0.02 * n_total))
            for post in targets:
                self.connect(pre, post)
                connections += 1
        logger.info(f"🔗 Created {connections} random sparse connections")
    
    def inject_stimulus(self, modality: str, stimulus):
        """
        Inject a stimulus from any supported modality.
        
        Args:
            modality: The sensory modality ("text", "visual", "audio", etc.)
            stimulus: The stimulus (character, image, etc.)
        """
        if modality not in self.encoders:
            logger.warning(f"Unknown modality: {modality}")
            return
        
        encoder = self.encoders[modality]
        
        # Special handling for text modality
        if modality == "text" and stimulus in self.sensory_maps[modality]:
            logger.info(f"📥 Injecting character: '{stimulus}'")
            spike_neurons = []
            for n in self.sensory_maps[modality][stimulus]:
                self._buf[n].append(1.0)
                spike_neurons.append(self.N[n].label)
            logger.info(f"   → Spiking neurons: {spike_neurons[:3]}{'...' if len(spike_neurons) > 3 else ''}")
        
        # Generic handling for other modalities
        else:
            indices = encoder.encode(stimulus)
            logger.info(f"📥 Injecting {modality} stimulus, activating {len(indices)} neurons")
            
            # For sensory maps with direct stimulus mapping
            if stimulus in self.sensory_maps.get(modality, {}):
                for n in self.sensory_maps[modality][stimulus]:
                    self._buf[n].append(1.0)
            
            # For more complex encodings that return relative indices
            else:
                base_idx = sum(len(self.N) for m, enc in self.encoders.items() if m != modality)
                for idx in indices:
                    if base_idx + idx < len(self.N):
                        self._buf[base_idx + idx].append(1.0)
    
    def reward(self, r: float):
        """Inject a reward signal (dopamine)."""
        old_dop = self.dopamine
        self.dopamine += r
        logger.info(f"🎁 Reward: {r:+.2f} (dopamine: {old_dop:.3f} → {self.dopamine:.3f})")
    
    def tick(self):
        """Process one millisecond timestep in the simulation."""
        spikes_this_tick = []
        
        # Spontaneous activity
        if random.random() < self.spontaneous_rate:
            random_res = random.choice(self.reservoir)
            self._buf[random_res].append(0.7)
            logger.debug(f"⚡ Spontaneous activity in reservoir neuron {self.N[random_res].label}")
        
        # 1. Update all neurons
        for n in self.N:
            if n.ref == 0:
                # Membrane decay and input integration
                n.v += (V_R - n.v) * (DT / TAU_M)
                while self._buf[n.idx]:
                    n.v += self._buf[n.idx].pop(0)
            else:
                # Refractory period
                n.ref -= DT
            
            # Check for spikes
            if n.v >= V_T and n.ref == 0:
                self._fire(n)
                spikes_this_tick.append(n.label or f"N{n.idx}")
                self.spike_count += 1
        
        # Log spikes periodically
        if spikes_this_tick and self._t % 100 == 0:
            logger.info(f"⚡ t={self._t}ms: {len(spikes_this_tick)} spikes: {spikes_this_tick[:5]}{'...' if len(spikes_this_tick) > 5 else ''}")
        
        # 2. Apply learning rules
        learning.apply_stdp(self)
        
        # 3. Update critic (prediction error → dopamine)
        self._critic()
        
        # 4. Update dopamine with adaptive baseline
        old_dop_base = self.dop_base
        self.dop_base = 0.999 * self.dop_base + 0.001 * self.dopamine
        self.dopamine -= self.dop_base
        self.dopamine *= DOP_DECAY
        
        # 5. Update time and context
        self._t += DT
        if self._t % 2000 == 0:
            old_context = self.context
            self.context <<= 1
            if self.context >= (1 << CTX_BITS):
                self.context = 1
            logger.info(f"🔄 Context shift: {old_context:04x} → {self.context:04x}")
        
        # 6. Periodic status logging
        if self._t % 5000 == 0:
            self._log_status()
    
    def _fire(self, n: Neuron):
        """Handle a neuron firing."""
        n.last, n.v, n.ref = self._t, V_RESET, REFRACTORY
        synapses_activated = 0
        
        # Propagate spike to postsynaptic neurons
        for s in n.out:
            if s.mask & self.context:
                self._buf[s.post].append(s.w)
                synapses_activated += 1
            s.elig = 1.0  # Set eligibility trace
        
        # Log important neuron firings
        if n.label and (n.label.startswith("PRED_") or n.label.startswith("SPEAK_")):
            logger.info(f"🔥 {n.label} fired (activated {synapses_activated} synapses)")
        
        # Update reservoir for text inputs
        if n.label and n.label.startswith("IN_"):
            parts = n.label.split("_")
            if len(parts) >= 3:
                try:
                    idx = int(parts[2])
                    self.inject_reservoir(idx)
                except ValueError:
                    pass
    
    def inject_reservoir(self, idx):
        """Activate a reservoir neuron (shift ring buffer)."""
        if 0 <= idx < len(self.reservoir):
            self._buf[self.reservoir[idx]].append(1.0)
    
    def _critic(self):
        """Implement the predictor-critic reward system."""
        # Currently only for text modality
        if "text" not in self.pred_map:
            return
        
        for ch, pred_idx in self.pred_map["text"].items():
            # Skip if no sensory neurons for this character
            if ch not in self.sensory_maps.get("text", {}):
                continue
            
            # Find earliest sensor spike
            sensor_times = [self.N[i].last for i in self.sensory_maps["text"][ch]]
            if not sensor_times:
                continue
            
            actual_t = min(sensor_times)
            pred_t = self.N[pred_idx].last
            
            # Skip if no recent spikes
            if actual_t < 0 or pred_t < 0:
                continue
            
            # Calculate prediction error
            err = abs(actual_t - pred_t)
            
            # Reward based on prediction accuracy
            if err == 0:
                self.reward(+0.5)
                logger.info(f"🎯 Perfect prediction for '{ch}' (err=0)")
            elif err <= 5:
                self.reward(+0.05)
                logger.info(f"🎯 Good prediction for '{ch}' (err={err}ms)")
            elif err > 20:
                self.reward(-0.3)
                logger.info(f"❌ Bad prediction for '{ch}' (err={err}ms)")
    
    def _log_status(self):
        """Log the current status of the brain."""
        active_synapses = sum(1 for s in self.S if not s.frozen)
        avg_weight = sum(abs(s.w) for s in self.S) / len(self.S) if self.S else 0
        
        logger.info(f"📊 Status t={self._t}ms:")
        logger.info(f"   Spikes: {self.spike_count} total")
        logger.info(f"   Dopamine: {self.dopamine:.3f} (baseline: {self.dop_base:.3f})")
        logger.info(f"   Synapses: {active_synapses}/{len(self.S)} active (avg |w|: {avg_weight:.3f})")
        logger.info(f"   Context: 0x{self.context:04x}")
        
        # Log encoder status
        for modality, encoder in self.encoders.items():
            num_inputs = len(self.sensory_maps.get(modality, {}))
            logger.info(f"   {modality.capitalize()} encoder: {num_inputs} mapped inputs")