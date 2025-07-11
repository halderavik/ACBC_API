from itertools import product
import random
import numpy as np
from typing import Dict, List, Any, Tuple

# Generate full factorial design
def full_factorial(attributes: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    keys = list(attributes.keys())
    levels = [attributes[k] for k in keys]
    combos = [dict(zip(keys, vals)) for vals in product(*levels)]
    return combos

def generate_byo_profile(byo: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Generate a BYO profile by selecting one level per attribute.
    This represents the respondent's ideal product.
    """
    byo_profile = {}
    for attribute, levels in byo.items():
        # Select a random level for each attribute as the "ideal" choice
        byo_profile[attribute] = random.choice(levels)
    return byo_profile

def generate_screening_matrix(byo: Dict[str, List[Any]], n_tasks: int = 10) -> List[Dict[str, Any]]:
    """
    Generate screening concepts by perturbing the BYO profile.
    
    Algorithm:
    1. Start from BYO profile (ideal product)
    2. Generate concepts by changing 1-2 attributes from BYO
    3. Ensure every level appears at least once for testing acceptability
    4. Generate 10-15 concepts (default: 10)
    
    Args:
        byo: Dictionary of attributes and their levels
        n_tasks: Number of screening concepts to generate (default: 10)
    
    Returns:
        List of screening concepts
    """
    # Step 1: Generate BYO profile (ideal product)
    byo_profile = generate_byo_profile(byo)
    
    # Step 2: Generate screening concepts by perturbing BYO profile
    concepts = []
    attributes = list(byo.keys())
    
    # Track which levels have been tested to ensure coverage
    tested_levels = {attr: set() for attr in attributes}
    
    # Add BYO profile as first concept
    concepts.append(byo_profile.copy())
    
    # Update tested levels for BYO profile
    for attr, level in byo_profile.items():
        tested_levels[attr].add(level)
    
    # Generate remaining concepts by perturbing BYO profile
    concept_count = 1  # We already added BYO profile
    
    while concept_count < n_tasks:
        # Create a new concept based on BYO profile
        new_concept = byo_profile.copy()
        
        # Randomly decide how many attributes to change (1 or 2)
        num_changes = random.choice([1, 2])
        attributes_to_change = random.sample(attributes, min(num_changes, len(attributes)))
        
        # Change selected attributes to different levels
        for attr in attributes_to_change:
            available_levels = [level for level in byo[attr] if level != byo_profile[attr]]
            if available_levels:
                new_level = random.choice(available_levels)
                new_concept[attr] = new_level
                tested_levels[attr].add(new_level)
        
        # Add concept if it's not a duplicate
        if new_concept not in concepts:
            concepts.append(new_concept)
            concept_count += 1
    
    # Step 3: Ensure every level appears at least once
    # If we haven't tested all levels, add additional concepts
    for attr, levels in byo.items():
        for level in levels:
            if level not in tested_levels[attr]:
                # Create a concept that includes this untested level
                new_concept = byo_profile.copy()
                new_concept[attr] = level
                
                # Change one more attribute randomly to make it different from BYO
                other_attrs = [a for a in attributes if a != attr]
                if other_attrs:
                    other_attr = random.choice(other_attrs)
                    available_levels = [l for l in byo[other_attr] if l != byo_profile[other_attr]]
                    if available_levels:
                        new_concept[other_attr] = random.choice(available_levels)
                
                # Add concept if it's not a duplicate and we haven't reached the limit
                if new_concept not in concepts and len(concepts) < n_tasks:
                    concepts.append(new_concept)
                    tested_levels[attr].add(level)
    
    # Shuffle concepts to randomize order (except keep BYO profile first)
    byo_concept = concepts[0]
    other_concepts = concepts[1:]
    random.shuffle(other_concepts)
    concepts = [byo_concept] + other_concepts
    
    return concepts

def create_design_matrix(profiles: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str]]:
    """
    Create a design matrix from profiles using effects coding.
    
    Args:
        profiles: List of product profiles
    
    Returns:
        Tuple of (design_matrix, variable_names)
    """
    if not profiles:
        return np.array([]), []
    
    # Get all unique attribute levels
    attribute_levels = {}
    for profile in profiles:
        for attr, level in profile.items():
            if attr not in attribute_levels:
                attribute_levels[attr] = set()
            attribute_levels[attr].add(level)
    
    # Create effects coding variables
    variables = []
    variable_names = []
    
    for attr, levels in attribute_levels.items():
        levels_list = sorted(list(levels))
        # Use effects coding: n-1 variables for n levels
        for i in range(len(levels_list) - 1):
            level = levels_list[i]
            variable_names.append(f"{attr}_{level}")
            variables.append([])
    
    # Fill the design matrix
    for profile in profiles:
        var_idx = 0
        for attr, levels in attribute_levels.items():
            levels_list = sorted(list(levels))
            current_level = profile[attr]
            
            for i in range(len(levels_list) - 1):
                level = levels_list[i]
                if current_level == level:
                    variables[var_idx].append(1)
                elif current_level == levels_list[-1]:  # Reference level
                    variables[var_idx].append(-1)
                else:
                    variables[var_idx].append(0)
                var_idx += 1
    
    design_matrix = np.array(variables).T
    return design_matrix, variable_names

def calculate_d_optimality(X: np.ndarray) -> float:
    """
    Calculate D-optimality criterion: det(X'X)
    
    Args:
        X: Design matrix
    
    Returns:
        D-optimality value (higher is better)
    """
    if X.shape[0] < X.shape[1]:
        return 0.0  # Not enough observations for parameters
    
    try:
        XtX = X.T @ X
        det_value = np.linalg.det(XtX)
        return det_value if det_value > 0 else 0.0
    except np.linalg.LinAlgError:
        return 0.0

def generate_choice_sets(profiles: List[Dict[str, Any]], n_options: int = 2, n_sets: int = 5) -> List[List[Dict[str, Any]]]:
    """
    Generate D-optimal choice sets using coordinate exchange algorithm.
    
    Args:
        profiles: List of all possible profiles
        n_options: Number of options per choice set (2 or 3)
        n_sets: Number of choice sets to generate
    
    Returns:
        List of choice sets, each containing n_options profiles
    """
    if len(profiles) < n_options:
        # Not enough profiles, return what we have
        return [profiles] if profiles else []
    
    # Create design matrix for all profiles
    X_all, var_names = create_design_matrix(profiles)
    
    if X_all.size == 0:
        # Fallback to random selection
        return [random.sample(profiles, min(n_options, len(profiles))) for _ in range(n_sets)]
    
    # Initialize choice sets randomly
    choice_sets = []
    for _ in range(n_sets):
        if len(profiles) >= n_options:
            choice_set = random.sample(profiles, n_options)
        else:
            choice_set = profiles.copy()
        choice_sets.append(choice_set)
    
    # Coordinate exchange algorithm for D-optimality
    max_iterations = 50
    for iteration in range(max_iterations):
        improved = False
        
        for set_idx in range(len(choice_sets)):
            current_set = choice_sets[set_idx]
            
            # Try replacing each profile in the set
            for profile_idx in range(len(current_set)):
                current_profile = current_set[profile_idx]
                
                # Try all other profiles as replacement
                for candidate_profile in profiles:
                    if candidate_profile in current_set:
                        continue
                    
                    # Create new set with replacement
                    new_set = current_set.copy()
                    new_set[profile_idx] = candidate_profile
                    
                    # Calculate D-optimality for all sets
                    all_sets = choice_sets.copy()
                    all_sets[set_idx] = new_set
                    
                    # Create combined design matrix
                    all_profiles = []
                    for cs in all_sets:
                        all_profiles.extend(cs)
                    
                    X_combined, _ = create_design_matrix(all_profiles)
                    
                    if X_combined.size > 0:
                        new_d_opt = calculate_d_optimality(X_combined)
                        
                        # Compare with current D-optimality
                        current_profiles = []
                        for cs in choice_sets:
                            current_profiles.extend(cs)
                        X_current, _ = create_design_matrix(current_profiles)
                        current_d_opt = calculate_d_optimality(X_current) if X_current.size > 0 else 0.0
                        
                        if new_d_opt > current_d_opt:
                            choice_sets[set_idx] = new_set
                            improved = True
                            break
                
                if improved:
                    break
            
            if improved:
                break
        
        if not improved:
            break
    
    return choice_sets

def calculate_optimal_tournament_tasks(filtered_byo: Dict[str, List[Any]], min_tasks_per_parameter: float = 2.0) -> int:
    """
    Calculate the optimal number of tournament tasks based on statistical requirements.
    
    Args:
        filtered_byo: Filtered BYO configuration with only acceptable levels
        min_tasks_per_parameter: Minimum tasks per parameter (default: 2.0)
    
    Returns:
        Optimal number of tournament tasks
    """
    # Calculate number of parameters to estimate
    total_parameters = 0
    for attribute, levels in filtered_byo.items():
        # For each attribute, we need (n-1) parameters where n = number of levels
        if len(levels) > 1:
            total_parameters += len(levels) - 1
    
    # Calculate minimum tasks needed
    min_tasks = max(3, int(total_parameters * min_tasks_per_parameter))
    
    # Add some buffer for better precision
    optimal_tasks = min_tasks + 2
    
    # Cap at reasonable maximum (e.g., 20 tasks)
    optimal_tasks = min(optimal_tasks, 20)
    
    return optimal_tasks

def generate_tournament_plan(previous_utilities: Dict[str, Dict[str, float]], byo: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Generate a complete tournament plan with optimal number of tasks.
    
    Args:
        previous_utilities: Dictionary of attribute-level utilities from screening
        byo: Original BYO configuration with all attributes and levels
    
    Returns:
        Tournament plan with number of tasks and design information
    """
    # Filter design space
    filtered_byo = filter_design_space_for_tournament(previous_utilities, byo)
    
    # Calculate optimal number of tasks
    optimal_tasks = calculate_optimal_tournament_tasks(filtered_byo)
    
    # Generate all possible profiles
    all_profiles = full_factorial(filtered_byo)
    
    # Calculate design efficiency metrics
    design_matrix, variable_names = create_design_matrix(all_profiles)
    d_opt_value = calculate_d_optimality(design_matrix)
    
    # Determine number of options per task (3 as default, 4 as fallback)
    if len(all_profiles) >= 6:
        n_options = 3  # Default: 3 options for 6+ profiles
    elif len(all_profiles) >= 3:
        n_options = 3  # Use 3 if we have at least 3 profiles
    elif len(all_profiles) >= 2:
        n_options = 2  # Use 2 if we only have 2 profiles
    else:
        n_options = 1  # Use 1 if we only have 1 profile
    
    return {
        "total_tasks": optimal_tasks,
        "options_per_task": n_options,
        "total_profiles": len(all_profiles),
        "parameters_to_estimate": len(variable_names),
        "design_efficiency": d_opt_value,
        "filtered_attributes": filtered_byo,
        "design_matrix_shape": design_matrix.shape if design_matrix.size > 0 else (0, 0)
    }

# Tournament: D-optimal design using filtered design space
def generate_tournament_set(previous_utilities: Dict[str, Dict[str, float]], byo: Dict[str, List[Any]], task_number: int, n_options: int = 3) -> List[Dict[str, Any]]:
    """
    Generate tournament concepts using D-optimal design with filtered design space.
    
    Args:
        previous_utilities: Dictionary of attribute-level utilities from screening
        byo: Original BYO configuration with all attributes and levels
        task_number: Current tournament task number
        n_options: Number of concepts to generate (default: 3 for choice sets)
    
    Returns:
        List of tournament concepts with IDs
    """
    # Filter design space based on screening utilities
    filtered_byo = filter_design_space_for_tournament(previous_utilities, byo)
    
    # Generate all possible profiles from filtered design space
    all_profiles = full_factorial(filtered_byo)
    
    # If we don't have enough profiles, fall back to original BYO
    if len(all_profiles) < n_options:
        all_profiles = full_factorial(byo)
    
    # Determine actual number of options based on available profiles
    actual_n_options = min(n_options, len(all_profiles))
    
    # Use 4 options as fallback only if we have significantly more profiles
    if actual_n_options == 3 and len(all_profiles) >= 8:
        # Try to use 4 options if we have 8+ profiles available
        actual_n_options = 4
    
    # Generate D-optimal choice sets
    choice_sets = generate_choice_sets(all_profiles, n_options=actual_n_options, n_sets=1)
    
    if not choice_sets:
        # Fallback to random selection
        sampled_concepts = random.sample(all_profiles, min(actual_n_options, len(all_profiles)))
    else:
        sampled_concepts = choice_sets[0]
    
    # Add concept IDs to each concept
    concepts_with_ids = []
    for i, concept in enumerate(sampled_concepts):
        concept_with_id = {
            "id": i,  # Concept ID (0, 1, 2, etc.)
            "attributes": concept
        }
        concepts_with_ids.append(concept_with_id)
    
    return concepts_with_ids

# Estimate utilities based on screening responses
def estimate_initial_utilities(responses: List[bool], tasks: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Estimate utilities based on screening responses using the algorithm from Screening_Concepts_algo.md.
    
    Algorithm:
    1. Tally accept/reject counts by attribute-level
    2. Infer acceptable and unacceptable levels
    3. Return utilities for acceptable levels only
    
    Args:
        responses: List of boolean responses (True = accept, False = reject)
        tasks: List of screening concepts shown to respondent
    
    Returns:
        Dictionary mapping attributes to their level utilities
    """
    if not tasks or not responses or len(tasks) != len(responses):
        return {}
    
    # Step 1: Tally accept/reject counts by attribute-level
    level_counts = {}  # {attribute: {level: {"accepted": count, "rejected": count}}}
    
    for task, response in zip(tasks, responses):
        for attribute, level in task.items():
            if attribute not in level_counts:
                level_counts[attribute] = {}
            if level not in level_counts[attribute]:
                level_counts[attribute][level] = {"accepted": 0, "rejected": 0}
            
            if response:  # Accepted
                level_counts[attribute][level]["accepted"] += 1
            else:  # Rejected
                level_counts[attribute][level]["rejected"] += 1
    
    # Step 2: Infer acceptable and unacceptable levels
    utilities = {}
    
    for attribute, levels in level_counts.items():
        utilities[attribute] = {}
        
        for level, counts in levels.items():
            accepted = counts["accepted"]
            rejected = counts["rejected"]
            
            # Rule: If level has at least one acceptance, it's acceptable
            if accepted > 0:
                # Calculate utility based on acceptance rate
                total_appearances = accepted + rejected
                utility = accepted / total_appearances if total_appearances > 0 else 0.5
                utilities[attribute][level] = utility
            # Rule: If level has only rejections and appears in multiple rejected concepts, it's unacceptable
            elif rejected >= 2:
                # Mark as unacceptable by setting utility to 0
                utilities[attribute][level] = 0.0
            else:
                # For levels with only 1 rejection, give them a chance (low utility)
                utilities[attribute][level] = 0.1
    
    return utilities

def filter_design_space_for_tournament(utilities: Dict[str, Dict[str, float]], byo: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    """
    Filter the design space for the tournament based on screening utilities.
    
    Args:
        utilities: Dictionary of attribute-level utilities from screening
        byo: Original BYO configuration with all attributes and levels
    
    Returns:
        Filtered BYO configuration with only acceptable levels
    """
    filtered_byo = {}
    
    for attribute, levels in byo.items():
        if attribute in utilities:
            # Only include levels with utility > 0 (acceptable levels)
            acceptable_levels = [
                level for level in levels 
                if level in utilities[attribute] and utilities[attribute][level] > 0
            ]
            
            # If no levels are acceptable, include all levels (fallback)
            if not acceptable_levels:
                acceptable_levels = levels
            
            filtered_byo[attribute] = acceptable_levels
        else:
            # If no utilities for this attribute, include all levels
            filtered_byo[attribute] = levels
    
    return filtered_byo

# Update utilities based on choice
def adaptive_update(current_utils: Dict[str, Dict[str, float]], choice: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """
    Update utilities based on the chosen concept in tournament.
    
    Args:
        current_utils: Current utilities dictionary {attribute: {level: utility}}
        choice: The chosen concept attributes
    
    Returns:
        Updated utilities dictionary
    """
    if not current_utils:
        return current_utils
    
    # Create a copy to avoid modifying the original
    updated_utils = {}
    for attr, level_utils in current_utils.items():
        # Use dict() to copy, which works for both float and numpy float
        updated_utils[attr] = dict(level_utils)
    
    # Simple update: increase utility for chosen levels
    for attr, level in choice.items():
        if attr in updated_utils and level in updated_utils[attr]:
            # Increase utility for chosen level
            updated_utils[attr][level] += 0.1
            
            # Optionally decrease utilities for other levels in the same attribute
            for other_level in updated_utils[attr]:
                if other_level != level:
                    updated_utils[attr][other_level] = max(0.0, updated_utils[attr][other_level] - 0.05)
    
    return updated_utils