from typing import Tuple, List


def tree_to_dot(tree_repr: str) -> str:
    """
    Convert GPTree prefix expression (__repr__) into DOT graph.
    """
    tokens = _tokenize(tree_repr)
    node_id_counter = [0]
    dot_lines = ["digraph GPTree {", "    node [shape=circle];"]

    _, root_id = _parse(tokens, dot_lines, node_id_counter)

    dot_lines.append("}")
    return "\n".join(dot_lines)


def _tokenize(expr: str) -> List[str]:
    """
    Tokenize the prefix S-expression.
    """
    token_pattern = r'\(|\)|[^\s()]+'
    return re.findall(token_pattern, expr)


def _parse(tokens: List[str], dot: List[str], counter: List[int]) -> Tuple[int, int]:
    """
    Recursive descent parser:
    returns (current_position, node_id)
    """
    if not tokens:
        raise ValueError("Invalid prefix expression")

    token = tokens.pop(0)

    # Terminal leaf node
    if token != "(":
        node_id = counter[0]
        dot.append(f'    {node_id} [label="{token}"];')
        counter[0] += 1
        return tokens, node_id

    # Function node
    func_name = tokens.pop(0)
    node_id = counter[0]
    dot.append(f'    {node_id} [label="{func_name}"];')
    counter[0] += 1

    # Parse children until ")"
    while tokens[0] != ")":
        tokens, child_id = _parse(tokens, dot, counter)
        dot.append(f"    {node_id} -> {child_id};")

    tokens.pop(0)  # remove ")"
    return tokens, node_id
