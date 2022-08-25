import dto


_nodes = [dto.Node(id=f'my_test_node{i}', title=f'My Test Node #{i}', description=f'Some notes about node {i}',
                   actions=[f'node{i}_action1', f'node{i}_action2'])
          for i in range(4)]


def get_nodes():
    return _nodes


def get_node_with_items(n: int):
    items = [dto.NodeItem(phone_id=1000 + i + n * 100, number=f'+19251001{n}0{i}') for i in range(5)]
    return dto.NodeWithItems(node=_nodes[n], items=items)
