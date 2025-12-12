from .gp_function import GPFunction

class GPNode:

    def __init__(self, 
                 value,
                 next=None,
                 is_learnable=False):
        """
        Initialize a GP Node.
        Args:
            value: Either a GPFunction or a terminal value (constant/variable)
            next: List of child nodes (for function nodes)
            is_learnable: True if this is a learnable constant (ERC), False for variables
        """
        self.value = value
        self.next = next if next is not None else []
        self.is_learnable = is_learnable

    def is_function(self):
        return isinstance(self.value, GPFunction)
    
    def is_terminal(self):
        return not self.is_function()
    
    def is_learnable_constant(self):
        """Check if this node is a learnable constant (ERC)."""
        return self.is_terminal() and self.is_learnable
    
    def is_variable(self):
        """Check if this node is a variable (non-learnable ter~minal)."""
        return self.is_terminal() and not self.is_learnable
    
    def arity(self):
        return self.value.arity if self.is_function() else 0

