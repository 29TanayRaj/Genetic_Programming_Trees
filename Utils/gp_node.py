from gp_function import GPFunction

class GPNode:

    def __init__(self,value,next=None):

        self.value = value
        self.next = next if next is not None else []

    def is_function(self):
        return isinstance(self.value,GPFunction)
    
    def arity(self):
        return self.value.arity if self.is_function() else 0
