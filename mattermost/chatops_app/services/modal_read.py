import json
from typing import List, Dict, Optional, Union


class ModalUtilsError(Exception):
    pass


def recursive_search(node, value, check_func):
    """
    node - where to search
    value - what to search
    check_func - how to check:
        check_func(node, value) -> bool

    Returns: dict node if found otherwise None
    """
    if isinstance(node, Dict):
        # Base case
        if check_func(node, value):
            return node

        # Recursive case
        inner_nodes = [i for i in node.values() if isinstance(i, (Dict, List))]
        if not inner_nodes:
            return
        return recursive_search(inner_nodes, value, check_func)

    # Recursive case
    elif isinstance(node, List):
        for i in node:
            result = recursive_search(i, value, check_func)
            if result:
                return result

    # number, string, boolean, None
    return


def find_by_id(node, node_id: str) -> Optional[Dict]:
    """
    Recursively find dict node with defined block_id/action_id
    """
    return recursive_search(
        node,
        node_id,
        lambda x, x_id: x_id in (x.get('block_id'), x.get('action_id'))
    )


def find_by_key(node, key: str) -> Union[Dict, List, str, int, bool, None]:
    """
    Recursively find the value of defined key
    """
    res = recursive_search(node, key, lambda x, x_id: x_id in x)
    if res:
        return res[key]


def get_value_for_key(node, key: str):
    """
    Find block with defined id. If found return value of key "value" inside it, otherwise return None
    """
    block = find_by_key(node, key)
    if block:
        return find_by_key(block, 'value')
