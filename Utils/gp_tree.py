from .gp_node import GPNode
from .gp_function import GPFunction
import random
from utils import constant
from typing import List, Union, Iterable

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

        self.root = self._random_init_recursive(min_d, max_d, method.lower() )
        return self.root


    def _random_init_recursive(self, min_d: int, max_d: int, method: str) -> GPNode:

        if min_d > 0:

            func = self._choose_random_element(self.func_set)
            subtree = [self._random_init_recursive(min_d - 1,max_d - 1, method) for _ in range(func.arity)]
            return GPNode(func, next=subtree)

        if (max_d == 0) or (method == constant.GROW and
            random.random() < len(self.term_set) / (len(self.term_set) + len(self.func_set))):

            terminal_value = self._choose_random_element(self.term_set)
            return GPNode(terminal_value)

        func = self._choose_random_element(self.func_set)
        subtree = [self._random_init_recursive(0,max_d - 1, method) for _ in range(func.arity)]

        return GPNode(func, next=subtree)
        
    @staticmethod
    def _choose_random_element(ele_list):
        return random.choice(ele_list)

    def eval_tree(self):
        pass 

    def prefix_rep(self):
        pass 

    def copy(self):
        pass

    def mutate_point(self):
        pass 

    def mutate_subtree(self):
        pass 

    def __repr__(self):
        return self._prefix(self.root)

    def _prefix(self, node):

        if node is None:
            return "<empty tree>"

        # Terminal
        if not node.is_function():
            return str(node.value)

        # Function
        func_name = node.value.name
        subtree = " ".join(self._prefix(child_node) for child_node in node.next)
        return f"({func_name} {subtree})"
