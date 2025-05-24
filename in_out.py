"""Input/output interfaces for the brain simulation."""
import asyncio
import sys
from abc import ABC, abstractmethod

from logger import logger
from encoders import TextEncoder, VisualEncoder, AudioEncoder

class InputInterface(ABC):
    """Abstract base class for input interfaces."""
    
    @abstractmethod
    async def run(self):
        """Run the input interface."""
        pass

class OutputInterface(ABC):
    """Abstract base class for output interfaces."""
    
    @abstractmethod
    async def run(self):
        """Run the output interface."""
        pass

class KeySensor(InputInterface):
    """Keyboard input interface."""
    
    def __init__(self, brain):
        """Initialize with a brain instance."""
        self.brain = brain
    
    async def run(self):
        """Read keyboard input and inject into the brain."""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            ch = (await reader.read(1)).decode(errors="ignore")
            if ch in self.brain.sensory_maps.get("text", {}):
                self.brain.inject_stimulus("text", ch)
            elif ch == '+':
                self.brain.reward(+1)
            elif ch == '-':
                self.brain.reward(-1)

class Speaker(OutputInterface):
    """Text output interface."""
    
    def __init__(self, brain):
        """Initialize with a brain instance."""
        self.brain = brain
        self.prev = {}
    
    async def run(self):
        """Monitor for speech output and print it."""
        while True:
            await asyncio.sleep(0.05)
            
            # Monitor text outputs
            if "text" in self.brain.speakers:
                for ch, idx in self.brain.speakers["text"].items():
                    if self.brain.N[idx].last != self.prev.get(idx, -1):
                        logger.info(f"🗣️  Speaking: '{ch}' (neuron {self.brain.N[idx].label})")
                        sys.stdout.write(ch)
                        sys.stdout.flush()
                        self.prev[idx] = self.brain.N[idx].last