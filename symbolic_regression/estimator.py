import numpy as np
from typing import List, Optional, Union, Callable

from genetic_algorithm.population import GAPopulation
from genetic_algorithm.evolution import EvolutionEngine
from utils.gp_function import GPFunction
from utils import loss_function, constant

# Default Functions
def _add(x, y): return x + y
def _sub(x, y): return x - y
def _mul(x, y): return x * y
def _div(x, y): return np.divide(x, y, out=np.zeros_like(x, dtype=float), where=y!=0)
def _sin(x): return np.sin(x)
def _cos(x): return np.cos(x)

DEFAULT_FUNC_SET = [
    GPFunction("add", _add, 2),
    GPFunction("sub", _sub, 2),
    GPFunction("mul", _mul, 2),
    GPFunction("div", _div, 2),
    GPFunction("sin", _sin, 1),
    GPFunction("cos", _cos, 1),
]

class SymbolicRegressor:
    def __init__(self,
                 population_size: int = 1000,
                 generations: int = 20,
                 tournament_size: int = 20,
                 crossover_rate: float = 0.9,
                 mutation_rate: float = 0.1,
                 elitism_size: int = 1,
                 min_depth: int = 2,
                 max_depth: int = 6,
                 use_erc: bool = True,
                 erc_range: tuple = (-10.0, 10.0),
                 func_set: Optional[List[GPFunction]] = None,
                 loss_metric: str = constant.MSE,
                 verbose: bool = True):
        """
        Symbolic Regressor using Genetic Programming.
        
        Args:
            population_size: Number of individuals in the population.
            generations: Number of generations to evolve.
            tournament_size: Size of tournament selection.
            crossover_rate: Probability of crossover.
            mutation_rate: Probability of mutation.
            elitism_size: Number of best individuals to keep.
            min_depth: Minimum depth of trees.
            max_depth: Maximum depth of trees.
            use_erc: Whether to use Ephemeral Random Constants.
            erc_range: Range for ERCs.
            func_set: List of GPFunction objects to use. Defaults to basic arithmetic.
            loss_metric: 'mse', 'mae', 'rmse', or 'log_cosh'.
            verbose: Whether to print progress.
        """
        self.population_size = population_size
        self.generations = generations
        self.tournament_size = tournament_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_size = elitism_size
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.use_erc = use_erc
        self.erc_range = erc_range
        self.func_set = func_set if func_set is not None else DEFAULT_FUNC_SET
        self.loss_metric = loss_metric
        self.verbose = verbose
        
        self.population: Optional[GAPopulation] = None
        self.best_estimator_ = None
        self.variable_names_ = None

    def fit(self, X: Union[np.ndarray, List[List[float]]], y: Union[np.ndarray, List[float]]):
        """
        Fit the symbolic regressor to the data.
        
        Args:
            X: Input features. Shape (n_samples, n_features).
            y: Target values. Shape (n_samples,).
        """
        X = np.array(X)
        y = np.array(y)
        
        # Determine variable names
        n_features = X.shape[1]
        self.variable_names_ = [f'x{i}' for i in range(n_features)]
        
        # Convert X to list of dicts for current GPTree evaluation
        # Optimization: Ideally GPTree should handle numpy arrays directly, 
        # but for now we adapt to the existing interface.
        data_dicts = [
            {name: val for name, val in zip(self.variable_names_, row)}
            for row in X
        ]
        
        # Select loss function
        if self.loss_metric == constant.MSE:
            loss_f = loss_function.mse
        elif self.loss_metric == constant.MAE:
            loss_f = loss_function.mae
        elif self.loss_metric == constant.RMSE:
            loss_f = loss_function.rmse
        elif self.loss_metric == constant.LOG_COSH:
            loss_f = loss_function.log_cosh
        else:
            raise ValueError(f"Unknown loss metric: {self.loss_metric}")
            
        # Initialize Population
        self.population = GAPopulation(self.population_size)
        self.population.initialize(
            func_set=self.func_set,
            variables=self.variable_names_,
            use_erc=self.use_erc,
            erc_range=self.erc_range,
            min_depth=self.min_depth,
            max_depth=self.max_depth
        )
        
        # Initialize Engine
        engine = EvolutionEngine(
            population=self.population,
            crossover_rate=self.crossover_rate,
            mutation_rate=self.mutation_rate,
            tournament_size=self.tournament_size,
            elitism_size=self.elitism_size
        )
        
        # Run Evolution
        self.best_estimator_ = engine.evolve(
            data=data_dicts,
            target_values=y,
            loss_function=loss_f,
            generations=self.generations,
            verbose=self.verbose
        )
        
        return self

    def predict(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """
        Predict targets for X.
        """
        if self.best_estimator_ is None:
            raise ValueError("Model is not fitted yet.")
            
        X = np.array(X)
        
        # Adapt data
        data_dicts = [
            {name: val for name, val in zip(self.variable_names_, row)}
            for row in X
        ]
        
        # Vectorized evaluation if possible, else loop
        # The population.evaluate loop did something similar.
        # We can implement a helper or just loop here.
        predictions = np.array([self.best_estimator_.eval_tree(**d) for d in data_dicts])
        
        return predictions
