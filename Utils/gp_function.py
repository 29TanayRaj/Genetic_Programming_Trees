class GPFunction:

    def __init__(self, name: str, expression: callable, arity: int):
        self.name = name
        self.expression = expression
        self.arity = arity

    def __call__(self, *args):

        return self.expression(*args)

    def __repr__(self)->str:
        return f"GPFunction(name='{self.name}', arity={self.arity})"

