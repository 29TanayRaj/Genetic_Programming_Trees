from .gp_node import GPNode
from .gp_function import GPFunction
import random
from utils import constant
from typing import List, Union, Iterable

class GPTree:
    def __init__(self,
                 func_set: Iterable[GPFunction], 
                 variables: List[str] = None,
                 use_erc: bool = False,
                 erc_range: tuple = (-1.0, 1.0),
                 root: GPNode = None):
        """
        Initialize a GP Tree.
        
        Args:
            func_set: Set of functions that can be used in the tree
            variables: List of variable names (e.g., ['x', 'y', 'z'])
            use_erc: If True, ephemeral random constants will be generated automatically
            erc_range: Tuple (min, max) for generating random constants
            root: Root node of the tree
        """
        self.func_set = list(func_set)
        self.variables = list(variables) if variables else []
        self.use_erc = use_erc
        self.erc_range = erc_range
        self.root = root
     
    def random_init(self, min_d: int, max_d: int, method: str) -> GPNode:
        if method.lower() not in (constant.FULL, constant.GROW):
            raise ValueError(f"method must be either '{constant.FULL}' or '{constant.GROW}'.")

        self.root = self._random_init_recursive(min_d, max_d, method.lower())
        return self.root

    def _random_init_recursive(self, min_d: int, max_d: int, method: str) -> GPNode:
        if min_d > 0:
            func = self._choose_random_element(self.func_set)
            subtree = [self._random_init_recursive(min_d - 1, max_d - 1, method) for _ in range(func.arity)]
            return GPNode(func, next=subtree)

        # Calculate terminal set size (variables + ERC if enabled)
        terminal_count = len(self.variables) + (1 if self.use_erc else 0)
        
        if (max_d == 0) or (method == constant.GROW and
            random.random() < terminal_count / (terminal_count + len(self.func_set))):
            # Choose between variable and ERC
            if self.use_erc and (not self.variables or random.random() < 0.5):
                # Generate ephemeral random constant
                erc_value = random.uniform(self.erc_range[0], self.erc_range[1])
                return GPNode(erc_value, is_learnable=True)
            else:
                # Choose a variable
                if self.variables:
                    terminal_value = self._choose_random_element(self.variables)
                    return GPNode(terminal_value, is_learnable=False)
                # Fallback to ERC if no variables
                erc_value = random.uniform(self.erc_range[0], self.erc_range[1])
                return GPNode(erc_value, is_learnable=True)

        func = self._choose_random_element(self.func_set)
        subtree = [self._random_init_recursive(0, max_d - 1, method) for _ in range(func.arity)]
        return GPNode(func, next=subtree)
        
    @staticmethod
    def _choose_random_element(ele_list):
        return random.choice(ele_list)

    def eval_tree(self, **kwargs):
        if self.root is None:
            raise ValueError("Cannot evaluate an empty tree")
        
        return self._eval_recursive(self.root, **kwargs)
    
    def _eval_recursive(self, node: GPNode, **kwargs):
        # Terminal node
        if not node.is_function():
            if isinstance(node.value, str) and node.value in kwargs:
                return kwargs[node.value]
            return node.value
        
        evaluated_args = [self._eval_recursive(child, **kwargs) for child in node.next]
        return node.value(*evaluated_args)

    def copy(self):
        new_tree = GPTree(self.func_set, 
                         variables=self.variables,
                         use_erc=self.use_erc,
                         erc_range=self.erc_range)
        if self.root is not None:
            new_tree.root = self._copy_node(self.root)
        return new_tree
    
    def _copy_node(self, node: GPNode) -> GPNode:
        if node is None:
            return None
        copied_children = [self._copy_node(child) for child in node.next]
        return GPNode(node.value, next=copied_children, is_learnable=node.is_learnable)

    def mutate(self, mutate_type: str):

        if self.root is None:
            raise ValueError("Cannot mutate an empty tree")
        
        if mutate_type.lower() == constant.POINT:
            self._point_mutation()
        elif mutate_type.lower() == constant.SUBTREE:
            self._subtree_mutation()
        elif mutate_type.lower() == constant.HOIST:
            self._hoist_mutation()
        else:
            raise ValueError(f"mutate_type must be either '{constant.POINT}', '{constant.SUBTREE}', or '{constant.HOIST}'")
        
        return self

    def _point_mutation(self):

        all_nodes = self._collect_all_nodes(self.root)
        
        if not all_nodes:
            return
        
        node_to_mutate = random.choice(all_nodes)
        
        if node_to_mutate.is_function():
            same_arity_funcs = [f for f in self.func_set if f.arity == node_to_mutate.value.arity]
            
            if same_arity_funcs:
                new_func = self._choose_random_element(same_arity_funcs)
                node_to_mutate.value = new_func
        else:
            # Terminal node - respect learnable vs variable distinction
            if node_to_mutate.is_learnable_constant():
                # Replace with a new random constant (ERC)
                if self.use_erc:
                    new_constant = random.uniform(self.erc_range[0], self.erc_range[1])
                    node_to_mutate.value = new_constant
                    node_to_mutate.is_learnable = True
            else:
                # Replace with another variable
                if self.variables:
                    new_terminal = self._choose_random_element(self.variables)
                    node_to_mutate.value = new_terminal
                    node_to_mutate.is_learnable = False

    def _subtree_mutation(self, max_depth: int = 3):

        all_nodes = self._collect_all_nodes(self.root)
        
        if not all_nodes:
            return
        
        node_to_replace = random.choice(all_nodes)
        
        new_subtree = self._random_init_recursive(0, max_depth, constant.GROW)
        
        node_to_replace.value = new_subtree.value
        node_to_replace.next = new_subtree.next

    def _hoist_mutation(self):
        """
        Hoist mutation: Select a subtree, then select a smaller subtree inside it
        and replace the larger subtree with the smaller one.
        This helps reduce tree size and control bloat.
        """
        all_nodes = self._collect_all_nodes(self.root)
        
        # Filter nodes that have at least one child (function nodes)
        function_nodes = [node for node in all_nodes if node.is_function() and node.next]
        
        if not function_nodes:
            # If no function nodes, fall back to point mutation
            self._point_mutation()
            return
        
        # Select a random subtree (must be a function node)
        selected_subtree = random.choice(function_nodes)
        
        # Collect all nodes within this subtree
        subtree_nodes = self._collect_all_nodes(selected_subtree)
        
        # If the subtree only has the root, we can't hoist anything
        if len(subtree_nodes) <= 1:
            # Fall back to point mutation
            self._point_mutation()
            return
        
        # Select a random node from within the subtree (excluding the root)
        # This will be hoisted up to replace the selected_subtree
        node_to_hoist = random.choice(subtree_nodes[1:])  # Exclude the first element (root)
        
        # Replace the selected subtree with the hoisted node
        selected_subtree.value = node_to_hoist.value
        selected_subtree.next = node_to_hoist.next

    def _collect_all_nodes(self, node: GPNode) -> List[GPNode]:

        if node is None:
            return []
        
        nodes = [node]
        
        for child in node.next:
            nodes.extend(self._collect_all_nodes(child))
        
        return nodes

    def get_depth(self, node: GPNode = None) -> int:

        if node is None:
            node = self.root
        
        if node is None or not node.next:
            return 0
        
        return 1 + max(self.get_depth(child) for child in node.next)

    def count_nodes(self, node: GPNode = None) -> int:

        if node is None:
            node = self.root
        
        if node is None:
            return 0
        
        count = 1
        for child in node.next:
            count += self.count_nodes(child)
        
        return count

    def __repr__(self):
        return self._prefix(self.root)

    def _prefix(self, node):
        if node is None:
            return constant.EMPTY_TREE

        # Terminal
        if not node.is_function():
            return str(node.value)

        # Function
        func_name = node.value.name
        subtree = " ".join(self._prefix(child_node) for child_node in node.next)
        return f"({func_name} {subtree})"