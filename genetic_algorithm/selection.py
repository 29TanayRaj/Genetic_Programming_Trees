import random
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.gp_tree import GPTree

def tournament_selection(population: List['GPTree'], tournament_size: int = 7) -> 'GPTree':
    """
    Selects the best individual from a random subset of the population.
    
    Args:
        population: List of GPTree individuals
        tournament_size: Number of individuals to compete in the tournament
        
    Returns:
        The fittest GPTree from the tournament
    """
    if not population:
        raise ValueError("Population is empty")
        
    # Ensure tournament size is not larger than population
    k = min(tournament_size, len(population))
    
    # Randomly select k individuals
    tournament = random.sample(population, k)
    
    # Return the one with the best (lowest) fitness
    # Assuming lower fitness is better (e.g., error minimization)
    # We filter out None fitness values just in case, though they should be evaluated
    valid_contestants = [ind for ind in tournament if ind.fitness is not None]
    
    if not valid_contestants:
        # Fallback if no fitnesses are set (should not happen in proper loop)
        return random.choice(tournament)
        
    return min(valid_contestants, key=lambda ind: ind.fitness)
