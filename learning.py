"""Learning mechanisms for the neural network."""
from config import BASE_LR, STDP_WIN, ELIG_DECAY, CONSOLIDATE_THRESH, CONSOLIDATE_TIME
from logger import logger

def apply_stdp(brain):
    """Apply STDP and dopamine-based learning to the brain."""
    weight_changes = 0
    new_frozen = 0
    
    for s in brain.S:
        # Skip frozen synapses and inactive contexts
        if s.frozen or not (s.mask & brain.context):
            continue
        
        # Calculate spike timing difference
        pre_t, post_t = brain.N[s.pre].last, brain.N[s.post].last
        dt = post_t - pre_t
        
        # STDP term
        hebb = BASE_LR * (1 if (0 < dt <= STDP_WIN) else -1 if (-STDP_WIN <= dt < 0) else 0)
        
        # Update weight
        old_w = s.w
        s.w += hebb + (brain.dopamine * s.elig * BASE_LR)
        
        # Track weight changes
        if abs(s.w - old_w) > 0.001:
            weight_changes += 1
        
        # Decay eligibility trace
        s.elig *= ELIG_DECAY
        
        # Check for consolidation
        if abs(s.w) > CONSOLIDATE_THRESH:
            if s.above_since < 0:
                s.above_since = brain._t
            elif brain._t - s.above_since >= CONSOLIDATE_TIME:
                if not s.frozen:
                    s.frozen = True
                    new_frozen += 1
                    brain.frozen_synapses += 1
        else:
            s.above_since = -1
    
    if new_frozen > 0:
        logger.info(f"🧊 {new_frozen} synapses frozen (total: {brain.frozen_synapses})")