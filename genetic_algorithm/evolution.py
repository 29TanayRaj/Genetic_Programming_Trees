import random
import copy
from typing import List, Callable, Optional, Dict

from genetic_algorithm.population import GAPopulation
from genetic_algorithm.selection import tournament_selection
from genetic_algorithm.crossover import subtree_crossover
from utils.gp_tree import GPTree
from utils import constant

class EvolutionEngine:
    def __init__(self, 
                 population: GAPopulation,
                 crossover_rate: float = 0.9,
                 mutation_rate: float = 0.1,
                 tournament_size: int = 7,
                 elitism_size: int = 1):
        """
        Engine to drive the genetic programming evolution process.
        
        Args:
            population: An initialized GAPopulation object
            crossover_rate: Probability of performing crossover
            mutation_rate: Probability of performing mutation (if not crossover)
            tournament_size: Size of tournament for selection
            elitism_size: Number of best individuals to carry over unchanged
        """
        self.population = population
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_size = elitism_size
        
        self.best_individual: Optional[GPTree] = None
        self.history: List[float] = [] # Track best fitness over generations

    def evolve(self, 
               data: List[dict], 
               target_values: List[float], 
               loss_function: Callable,
               generations: int = 50,
               verbose: bool = True):
        """
        Run the evolution for a specified number of generations.
        
        Args:
            data: Input data for evaluation
            target_values: Target output values
            loss_function: Loss function (predicted, actual) -> float
            generations: Number of generations to run
            verbose: Whether to print progress
        """
        
        # Initial evaluation
        self.population.evaluate(data, target_values, loss_function)
        self._update_best_individual()
        
        if verbose:
            print(f"Gen 0: Best Fitness = {self.best_individual.fitness:.5f}")
        
        for gen in range(1, generations + 1):
            new_individuals = []
            
            # 1. Elitism
            sorted_pop = sorted(self.population.population, key=lambda x: x.fitness)
            elites = [ind.copy() for ind in sorted_pop[:self.elitism_size]]
            for elite in elites:
                elite.fitness = sorted_pop[elites.index(elite)].fitness # Copy fitness too (optimization)
            new_individuals.extend(elites)
            
            # 2. Main Loop
            while len(new_individuals) < self.population.population_size:
                if random.random() < self.crossover_rate:
                    # Crossover
                    parent1 = tournament_selection(self.population.population, self.tournament_size)
                    parent2 = tournament_selection(self.population.population, self.tournament_size)
                    child = subtree_crossover(parent1, parent2)
                else:
                    # Mutation
                    # Select one parent and mutate it
                    parent = tournament_selection(self.population.population, self.tournament_size)
                    child = parent.copy()
                    
                    # Choose mutation type
                    mut_type = random.choice([constant.POINT, constant.SUBTREE, constant.HOIST])
                    child.mutate(mut_type)
                
                new_individuals.append(child)
            
            # 3. Update Population
            self.population.population = new_individuals
            
            # 4. Evaluate New Population
            # Check if we need to re-evaluate elites? 
            # If data is static, we don't need to, but it's safer/easier to just call evaluate on all.
            # Optimization: could skip elites if we carried over fitness.
            self.population.evaluate(data, target_values, loss_function)
            
            # 5. Statistics
            self._update_best_individual()
            self.history.append(self.best_individual.fitness)
            
            if verbose and (gen % 1 == 0 or gen == generations):
                print(f"Gen {gen}: Best Fitness = {self.best_individual.fitness:.5f}")

        return self.best_individual

    def _update_best_individual(self):
        """Find the best individual in current population and update global best."""
        current_best = min(self.population.population, key=lambda x: x.fitness)
        
        if self.best_individual is None or current_best.fitness < self.best_individual.fitness:
            # We copy it so it doesn't get mutated in next generation if it wasn't an elite
            self.best_individual = current_best.copy()
            self.best_individual.fitness = current_best.fitness
