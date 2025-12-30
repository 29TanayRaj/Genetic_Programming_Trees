import random
from utils.gp_tree import GPTree
from utils import constant

def subtree_crossover(parent1: GPTree, parent2: GPTree) -> GPTree:
    """
    Performs subtree crossover between two parents to produce a new child.
    
    1. Select a random crossover point (node) in parent1.
    2. Select a random crossover point (node) in parent2.
    3. Create a copy of parent1.
    4. Replace the subtree at the crossover point in the copy with a copy of 
       the subtree from parent2.
       
    Args:
        parent1: The first parent GPTree (receives the subtree)
        parent2: The second parent GPTree (donates the subtree)
        
    Returns:
        A new GPTree instance representing the child.
    """
    # Create a copy of parent1 to be the base of the child
    child = parent1.copy()
    
    # Collect all nodes from the child (which is a copy of parent1)
    child_nodes = child._collect_all_nodes(child.root)
    if not child_nodes:
        return child # Should not happen for valid trees
        
    # Select crossover point in child
    destination_node = random.choice(child_nodes)
    
    # Collect all nodes from parent2
    parent2_nodes = parent2._collect_all_nodes(parent2.root)
    if not parent2_nodes:
        return child # Parent2 is empty? Return parent1 copy
        
    # Select crossover point in parent2 (source of the new subtree)
    source_node = random.choice(parent2_nodes)
    
    # Create a copy of the source subtree to avoid modifying parent2 later
    # We can use the internal _copy_node method from the child instance 
    # since it's a static utility effectively, or we need to access it publicly.
    # GPTree._copy_node is technically internal but we can use it on the instance.
    new_subtree = child._copy_node(source_node)
    
    # Replace the destination node's content with the new subtree
    # Changing values in place works because we are modifying the 'child' tree objects
    destination_node.value = new_subtree.value
    destination_node.next = new_subtree.next
    destination_node.is_learnable = new_subtree.is_learnable
    
    return child
