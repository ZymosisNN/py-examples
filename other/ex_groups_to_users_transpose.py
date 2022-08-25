import json
from itertools import chain

in_data = {
    'A': ['1111', '2222', '3333', '4444'],
    'B': ['1111', '2222', '3333'],
    'C': ['2222', '3333'],
    'D': ['4444'],
    'E': [],
}

# Expect this
out_data = {
    '1111': ['A', 'B'],
    '2222': ['A', 'B', 'C'],
    '3333': ['A', 'B', 'C'],
    '4444': ['A', 'D'],
}


def transpose(in_data: dict) -> dict:
    total = set(chain(*in_data.values()))
    return {user: [g_name for g_name, g_users in in_data.items() if user in g_users] for user in total}


print(json.dumps(in_data, indent=4))

print('------')
converted = transpose(in_data)
print(json.dumps(converted, indent=4))

print('------')
converted = transpose(converted)
print(json.dumps(converted, indent=4))
