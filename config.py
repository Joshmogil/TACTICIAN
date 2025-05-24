"""Configuration parameters for the brain simulation."""

# Neural network dimensions
DIM = 128               # Dimensions for semantic pointers
SPARSITY = 0.25         # Sparsity of activations (25%)
POP_SIZE = 32           # Population code width per input
N_INT_EXC = 700         # Number of excitatory interneurons
N_INT_INH = 100         # Number of inhibitory interneurons
RESERVOIR_LEN = 50      # Reservoir buffer length

# Neuron parameters
DT = 1                  # Simulation time step (ms)
TAU_M = 20.0            # Membrane time constant
V_R = -70.0             # Resting potential
V_T = -50.0             # Threshold potential
V_RESET = -80.0         # Reset potential after spike
REFRACTORY = 5          # Refractory period (ms)

# Learning parameters
STDP_WIN = 20           # STDP time window
BASE_LR = 0.01          # Base learning rate
ELIG_DECAY = 0.98       # Eligibility trace decay
DOP_DECAY = 0.95        # Dopamine decay rate
CTX_BITS = 16           # Context mask bits
CONSOLIDATE_THRESH = 0.5 # Threshold for weight consolidation
CONSOLIDATE_TIME = 10_000 # Time required above threshold for consolidation

# Activity parameters
SPONTANEOUS_RATE = 0.01  # Spontaneous activity rate