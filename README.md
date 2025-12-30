# Tree-Based Genetic Programming

This project is intended as my personal project for genetic programming with individuals having a tree representation, which could be used for further applications such as symbolic regression.

## Acknowledgement and Source Material

I had been reading the book "A Field Guide to Genetic Programming" by Nicholas Freitag McPhee, Riccardo Poli, and William B. Langdon and wanted to apply some of the concepts and come up with a code. I have tried to use the naming notations for some of the programs and have used some of the algorithms mentioned in the book. So do check out the book for more information.

---

## Project Folder Structure

```
Tree Based Genetic Programming/
├── genetic_algorithm/
│   ├── __init__.py
│   └── population.py     # Population management
├── graph_builder/
│   ├── __init__.py
│   ├── dot_converter.py  # Convert trees to DOT format
│   └── graph_builder.py  # Generate tree visualizations
├── utils/
│   ├── __init__.py
│   ├── gp_function.py    # Function wrapper class
│   ├── gp_node.py        # Tree node class
│   ├── gp_tree.py        # Main GP tree class
│   └── constant.py       # Constants and configuration
└── README.md
```

---

## File Descriptions

1. **gp_function.py**: Contains the `GPFunction` class which wraps callable functions for use in GP trees
2. **gp_node.py**: Contains the `GPNode` class, the building block for trees (can be either a terminal or function node)
3. **gp_tree.py**: Contains the `GPTree` class which represents individuals in genetic algorithm programs
4. **constant.py**: Stores repetitive string constants used throughout the project
5. **dot_converter.py**: Takes tree representation in string format and returns a DOT representation
6. **graph_builder.py**: Returns an image of a graph using Graphviz based on DOT representation
7. **population.py**: Manages a population of `GPTree` individuals
8. **loss_function.py**: Contains standard loss functions (MSE, MAE, etc.) for fitness evaluation

---

## Class Documentation

### 1. GPFunction (`gp_function.py`)

Wrapper class for functions used in genetic programming trees.

#### Parameters:
- **name** (`str`): The name/symbol of the function (e.g., '+', 'sin', 'add')
- **expression** (`callable`): The actual Python function to execute
- **arity** (`int`): Number of arguments the function takes

#### Methods:
- **`__call__(*args)`**: Makes the GPFunction callable, executes the wrapped expression
- **`__repr__()`**: Returns string representation showing name and arity

#### Example:
```python
add_func = GPFunction('+', lambda x, y: x + y, 2)
result = add_func(3, 5)  # Returns 8
```

---

### 2. GPNode (`gp_node.py`)

Represents a single node in a genetic programming tree. Can be either a function node or a terminal node.

#### Parameters:
- **value** (`GPFunction | Any`): Either a GPFunction object or a terminal value (number, variable name, etc.)
- **next** (`List[GPNode]`, optional): List of child nodes (empty for terminals). Default: `[]`
- **is_learnable** (`bool`, optional): True if this is an Ephemeral Random Constant (ERC), False for variables. Default: `False`

#### Attributes:
- **value**: The value stored in this node
- **next**: List of child nodes
- **is_learnable**: Flag indicating if this is a learnable constant

#### Methods:

##### `is_function() -> bool`
Returns `True` if this node contains a GPFunction, `False` otherwise.

##### `is_terminal() -> bool`
Returns `True` if this node is a terminal (not a function), `False` otherwise.

##### `is_learnable_constant() -> bool`
Returns `True` if this node is a learnable constant (ERC), `False` otherwise.

##### `is_variable() -> bool`
Returns `True` if this node is a variable (non-learnable terminal), `False` otherwise.

##### `arity() -> int`
Returns the arity of the function if this is a function node, or 0 for terminals.

#### Example:
```python
# Function node
func_node = GPNode(GPFunction('+', lambda x,y: x+y, 2))

# Variable node
var_node = GPNode('x', is_learnable=False)

# Ephemeral Random Constant node
erc_node = GPNode(3.14159, is_learnable=True)
```

---

### 3. GPTree (`gp_tree.py`)

Main class representing a complete genetic programming tree. This is the individual in a GP population.

#### Parameters:
- **func_set** (`Iterable[GPFunction]`): Set of functions that can be used in the tree
- **variables** (`List[str]`, optional): List of variable names (e.g., `['x', 'y', 'z']`). Default: `[]`
- **use_erc** (`bool`, optional): If `True`, Ephemeral Random Constants will be generated automatically. Default: `False`
- **erc_range** (`tuple`, optional): Tuple `(min, max)` for generating random constants. Default: `(-1.0, 1.0)`
- **root** (`GPNode`, optional): Root node of the tree. Default: `None`

#### Attributes:
- **func_set**: List of available functions
- **variables**: List of variable names
- **use_erc**: Whether ERCs are enabled
- **erc_range**: Range for generating ERCs
- **root**: Root node of the tree

---

#### Tree Initialization Methods

##### `random_init(min_d: int, max_d: int, method: str) -> GPNode`
Initializes the tree randomly using either FULL or GROW method.

**Parameters:**
- **min_d**: Minimum depth of the tree
- **max_d**: Maximum depth of the tree
- **method**: Initialization method - either `'full'` or `'grow'`
  - **FULL**: All branches grow to max_d (creates bushy trees)
  - **GROW**: Branches can terminate early (creates varied shapes)

**Returns:** The root node of the initialized tree

**Example:**
```python
tree.random_init(min_d=2, max_d=4, method='grow')
```

---

#### Evaluation Methods

##### `eval_tree(**kwargs) -> float`
Evaluates the tree with given variable values.

**Parameters:**
- **kwargs**: Variable names and their values (e.g., `x=2.0, y=3.0`)

**Returns:** The numerical result of evaluating the tree

**Example:**
```python
result = tree.eval_tree(x=2.0, y=3.0)
```

---

#### Mutation Methods

##### `mutate(mutate_type: str) -> GPTree`
Mutates the tree using the specified mutation type.

**Parameters:**
- **mutate_type**: Type of mutation - `'point'`, `'subtree'`, or `'hoist'`

**Returns:** Self (for method chaining)

**Mutation Types:**

1. **Point Mutation** (`'point'`):
   - Randomly selects a single node and replaces it
   - Function nodes → replaced by functions with same arity
   - ERC nodes → replaced by new random constants
   - Variable nodes → replaced by other variables

2. **Subtree Mutation** (`'subtree'`):
   - Randomly selects a node and replaces entire subtree
   - New subtree generated using GROW method
   - Can cause significant structural changes
   - Default max depth: 3

3. **Hoist Mutation** (`'hoist'`):
   - Selects a subtree, then a smaller subtree within it
   - Replaces larger subtree with the smaller one
   - Reduces tree size and helps control bloat
   - Encourages simpler solutions

**Example:**
```python
tree.mutate('point')     # Point mutation
tree.mutate('subtree')   # Subtree mutation
tree.mutate('hoist')     # Hoist mutation
```

---

#### Utility Methods

##### `copy() -> GPTree`
Creates a deep copy of the tree.

**Returns:** A new GPTree with identical structure and values

**Example:**
```python
tree_copy = tree.copy()
```

##### `get_depth(node: GPNode = None) -> int`
Returns the depth of the tree (or subtree).

**Parameters:**
- **node**: Starting node (uses root if None)

**Returns:** Maximum depth from the given node

**Example:**
```python
depth = tree.get_depth()  # Depth of entire tree
```

##### `count_nodes(node: GPNode = None) -> int`
Counts the total number of nodes in the tree (or subtree).

**Parameters:**
- **node**: Starting node (uses root if None)

**Returns:** Total number of nodes

**Example:**
```python
num_nodes = tree.count_nodes()
```

---

#### Representation Methods

##### `__repr__() -> str`
Returns the tree in prefix notation.

**Returns:** String representation in prefix format

**Example:**
```python
print(tree)  # Output: (+ (* x 2.5) y)
```

##### `to_infix() -> str`
Converts the tree to infix notation for better readability.

**Returns:** String representation in infix format

**Handles:**
- Unary operators: `sin(x)`, `cos(x)`
- Binary operators: `(x + 2.5)`, `(a * b)`
- N-ary operators: `max(a, b, c)`

**Example:**
```python
print(tree.to_infix())  # Output: ((x * 2.5) + y)
```

### 4. GAPopulation (`genetic_algorithm/population.py`)

Manages a population of `GPTree` individuals.

#### Parameters:
- **population_size** (`int`): Number of individuals in the population. Default: `500`

#### Methods:
- **`initialize(...)`**: Initializes the population using Ramped Half-and-Half method.
- **`evaluate(data, target_values, loss_function)`**: Evaluates fitness of all individuals using vectorized operations.

---

### 5. Loss Functions (`utils/loss_function.py`)

Standard loss functions implemented using `numpy` for performance:
- **`mse(predicted, actual)`**: Mean Squared Error
- **`mae(predicted, actual)`**: Mean Absolute Error
- **`rmse(predicted, actual)`**: Root Mean Squared Error
- **`log_cosh(predicted, actual)`**: Log Cosh Loss

---

## Usage Example

```python
import numpy as np
from utils.gp_tree import GPTree
from utils.gp_function import GPFunction
from utils import constant, loss_function
from genetic_algorithm.population import GAPopulation

# Define function set
func_set = [
    GPFunction('+', lambda x, y: x + y, 2),
    GPFunction('*', lambda x, y: x * y, 2),
    GPFunction('-', lambda x, y: x - y, 2),
]

# 1. Initialize Population
pop = GAPopulation(population_size=50)
pop.initialize(
    func_set=func_set,
    variables=['x'],
    use_erc=True,
    erc_range=(-5.0, 5.0),
    min_depth=2,
    max_depth=5
)

# 2. Prepare Data (using numpy)
# Target function: y = x^2 + 2x
data = [{'x': i} for i in np.linspace(-5, 5, 20)]
target_values = np.array([d['x']**2 + 2*d['x'] for d in data])

# 3. Evaluate Fitness
pop.evaluate(
    data=data,
    target_values=target_values,
    loss_function=loss_function.mse
)

# 4. Inspect Best Individual
best_tree = min(pop.population, key=lambda t: t.fitness)
print(f"Best Fitness: {best_tree.fitness}")
print(f"Best Tree: {best_tree}")
```

---

## Features

 **Tree Initialization**: FULL and GROW methods  
 **Ramped Half-and-Half**: Diverse population initialization  
 **Vectorized Evaluation**: Fast fitness calculation using `numpy`  
 **Ephemeral Random Constants (ERCs)**: Automatically generated learnable constants  
 **Multiple Mutation Types**: Point, Subtree, and Hoist mutations  
 **Standard Loss Functions**: MSE, MAE, RMSE, Log Cosh  
 **Bloat Control**: Hoist mutation helps reduce tree size  
 **Type Safety**: Distinction between variables and learnable constants

---

## Future Enhancements

- Crossover operations for recombination
- Selection operators (Tournament, Roulette Wheel)
- Symbolic regression examples
- Advanced bloat control mechanisms
