from .gp_node import GPNode
from .gp_function import GPFunction
import random
from utils import constant
from typing import List, Union, Iterable

import random
from typing import List, Iterable

class GPFunction:
    def __init__(self, name: str, expression: callable, arity: int):
        self.name = name
        self.expression = expression
        self.arity = arity

    def __call__(self, *args):
        return self.expression(*args)

    def __repr__(self) -> str:
        return f"GPFunction(name='{self.name}', arity={self.arity})"


class GPNode:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next if next is not None else []

    def is_function(self):
        return isinstance(self.value, GPFunction)
    
    def arity(self):
        return self.value.arity if self.is_function() else 0

class GPTree:
    def __init__(self,
                 func_set: Iterable[GPFunction], 
                 term_set: List,
                 root: GPNode = None):
        
        self.func_set = list(func_set)
        self.term_set = list(term_set)
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

        if (max_d == 0) or (method == constant.GROW and
            random.random() < len(self.term_set) / (len(self.term_set) + len(self.func_set))):
            terminal_value = self._choose_random_element(self.term_set)
            return GPNode(terminal_value)

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
        new_tree = GPTree(self.func_set, self.term_set)
        if self.root is not None:
            new_tree.root = self._copy_node(self.root)
        return new_tree
    
    def _copy_node(self, node: GPNode) -> GPNode:
        if node is None:
            return None
        copied_children = [self._copy_node(child) for child in node.next]
        return GPNode(node.value, next=copied_children)

    def mutate(self, mutate_type: str):

        if self.root is None:
            raise ValueError("Cannot mutate an empty tree")
        
        if mutate_type.lower() == constant.POINT:
            self._point_mutation()
        elif mutate_type.lower() == constant.SUBTREE:
            self._subtree_mutation()
        else:
            raise ValueError(f"mutate_type must be either '{constant.POINT}' or '{constant.SUBTREE}'")
        
        return self

    def _point_mutation(self):

        all_nodes = self._collect_all_nodes(self.root)
        
        if not all_nodes:
            return
        
        # Choose a random node to mutate
        node_to_mutate = random.choice(all_nodes)
        
        if node_to_mutate.is_function():
            # Replace function with another function of same arity
            same_arity_funcs = [f for f in self.func_set if f.arity == node_to_mutate.value.arity]
            
            if same_arity_funcs:
                new_func = self._choose_random_element(same_arity_funcs)
                node_to_mutate.value = new_func
        else:
            # Replace terminal with another terminal
            new_terminal = self._choose_random_element(self.term_set)
            node_to_mutate.value = new_terminal

    def _subtree_mutation(self, max_depth: int = 3):

        all_nodes = self._collect_all_nodes(self.root)
        
        if not all_nodes:
            return
        
        # Choose a random node whose subtree will be replaced
        node_to_replace = random.choice(all_nodes)
        
        # Generate a new random subtree
        new_subtree = self._random_init_recursive(0, max_depth, constant.GROW)
        
        # Replace the node's value and children
        node_to_replace.value = new_subtree.value
        node_to_replace.next = new_subtree.next

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
