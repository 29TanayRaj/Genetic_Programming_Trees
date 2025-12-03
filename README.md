This project is intended as my personal project for genetic programming with individuals having a tree repersentation, whcih could be used for further applications such as symbolic regression. 

#### Some Acknowlegement and source material 
I had been reading the book "A Field Guide to Genetic Programming by Nicholas Freitag McPhee, Riccardo Poli, William B. Langdon" and wanted to apply some of the concepts and come up with a code. I have tried to use the naming notations for some of the programs amd have used some of the alogrithems mentioned in the book. So do check out the book for more information.


Project folder Structure: 
- utils
    - __init__.py
    - gp_function.py
    - gp_node.py 
    - gp_tree.py
    - constant.py 
- graph_builder
    - __init__.py 
    - dot_converter.py 
    - graph_builder.py

File Decription: 

1. gp_function.py : contains a function class GPFunction which will be used for creating the functions. 
2. gp_node.py : contains a node class GPNode which is the building block for a tree and can be used for both a terminal and a function node for a tree. 
3. gp_tree.py : contains a tree class GPTree which will act as the individuals for genetic algorithem programs. 
4. constant.py : made for storing repeataive strings 
5. dot_converter.py: takes tree representation in string format and returns a dot represenation.
6. graph_builder.py: retruns a image of a graph using graphviz based on dot represenation.

Current Challenges:
- Mutations of GP trees:
- Need to work on the following 
## 1. Point Mutation
- A single node in the GP tree is mutated
- Terminal nodes are replaced by other terminals
- Function nodes are replaced by other functions
- A threshold is used to decide whether to mutate the selected node
- Node is selected randomly from the GP tree

## 2. Subtree Mutation
- A randomly selected node is replaced with a newly generated subtree
- New subtree is generated using standard GP initialization methods (grow/full/RHH)
- Depth limits are applied to avoid excessive tree bloat
- Node selection is random — uniform or depth-biased
- Produces large structural changes and increases exploration

## 3. Hoist Mutation
- Select a subtree, then select a smaller subtree inside it and “hoist” it upwards
- The smaller internal subtree replaces the larger subtree
- Helps reduce tree size and control bloat
- Node and internal subtree selections are random
- Encourages simpler, more general GP trees