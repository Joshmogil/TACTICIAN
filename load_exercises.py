from pathlib import Path
from typing import Dict

import yaml


def load_exercises(directory: str = "exercises") -> Dict[str, dict]:
    """Load all exercise YAML files into a mapping by exercise name.

    Each exercise dictionary contains ``name``, ``movement`` and ``muscles``
    keys exactly as specified in the YAML files.
    """
    result: Dict[str, dict] = {}
    for yaml_file in Path(directory).rglob("*.yaml"):
        with yaml_file.open() as f:
            data = yaml.safe_load(f) or []
            for exercise in data:
                if isinstance(exercise, dict) and "name" in exercise:
                    result[exercise["name"]] = exercise
    return result


if __name__ == "__main__":
    loaded = load_exercises()
    print(f"Loaded {len(loaded)} exercises")
    for name in list(loaded)[:5]:
        print("-", name)
