from gp_node import GPNode
from gp_function import GPFunction
import random
from typing import List, Union

class GPTree:

    def __init__(self,root = None):
        self.root = root if root is not None else GPNode()

    def random_init(self,func_set: List[GPFunction], 
                 term_set: List, 
                 max_d: int, 
                 method: str) -> GPNode:
        
        if max_d == 0 or (method == 'grow' and 
                      random.random() < len(term_set) / (len(term_set) + len(func_set))):
        # Choose a random terminal
            expr = self._choose_random_element(term_set)
            return GPNode(expr)
    
        else:
            # Choose a random function
            func = self._choose_random_element(func_set)
            
            # Generate child nodes for each argument
            children = []
            for i in range(func.arity):
                arg = self.random_init(func_set, term_set, max_d - 1, method)
                children.append(arg)
            
            # Create function node with children
            return GPNode(func, next=children)
        

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