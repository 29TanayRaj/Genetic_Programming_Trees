from utils.gp_tree import GPTree
from utils.gp_function import GPFunction
from utils.gp_node import GPNode
from utils import constant
import random
import numpy as np
from typing import List, Union, Iterable



class GAPopulation:

    def __init__(self, population_size =500):
        self.population_size = population_size
        self.population = None

    def initialize(self, func_set: Iterable[GPFunction], 
                 variables: List[str],
                 use_erc: bool = False,
                 erc_range: tuple = (-1.0, 1.0),
                 min_depth: int = 2,
                 max_depth: int = 6):
        """
        Initialize the ga_population using the Ramped Half-and-Half method.
        
        Args:
            func_set: Set of functions for the trees
            variables: List of variable names
            use_erc: Whether to use Ephemeral Random Constants
            erc_range: Range for ERC values
            min_depth: Minimum depth for initialization
            max_depth: Maximum depth for initialization
        """
        self.population = []
        
        # Ramped Half-and-Half: 
        # Divide the population into depth ranges from min_depth to max_depth.
        # For each depth, half the individuals are created with GROW and half with FULL.
        
        depth_ranges = list(range(min_depth, max_depth + 1))
        num_depths = len(depth_ranges)
        pop_per_depth = self.population_size // num_depths
        
        for depth in depth_ranges:
            # For each depth, create half GROW and half FULL
            num_full = pop_per_depth // 2
            num_grow = pop_per_depth - num_full
            
            for _ in range(num_full):
                tree = GPTree(func_set, variables, use_erc, erc_range)
                tree.random_init(min_d=depth, max_d=depth, method=constant.FULL)
                self.population.append(tree)
                
            for _ in range(num_grow):
                tree = GPTree(func_set, variables, use_erc, erc_range)
                tree.random_init(min_d=depth, max_d=depth, method=constant.GROW)
                self.population.append(tree)
        
        # Fill any remaining slots due to integer division
        while len(self.population) < self.population_size:
            method = random.choice([constant.FULL, constant.GROW])
            depth = random.choice(depth_ranges)
            tree = GPTree(func_set, variables, use_erc, erc_range)
            tree.random_init(min_d=depth, max_d=depth, method=method)
            self.population.append(tree)

    def evaluate(self, data: List[dict], target_values: List[float], loss_function: callable):
        """
        Evaluate the fitness of each individual in the population.
        
        Args:
            data: List of dictionaries, where each dict contains variable values (e.g., [{'x': 1}, {'x': 2}])
            target_values: List of expected output values corresponding to the data points
            loss_function: Function that takes (predicted, actual) and returns a loss value (lower is better)
        """
        if not self.population:
            raise ValueError("Population is empty. Call initialize() first.")

        # Convert target_values to numpy array once
        targets = np.array(target_values)

        for tree in self.population:
            try:
                # Vectorized evaluation if possible, or list comprehension then conversion
                # Assuming eval_tree handles single point, we loop. 
                # Optimization: If eval_tree could handle vectors, that would be better, 
                # but for now we collect results.
                predictions = np.array([tree.eval_tree(**input_data) for input_data in data])
                
                # Calculate fitness using the vectorized loss function
                tree.fitness = loss_function(predictions, targets)
            except Exception as e:
                # If evaluation fails (e.g., division by zero), assign infinite fitness
                tree.fitness = float('inf')

    

        

