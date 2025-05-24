"""Main application for the brain simulation."""
import asyncio
import os
import sys

from brain import Brain
from in_out import KeySensor, Speaker
from logger import logger
from encoders import TextEncoder, VisualEncoder, AudioEncoder

async def ticker(brain):
    """Run the brain's tick function in an async loop."""
    while True:
        brain.tick()
        await asyncio.sleep(0)

async def pre_train(brain, pattern, repetitions=5, ticks_per_char=10, reward=0.5):
    """Pre-train the brain with a pattern."""
    for _ in range(repetitions):
        for c in pattern:
            brain.inject_stimulus("text", c)
            for _ in range(ticks_per_char):
                brain.tick()
        brain.reward(reward)

async def main():
    """Main application entry point."""
    print(f"Detailed logs being written to: {os.path.abspath('brain.log')}")
    print("You can watch logs with: tail -f brain.log")
    
    # Initialize brain
    brain = Brain()
    
    # Add sensory modalities
    brain.setup_encoder("text", TextEncoder())
    # Uncomment to add more modalities:
    # brain.setup_encoder("visual", VisualEncoder())
    # brain.setup_encoder("audio", AudioEncoder())
    
    # Pre-train with some patterns
    print("Pre-training with some patterns...")
    await pre_train(brain, "hello", repetitions=5)
    await pre_train(brain, "world", repetitions=3)
    
    print("Ready! Type letters to interact with the brain.")
    
    # Run all components
    await asyncio.gather(
        KeySensor(brain).run(),
        Speaker(brain).run(),
        ticker(brain)
    )

if __name__ == "__main__":
    try:
        print("Type letters (a-z or space). '+' reward, '-' punish. Ctrl-C to quit.")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[shutdown]")