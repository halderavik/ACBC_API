from itertools import product
import random
from typing import Dict, List, Any

# Generate full factorial design
def full_factorial(attributes: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    keys = list(attributes.keys())
    levels = [attributes[k] for k in keys]
    combos = [dict(zip(keys, vals)) for vals in product(*levels)]
    return combos

# Screening: sample first N tasks
def generate_screening_matrix(byo: Dict[str, List[Any]], n_tasks: int = 5) -> List[Dict[str, Any]]:
    design = full_factorial(byo)
    random.shuffle(design)
    return design[:n_tasks]

# Tournament: adaptive selection (placeholder random)
def generate_tournament_set(previous_utilities: Dict[str, float], byo: Dict[str, List[Any]], task_number: int, n_options: int = 3) -> List[Dict[str, Any]]:
    design = full_factorial(byo)
    return random.sample(design, n_options)

# Estimate utilities (simple counting)
def estimate_initial_utilities(responses: List[bool], tasks: List[Dict[str, Any]]) -> Dict[str, float]:
    # placeholder: equal utilities
    return {k: 1.0 for k in tasks[0].keys()}

# Update utilities (placeholder)
def adaptive_update(current_utils: Dict[str, float], choice: Dict[str, Any]) -> Dict[str, float]:
    return current_utils